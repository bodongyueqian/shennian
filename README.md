# Shennian Agent Protocol

> Build an AI agent in any language. Control it from your phone.

[Shennian](https://codyer.com) is a mobile control console for AI agents. This repo defines the **open protocol** for plugging any agent into the Shennian platform — and provides SDKs and examples to get you started in minutes.

```
Your Phone ←→ Shennian Cloud ←→ Shennian CLI ←→ stdin/stdout ←→ Your Agent
```

Your agent is just a CLI program. It reads from stdin, writes JSON Lines to stdout. Shennian handles everything else — WebSocket relay, mobile UI, push notifications, file transfer.

---

## Quick Start

### 1. Write your agent

The simplest agent is a script that handles two commands:

**Python** — `my_agent.py`

```python
#!/usr/bin/env python3
import sys, json

if sys.argv[1] == "/caps":
    print(json.dumps({
        "name": "My Agent",
        "model": "gpt-4o",
        "mode": "spawn",
        "version": "1.0.0"
    }))
    sys.exit(0)

if sys.argv[1] == "/run":
    message = sys.stdin.read()
    print(json.dumps({"state": "delta", "text": f"You said: {message}"}))
    print(json.dumps({"state": "final"}))
```

**Bash** — `my_agent.sh`

```bash
#!/bin/bash
if [ "$1" = "/caps" ]; then
  echo '{"name":"My Agent","model":"echo-v1","mode":"spawn","version":"1.0.0"}'
  exit 0
fi
if [ "$1" = "/run" ]; then
  msg=$(cat)
  echo "{\"state\":\"delta\",\"text\":\"You said: $msg\"}"
  echo '{"state":"final"}'
fi
```

### 2. Register with Shennian

```bash
# Make sure Shennian CLI is running on your machine
shennian agent add my-agent --command "python /path/to/my_agent.py"
```

### 3. Use it from your phone

Open the Shennian app → select your machine → pick "My Agent" → start chatting.

That's it. Three steps.

---

## Protocol at a Glance

| Command | Purpose |
|---|---|
| `my-agent /caps` | Declare capabilities (name, model, mode) |
| `my-agent /run --workdir=<path>` | Handle one message (spawn mode) |
| `my-agent /start --workdir=<path>` | Start long-lived session (stdio mode) |

### Two Modes

| Mode | How it works | Best for |
|---|---|---|
| **spawn** | New process per message. stdin = text, stdout = events, exit = done | Simple agents, scripts |
| **stdio** | Long-lived process. stdin/stdout = JSON Lines bidirectional | Stateful agents, proactive push |

### Event Types (stdout JSON Lines)

| State | Purpose |
|---|---|
| `delta` | Stream a text chunk to the user |
| `final` | Signal turn complete |
| `error` | Report an error (ends turn) |
| `tool-call` | Show tool invocation in UI |
| `tool-result` | Show tool result in UI |
| `notify` | Push notification (proactive agents only) |

Full specification: **[PROTOCOL.md](./PROTOCOL.md)**

---

## Examples

Minimal agents with no SDK dependency — just raw stdin/stdout:

| Language | Mode | Source |
|---|---|---|
| Bash | spawn | [examples/bash/agent.sh](./examples/bash/agent.sh) |
| Python | spawn | [examples/python/agent.py](./examples/python/agent.py) |
| Node.js | stdio | [examples/node/agent.mjs](./examples/node/agent.mjs) |

---

## SDK

Optional helper libraries that handle protocol boilerplate for you:

### Python

```bash
pip install shennian-agent
```

```python
from shennian_agent import Agent

agent = Agent(name="My Agent", model="gpt-4o")

@agent.on_send
def handle(text, session_id, attachments):
    for chunk in call_my_llm(text):
        agent.delta(chunk)
    agent.final()

agent.run()
```

See [sdk/python/](./sdk/python/) for full docs and examples.

### Node.js

```bash
npm install @shennian/agent
```

```typescript
import { Agent } from '@shennian/agent'

const agent = new Agent({ name: 'My Agent', model: 'gpt-4o' })

agent.onSend(async ({ text }) => {
  for await (const chunk of callMyLLM(text)) {
    agent.delta(chunk)
  }
  agent.final()
})

agent.run()
```

See [sdk/node/](./sdk/node/) for full docs and examples.

---

## Proactive Agents

Agents in **stdio** mode with `proactive: true` can push messages without user interaction — monitoring alerts, cron results, webhook notifications:

```python
agent = Agent(name="Monitor", model="monitor-v1", mode="stdio", proactive=True)

@agent.on_send
def handle(text, **kwargs):
    agent.delta("Monitoring configured.")
    agent.final()

def on_alert(alert):
    agent.notify(title="Alert", text=alert.message, source="monitor:cpu")

agent.run()
```

The user gets a push notification on their phone. Just like a built-in agent.

---

## Registration

```bash
# Add
shennian agent add <name> --command "<command>"

# List
shennian agent list

# Remove
shennian agent remove <name>
```

The agent appears in the Shennian app as `custom:<name>` alongside built-in agents.

---

## License

Protocol specification, SDKs, and examples are released under the [MIT License](./LICENSE).
