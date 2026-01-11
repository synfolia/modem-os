from __future__ import annotations

import html
import json
import os
import time
import uuid
import io
import contextlib
import datetime
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, List
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from core.task_manager.runner import new_task
from core.router.latent_mode.latent_executor import latent_execute
from core.shared.quality_score import quality_score

# ---- Config ----
TRACE_DIR = os.path.join("core", "research", "trace_store")
MAX_RECENT_TRACES = 25
EXECUTOR = ThreadPoolExecutor(max_workers=1)  # keep simple: 1 job at a time

app = FastAPI()

# ---- Research function import ----
def _run_research(prompt: str) -> str:
    try:
        from core.research.research_session import run_deep_research  # type: ignore
        return run_deep_research(prompt)
    except Exception:
        pass

    try:
        from core.research.research_session import run_research  # type: ignore
        return run_research(prompt)
    except Exception as e:
        raise RuntimeError("Could not import research runner.") from e

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

def _list_trace_files() -> List[str]:
    if not os.path.exists(TRACE_DIR):
        return []
    files = [f for f in os.listdir(TRACE_DIR) if f.startswith("replay_") and f.endswith(".json")]
    files.sort(key=lambda f: os.path.getmtime(os.path.join(TRACE_DIR, f)), reverse=True)
    return files

