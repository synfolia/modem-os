# Coconut Latent Mode Executor

import requests

def latent_execute(sap_text):
    print(f"Executing in latent mode with DeepSeek: {sap_text}")

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "deepseek-r1:latest",
            "prompt": f"Reason in latent space about: {sap_text}",
            "stream": False
        }
    )

    response_json = response.json()
    return response_json.get("response", "")