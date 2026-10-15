#!/usr/bin/env python3
"""Restricted local Cloudroom Core client for S2 OpenClaw."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.request
from urllib.parse import urlsplit

DEFAULT_API = "http://127.0.0.1:9840"
DEFAULT_REPO = "/mnt/d/dev/S2-Cloudroom-GUI"
VALID_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,99}$")


class CloudroomError(Exception):
    pass


def endpoint_base():
    value = os.environ.get("CLOUDROOM_API_URL", DEFAULT_API).rstrip("/")
    parsed = urlsplit(value)
    if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost", "::1"):
        raise CloudroomError("Core API must use a private loopback HTTP address")
    if parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
        raise CloudroomError("Invalid Core API base URL")
    return value


def token():
    filename = Path(os.environ.get("CLOUDROOM_TOKEN_FILE", "~/.config/s2-cloudroom/token")).expanduser()
    if not filename.is_file():
        return None
    if os.name != "nt" and filename.stat().st_mode & 0o077:
        raise CloudroomError("Token file permissions must be 0600")
    value = filename.read_text(encoding="utf-8").strip()
    if not value or len(value) > 1024 or "\n" in value or "\r" in value:
        raise CloudroomError("Invalid token file")
    return value


def call(method, path, payload=None, timeout=8):
    base = endpoint_base()
    auth = token()
    if not auth:
        raise CloudroomError("Cloudroom token is not configured; set CLOUDROOM_TOKEN_FILE")
    headers = {"Authorization": "Bearer " + auth, "Accept": "application/json"}
    body = None
    if payload is not None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(base + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read(2 * 1024 * 1024)
            return {"http_status": response.status, "response": json.loads(data) if data else {}}
    except urllib.error.HTTPError as exc:
        raise CloudroomError("Core HTTP " + str(exc.code)) from None
    except (urllib.error.URLError, TimeoutError) as exc:
        raise CloudroomError("Core API unavailable at " + base) from None


def require_id(value):
    if not VALID_ID.fullmatch(value):
        raise CloudroomError("Invalid ID: use 1-100 letters, digits, underscores or hyphens")
    return value


def repo_status():
    repo = Path(os.environ.get("CLOUDROOM_REPO", DEFAULT_REPO)).resolve()
    if not (repo / ".git").exists():
        raise CloudroomError("Fork checkout not found: " + str(repo))
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short=12", "HEAD"],
                          text=True, capture_output=True, timeout=30, check=False)
    branch = subprocess.run(["git", "-C", str(repo), "branch", "--show-current"],
                            text=True, capture_output=True, timeout=30, check=False)
    return {"path": str(repo), "git_head": head.stdout.strip(),
            "branch": branch.stdout.strip(),
            "git_exit_code": head.returncode or branch.returncode}


def run(args):
    if args.command == "repo":
        return repo_status()
    if args.command == "status":
        result = {"fork": repo_status(), "core_url": endpoint_base(), "core_ready": False}
        try:
            answer = call("GET", "/v1/ready")
            result["core_ready"] = bool(answer.get("response", {}).get("ready"))
        except CloudroomError as exc:
            result["core_error"] = str(exc)
        return result
    if args.command == "session":
        return call("GET", "/v1/sessions/" + require_id(args.session))
    if args.command == "events":
        return call("GET", "/v1/sessions/" + require_id(args.session) + "/events")
    if args.command == "start":
        body = {"request_id": require_id(args.request_id), "harness": args.harness}
        if args.workspace:
            body["workspace"] = require_id(args.workspace)
        return call("POST", "/v1/sessions", body)
    if args.command == "prompt":
        text = args.text
        if not text or len(text) > 32000:
            raise CloudroomError("Prompt must be 1 to 32000 characters")
        return call("POST", "/v1/sessions/" + require_id(args.session) + "/prompts",
                    {"request_id": require_id(args.request_id), "text": text})
    if args.command == "close":
        return call("POST", "/v1/sessions/" + require_id(args.session) + "/close",
                    {"request_id": require_id(args.request_id)})
    raise CloudroomError("Unsupported command")


def main():
    parser = argparse.ArgumentParser(description="S2Tech restricted Cloudroom Core client")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("repo", "status"):
        sub.add_parser(name)
    for name in ("session", "events"):
        sub.add_parser(name).add_argument("--session", required=True)
    start = sub.add_parser("start")
    start.add_argument("--request-id", required=True)
    start.add_argument("--harness", choices=("codex", "pi"), default="codex")
    start.add_argument("--workspace")
    prompt = sub.add_parser("prompt")
    prompt.add_argument("--session", required=True)
    prompt.add_argument("--request-id", required=True)
    prompt.add_argument("--text", required=True)
    close = sub.add_parser("close")
    close.add_argument("--session", required=True)
    close.add_argument("--request-id", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args), indent=2))
        return 0
    except (CloudroomError, OSError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
