# Shennian — 随时随地，掌控你的 AI Agent

> AI Agent 触手可及。无需端口转发，无需 VPN，一条命令启动，扫码即用。

[English](./README.md) · [协议规范](./PROTOCOL.md) · [shennian.ai](https://shennian.ai) · [shennian.net](https://shennian.net)

---

在本机运行 `npx shennian`，扫码配对，即可从手机、浏览器或桌面远程操控 Claude、Codex、Nian 与自定义 Agent，查看文件系统，接收推送通知。

```bash
npx shennian
```

```
✓ Shennian v0.1.0 启动中...
✓ 已连接到中继：shennian.ai
◉ 扫描二维码或输入 Token 进行配对
  Token: sn-a3f9...
```

用神念 App 扫描二维码，30 秒内完成配对。

---

## 核心功能

**多 Agent 支持**
在一个控制台内自由切换 Claude、Codex、Nian。每个 Agent 独立会话，完整历史记录，断线自动恢复。

| Agent | 安装方式 |
|---|---|
| [Claude](https://claude.ai/code) | `npm install -g @anthropic-ai/claude-code` |
| [Codex](https://github.com/openai/codex) | `npm install -g @openai/codex` |
| Nian (Pi) | 内置 |

**内置文件系统**
直接从手机浏览目录树、预览代码文件、上传下载——无需 SSH。

**推送通知**
Agent 任务完成、Cron 触发、Hook 执行时即时推送。离开机器，完成时回来即可。

**端到端加密**
全程 TLS 加密。基于二维码的机器认证，支持权限级别与有效期设置。本地零端口暴露。

**机器共享**
生成有时效、有权限范围的二维码，让队友访问你的本地 Agent 环境，随时可撤销。

**全平台支持**
iOS、Android、Web、macOS、Windows，一个账号，所有设备无缝切换。

---

## 快速开始

### 1. 安装并运行

```bash
# 直接运行（无需安装）
npx shennian

# 或全局安装
npm install -g shennian
shennian
```

### 2. 扫码配对

用神念 App 扫描二维码或粘贴 Token——永久配对。

### 3. 开始掌控

在手机上选择 Agent，发送消息，浏览文件。

---

## 自定义 Agent 协议

除内置 Agent 外，神念支持通过本开放协议接入任意自定义 Agent。

你的 Agent 是一个从 stdin 读取、向 stdout 输出 JSON Lines 的命令行程序。Shennian 负责 WebSocket 中继、移动端 UI 和推送通知。

```
手机 / 浏览器 ←→ 神念云 ←→ Shennian CLI ←→ stdin/stdout ←→ 你的 Agent
```

### 你的 Agent 至少要实现什么

- `/caps`：声明 `name`、`model`、`models`、`defaultModel`、`mode`、`resume`
- `/run`：从 stdin 读取用户输入，并向 stdout 输出 JSONL 事件
- `--resume <id>`：如果你要支持真正的多轮续聊
- `--model <id>`：如果你希望在神念里切换模型

### 可直接复制的无 SDK Demo

公开 subtree 里已经放了两份推荐起点：

- Node: [examples/node/agent.mjs](./examples/node/agent.mjs)
- Python: [examples/python/agent.py](./examples/python/agent.py)

这两份 demo 都是：

- 纯 Node.js / 纯 Python
- 不依赖 Shennian SDK
- 直接对接 DeepSeek OpenAI 兼容接口
- 本地文件持久化 session，实现 `resume`
- 在神念里暴露 `deepseek-chat` 和 `deepseek-reasoner`

#### Node demo

```bash
cp examples/node/.env.example examples/node/.env
# 在 examples/node/.env 里填 LLM_API_KEY

shennian agent add demo-node --command "node $(pwd)/examples/node/agent.mjs"
shennian agent list
```

关键逻辑：

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
# 在 examples/python/.env 里填 LLM_API_KEY

shennian agent add demo-python --command "python3 $(pwd)/examples/python/agent.py"
shennian agent list
```

关键逻辑：

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

### 注册、使用、移除

```bash
shennian agent add demo-node --command "node /绝对路径/examples/node/agent.mjs"
shennian agent add demo-python --command "python3 /绝对路径/examples/python/agent.py"

shennian agent list

shennian agent remove demo-node
shennian agent remove demo-python
```

`agent add` 后，它会在神念里显示为 `custom:demo-node` 或 `custom:demo-python`。可以正常选择、发送第一轮、继续发送第二轮，并通过 `agentSessionId` 持续续聊，因为 demo 自己负责本地 session 管理。

完整协议规范：**[PROTOCOL.md](./PROTOCOL.md)**

---

## SDK

SDK 是可选项，不是接入前提。想完全手写协议，就直接用上面的 demo 即可。

| 语言 | 包 |
|---|---|
| Node.js | `npm install @shennian/agent` |
| Python | `pip install shennian-agent` |

## 示例

以下示例无需 SDK，零依赖即可运行：

| 语言 | 源码 |
|---|---|
| Node.js | [examples/node/hello-spawn.mjs](./examples/node/hello-spawn.mjs) |
| Python | [examples/python/agent.py](./examples/python/agent.py) |
| Bash | [examples/bash/agent.sh](./examples/bash/agent.sh) |

---

## 许可证

协议规范、SDK 及示例均以 [MIT License](./LICENSE) 开源。
