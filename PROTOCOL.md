# Shennian Agent Protocol v1

A standard protocol for integrating third-party AI agents into the [Shennian](https://codyer.com) platform.

Shennian is a mobile control console for AI agents. You run agents on your local machine, and control them from your phone or browser — anywhere. This protocol defines how any agent can plug into that system.

---

## Overview

An agent is a **command-line program** that communicates via **stdin/stdout** using **JSON Lines** (one JSON object per line). Shennian CLI spawns your agent process and bridges messages between the Shennian relay server and your agent. Your agent never touches WebSocket, HTTP, or any network protocol — just stdin and stdout.

```
Phone/Browser ←→ Shennian Relay Server ←→ Shennian CLI ←→ [stdin/stdout] ←→ Your Agent
```

Your agent runs in a specified working directory and has full local filesystem access, just like any CLI tool.

---

## Terminology

| Term | Meaning |
|---|---|
| **Agent** | A CLI program that implements this protocol |
| **Shennian CLI** | The bridge process (`npx shennian`) that runs on the user's machine |
| **Relay** | Shennian's cloud server that routes messages between clients and CLI |
| **Session** | A conversation thread between user and agent |
| **Run** | A single turn within a session (user sends → agent responds) |
| **Event** | A JSON object written by the agent to stdout |

---

## 1. Capabilities Discovery

Every agent MUST respond to the `/caps` command:

```bash
my-agent /caps
```

The agent prints a single JSON line to stdout and exits:

```json
{
  "name": "My Agent",
  "model": "gpt-4o",
  "mode": "spawn",
  "proactive": false,
  "resume": false,
  "version": "1.0.0"
}
```

### Fields

| Field | Required | Type | Description |
|---|---|---|---|
| `name` | yes | string | Display name shown in Shennian clients |
| `model` | yes | string | Model identifier shown in agent list |
| `mode` | yes | `"spawn"` \| `"stdio"` | Lifecycle mode (see sections 2 and 3) |
| `proactive` | no | boolean | Can the agent send unsolicited messages? Default `false`. Only valid when `mode` is `"stdio"` |
| `resume` | no | boolean | Does the agent support resuming previous sessions? Default `false` |
| `version` | no | string | Agent version (semver recommended) |

---

## 2. Spawn Mode

In spawn mode, Shennian CLI launches a **new process for each user message**.

### Invocation

```bash
my-agent /run [options]
```

### Options

| Option | Required | Description |
|---|---|---|
| `--workdir <path>` | yes | Working directory for the agent |
| `--session <id>` | no | Shennian session ID |
| `--resume <id>` | no | Agent-native session ID to resume (only if `resume: true` in caps) |
| `--attachment <path>` | no | Path to an attached file. Can be repeated for multiple files |

### stdin

The user's message text. Read until EOF.

### stdout

JSON Lines events (see [Section 4: Events](#4-event-format)).

### Lifecycle

1. Shennian spawns the process with the options above
2. Writes the user message to stdin, then closes stdin
3. Reads JSONL events from stdout as the agent streams its response
4. Process exits with code 0 → success
5. Process exits with non-zero code → Shennian reads stderr as error message

### Example flow

```
$ echo "What files are in this project?" | my-agent /run --workdir=/home/user/project

{"state":"delta","text":"Let me check the project structure.\n"}
{"state":"tool-call","name":"list_dir","args":{"path":"."}}
{"state":"tool-result","name":"list_dir","result":"src/ package.json README.md"}
{"state":"delta","text":"This project contains:\n- `src/` — source code\n- `package.json`\n- `README.md`"}
{"state":"final","usage":{"inputTokens":42,"outputTokens":128}}
```

---

## 3. Stdio Mode

In stdio mode, Shennian CLI launches the agent **once** and communicates through stdin/stdout for the entire session lifecycle.

### Invocation

```bash
my-agent /start [options]
```

### Options

| Option | Required | Description |
|---|---|---|
| `--workdir <path>` | yes | Working directory for the agent |

### stdin (Shennian → Agent)

JSON Lines messages, one per line:

#### `send` — User sends a message

```json
{
  "method": "send",
  "id": "msg-001",
  "params": {
    "sessionId": "session-abc",
    "text": "Hello, help me refactor this code",
    "attachments": [
      {"path": "/tmp/shennian/screenshot.png", "name": "screenshot.png", "mime": "image/png"}
    ]
  }
}
```

#### `resume` — Resume a previous session

```json
{
  "method": "resume",
  "id": "msg-002",
  "params": {
    "sessionId": "session-abc",
    "agentSessionId": "agent-native-session-xyz"
  }
}
```

#### `stop` — Shutdown gracefully

```json
{
  "method": "stop",
  "id": "msg-003"
}
```

The agent should flush any pending work, write a `final` event if mid-response, and exit cleanly.

### stdout (Agent → Shennian)

JSON Lines events (see [Section 4: Events](#4-event-format)).

### Proactive Messages

When `proactive: true` in caps, the agent MAY write events to stdout at any time — even without a preceding `send` message. This enables agents that monitor systems, run scheduled tasks, or receive external webhooks to push notifications to the user's phone.

---

## 4. Event Format

Every line written to stdout MUST be a valid JSON object with a `state` field.

### 4.1 `delta` — Streaming text chunk

```json
{"state": "delta", "text": "Hello, "}
```

With thinking/reasoning content (displayed as a collapsible block in the UI):

```json
{"state": "delta", "text": "Let me think about this...", "thinking": true}
```

### 4.2 `final` — Turn complete

```json
{"state": "final"}
```

With usage stats (optional):

```json
{"state": "final", "usage": {"inputTokens": 150, "outputTokens": 320}}
```

Every response MUST end with a `final` event. This signals to Shennian that the agent is done with the current turn.

### 4.3 `error` — Something went wrong

```json
{"state": "error", "message": "API rate limit exceeded"}
```

After an `error`, the turn is considered complete (no `final` needed).

### 4.4 `tool-call` — Agent is invoking a tool

```json
{"state": "tool-call", "name": "read_file", "args": {"path": "src/main.ts"}}
```

This is purely informational — it tells the Shennian UI to render a tool call block. The agent executes the tool locally; Shennian does not intercede.

### 4.5 `tool-result` — Tool execution result

```json
{"state": "tool-result", "name": "read_file", "result": "import express from 'express';\n..."}
```

### 4.6 `notify` — Proactive notification (stdio mode only)

```json
{"state": "notify", "title": "Build Complete", "text": "Project built successfully in 12s", "source": "ci:build"}
```

| Field | Required | Description |
|---|---|---|
| `title` | no | Notification title (used in push notifications) |
| `text` | yes | Notification body |
| `source` | no | Identifier for the notification source (e.g. `"cron:backup"`, `"hook:github"`) |

`notify` events trigger push notifications on the user's phone when the app is in background.

### Optional fields on all events

| Field | Type | Description |
|---|---|---|
| `runId` | string | Identifies a conversation turn. If omitted, Shennian auto-generates one |
| `seq` | number | Sequence number within a run. If omitted, Shennian auto-increments |

These are useful for advanced agents that manage their own turn tracking. Most agents can omit them.

---

## 5. Registration

Users register third-party agents via the Shennian CLI:

```bash
# Add an agent
shennian agent add my-agent --command "python /path/to/my_agent.py"
shennian agent add my-agent --command "npx my-agent-package"
shennian agent add my-agent --command "/usr/local/bin/my-agent"

# Shennian automatically runs: my-agent /caps
# and stores the result in ~/.shennian/config.json

# List registered agents
shennian agent list

# Remove an agent
shennian agent remove my-agent
```

Once registered, the agent appears in the Shennian mobile/web app alongside built-in agents (Claude, Cursor, etc.) under the type `custom:<name>`.

---

## 6. Error Handling

### Agent crash (non-zero exit)

If the agent process exits with a non-zero code, Shennian reads stderr and sends an `error` event to the client:

```json
{"state": "error", "message": "<stderr content>"}
```

### Malformed output

Lines that are not valid JSON are silently ignored. Shennian logs them locally for debugging.

### Timeout

Shennian does not impose a global timeout. The user can abort a running agent from the client, which:
- **Spawn mode**: sends SIGTERM to the process (SIGKILL after 3s)
- **Stdio mode**: writes `{"method":"stop"}` to stdin. If the agent doesn't exit within 5s, SIGTERM → SIGKILL

---

## 7. Quick Reference

### Minimum viable agent (spawn mode)

Your agent must handle two commands:
1. `my-agent /caps` → print caps JSON, exit
2. `my-agent /run --workdir=<path>` → read stdin, print JSONL events to stdout, exit

That's it. Everything else is optional.

### Minimum viable agent (stdio mode)

Your agent must handle:
1. `my-agent /caps` → print caps JSON, exit
2. `my-agent /start --workdir=<path>` → read JSONL from stdin, write JSONL events to stdout, stay alive

### Event state cheat sheet

```
delta        → streaming text (required for any response)
final        → turn complete (required to end a turn)
error        → something broke (ends the turn)
tool-call    → show a tool call in UI (optional)
tool-result  → show tool result in UI (optional)
notify       → push notification (proactive only)
```

---

## 8. Versioning

This document describes protocol version 1. The version is implicit in the protocol behavior. Future versions will maintain backward compatibility where possible, and agents can declare their supported protocol version in caps if needed.

---

## License

This protocol specification is released under the [MIT License](./LICENSE).
