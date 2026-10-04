"""Sends the pipeline result (status, stages, duration, logs, git info) to the NEXUS backend."""
import json
import os
import sys
import time
import urllib.request

STAGES = ["build", "test", "security", "docker"]
STATUS_MAP = {"success": "passed", "failure": "failed"}


def read(path, default=""):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        return default


def read_int(path):
    try:
        return int(read(path, "0").strip() or 0)
    except ValueError:
        return 0


def main():
    url = os.getenv("NEXUS_API_URL", "").rstrip("/")
    if not url:
        print("NEXUS_API_URL is not set, skipping report.")
        return 0

    outcomes = {s: os.getenv(f"OUTCOME_{s.upper()}", "skipped") for s in STAGES}
    failed_stage = next((s for s in STAGES if outcomes[s] == "failure"), None)
    status = "failed" if failed_stage else "success"
    duration = int(time.time()) - int(os.getenv("PIPELINE_START", time.time()))

    stages = [
        {"name": s, "status": STATUS_MAP.get(outcomes[s], "skipped"), "duration": read_int(f"{s}.dur")}
        for s in STAGES
    ]
    logs = read(f"{failed_stage}.log")[-3000:] if failed_stage else ""

    repo = os.getenv("GITHUB_REPOSITORY", "local")
    server = os.getenv("GITHUB_SERVER_URL", "https://github.com")
    run_id = os.getenv("GITHUB_RUN_ID")
    payload = {
        "pipeline_id": f"{repo}#{os.getenv('GITHUB_RUN_NUMBER', '0')}",
        "status": status,
        "failed_stage": failed_stage,
        "duration": duration,
        "logs": logs,
        "branch": os.getenv("GITHUB_REF_NAME"),
        "commit": os.getenv("GITHUB_SHA"),
        "author": os.getenv("GITHUB_ACTOR"),
        "run_url": f"{server}/{repo}/actions/runs/{run_id}" if run_id else None,
        "stages": stages,
    }
    print("Stage outcomes:", outcomes)
    print("Sending to NEXUS:", {k: v for k, v in payload.items() if k != "logs"})

    req = urllib.request.Request(
        f"{url}/api/telemetry",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            print("NEXUS responded:", res.status)
    except Exception as e:
        # Never fail the pipeline just because the dashboard is unreachable
        print(f"Could not reach NEXUS: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
