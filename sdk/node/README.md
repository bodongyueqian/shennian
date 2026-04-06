# @shennian/agent

Node.js/TypeScript SDK for the [Shennian Agent Protocol](../../PROTOCOL.md).

Build AI agents that plug into the Shennian platform with a few lines of code.

## Install

```bash
npm install @shennian/agent
```

## Quick Start

```typescript
import { Agent } from '@shennian/agent'

const agent = new Agent({
  name: 'My Agent',
  models: ['gpt-4o', 'gpt-4.1'],
  defaultModel: 'gpt-4o',
})

agent.onSend(async ({ text, sessionId, modelId }) => {
  agent.delta(`Thinking with ${modelId ?? 'default model'}...`)
  // call your LLM here
  agent.delta('Here is the answer.')
  agent.final()
})

agent.run()
```

## Modes

**Spawn mode** (default) — CLI starts a new process per user message:

```bash
echo "Hello" | my-agent /run --session abc --workdir /tmp
```

With explicit model selection:

```bash
echo "Hello" | my-agent /run --session abc --workdir /tmp --model gpt-4.1
```

**Stdio mode** — long-running process, receives JSONL on stdin:

```typescript
const agent = new Agent({
  name: 'My Agent',
  models: ['gpt-4o', 'gpt-4.1'],
  defaultModel: 'gpt-4o',
  mode: 'stdio',
  proactive: true,
})
```

## Emitting Events

```typescript
agent.delta('partial text')          // stream text to user
agent.delta('thinking...', true)     // thinking indicator
agent.toolCall('search', { q: 'x' }) // tool call
agent.toolResult('search', '42')     // tool result
agent.notify('Done!', 'Title')       // notification
agent.error('Something went wrong')  // error (ends run)
agent.final()                        // end run
```

## Protocol

See [PROTOCOL.md](../../PROTOCOL.md) for the full specification.
