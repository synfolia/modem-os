import time
import requests
import threading
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import os
import sys

# Ensure we can import dashboard
sys.path.append(os.getcwd())
from modem_api.ui.dashboard import app

# Create a mock scroll engine server
def run_scroll_server():
    from flask import Flask, jsonify
    server = Flask(__name__)
    @server.route('/health')
    def health():
        return jsonify({"status": "OK"})
    server.run(port=8282)

# Run scroll server in background
import threading
scroll_thread = threading.Thread(target=run_scroll_server, daemon=True)
scroll_thread.start()

# Run dashboard in background
def run_dashboard():
    uvicorn.run(app, host="127.0.0.1", port=8347, log_level="error")

dash_thread = threading.Thread(target=run_dashboard, daemon=True)
dash_thread.start()

# Wait for servers to start
time.sleep(3)

# Playwright script
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    try:
        page.goto("http://127.0.0.1:8347/")
        page.screenshot(path="verification/dashboard_screenshot.png", full_page=True)
        print("Screenshot taken.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        browser.close()
