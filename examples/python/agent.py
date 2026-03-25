#!/usr/bin/env python3
"""
Minimal Shennian agent in Python (spawn mode, no SDK).
Echoes the user's message back. Replace the logic with your own LLM calls.

Register:  shennian agent add echo-python --command "python /path/to/agent.py"
"""
from __future__ import annotations

import sys
import json
import argparse


def caps():
    print(json.dumps({
        "name": "Echo Agent (Python)",
        "model": "echo-v1",
        "mode": "spawn",
        "version": "1.0.0",
    }))


def run(workdir: str, session: str | None, resume: str | None, attachments: list[str]):
    message = sys.stdin.read()

    parts = [f"Echo: {message}"]
    if attachments:
        parts.append(f"\nAttachments received: {', '.join(attachments)}")

    print(json.dumps({"state": "delta", "text": "".join(parts)}))
    sys.stdout.flush()
    print(json.dumps({"state": "final"}))
    sys.stdout.flush()


def main():
    if len(sys.argv) < 2:
        print("Usage: agent.py /caps | /run --workdir=<path>", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command == "/caps":
        caps()
        return

    if command == "/run":
        parser = argparse.ArgumentParser()
        parser.add_argument("--workdir", required=True)
        parser.add_argument("--session", default=None)
        parser.add_argument("--resume", default=None)
        parser.add_argument("--attachment", action="append", default=[])
        args = parser.parse_args(sys.argv[2:])
        run(args.workdir, args.session, args.resume, args.attachment)
        return

    print(f"Unknown command: {command}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
