## 2024-05-22 - Path Traversal in Replay Engine
**Vulnerability:** A path traversal vulnerability existed in `core/research/replay_engine.py` where user-supplied filenames were directly joined with a base path, allowing access to arbitrary files via `../`.
**Learning:** Even when using `os.path.join`, input validation is crucial. Relative paths in input can escape the intended directory.
**Prevention:** Always sanitize filenames using `os.path.basename()` when the intent is to access a file within a specific directory, or validate that the resolved absolute path starts with the intended base directory.
