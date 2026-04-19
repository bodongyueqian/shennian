# Shennian — Control Your AI Agents, Anywhere

> AI Agents at Your Fingertips. No port forwarding. No VPN. One command to start, scan to use.

[中文文档](./README.zh.md) · [Protocol Spec](./PROTOCOL.md) · [shennian.ai](https://shennian.ai) · [shennian.net](https://shennian.net)

---

Run `npx shennian` on your machine, scan to pair, and remotely control Claude, Codex, Nian, and custom agents from your phone, browser, or desktop.

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
Switch between Claude, Codex, and Nian in one console. Independent sessions per agent, full history, reconnect and resume.

| Agent | Install |
|---|---|
| [Claude](https://claude.ai/code) | `npm install -g @anthropic-ai/claude-code` |
| [Codex](https://github.com/openai/codex) | `npm install -g @openai/codex` |
| Nian (Pi) | Built in |

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

### What your agent must implement

- `/caps` to describe `name`, `model`, `models`, `defaultModel`, `mode`, and `resume`
- `/run` to read user text from stdin and emit JSONL events to stdout
- `--resume <id>` if you want real multi-turn continuity
- `--model <id>` if you expose multiple models in the UI

### Zero-SDK demos you can copy

The public examples in this repo are the recommended starting point:

- Node: [examples/node/agent.mjs](./examples/node/agent.mjs)
- Python: [examples/python/agent.py](./examples/python/agent.py)

Both demos are:

- plain Node.js / plain Python
- no Shennian SDK
- wired to the DeepSeek OpenAI-compatible API
- local-file based for `resume`
- exposing `deepseek-chat` and `deepseek-reasoner` through `models`

#### Node demo

```bash
cp examples/node/.env.example examples/node/.env
# fill LLM_API_KEY in examples/node/.env

shennian agent add demo-node --command "node $(pwd)/examples/node/agent.mjs"
shennian agent list
```

Key parts of the demo:

```javascript
const supportedModels = ['sonnet-4', 'gpt-4.1']

if (command === '/caps') {
  emit({
    name: 'My Demo Agent',
    model: 'sonnet-4',
    models: supportedModels,
    defaultModel: 'sonnet-4',
    mode: 'spawn',
    resume: true,
  })
}

if (command === '/run') {
  const agentSessionId = args.resumeId || args.sessionId || randomUUID()
  const history = loadSessionMessages('.sessions', agentSessionId)
  const userText = await readStdin()
  const messages = [
    { role: 'system', content: 'You are a helpful coding agent.' },
    ...history,
    { role: 'user', content: userText },
  ]

  const reply = await callYourModelProvider({
    apiKey: process.env.LLM_API_KEY,
    baseUrl: 'https://api.example.com/v1',
    model: args.modelId || 'sonnet-4',
    messages,
  })

  saveSessionMessages('.sessions', agentSessionId, [
    ...history,
    { role: 'user', content: userText },
    { role: 'assistant', content: reply.text },
  ])

  emit({ state: 'delta', text: reply.text })
  emit({ state: 'final', usage: reply.usage, agentSessionId })
}
```

#### Python demo

```bash
cp examples/python/.env.example examples/python/.env
# fill LLM_API_KEY in examples/python/.env

shennian agent add demo-python --command "python3 $(pwd)/examples/python/agent.py"
shennian agent list
```

Key parts of the demo:

```python
def caps() -> None:
    emit(
        {
            "name": "My Demo Agent",
            "model": "sonnet-4",
            "models": ["sonnet-4", "gpt-4.1"],
            "defaultModel": "sonnet-4",
            "mode": "spawn",
            "resume": True,
        }
    )

def run(workdir: str, session: str | None, resume: str | None, model: str | None, attachments: list[str]) -> None:
    agent_session_id = resume or session or str(uuid.uuid4())
    history = load_session_messages(".sessions", agent_session_id)
    user_text = sys.stdin.read().strip()
    messages = [{"role": "system", "content": "You are a helpful coding agent."}, *history, {"role": "user", "content": user_text}]
    reply_text, usage = call_model_provider(
        api_key=os.environ["LLM_API_KEY"],
        base_url="https://api.example.com/v1",
        model=model or "sonnet-4",
        messages=messages,
    )
    save_session_messages(
        ".sessions",
        agent_session_id,
        [*history, {"role": "user", "content": user_text}, {"role": "assistant", "content": reply_text}],
    )
    emit({"state": "delta", "text": reply_text})
    emit({"state": "final", "usage": usage, "agentSessionId": agent_session_id})
```

### Register, use, and remove

```bash
shennian agent add demo-node --command "node /abs/path/to/examples/node/agent.mjs"
shennian agent add demo-python --command "python3 /abs/path/to/examples/python/agent.py"

shennian agent list

shennian agent remove demo-node
shennian agent remove demo-python
```

After `agent add`, the agent appears in Shennian as `custom:demo-node` or `custom:demo-python`. You can select it, chat normally, send a second turn, and keep resuming because the demo stores its own session state and returns `agentSessionId` on every `final`.

Full protocol specification: **[PROTOCOL.md](./PROTOCOL.md)**

---

## SDK

SDKs are optional. Use them only if you want helpers instead of writing the protocol yourself.

| Language | Package |
|---|---|
| Node.js | `npm install @shennian/agent` |
| Python | `pip install shennian-agent` |

## Examples

Zero-dependency examples, no SDK required:

| Language | Source |
|---|---|
| Node.js | [examples/node/hello-spawn.mjs](./examples/node/hello-spawn.mjs) |
| Python | [examples/python/agent.py](./examples/python/agent.py) |
| Bash | [examples/bash/agent.sh](./examples/bash/agent.sh) |

---

## License

Protocol specification, SDKs, and examples are released under the [MIT License](./LICENSE).
