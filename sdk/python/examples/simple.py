#!/usr/bin/env python3
"""Minimal echo agent using spawn mode."""
from __future__ import annotations

from shennian_agent import Agent

agent = Agent(name="Echo Agent", model="echo", mode="spawn")


@agent.on_send
def handle(text: str, session_id: str | None, attachments: list) -> None:
    agent.delta(f"You said: {text}")
    agent.final()


if __name__ == "__main__":
    agent.run()
