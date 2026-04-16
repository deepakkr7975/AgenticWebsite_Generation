"""
server.py — Flask API backend for WebGen UI
Run: python server.py
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder=".")
CORS(app)

# In-memory job store
jobs: dict[str, dict] = {}


def run_pipeline(job_id: str, requirement: str, reference_site: str, max_iterations: int, output_name: str):
    """Run main.py as subprocess and stream logs."""
    job = jobs[job_id]
    job["status"] = "running"
    job["logs"] = []
    job["score"] = None
    job["output_dir"] = None

    output_dir = f"./output/{output_name}"

    cmd = [
        sys.executable, "main.py",
        "--requirement", requirement,
        "--max-iterations", str(max_iterations),
        "--output-dir", output_dir,
    ]
    if reference_site.strip():
        cmd += ["--reference-sites", reference_site.strip()]

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=str(Path(__file__).parent),
        )

        for line in process.stdout:
            line = line.rstrip()
            if line:
                job["logs"].append(line)
                # Extract score from logs
                if "Final score" in line or "Score:" in line:
                    import re
                    m = re.search(r"(\d+\.\d+)", line)
                    if m:
                        job["score"] = float(m.group(1))

        process.wait()

        if process.returncode == 0:
            job["status"] = "done"
            job["output_dir"] = str(Path(output_dir) / "final")
        else:
            job["status"] = "failed"

    except Exception as e:
        job["logs"].append(f"ERROR: {e}")
        job["status"] = "failed"


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json
    requirement = data.get("requirement", "").strip()
    reference_site = data.get("reference_site", "").strip()
    max_iterations = int(data.get("max_iterations", 2))
    output_name = data.get("output_name", "").strip() or f"site-{int(time.time())}"

    if not requirement:
        return jsonify({"error": "Requirement is required"}), 400

    if not os.getenv("GEMINI_API_KEY"):
        return jsonify({"error": "GEMINI_API_KEY not set in .env file"}), 400

    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        "id": job_id,
        "requirement": requirement,
        "reference_site": reference_site,
        "max_iterations": max_iterations,
        "output_name": output_name,
        "status": "queued",
        "logs": [],
        "score": None,
        "output_dir": None,
        "created_at": time.time(),
    }

    thread = threading.Thread(
        target=run_pipeline,
        args=(job_id, requirement, reference_site, max_iterations, output_name),
        daemon=True,
    )
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/api/jobs/<job_id>", methods=["GET"])
def get_job(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


@app.route("/api/jobs/<job_id>/logs", methods=["GET"])
def get_logs(job_id: str):
    """SSE endpoint for live log streaming."""
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    def stream():
        sent = 0
        while True:
            logs = job.get("logs", [])
            while sent < len(logs):
                yield f"data: {json.dumps({'log': logs[sent]})}\n\n"
                sent += 1
            if job["status"] in ("done", "failed"):
                yield f"data: {json.dumps({'status': job['status'], 'score': job.get('score'), 'output_dir': job.get('output_dir')})}\n\n"
                break
            time.sleep(0.3)

    return Response(stream(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/api/jobs", methods=["GET"])
def list_jobs():
    return jsonify(list(reversed(list(jobs.values()))))


@app.route("/api/jobs/<job_id>", methods=["DELETE"])
def delete_job(job_id: str):
    jobs.pop(job_id, None)
    return jsonify({"ok": True})


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


if __name__ == "__main__":
    print("\n🚀 WebGen UI running at http://localhost:8080\n")
    app.run(port=8080, debug=False, threaded=True)
