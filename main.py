"""
MoDEM Main Runner
This script manages tasks, research, and optimization for the MoDEM system.
"""
from core.research.replay_engine import replay_trace
from core.research.research_session import run_deep_research
from core.task_manager.runner import new_task
from prompt import prompt


# Run
if __name__ == "__main__":
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "default"
    if mode == "research":
        research_result = run_deep_research(prompt)
        print("Research Result:", research_result)
    elif mode == "replay":
        filename = sys.argv[2] if len(sys.argv) > 2 else None
        if filename:
            replay_trace(filename)
        else:
            print("Usage: python3 main.py replay <trace_filename>")
    else:
        final_result = new_task(prompt, latent_mode=True)
        print("Final Result:\n", final_result)