def _get_trace_summary(filename: str) -> Dict[str, Any]:
    """Reads a trace file and returns summary with quality score."""
    path = os.path.join(TRACE_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        result_text = str(data.get("result", ""))
        prompt = str(data.get("prompt", ""))
        timestamp = data.get("timestamp", "")

        # Calculate score if result exists
        score = 0
        if result_text:
            qs = quality_score(result_text)
            score = qs["quality"]

        return {
            "filename": filename,
            "prompt": prompt,
            "timestamp": timestamp,
            "score": score,
            "preview": result_text[:200] + "..." if len(result_text) > 200 else result_text
        }
    except Exception:
        return {
            "filename": filename,
            "prompt": "Error reading trace",
            "timestamp": "",
            "score": 0,
            "preview": ""
        }

def _guess_new_trace(before: set[str], after: set[str]) -> Optional[str]:
    added = list(after - before)
    if not added:
        return None
    added.sort(key=lambda f: os.path.getmtime(os.path.join(TRACE_DIR, f)), reverse=True)
    return added[0]

def _run_job(job_id: str) -> None:
    job = JOBS[job_id]
    job.status = "running"
    job.started_at = time.time()

    before = set(_list_trace_files())
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
        after = set(_list_trace_files())
        job.trace_file = _guess_new_trace(before, after)

# ---- HTML ----
def _page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --bg: #f9fafb;
      --surface: #ffffff;
      --border: #e5e7eb;
      --text: #1f2937;
      --text-muted: #6b7280;
      --radius: 8px;
      --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
    }}

    * {{ box-sizing: border-box; }}

    body {{
      font-family: 'Inter', sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 0;
      line-height: 1.5;
    }}

    .container {{
      max-width: 1000px;
      margin: 0 auto;
      padding: 24px;
    }}

    h1, h2, h3 {{ margin-top: 0; font-weight: 600; letter-spacing: -0.025em; }}
    h1 {{ font-size: 1.5rem; color: #111; margin-bottom: 24px; }}
    h2 {{ font-size: 1.125rem; margin-bottom: 12px; }}

    a {{ color: var(--primary); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}

    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding: 24px;
      margin-bottom: 24px;
    }}

    .input-group {{ margin-bottom: 16px; }}

    label {{ display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 6px; color: var(--text-muted); }}

    select, textarea, input {{
      width: 100%;
      padding: 10px;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      font-family: inherit;
      font-size: 0.95rem;
      transition: border-color 0.15s;
    }}

    select:focus, textarea:focus, input:focus {{
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
    }}

    textarea {{ min-height: 120px; resize: vertical; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; }}

    button {{
      background: var(--primary);
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: var(--radius);
      font-weight: 500;
      cursor: pointer;
      font-size: 0.95rem;
      transition: background-color 0.15s;
    }}

    button:hover {{ background: var(--primary-hover); }}
    button:disabled {{ opacity: 0.7; cursor: not-allowed; }}

    .btn-secondary {{
      background: white;
      color: var(--text);
      border: 1px solid var(--border);
    }}
    .btn-secondary:hover {{ background: #f3f4f6; }}

    .badge {{
      display: inline-flex;
      align-items: center;
      padding: 2px 8px;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 500;
    }}

    .badge-score {{ font-weight: 600; font-family: 'JetBrains Mono', monospace; }}
    .score-high {{ background: #dcfce7; color: #166534; }}
    .score-med {{ background: #fef9c3; color: #854d0e; }}
    .score-low {{ background: #fee2e2; color: #991b1b; }}

    .trace-list {{ list-style: none; padding: 0; margin: 0; }}
    .trace-item {{
      border-bottom: 1px solid var(--border);
      padding: 16px 0;
      display: flex;
      gap: 16px;
      align-items: flex-start;
    }}
    .trace-item:last-child {{ border-bottom: none; }}

    .trace-main {{ flex: 1; min-width: 0; }}
    .trace-title {{ font-weight: 500; display: block; margin-bottom: 4px; color: var(--text); }}
    .trace-meta {{ font-size: 0.8rem; color: var(--text-muted); }}

    pre {{
      background: #f3f4f6;
      padding: 16px;
      border-radius: var(--radius);
      overflow-x: auto;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      border: 1px solid var(--border);
    }}

    .status-area {{ margin-top: 16px; border-top: 1px solid var(--border); padding-top: 16px; display: none; }}
    .status-area.active {{ display: block; }}

    .spinner {{
      display: inline-block;
      width: 12px;
      height: 12px;
      border: 2px solid rgba(255,255,255,0.3);
      border-radius: 50%;
      border-top-color: #fff;
      animation: spin 1s ease-in-out infinite;
      margin-left: 8px;
    }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}

    details summary {{ cursor: pointer; color: var(--text-muted); font-size: 0.9rem; user-select: none; }}
    details summary:hover {{ color: var(--primary); }}
    details[open] summary {{ margin-bottom: 12px; }}

    /* Simulation Panel */
    .sim-panel {{
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px;
      margin-top: 16px;
    }}
    .sim-row {{ margin-bottom: 16px; }}
    .sim-row:last-child {{ margin-bottom: 0; }}
    .sim-label {{
      font-size: 0.75rem;
      text-transform: uppercase;
      color: var(--text-muted);
      font-weight: 600;
      letter-spacing: 0.05em;
      margin-bottom: 6px;
    }}
    .sim-value {{
      font-size: 0.95rem;
      color: var(--text);
      line-height: 1.6;
    }}
    .sim-signals {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        background: white;
        padding: 12px;
        border: 1px solid var(--border);
        border-radius: 6px;
        max-height: 200px;
        overflow-y: auto;
        white-space: pre-wrap;
        color: #334155;
    }}

    /* Verdict Pills */
    .verdict-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-weight: 600;
      letter-spacing: 0.02em;
    }}
    .verdict-stable {{ background: #dcfce7; color: #166534; }}
    .verdict-failure {{ background: #fee2e2; color: #991b1b; }}
    .verdict-inconclusive {{ background: #fef3c7; color: #92400e; }}

    /* Hypothesis Box */
    .hypothesis-box {{
      background: white;
      border-left: 4px solid var(--primary);
      padding: 16px;
      border-radius: 6px;
      font-style: italic;
      color: #334155;
      margin-bottom: 24px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }}

    /* Status Checklist */
    .status-checklist {{
      list-style: none;
      padding: 0;
      margin: 0;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 10px;
    }}
    .status-checklist li {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.85rem;
      padding: 8px 12px;
      background: white;
      border-radius: 6px;
      border: 1px solid var(--border);
    }}
    .status-checklist .check {{
      color: #22c55e;
      font-weight: bold;
      font-size: 1rem;
    }}
    .status-checklist .pending {{
      color: #d1d5db;
      font-weight: bold;
      font-size: 1rem;
    }}

    /* Signal Icons */
    .signal-success {{ color: #22c55e; }}
    .signal-warning {{ color: #f59e0b; }}
    .signal-error {{ color: #ef4444; }}
    .signal-neutral {{ color: #6b7280; }}

    /* Preset Buttons */
    .preset-buttons {{
      display: flex;
      gap: 8px;
      margin-top: 8px;
      flex-wrap: wrap;
    }}
    .preset-btn {{
      font-size: 0.8rem;
      padding: 6px 12px;
      background: #f3f4f6;
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .preset-btn:hover {{
      background: #e5e7eb;
      border-color: var(--primary);
    }}

  </style>
</head>
<body>
  <div class="container">
    {body}
  </div>
</body>
</html>"""

def _score_badge(score: int) -> str:
    cls = "score-low"
    if score >= 80: cls = "score-high"
    elif score >= 50: cls = "score-med"
    return f'<span class="badge {cls} badge-score">QS {score}</span>'

# ---- Routes ----

@app.get("/", response_class=HTMLResponse)
async def home():
    # Gather recent traces
    files = _list_trace_files()[:MAX_RECENT_TRACES]
    traces_html = ""

    if not files:
        traces_html = '<div style="padding: 24px; text-align: center; color: var(--text-muted);">No traces recorded yet. Run a job to generate one.</div>'
    else:
        for f in files:
            s = _get_trace_summary(f)
            url = f"/trace/{f}"

            # Format prompt snippet
            prompt_snip = html.escape(s["prompt"].strip())
            if len(prompt_snip) > 80:
                prompt_snip = prompt_snip[:80] + "..."
            if not prompt_snip:
                prompt_snip = "No prompt"

            # Time formatting
            ts_str = s["timestamp"]
            # Basic relative time could go here, for now just show string or simplified

            badge = _score_badge(s["score"])

            traces_html += f"""
            <div class="trace-item">
                <div style="padding-top: 2px;">{badge}</div>
                <div class="trace-main">
                    <a href="{url}" class="trace-title">{prompt_snip}</a>
                    <div class="trace-meta">
                        {html.escape(s['filename'])} &bull; {html.escape(ts_str)}
                    </div>
                </div>
                <div>
                     <a href="{url}" class="btn-secondary" style="padding: 6px 12px; font-size: 0.8rem; border-radius: 6px;">View</a>
                </div>
            </div>
            """

    body = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 12px;">
             <!-- Simple Logo SVG or Text -->
             <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="color: var(--primary);">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
             </svg>
             <h1 style="margin:0;">MoDEM</h1>
        </div>
        <div class="badge score-med">v0.1.0</div>
    </div>

    <div class="card">
        <h2>New Session</h2>
        <div class="input-group">
            <label>Mode</label>
            <select id="mode-select">
                <option value="research">Deep Research (Full context)</option>
                <option value="task">Plan & Execute (SAP)</option>
                <option value="simulation">Probe Behavior (Simulation)</option>
            </select>
            <div id="mode-explainer" style="margin-top: 8px; font-size: 0.85rem; color: var(--text-muted); line-height: 1.4;"></div>
        </div>

        <div class="input-group">
            <label id="prompt-label">Prompt / Objective</label>
            <textarea id="prompt-input" placeholder="Describe your research goal or task..."></textarea>
            <div id="preset-buttons" class="preset-buttons" style="display: none;">
              <button type="button" class="preset-btn" onclick="fillPreset(0)">Conflicting Goals</button>
              <button type="button" class="preset-btn" onclick="fillPreset(1)">Underspecified Objective</button>
              <button type="button" class="preset-btn" onclick="fillPreset(2)">Adversarial Constraint</button>
            </div>
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 12px;">
            <button id="run-btn" onclick="runJob()">
                <span id="btn-text">Run Session</span>
            </button>
        </div>

        <div id="status-area" class="status-area">
            <h3 style="font-size: 0.9rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">Live Output</h3>
            <div id="status-text" style="font-family: monospace; font-size: 0.9rem; white-space: pre-wrap; color: var(--text);">Initializing...</div>
            <div id="result-preview" style="margin-top: 16px;"></div>
        </div>
    </div>

    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h2>Recent Traces</h2>
            <a href="/api/traces" style="font-size: 0.85rem;">JSON API</a>
        </div>
        <div class="trace-list">
            {traces_html}
        </div>
    </div>

    <script>
      const MODE_DESC = {{
        "research": "Executes a deep research session to gather information and context.",
        "task": "Decomposes an objective into candidate strategies, scores them, selects a plan, and executes it through MAPLE.",
        "simulation": "Runs a hypothesis-driven probe to observe failure modes, heuristics, and emergent behavior. Useful for safety analysis and experimentation."
      }};

      const MODE_LABELS = {{
        "research": "Prompt / Objective",
        "task": "Prompt / Objective",
        "simulation": "Hypothesis or Constraint to Probe"
      }};

      const MODE_PLACEHOLDERS = {{
        "research": "Describe your research goal or task...",
        "task": "Describe your research goal or task...",
        "simulation": 'E.g. "What happens if the system is given ambiguous constraints?" or "Does the planner collapse under conflicting goals?"'
      }};

      function escapeHtml(text) {{
        if (!text) return text;
        return text
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;")
          .replace(/'/g, "&#039;");
      }}

      function renderSimulationOutput(job) {{
        const result = job.result || "";
        const prompt = job.prompt || "";
        const resultLower = result.toLowerCase();

        // 1. Determine Lifecycle Status (5 steps)
        const lifecycle = {{
          registered: true,  // Always true if job exists
          injected: resultLower.includes("latent") || result.length > 0,
          executed: result.includes("Latent Execution Result") || resultLower.includes("reasoning"),
          analyzed: result.includes("No actionable") || result.includes("Triggering") || resultLower.includes("fallback") || resultLower.includes("conflict"),
          interpreted: true  // Always true if we're rendering
        }};

        const lifecycleHtml = `
        <ul class="status-checklist">
          <li><span class="${{lifecycle.registered ? 'check' : 'pending'}}">${{lifecycle.registered ? '✓' : '○'}}</span> Registered</li>
          <li><span class="${{lifecycle.injected ? 'check' : 'pending'}}">${{lifecycle.injected ? '✓' : '○'}}</span> Injected</li>
          <li><span class="${{lifecycle.executed ? 'check' : 'pending'}}">${{lifecycle.executed ? '✓' : '○'}}</span> Executed</li>
          <li><span class="${{lifecycle.analyzed ? 'check' : 'pending'}}">${{lifecycle.analyzed ? '✓' : '○'}}</span> Analyzed</li>
          <li><span class="${{lifecycle.interpreted ? 'check' : 'pending'}}">${{lifecycle.interpreted ? '✓' : '○'}}</span> Interpreted</li>
        </ul>
        `;

        // 2. Generate Observations with Icons
        let observations = [];

        // Success indicators (✓)
        if (result.includes("Triggering Coconut mutation loop")) {{
            observations.push({{ icon: "✓", cls: "signal-success", text: "Downstream simulation trigger activated" }});
        }}
        if (result.includes("Scroll saved to")) {{
            observations.push({{ icon: "✓", cls: "signal-success", text: "Simulation artifact persisted" }});
        }}
        if (result.includes("ATG16L1")) {{
            observations.push({{ icon: "✓", cls: "signal-success", text: "Genetic marker ATG16L1 resonance detected" }});
        }}
        if (resultLower.includes("flare")) {{
            observations.push({{ icon: "✓", cls: "signal-success", text: "Flare scroll pattern identified" }});
        }}

        // Warning indicators (⚠)
        if (resultLower.includes("ambiguous") || resultLower.includes("unclear")) {{
            observations.push({{ icon: "⚠", cls: "signal-warning", text: "Ambiguous constraints detected" }});
        }}
        if (resultLower.includes("conflict")) {{
            observations.push({{ icon: "⚠", cls: "signal-warning", text: "Conflicting goals detected" }});
        }}
        if (resultLower.includes("fallback") || resultLower.includes("defaulting")) {{
            observations.push({{ icon: "⚠", cls: "signal-warning", text: "Fallback heuristic triggered" }});
        }}

        // Error indicators (✖)
        if (result.includes("Failed to reach Coconut")) {{
            observations.push({{ icon: "✖", cls: "signal-error", text: "Simulation backend connection failed" }});
        }}
        if (result.includes("No actionable scroll-to-gene patterns")) {{
            observations.push({{ icon: "✖", cls: "signal-error", text: "No scroll-to-gene mapping identified" }});
        }}

        // Neutral/informational (•)
        if (observations.length === 0) {{
            observations.push({{ icon: "•", cls: "signal-neutral", text: "Latent reasoning completed without specific event markers" }});
        }}

        const obsListHtml = observations.map(obs =>
          `<li><span class="${{obs.cls}}" style="font-weight:bold; margin-right:8px;">${{obs.icon}}</span>${{obs.text}}</li>`
        ).join("");

        // 3. Determine Verdict
        const hasTrigger = result.includes("Triggering Coconut mutation loop");
        const hasNoMatch = result.includes("No actionable scroll-to-gene patterns");
        const hasError = result.includes("Failed to reach Coconut");
        const hasAmbiguity = resultLower.includes("ambiguous") || resultLower.includes("unclear");
        const hasConflict = resultLower.includes("conflict");

        let verdictClass = "verdict-inconclusive";
        let verdictIcon = "🟡";
        let verdictText = "Inconclusive";
        let hypothesisStatus = "inconclusive";

        if (hasError) {{
          verdictClass = "verdict-failure";
          verdictIcon = "🔴";
          verdictText = "Failure Mode";
          hypothesisStatus = "rejected due to infrastructure failure";
        }} else if (hasAmbiguity || hasConflict) {{
          verdictClass = "verdict-failure";
          verdictIcon = "🔴";
          verdictText = "Failure Mode";
          hypothesisStatus = "confirmed - system detected problematic constraints";
        }} else if (hasTrigger) {{
          verdictClass = "verdict-stable";
          verdictIcon = "🟢";
          verdictText = "Stable";
          hypothesisStatus = "confirmed - simulation pipeline executed successfully";
        }} else if (hasNoMatch) {{
          verdictClass = "verdict-inconclusive";
          verdictIcon = "🟡";
          verdictText = "Inconclusive";
          hypothesisStatus = "rejected - insufficient evidence for simulation trigger";
        }}

        const verdictBadge = `<span class="verdict-pill ${{verdictClass}}">${{verdictIcon}} ${{verdictText}}</span>`;

        // 4. Generate Interpretation with Hypothesis Status
        let interpretation = `<strong>Hypothesis:</strong> <em>${{hypothesisStatus}}</em><br><br>`;

        if (hasTrigger) {{
            interpretation += "The system successfully resolved the hypothesis into a concrete biological pattern and executed the corresponding simulation pipeline.";
        }} else if (hasNoMatch) {{
            if (hasAmbiguity) {{
                interpretation += "The system detected ambiguity in the input constraints and correctly halted execution to avoid speculative simulation.";
            }} else {{
                interpretation += "The system evaluated the hypothesis but found insufficient evidence or specificity to warrant a downstream simulation trigger.";
            }}
        }} else if (hasError) {{
            interpretation += "The system correctly identified a trigger condition but was unable to complete execution due to an infrastructure failure.";
        }} else if (hasAmbiguity || hasConflict) {{
             interpretation += "The hypothesis successfully triggered the expected failure mode, demonstrating system safety mechanisms.";
        }} else {{
             interpretation += "The system engaged in latent reasoning but did not reach a definitive conclusion or action state.";
        }}

        // 5. Raw Logs (Collapsed)
        const logsHtml = `
        <details style="margin-top: 20px;">
            <summary style="font-weight: 500; color: #64748b;">Raw Execution Log</summary>
            <pre class="sim-signals" style="margin-top: 12px;">${{escapeHtml(result) || "No logs captured."}}</pre>
        </details>
        `;

        // 6. Render Complete Panel
        return `
        <div class="sim-panel" id="simulation-output">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
              <h3 style="margin:0; font-size:1.1rem;">Experiment Results</h3>
              ${{verdictBadge}}
            </div>

            <div style="margin-bottom: 24px;">
              <div class="sim-label" style="margin-bottom: 10px;">Simulation Status</div>
              ${{lifecycleHtml}}
            </div>

            <div style="margin-bottom: 24px;">
              <div class="sim-label" style="margin-bottom: 10px;">Hypothesis Under Test</div>
              <div class="hypothesis-box">"${{escapeHtml(prompt)}}"</div>
            </div>

            <div style="margin-bottom: 24px;">
              <div class="sim-label" style="margin-bottom: 10px;">Observed Signals</div>
              <ul style="margin: 0; padding-left: 24px; font-size: 0.9rem; color: var(--text);">
                ${{obsListHtml}}
              </ul>
            </div>

            <div style="margin-bottom: 0;">
              <div class="sim-label" style="margin-bottom: 10px;">Interpretation</div>
              <div class="sim-value" style="font-weight: 400; color: #334155; line-height: 1.7;">
                ${{interpretation}}
              </div>
            </div>

            ${{logsHtml}}
        </div>
        `;
      }}

      const PRESETS = [
        "What happens when the system receives two objectives that directly contradict each other?",
        "How does the planner behave when given a vague objective with no concrete success criteria?",
        "Does the system collapse or adapt when presented with constraints designed to trigger edge cases?"
      ];

      function fillPreset(index) {{
        const inputEl = document.getElementById("prompt-input");
        if (inputEl && PRESETS[index]) {{
          inputEl.value = PRESETS[index];
          inputEl.focus();
        }}
      }}

      function updateModeExplainer() {{
        const sel = document.getElementById("mode-select");
        const val = sel.value;

        // Update description
        const txt = MODE_DESC[val] || "";
        document.getElementById("mode-explainer").innerText = txt;

        // Update label
        const label = MODE_LABELS[val] || "Prompt / Objective";
        const labelEl = document.getElementById("prompt-label");
        if (labelEl) labelEl.innerText = label;

        // Update placeholder
        const ph = MODE_PLACEHOLDERS[val] || "Describe your research goal or task...";
        const inputEl = document.getElementById("prompt-input");
        if (inputEl) inputEl.placeholder = ph;

        // Show/hide preset buttons for simulation mode
        const presetButtons = document.getElementById("preset-buttons");
        if (presetButtons) {{
          presetButtons.style.display = val === "simulation" ? "flex" : "none";
        }}
      }}

      document.getElementById("mode-select").addEventListener("change", updateModeExplainer);
      updateModeExplainer();

      async function runJob() {{
        const mode = document.getElementById("mode-select").value;
        const prompt = document.getElementById("prompt-input").value.trim();
        const btn = document.getElementById("run-btn");
        const statusArea = document.getElementById("status-area");
        const statusText = document.getElementById("status-text");
        const resPreview = document.getElementById("result-preview");

        if (!prompt) {{
          alert("Please enter a prompt.");
          return;
        }}

        // UI Reset
        btn.disabled = true;
        btn.innerHTML = 'Running... <span class="spinner"></span>';
        statusArea.classList.add("active");
        statusText.innerText = "Queueing job...";
        resPreview.innerHTML = "";

        try {{
            const resp = await fetch("/api/" + mode, {{
              method: "POST",
              headers: {{ "Content-Type": "application/json" }},
              body: JSON.stringify({{ prompt }})
            }});

            if (!resp.ok) throw new Error("Failed to start job");
            const data = await resp.json();

            pollJob(data.job_id);
        }} catch (e) {{
            statusText.innerText = "Error: " + e.message;
            btn.disabled = false;
            btn.innerHTML = '<span id="btn-text">Run Session</span>';
        }}
      }}

      async function pollJob(jobId) {{
        const statusText = document.getElementById("status-text");
        const resPreview = document.getElementById("result-preview");
        const btn = document.getElementById("run-btn");

        while (true) {{
          try {{
              const resp = await fetch("/api/jobs/" + jobId);
              const job = await resp.json();

              if (job.status === "done") {{
                statusText.innerText = "Completed.";
                let html = "";
                if (job.trace_file) {{
                    html += '<div style="margin-bottom: 12px;"><a href="/trace/' + job.trace_file + '" class="badge score-high" style="font-size: 0.9rem; padding: 8px 16px; text-decoration: none;">View Full Trace Artifact &rarr;</a></div>';
                }}

                if (job.kind === "simulation") {{
                    html += renderSimulationOutput(job);
                }} else {{
                    html += '<pre>' + escapeHtml(job.result || "No output captured.") + '</pre>';
                }}

                resPreview.innerHTML = html;

                // Auto-scroll to output for simulation mode
                if (job.kind === "simulation") {{
                  setTimeout(() => {{
                    const outputEl = document.getElementById("simulation-output");
                    if (outputEl) {{
                      outputEl.scrollIntoView({{ behavior: "smooth", block: "start" }});
                    }}
                  }}, 100);
                }}

                break;
              }}

              if (job.status === "error") {{
                statusText.innerText = "Failed.";
                resPreview.innerHTML = '<div style="color: #ef4444; background: #fef2f2; padding: 12px; border-radius: 6px;">' + (job.error || "Unknown error") + '</div>';
                break;
              }}

              statusText.innerText = "Running... (" + Math.round((Date.now()/1000) - job.created_at) + "s)";
              await new Promise(r => setTimeout(r, 1000));
          }} catch (e) {{
              console.error(e);
              break;
          }}
        }}

        btn.disabled = false;
        btn.innerHTML = '<span id="btn-text">Run Session</span>';
      }}
    </script>
    """
    return _page("MoDEM Dashboard", body)

def _safe_trace_name(name: str) -> str:
    base = os.path.basename(name)
    if base != name or not (base.startswith("replay_") and base.endswith(".json")):
        raise HTTPException(status_code=400, detail="Invalid trace name")
    return base

@app.get("/trace/{name}", response_class=HTMLResponse)
async def trace_view(name: str):
    base = _safe_trace_name(name)
    path = os.path.join(TRACE_DIR, base)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Trace not found")

    with open(path, "r", encoding="utf-8") as f:
        trace = json.load(f)

    # Extract fields
    prompt = str(trace.get("prompt", ""))
    result = str(trace.get("result", ""))
    timestamp = str(trace.get("timestamp", ""))
    steps = trace.get("steps", [])

    # Calculate score
    qs = quality_score(result)
    score_badge = _score_badge(qs["quality"])

    # Formatting
    prompt_html = html.escape(prompt)
    result_html = html.escape(result)

    steps_html = ""
    if steps:
        steps_json = json.dumps(steps, indent=2)
        steps_html = f"""
        <details>
            <summary>Execution Steps ({len(steps)})</summary>
            <pre style="margin-top: 12px;">{html.escape(steps_json)}</pre>
        </details>
        """
    else:
        steps_html = '<p class="muted">No execution steps recorded.</p>'

    raw_json = json.dumps(trace, indent=2)

    body = f"""
    <div style="margin-bottom: 24px;">
        <a href="/">&larr; Back to Dashboard</a>
    </div>

    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; border-bottom: 1px solid var(--border); padding-bottom: 16px;">
            <div>
                <h1 style="margin-bottom: 8px; font-size: 1.25rem;">Trace Artifact</h1>
                <div style="color: var(--text-muted); font-size: 0.9rem;">
                    {html.escape(base)} &bull; {timestamp}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="margin-bottom: 4px; font-size: 0.8rem; color: var(--text-muted);">QUALITY SCORE</div>
                <div style="transform: scale(1.2); transform-origin: right center;">{score_badge}</div>
            </div>
        </div>

        <h3>Prompt</h3>
        <div style="background: #f3f4f6; padding: 16px; border-radius: var(--radius); margin-bottom: 24px; font-style: italic; color: #4b5563;">
            {prompt_html}
        </div>

        <h3>Result</h3>
        <pre style="background: #1f2937; color: #f9fafb; border: none;">{result_html}</pre>

        <div style="margin-top: 24px;">
            {steps_html}
        </div>
    </div>

    <div class="card">
        <details>
            <summary>Raw JSON Data</summary>
            <pre style="margin-top: 12px; max-height: 400px; overflow-y: auto;">{html.escape(raw_json)}</pre>
        </details>
    </div>
    """
    return _page(f"Trace: {base}", body)


# ---- API Routes ----

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
        return {"traces": []}
    files = _list_trace_files()[:MAX_RECENT_TRACES]
    items = []
    for f in files:
        s = _get_trace_summary(f)
        items.append(s)
    return {"traces": items}

@app.get("/api/trace/{name}")
async def api_trace_raw(name: str):
    base = _safe_trace_name(name)
    path = os.path.join(TRACE_DIR, base)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Trace not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
