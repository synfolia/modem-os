#!/usr/bin/env python3

import sys
import subprocess

def print_help():
    print("""
modemctl - MAPLE OS CLI

Commands:
  modemctl dashboard          Launch the local scroll HUD
  modemctl replay <file>     Replay a scroll file (.brs)
  modemctl simulate          Run a flare trial through the latent executor
""")

def run_dashboard():
    print("[MAPLE] Launching dashboard at http://localhost:8347 ...")
    subprocess.run(["uvicorn", "modem_api.ui.dashboard:app", "--port", "8347", "--reload"])

def run_replay(scroll_file):
    subprocess.run(["python3", "modem_api/core/replay_engine.py", scroll_file])

def run_simulate():
    subprocess.run(["python3", "-c", "from modem_os.core.latent_mode.latent_executor import latent_execute; latent_execute('Flare likely triggered by trauma. Consider ATG16L1 immune pathway drift.')"])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
    elif sys.argv[1] == "dashboard":
        run_dashboard()
    elif sys.argv[1] == "replay" and len(sys.argv) == 3:
        run_replay(sys.argv[2])
    elif sys.argv[1] == "simulate":
        run_simulate()
    else:
        print_help()