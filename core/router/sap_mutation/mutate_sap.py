import requests
import re
from core.config import get_config

def mutate_sap(prompt, num_proposals=3):
    config = get_config()
    print(f"Mutating SAP using DeepSeek for prompt: {prompt}")

    response = requests.post(
        config.ollama_url,
        json={
            "model": config.ollama_model,
            "prompt": f"Generate {num_proposals} creative action proposals for: {prompt}. Format with headings: ### 1. Title",
            "stream": False
        },
        timeout=config.ollama_timeout
    )

    response_json = response.json()
    raw_output = response_json.get("response", "")

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