from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import os

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>MoDEM Dashboard</title>
        </head>
        <body>
            <h1>MoDEM Dashboard</h1>
            <p>System Status: OK</p>
            <ul>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/traces">Traces</a></li>
            </ul>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "OK"}

@app.get("/traces")
async def list_traces():
    trace_dir = "core/research/trace_store"
    if not os.path.exists(trace_dir):
         return JSONResponse(content={"error": "Trace directory not found", "path": trace_dir}, status_code=404)

    try:
        files = os.listdir(trace_dir)
        return {"traces": files}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
