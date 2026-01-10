import sys
import os

# Add project root to sys.path to allow imports from core
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core.research.replay_engine import replay_trace
except ImportError as e:
    print(f"Error importing core.research.replay_engine: {e}")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 replay_engine.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    try:
        replay_trace(filename)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
