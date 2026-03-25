// In production: import { Agent } from '@shennian/agent'
import { Agent } from '../dist/index.js'

const agent = new Agent({
  name: 'Echo Agent',
  model: 'echo',
})

agent.onSend(({ text }) => {
  agent.delta(`You said: ${text}`)
  agent.final()
})

agent.run()
