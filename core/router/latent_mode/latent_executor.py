import requests
import os
import json
from datetime import datetime

def latent_execute(sap_text):
    print(f"Executing in latent mode with MAPLE OS model: {sap_text}")

    # Step 1: Latent reasoning via MAPLE model
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "maple-os-1:latest",
            "prompt": f"Reason in latent space about: {sap_text}",
            "stream": False
        },
        timeout=10
    )

    response_json = response.json()
    response_text = response_json.get("response", "")
    print("MAPLE Reasoning:", response_text)

    # Step 2: Gene intervention if pattern is matched
    if "flare" in response_text.lower() and "ATG16L1" in response_text:
        print("MAPLE: Flare scroll detected with genetic resonance (ATG16L1).")
        print("→ Triggering Coconut mutation loop simulation via Go bridge...")

        go_payload = {
            "id": "flare_prediction_vector_2024",
            "trigger": "flare",
            "trust_score": 0.91,
            "genetic_markers": ["ATG16L1", "TNFSF15"]
        }
        try:
            go_response = requests.post(
                "http://localhost:8282/simulate",
                json=go_payload,
                timeout=10
            )
            if go_response.ok:
                result = go_response.json()
                print(":", result)

                # Scroll archive path
                ts = datetime.utcnow().isoformat().replace(":", "-")
                out_path = (
                    f"scrolls/r_and_d/maria_lab/flare_trials/"
                    f"flare_{ts}.brs"
                )
                os.makedirs(os.path.dirname(out_path), exist_ok=True)

                # Save scroll result
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "timestamp": ts,
                        "result": result,
                        "source": "latent_execute"
                    }, f, indent=2)
                print(f"MAPLE: Scroll saved to {out_path}")
            else:
                # Handle Go server error
                go_response.raise_for_status()
                # Log error response
                print(
                    "MAPLE: Go server error:",
                    go_response.status_code,
                    go_response.text
                )
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print("MAPLE: Failed to reach Coconut Go server:", str(e))
    else:
        print("MAPLE: No actionable scroll-to-gene patterns found.")

    return response_text