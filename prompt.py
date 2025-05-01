import sys


prompt = (
    " ".join(sys.argv[2:])
    if len(sys.argv) > 2
    else "Draft a cybersecurity incident report."
)