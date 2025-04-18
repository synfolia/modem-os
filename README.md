# MoDEM OS

**Modular Decision Engine & Memory** — local-first, scroll-powered, and designed for sovereign execution.

Built by James Kierstead as part of **Project Trees**, MoDEM OS enables trust-driven reasoning, replayable research, and dynamic scroll execution across decentralized expert systems.

---

## Features

- **Replayable Deep Research**  
  Generate structured, stepwise thought scrolls from local expert models and store them as `.json` traces.

- **Latent-Space Reasoning Support**  
  Optionally simulate continuous (Coconut-style) thought steps outside traditional token flow.

- **Scroll Engine**  
  Mutate, fork, and replay reasoning paths like living memory branches. Each trace is a sapline.

- **Local-First by Design**  
  All reasoning, storage, and execution happens on your machine. No remote calls. No phantoms.

---

## Getting Started


```bash
git clone https://github.com/synfolia/modem-os
cd modem-os
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # Only if needed
```
---

## Usage
### Run a New Deep Research Session
```python
python3 main.py research "How does latent reasoning outperform language-based planning?"
```
### Replay a Saved Scroll
```python
python3 main.py replay replay_2025-04-18T09-00-00.json
```
---
## Project Structure
```markdown
core/
  research/
    research_session.py   # Executes and records scrolls
    replay_engine.py      # Replays saved deep research traces
    trace_store/          # Saved .json files from each scroll session
  sap_mutation/
    mutate_sap.py         # (Optional) mutation step logic
main.py                   # CLI entry point
```
---

## Example Output
```json
{
  "timestamp": "2025-04-18T09:00:00Z",
  "prompt": "How does federated latent reasoning scale?",
  "steps": [
    "Step 1: Parsed structure of federation nodes.",
    "Step 2: Simulated parallel thought traces.",
    "Step 3: Composed MAPLE snapshot."
  ],
  "result": "Federated latent reasoning scales by preserving local agency while synchronizing emergent structure."
}
```

## License
```markdown
This project is open-source under a custom trust-aligned license.
It is not to be used for centralized surveillance, manipulation, or extractive AI systems.

For contributions and MAPLE submission flow, see /scrolls/contribute.
```
---

## Credits
```markdown
Built by James Kierstead.
Model execution occurred locally.
No upstream provider or AI vendor has authorship or rights to this system.
```