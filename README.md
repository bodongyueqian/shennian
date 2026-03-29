# Shennian — Control Your AI Agents, Anywhere

> AI Agents at Your Fingertips. No port forwarding. No VPN. One command to start, scan to use.

[中文文档](./README.zh.md) · [Protocol Spec](./PROTOCOL.md) · [shennian.ai](https://shennian.ai) · [shennian.net](https://shennian.net)

---

Run `npx shennian` on your machine, scan to pair, and remotely control Claude, Codex, Gemini, Cursor, OpenClaw and more from your phone, browser, or desktop.

```bash
npx shennian
```

```
✓ Shennian v0.1.0 starting...
✓ Connected to relay: shennian.ai
◉ Scan QR or enter token to pair
  Token: sn-a3f9...
```

Scan the QR code with the Shennian app — paired in under 30 seconds.

---

## Features

**Multi-Agent Support**
Switch between Claude, Codex, Gemini, Cursor, OpenClaw in one console. Independent sessions per agent, full history, reconnect and resume.

| Agent | Install |
|---|---|
| [Claude](https://claude.ai/code) | `npm install -g @anthropic-ai/claude-code` |
| [Codex](https://github.com/openai/codex) | `npm install -g @openai/codex` |
| [Gemini](https://github.com/google-gemini/gemini-cli) | `npm install -g @google/gemini-cli` |
| [Cursor](https://www.cursor.com) | Desktop app |
| [OpenClaw](https://openclaw.ai) | `npm install -g openclaw` |

**Built-in File System**
Browse directory trees, preview code files, upload and download — all from your phone. No SSH required.

**Push Notifications**
Get notified when an Agent task completes, a cron fires, or a hook triggers. Step away and come back when it's done.

**End-to-End Encryption**
All traffic encrypted over TLS. QR-based machine auth with permission levels and expiry. Zero local port exposure.

**Machine Sharing**
Generate time-limited, permission-scoped QR codes to let teammates access your local Agent environment. Revoke anytime.

**All Platforms**
iOS, Android, Web, macOS, and Windows. One account, all devices, seamless switching.

---

## Get Started

### 1. Install and run

```bash
# One-time run
npx shennian

# Or install globally
npm install -g shennian
shennian
```

### 2. Scan to pair

Scan the QR code or paste the token into the Shennian app — pairs permanently.

### 3. Take control

Select an Agent on your phone, send messages, browse files.

---

## Custom Agent Protocol

Beyond built-in agents, Shennian supports any custom agent via this open protocol.

Your agent is a CLI program that reads from stdin and writes JSON Lines to stdout. Shennian handles the WebSocket relay, mobile UI, and push notifications.

```
Phone / Browser ←→ Shennian Cloud ←→ Shennian CLI ←→ stdin/stdout ←→ Your Agent
```

### Quickstart

**Python**

```python
#!/usr/bin/env python3
import sys, json

if sys.argv[1] == "/caps":
    print(json.dumps({"name": "My Agent", "model": "gpt-4o", "mode": "spawn"}))
    sys.exit(0)

if sys.argv[1] == "/run":
    message = sys.stdin.read()
    print(json.dumps({"state": "delta", "text": f"You said: {message}"}))
    print(json.dumps({"state": "final"}))
```

**Node.js**

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

### Register

```bash
shennian agent add my-agent --command "python /path/to/my_agent.py"
shennian agent list
shennian agent remove my-agent
```

The agent appears in the Shennian app alongside Claude, Codex, and other built-in agents.

Full protocol specification: **[PROTOCOL.md](./PROTOCOL.md)**

---

## SDK

| Language | Package |
|---|---|
| Node.js | `npm install @shennian/agent` |
| Python | `pip install shennian-agent` |

## Examples

Zero-dependency examples, no SDK required:

| Language | Mode | Source |
|---|---|---|
| Node.js | spawn | [examples/node/hello-spawn.mjs](./examples/node/hello-spawn.mjs) |
| Node.js | stdio | [examples/node/agent.mjs](./examples/node/agent.mjs) |
| Python | spawn | [examples/python/agent.py](./examples/python/agent.py) |
| Bash | spawn | [examples/bash/agent.sh](./examples/bash/agent.sh) |

---

## License

Protocol specification, SDKs, and examples are released under the [MIT License](./LICENSE).
