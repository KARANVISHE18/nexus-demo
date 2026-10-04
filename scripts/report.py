"""Sends the pipeline result (status, failed stage, duration, logs) to the NEXUS backend."""
import json
import os
import sys
import time
import urllib.request

STAGES = ["build", "test", "security", "docker"]


def tail(path, max_chars=3000):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()[-max_chars:]
    except FileNotFoundError:
        return ""


def main():
    url = os.getenv("NEXUS_API_URL", "").rstrip("/")
    if not url:
        print("NEXUS_API_URL is not set, skipping report.")
        return 0

    outcomes = {s: os.getenv(f"OUTCOME_{s.upper()}", "skipped") for s in STAGES}
    failed_stage = next((s for s in STAGES if outcomes[s] == "failure"), None)
    status = "failed" if failed_stage else "success"
    duration = int(time.time()) - int(os.getenv("PIPELINE_START", time.time()))

    logs = tail(f"{failed_stage}.log") if failed_stage else ""
    payload = {
        "pipeline_id": f"{os.getenv('GITHUB_REPOSITORY', 'local')}#{os.getenv('GITHUB_RUN_NUMBER', '0')}",
        "status": status,
        "failed_stage": failed_stage,
        "duration": duration,
        "logs": logs,
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
