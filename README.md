# NEXUS Demo App

A tiny Flask app used to demonstrate the NEXUS CI/CD intelligence layer.

Pipeline (`.github/workflows/ci-cd.yml`): Build -> Test -> Security scan -> Docker build.
After every run, `scripts/report.py` sends the result to the NEXUS backend (`POST /api/telemetry`).

## Run locally
    pip install -r requirements.txt
    python -m pytest -q
    python app.py

## Break it on purpose (to see NEXUS analyse a failure)
- Remove `requests` from `requirements.txt` -> test stage fails with `ModuleNotFoundError`.
- Change an assertion in `tests/test_app.py` -> test stage fails with `AssertionError`.
