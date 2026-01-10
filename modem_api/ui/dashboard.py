from __future__ import annotations

import html
import json
import os
import time
import uuid
import io
import contextlib
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, List
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from core.task_manager.runner import new_task
from core.router.latent_mode.latent_executor import latent_execute

# ---- Config ----
TRACE_DIR = os.path.join("core", "research", "trace_store")
MAX_RECENT_TRACES = 25
EXECUTOR = ThreadPoolExecutor(max_workers=1)  # keep simple: 1 job at a time (safe for stdout capture)

app = FastAPI()


# ---- Research function import (adjust if needed) ----
def _run_research(prompt: str) -> str:
    """
    Runs a research session and returns the text result.
    This should call the same underlying function your CLI uses.
    """
    # Try likely function names without hard failing the dashboard.
    try:
        from core.research.research_session import run_deep_research  # type: ignore
        return run_deep_research(prompt)
    except Exception:
        pass

    try:
        # If you have a different entrypoint, swap this to match.
        from core.research.research_session import run_research  # type: ignore
        return run_research(prompt)
    except Exception as e:
        raise RuntimeError(
            "Could not import research runner. "
            "Update _run_research() to call your project’s research entrypoint."
        ) from e


def _run_task_wrapper(prompt: str) -> str:
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        res = new_task(prompt, latent_mode=True)
        print("\nFinal Return:", res)
    return f.getvalue()

def _run_simulate_wrapper(prompt: str) -> str:
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        res = latent_execute(prompt)
        print("\nLatent Execution Result:", res)
    return f.getvalue()


# ---- Jobs ----
@dataclass
class Job:
    id: str
    kind: str
    status: str  # queued|running|done|error
    created_at: float
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    prompt: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    trace_file: Optional[str] = None


JOBS: Dict[str, Job] = {}


def _list_traces() -> List[str]:
    if not os.path.exists(TRACE_DIR):
        return []
    files = [f for f in os.listdir(TRACE_DIR) if f.startswith("replay_") and f.endswith(".json")]
    # sort newest-first by mtime
    files.sort(key=lambda f: os.path.getmtime(os.path.join(TRACE_DIR, f)), reverse=True)
    return files


def _guess_new_trace(before: set[str], after: set[str]) -> Optional[str]:
    # Return newest added file if any
    added = list(after - before)
    if not added:
        return None
    added.sort(key=lambda f: os.path.getmtime(os.path.join(TRACE_DIR, f)), reverse=True)
    return added[0]


def _run_job(job_id: str) -> None:
    job = JOBS[job_id]
    job.status = "running"
    job.started_at = time.time()

    # Best-effort trace detection: compare directory before/after.
    before = set(_list_traces())
    try:
        result = ""
        if job.kind == "research":
            result = _run_research(job.prompt or "")
        elif job.kind == "task":
            result = _run_task_wrapper(job.prompt or "")
        elif job.kind == "simulation":
            result = _run_simulate_wrapper(job.prompt or "")

        job.result = result
        job.status = "done"
    except Exception as e:
        job.status = "error"
        job.error = str(e)
    finally:
        job.finished_at = time.time()
        after = set(_list_traces())
        # Only research produces traces usually, but we check anyway
        job.trace_file = _guess_new_trace(before, after)


