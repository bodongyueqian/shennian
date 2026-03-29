# Shennian Agent Protocol

**Build an AI agent in any language. Control it from your phone — anywhere.**

[中文文档](./README.zh.md) · [Protocol Spec](./PROTOCOL.md) · [shennian.ai](https://shennian.ai) · [shennian.net](https://shennian.net)

---

## What is Shennian?

**Shennian** is a mobile console for AI agents. Run one command on your machine, scan to pair, and remotely control your AI agents from your phone, browser, or desktop — with push notifications, file browsing, and machine sharing built in.

**Try it:** [shennian.ai](https://shennian.ai) · [shennian.net](https://shennian.net)

```bash
# Start the Shennian CLI on your machine
npx shennian

# Scan the QR code to pair — then control from your phone
```

**Built-in agents** (ready to use, no configuration needed):

| Agent | Install |
|---|---|
| [Claude](https://claude.ai/code) | `npm install -g @anthropic-ai/claude-code` |
| [Codex](https://github.com/openai/codex) | `npm install -g @openai/codex` |
| [Gemini](https://github.com/google-gemini/gemini-cli) | `npm install -g @google/gemini-cli` |
| [Cursor](https://www.cursor.com) | Desktop app |
| [OpenClaw](https://openclaw.ai) | `npm install -g openclaw` |

Once any of these are installed on your machine, they appear automatically in the Shennian app — no extra setup.

---

## This Repo: The Custom Agent Protocol

Beyond the built-in agents, Shennian supports **any custom agent** via this open protocol. Your agent is just a CLI program that reads stdin and writes JSON Lines to stdout. Shennian handles the rest.

```
Phone / Browser ←→ Shennian Cloud ←→ Shennian CLI ←→ stdin/stdout ←→ Your Agent
```

---

## Quickstart — Three Steps

### 1. Write your agent

The minimum viable agent handles two commands: `/caps` and `/run`.

**Python**

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

**Node.js** (using the SDK)

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

**Bash**

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

### 2. Install Shennian CLI and register your agent

```bash
# Install CLI (requires Node.js 18+)
npx shennian

# Register your agent (CLI auto-runs /caps to detect capabilities)
shennian agent add my-agent --command "python /path/to/my_agent.py"
```

### 3. Use it from your phone

Open Shennian → select your machine → pick **My Agent** → start chatting.

That's it.

---

## Protocol at a Glance

### Two Lifecycle Modes

| Mode | How it works | Best for |
|---|---|---|
| **spawn** | New process per message. stdin = text, stdout = events, exit = done. | Simple scripts, stateless agents |
| **stdio** | Long-lived process. Bidirectional JSON Lines over stdin/stdout. | Stateful agents, proactive push |

### Commands

| Command | Purpose |
|---|---|
| `my-agent /caps` | Declare capabilities (name, model, mode) |
| `my-agent /run --workdir=<path>` | Handle one message (spawn mode) |
| `my-agent /start --workdir=<path>` | Start long-lived session (stdio mode) |

### Event Types (stdout → Shennian)

| State | Description |
|---|---|
| `delta` | Stream a text chunk to the user |
| `final` | Signal turn complete |
| `error` | Report an error, ends the turn |
| `tool-call` | Show a tool invocation in the UI |
| `tool-result` | Show a tool result in the UI |
| `notify` | Push notification to phone (stdio + proactive only) |

Full specification: **[PROTOCOL.md](./PROTOCOL.md)**

---

## Proactive Agents

Agents in **stdio** mode with `proactive: true` can push notifications without user interaction — perfect for monitoring, cron jobs, and webhook triggers:

```python
from shennian_agent import Agent

agent = Agent(name="Monitor", model="monitor-v1", mode="stdio", proactive=True)

@agent.on_send
def handle(text, **kwargs):
    agent.delta("Monitoring active.")
    agent.final()

def on_alert(message):
    agent.notify(title="Alert", text=message, source="monitor:cpu")

agent.run()
```

The user gets a push notification on their phone — no polling required.

---

## CLI Reference

```bash
# Register a custom agent
shennian agent add <name> --command "<command>"

# Examples
shennian agent add gpt      --command "python ~/agents/gpt_agent.py"
shennian agent add searcher --command "node ~/agents/search.mjs"
shennian agent add local    --command "/usr/local/bin/my-agent"

# List registered agents
shennian agent list

# Remove an agent
shennian agent remove <name>
```

Once registered, the agent appears in the Shennian app as `custom:<name>` alongside built-in agents (Claude, Codex, Gemini, etc.).

---

## SDK

Optional helper libraries — handle protocol boilerplate so you can focus on your agent logic.

| Language | Package | Source |
|---|---|---|
| Node.js | `npm install @shennian/agent` | [sdk/node/](./sdk/node/) |
| Python | `pip install shennian-agent` | [sdk/python/](./sdk/python/) |

---

## Examples

Zero-dependency examples — just raw stdin/stdout, no SDK required:

| Language | Mode | Source |
|---|---|---|
| Node.js | spawn | [examples/node/hello-spawn.mjs](./examples/node/hello-spawn.mjs) |
| Node.js | stdio | [examples/node/agent.mjs](./examples/node/agent.mjs) |
| Python | spawn | [examples/python/agent.py](./examples/python/agent.py) |
| Bash | spawn | [examples/bash/agent.sh](./examples/bash/agent.sh) |

---

## License

Protocol specification, SDKs, and examples are released under the [MIT License](./LICENSE).
