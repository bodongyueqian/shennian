# shennian-agent

Python SDK for the [Shennian Agent Protocol](../../PROTOCOL.md).

Build AI agents that plug into the [Shennian](https://codyer.com) platform with a few lines of Python.

## Install

```bash
pip install shennian-agent
```

Or install from source:

```bash
pip install -e sdk/python/
```

## Quick Start

```python
from shennian_agent import Agent

agent = Agent(name="My Agent", model="gpt-4o", mode="spawn")

@agent.on_send
def handle(text, session_id, attachments):
    agent.delta(f"You said: {text}")
    agent.final()

if __name__ == "__main__":
    agent.run()
```

Register with Shennian CLI:

```bash
shennian agent add my-agent --command "python my_agent.py"
```

## API

### `Agent(name, model, mode="stdio", proactive=False, resume=False, version="1.0.0")`

- `mode="spawn"` — new process per message (`/run`)
- `mode="stdio"` — long-running process (`/start`)

### Decorators

- `@agent.on_send` — handle user messages `fn(text, session_id, attachments)`
- `@agent.on_resume` — handle session resume `fn(session_id, agent_session_id)`

### Emit Methods

| Method | Description |
|---|---|
| `agent.delta(text, thinking=False)` | Stream a text chunk |
| `agent.tool_call(name, args=None)` | Show a tool invocation in the UI |
| `agent.tool_result(name, result)` | Show a tool result in the UI |
| `agent.final(usage=None)` | End the current turn |
| `agent.error(message)` | Report an error (ends the turn) |
| `agent.notify(text, title, source)` | Push notification (proactive only) |

### Events

All event types are available as dataclasses: `DeltaEvent`, `FinalEvent`, `ErrorEvent`, `ToolCallEvent`, `ToolResultEvent`, `NotifyEvent`.

Use `serialize(event)` to convert any event to a JSON line string.

## Examples

- [`examples/simple.py`](examples/simple.py) — minimal echo agent (spawn mode)
- [`examples/proactive.py`](examples/proactive.py) — monitoring agent with background notifications (stdio mode)

## License

MIT