# ---- HTML helpers ----
def _page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 24px; }}
    .card {{ max-width: 980px; border: 1px solid #ddd; border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
    textarea {{ width: 100%; min-height: 80px; padding: 10px; }}
    button {{ padding: 10px 14px; border-radius: 10px; border: 1px solid #ccc; cursor: pointer; }}
    code, pre {{ background: #f6f6f6; padding: 10px; border-radius: 10px; overflow-x: auto; }}
    .muted {{ color: #555; }}
    a {{ text-decoration: none; }}
    ul {{ padding-left: 20px; }}
    .row {{ display: flex; gap: 12px; flex-wrap: wrap; }}
    .row > * {{ flex: 1; min-width: 280px; }}
    h2 {{ margin-top: 0; }}
  </style>
</head>
<body>
{body}
</body>
</html>"""


def _safe_trace_name(name: str) -> str:
    base = os.path.basename(name)
    if base != name:
        # disallow path traversal
        raise HTTPException(status_code=400, detail="Invalid trace name")
    if not (base.startswith("replay_") and base.endswith(".json")):
        raise HTTPException(status_code=400, detail="Invalid trace filename")
    return base


# ---- Routes ----
@app.get("/", response_class=HTMLResponse)
async def home():
    recent = _list_traces()[:MAX_RECENT_TRACES]
    traces_html = "".join(
        f'<li><a href="/trace/{html.escape(t)}">{html.escape(t)}</a></li>'
        for t in recent
    ) or '<li class="muted">No traces yet.</li>'

    body = f"""
    <h1>MoDEM Dashboard</h1>

    <div class="row">
      <!-- Run Research -->
      <div class="card">
        <h2>Run Research</h2>
        <p class="muted">Starts a deep research session.</p>
        <textarea id="prompt_research" placeholder="Enter a research prompt..."></textarea>
        <div style="margin-top: 10px;">
          <button onclick="startJob('research', 'prompt_research', 'job_research')">Run Research</button>
        </div>
        <div id="job_research" style="margin-top: 12px;"></div>
      </div>

      <!-- Run Task -->
      <div class="card">
        <h2>Run Task</h2>
        <p class="muted">Executes a new task (SAP + MAPLE).</p>
        <textarea id="prompt_task" placeholder="Enter task description..."></textarea>
        <div style="margin-top: 10px;">
          <button onclick="startJob('task', 'prompt_task', 'job_task')">Run Task</button>
        </div>
        <div id="job_task" style="margin-top: 12px;"></div>
      </div>

       <!-- Run Simulation -->
      <div class="card">
        <h2>Simulate</h2>
        <p class="muted">Run latent execution (simulation).</p>
        <textarea id="prompt_sim" placeholder="Enter simulation query..."></textarea>
        <div style="margin-top: 10px;">
          <button onclick="startJob('simulation', 'prompt_sim', 'job_sim')">Simulate</button>
        </div>
        <div id="job_sim" style="margin-top: 12px;"></div>
      </div>
    </div>

    <div class="row">
      <div class="card">
        <h2>Recent Traces</h2>
        <ul>{traces_html}</ul>
        <p class="muted"><a href="/api/traces">API: /api/traces</a></p>
      </div>

      <div class="card">
        <h2>Status</h2>
        <ul>
          <li><a href="/health">Health Check</a></li>
        </ul>
      </div>
    </div>

    <script>
      async function startJob(kind, inputId, outputId) {{
        const prompt = document.getElementById(inputId).value.trim();
        if (!prompt) {{
          alert("Enter a prompt first.");
          return;
        }}
        const el = document.getElementById(outputId);
        el.innerHTML = "<p>Starting " + kind + "...</p>";

        const endpoint = "/api/" + kind;
        const resp = await fetch(endpoint, {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ prompt }})
        }});
        const data = await resp.json();
        if (!resp.ok) {{
          el.innerHTML = "<pre>" + (data.detail || JSON.stringify(data)) + "</pre>";
          return;
        }}
        pollJob(data.job_id, outputId);
      }}

      async function pollJob(jobId, outputId) {{
        const el = document.getElementById(outputId);
        el.innerHTML = "<p>Job " + jobId + " running...</p>";
        while (true) {{
          const resp = await fetch("/api/jobs/" + jobId);
          const job = await resp.json();
          if (job.status === "done") {{
            let link = "";
            if (job.trace_file) {{
              link = '<p><a href="/trace/' + job.trace_file + '">View trace: ' + job.trace_file + '</a></p>';
            }}
            el.innerHTML = link + "<h3>Result</h3><pre>" + (job.result || "") + "</pre>";
            break;
          }}
          if (job.status === "error") {{
            el.innerHTML = "<h3>Error</h3><pre>" + (job.error || "unknown") + "</pre>";
            break;
          }}
          await new Promise(r => setTimeout(r, 750));
        }}
      }}
    </script>
    """
    return _page("MoDEM Dashboard", body)


@app.get("/health")
async def health_check():
    return {"status": "OK"}


@app.post("/api/research")
async def api_research(payload: Dict[str, Any]):
    return _create_job("research", payload)

@app.post("/api/task")
async def api_task(payload: Dict[str, Any]):
    return _create_job("task", payload)

@app.post("/api/simulation")
async def api_simulation(payload: Dict[str, Any]):
    return _create_job("simulation", payload)

def _create_job(kind: str, payload: Dict[str, Any]):
    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing prompt")

    job_id = uuid.uuid4().hex
    job = Job(
        id=job_id,
        kind=kind,
        status="queued",
        created_at=time.time(),
        prompt=prompt,
    )
    JOBS[job_id] = job
    EXECUTOR.submit(_run_job, job_id)
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}")
async def api_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return asdict(job)


@app.get("/api/traces")
async def api_traces():
    if not os.path.exists(TRACE_DIR):
        return JSONResponse(
            content={"error": "Trace directory not found", "path": TRACE_DIR},
            status_code=404,
        )
    files = _list_traces()[:MAX_RECENT_TRACES]
    items = []
    for f in files:
        p = os.path.join(TRACE_DIR, f)
        items.append(
            {
                "name": f,
                "mtime": os.path.getmtime(p),
                "size": os.path.getsize(p),
                "url": f"/trace/{f}",
                "raw_url": f"/api/trace/{f}",
            }
        )
    return {"trace_dir": TRACE_DIR, "traces": items}


@app.get("/api/trace/{name}")
async def api_trace(name: str):
    base = _safe_trace_name(name)
    path = os.path.join(TRACE_DIR, base)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Trace not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/trace/{name}", response_class=HTMLResponse)
async def trace_view(name: str):
    base = _safe_trace_name(name)
    path = os.path.join(TRACE_DIR, base)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Trace not found")

    with open(path, "r", encoding="utf-8") as f:
        trace = json.load(f)

    prompt = html.escape(str(trace.get("prompt", "")))
    ts = html.escape(str(trace.get("timestamp", "")))
    result = html.escape(str(trace.get("result", "")))

    steps = trace.get("steps") or []
    steps_html = ""
    if steps:
        pretty_steps = html.escape(json.dumps(steps, indent=2))
        steps_html = f"<h3>Steps</h3><pre>{pretty_steps}</pre>"

    raw = html.escape(json.dumps(trace, indent=2))

    body = f"""
    <p><a href="/">← Back</a></p>
    <div class="card">
      <h2>{html.escape(base)}</h2>
      <p><b>Timestamp:</b> {ts}</p>
      <h3>Prompt</h3>
      <pre>{prompt}</pre>
      {steps_html}
      <h3>Result</h3>
      <pre>{result}</pre>
      <p class="muted"><a href="/api/trace/{html.escape(base)}">Raw JSON</a></p>
    </div>

    <div class="card">
      <h3>Raw</h3>
      <pre>{raw}</pre>
    </div>
    """
    return _page(f"Trace: {base}", body)
