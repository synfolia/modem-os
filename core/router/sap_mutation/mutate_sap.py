import requests
import re
from core.config import get_config

def mutate_sap(prompt, num_proposals=3):
    config = get_config()
    print(f"Mutating SAP using DeepSeek for prompt: {prompt}")

    try:
        options = {
            "num_predict": config.ollama_num_predict,
            "temperature": config.ollama_temperature
        }

        response = requests.post(
            config.ollama_url,
            json={
                "model": config.ollama_model,
                "prompt": f"Generate {num_proposals} creative action proposals for: {prompt}. Format with headings: ### 1. Title. Be concise. No preamble.",
                "stream": False,
                "options": options
            },
            timeout=config.ollama_timeout
        )
        response.raise_for_status()
        response_json = response.json()
        raw_output = response_json.get("response", "")
    except requests.exceptions.HTTPError as e:
        error_msg = f"Ollama HTTP error: {e.response.status_code}"
        if e.response.text:
            error_msg += f" - {e.response.text[:200]}"
        print(f"ERROR: {error_msg}")
        return [{
            "title": "Error",
            "description": f"Failed to get response from Ollama - {error_msg}"
        }]
    except requests.exceptions.Timeout:
        print(f"ERROR: Ollama request timed out after {config.ollama_timeout} seconds")
        return [{
            "title": "Error",
            "description": f"Ollama request timed out after {config.ollama_timeout} seconds"
        }]
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Failed to connect to Ollama: {str(e)}")
        return [{
            "title": "Error",
            "description": f"Failed to connect to Ollama at {config.ollama_url}"
        }]
    except Exception as e:
        print(f"ERROR: Unexpected error calling Ollama: {str(e)}")
        return [{
            "title": "Error",
            "description": f"Unexpected error - {str(e)}"
        }]

    raw_output = re.sub(r"<think>.*?</think>", "", raw_output, flags=re.DOTALL)

    sap_list = []

    matches = re.split(r"###\s*\d+\.\s*", raw_output)
    for match in matches[1:]:
        lines = match.strip().splitlines()
        if lines:
            title = lines[0].strip()
            description = " ".join(line.strip() for line in lines[1:] if line.strip())
            sap_list.append({
                "title": title,
                "description": description
            })

    if not sap_list:
        print("[Warning] No SAPs found, using raw output.")
        sap_list = [{
            "title": "Fallback Proposal",
            "description": raw_output[:200]
        }]

    return sap_list