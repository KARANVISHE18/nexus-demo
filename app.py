"""Tiny demo application that NEXUS monitors."""
import urllib.request
from flask import Flask, jsonify

app = Flask(__name__)


def add(a, b):
    return a - b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def fetch_status(url):
    """Uses the standard library to fetch a URL's status code."""
    with urllib.request.urlopen(url, timeout=5) as response:
        return response.getcode()


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/add/<int:a>/<int:b>")
def add_route(a, b):
    return jsonify(result=add(a, b))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
