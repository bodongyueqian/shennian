#!/usr/bin/env node
/**
 * Minimal Shennian agent in Node.js (stdio mode, no SDK).
 * Long-lived process that echoes user messages.
 * Replace the echo logic with your own LLM calls.
 *
 * Register:  shennian agent add echo-node --command "node /path/to/agent.mjs"
 */
import { createInterface } from 'node:readline'

const args = process.argv.slice(2)
const command = args[0]

function emit(event) {
  process.stdout.write(JSON.stringify(event) + '\n')
}

if (command === '/caps') {
  emit({
    name: 'Echo Agent (Node)',
    model: 'echo-v1',
    mode: 'stdio',
    proactive: false,
    resume: false,
    version: '1.0.0',
  })
  process.exit(0)
}

if (command === '/start') {
  let workdir = '.'
  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--workdir' && args[i + 1]) {
      workdir = args[++i]
    } else if (args[i].startsWith('--workdir=')) {
      workdir = args[i].split('=')[1]
    }
  }

  const rl = createInterface({ input: process.stdin })

  rl.on('line', (line) => {
    let msg
    try {
      msg = JSON.parse(line)
    } catch {
      return
    }

    if (msg.method === 'send') {
      const text = msg.params?.text ?? ''
      emit({ state: 'delta', text: `Echo: ${text}` })
      emit({ state: 'final' })
    }

    if (msg.method === 'stop') {
      process.exit(0)
    }
  })

  rl.on('close', () => process.exit(0))
} else {
  process.stderr.write('Usage: agent.mjs /caps | /start --workdir=<path>\n')
  process.exit(1)
}
