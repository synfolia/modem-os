import requests
import re
from core.config import get_config

def mutate_sap(prompt, num_proposals=3):
    config = get_config()
    print(f"Mutating SAP using DeepSeek for prompt: {prompt}")

    try:
        options = {
            "num_predict": 500,  # Increase from 220 to allow for 3 proposals
            "temperature": 0.5   # Increase creativity for diverse proposals
        }

        response = requests.post(
            config.ollama_url,
            json={
                "model": config.ollama_model,
                "prompt": f"""Generate exactly {num_proposals} different strategic action proposals for this task: {prompt}

Format each proposal EXACTLY like this:
### 1. [Title]
[Description in 1-2 sentences]

### 2. [Title]
[Description in 1-2 sentences]

### 3. [Title]
[Description in 1-2 sentences]

Be concise. No preamble or extra text.""",
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

    # Remove thinking tags
    raw_output = re.sub(r"<think>.*?</think>", "", raw_output, flags=re.DOTALL)

    print(f"[DEBUG] Raw output length: {len(raw_output)} chars")
    print(f"[DEBUG] Raw output preview: {raw_output[:200]}...")

    sap_list = []

    # Try multiple parsing patterns for robustness
    # Pattern 1: ### 1. Title format
    matches = re.split(r"###\s*\d+\.\s*", raw_output)
    if len(matches) > 1:
        for match in matches[1:]:
            lines = match.strip().splitlines()
            if lines:
                title = lines[0].strip().rstrip('.')  # Remove trailing period
                description = " ".join(line.strip() for line in lines[1:] if line.strip())
                if title:  # Only add if title is not empty
                    sap_list.append({
                        "title": title,
                        "description": description or "No description provided"
                    })

    # Pattern 2: Fallback - try numbered list without ###
    if not sap_list:
        print("[DEBUG] Pattern 1 failed, trying numbered list pattern")
        matches = re.split(r"^\d+\.\s*", raw_output, flags=re.MULTILINE)
        if len(matches) > 1:
            for match in matches[1:]:
                lines = match.strip().splitlines()
                if lines:
                    title = lines[0].strip().rstrip('.')
                    description = " ".join(line.strip() for line in lines[1:] if line.strip())
                    if title:
                        sap_list.append({
                            "title": title,
                            "description": description or "No description provided"
                        })

    # Final fallback: generate default proposals if parsing completely failed
    if not sap_list:
        print(f"[WARNING] SAP parsing failed completely. Generating {num_proposals} default proposals.")
        base_prompt_short = prompt[:50] if len(prompt) > 50 else prompt
        sap_list = [
            {
                "title": f"Direct Implementation",
                "description": f"Implement the requested task directly: {base_prompt_short}"
            },
            {
                "title": f"Optimized Approach",
                "description": f"Optimize and refine the implementation for better performance and reliability"
            },
            {
                "title": f"Experimental Solution",
                "description": f"Explore innovative alternatives and experimental techniques"
            }
        ][:num_proposals]

    # Ensure we have exactly num_proposals by padding or truncating
    if len(sap_list) < num_proposals:
        print(f"[WARNING] Only found {len(sap_list)} SAPs, padding to {num_proposals}")
        while len(sap_list) < num_proposals:
            sap_list.append({
                "title": f"Alternative Approach {len(sap_list) + 1}",
                "description": f"Additional strategic approach to the task"
            })
    elif len(sap_list) > num_proposals:
        print(f"[INFO] Found {len(sap_list)} SAPs, truncating to {num_proposals}")
        sap_list = sap_list[:num_proposals]

    print(f"[INFO] Successfully generated {len(sap_list)} SAP proposals")
    for idx, sap in enumerate(sap_list, 1):
        print(f"  SAP {idx}: {sap['title'][:40]}...")

    return sap_list