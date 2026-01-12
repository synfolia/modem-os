import os
import json
import requests
from datetime import datetime
from core.config import get_config
from core.shared.output_cleaner import clean_output

TRACE_DIR = "core/research/trace_store"

def run_local_research_ollama(prompt: str):
    """
    Runs research locally using Ollama with deepseek-r1.
    """
    config = get_config()
    print("[*] Running local research via Ollama (deepseek-r1)...")
    try:
        options = {
            "num_predict": config.ollama_num_predict,
            "temperature": config.ollama_temperature
        }

        # Prepend constraints to prompt
        constrained_prompt = (
            f"{prompt}\n\n"
            "Format your response as short narrative paragraphs with optional titled sections "
            "(e.g. 'Findings', 'Context', 'Open Questions').\n"
            "Do NOT use bullet points or checklists.\n"
            "Do NOT include meta-instructions (e.g. 'verify intent') or step-by-step reasoning.\n"
            "No preamble."
        )

        response = requests.post(
            config.ollama_url,
            json={
                "model": config.ollama_model,
                "prompt": constrained_prompt,
                "stream": False,
                "options": options
            },
            timeout=config.ollama_timeout
        )
        response.raise_for_status()
        data = response.json()
        raw_response = data.get("response", "[No response from Ollama]")
        return clean_output(raw_response)
    except requests.exceptions.HTTPError as e:
        error_msg = f"Ollama HTTP error: {e.response.status_code}"
        if e.response.text:
            error_msg += f" - {e.response.text[:200]}"
        print(f"ERROR: {error_msg}")
        return f"[Error: {error_msg}]"
    except requests.exceptions.Timeout:
        error_msg = f"Ollama request timed out after {config.ollama_timeout} seconds"
        print(f"ERROR: {error_msg}")
        return f"[Error: {error_msg}]"
    except requests.exceptions.ConnectionError:
        return f"[Error: Ollama at {config.ollama_url} is unreachable. Please ensure it is running.]"
    except Exception as e:
        print(f"ERROR: Unexpected error: {str(e)}")
        return f"[Error running local research: {str(e)}]"

def run_deep_research(prompt: str):
    trace = {
        "timestamp": datetime.utcnow().isoformat(),
        "prompt": prompt,
        "steps": [],
        "result": None
    }

    router_url = os.environ.get("MODEM_ROUTER_URL")

    # Logic:
    # 1. If MODEM_ROUTER_URL is set, try to use it.
    # 2. If it fails (connection error), fallback to local.
    # 3. If MODEM_ROUTER_URL is not set, use local directly.

    used_router = False

    if router_url:
        try:
            print(f"[*] Attempting to route research via {router_url}...")
            response = requests.post(
                router_url,
                json={"prompt": prompt}
            )
            response.raise_for_status()
            data = response.json()

            trace["steps"] = data.get("steps", [])
            trace["result"] = clean_output(data.get("result", "[No result returned]"))
            used_router = True

        except requests.exceptions.ConnectionError:
            print(f"[!] Router at {router_url} is unreachable. Falling back to local Ollama.")
            # Fallback will happen below
        except Exception as e:
            trace["result"] = f"[Router error: {str(e)}]"
            # If it's a non-connection error (e.g. 500 or 400), we might still want to fallback or just fail.
            # The prompt says: "If set but router unreachable, print a friendly message and fallback to local."
            # "Unreachable" usually implies connection error.
            # For other errors, I'll stick to current behavior of logging error, unless user implied otherwise.
            # But let's assume we proceed to save trace and return.
            pass

    if not used_router:
        # Check if we already have a result (from non-connection error above)
        if trace["result"] is None:
            # Run local research
            result = run_local_research_ollama(prompt)
            trace["result"] = result
            trace["steps"].append({"action": "local_inference", "model": "deepseek-r1", "status": "completed"})

    save_trace(trace)
    return trace["result"]


def save_trace(trace: dict):
    os.makedirs(TRACE_DIR, exist_ok=True)
    timestamp = trace.get("timestamp", datetime.utcnow().isoformat())
    filename = f"replay_{timestamp.replace(':', '-')}.json"
    filepath = os.path.join(TRACE_DIR, filename)

    with open(filepath, "w") as f:
        json.dump(trace, f, indent=2)

    print(f"[+] Trace saved to {filepath}")
