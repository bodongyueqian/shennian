# Shennian — 随时随地，指挥你的 AI Agent

> 手机在哪，那台电脑上的 Agent 就在哪——不用守着桌子。

[English](./README.md) · [协议规范](./PROTOCOL.md) · [shennian.ai](https://shennian.ai) · [shennian.net](https://shennian.net)

<p align="center">
  <img src="./docs/screens/screen-chat.png" alt="神念 — 手机上对话，电脑上执行" width="320" />
</p>

神念把你已经有的那些电脑，变成可以从口袋里指挥的东西。在一台机器上跑一次 `shennian`，手机扫码配对一次，从此 Claude Code、Codex、Gemini、Cursor，以及你自己接入的任何 Agent，都在你手边一次点按之内——无论你在咖啡馆、地铁、厨房，还是躺在床上。

Agent 仍然跑在 **你自己的** 电脑上，神念只是那座桥，不是算力本身。

```bash
npm install -g shennian
shennian
```

```
✓ Shennian v0.1.0 启动中...
✓ 已连接到中继：shennian.ai
◉ 扫描二维码或输入 Token 进行配对
  Token: sn-a3f9...
```

---

## 为什么需要神念

**一台不用坐在前面的工作站。**
代码、凭证、环境本来就都在你那台电脑上。神念让这台电脑能「接电话」——从任何地方打开会话，Agent 继续在你的硬件上运行，读你的文件，调你的 API，用你的 SSH key。

**不是又一个云端 IDE。**
不上传代码，不做端口转发，不配 VPN，不用在路由器上开入站规则。CLI 只建立一条出站中继连接，其它一切都留在本机。

**一个控制台，覆盖所有 Agent。**
Claude Code、Codex、Gemini CLI、Cursor Agent、OpenClaw、内置的 Nian，再加上你按协议接入的任何自定义 Agent，共享同一个手机端、同一套会话列表、同一套推送。

---

## 核心能力

### 主流 Agent 开箱即用
自动检测本机已装好的 Agent，不需要额外适配，也不用再写配置，装好即显示在手机里。

| Agent | 在你电脑上的安装方式 |
|---|---|
| [Claude Code](https://claude.ai/code) | `npm install -g @anthropic-ai/claude-code` |
| [Codex](https://github.com/openai/codex) | `npm install -g @openai/codex` |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | `npm install -g @google/gemini-cli` |
| [Cursor Agent](https://cursor.com) | 随 Cursor 一并安装 |
| [OpenClaw](https://openclaw.com) | 神念自动识别本地网关 |
| Nian（内置） | CLI 自带，无需 API Key |

### 多机都是你的工作站
家里的 Mac、公司的台式机、柜子里那台 GPU 机器、租来的云主机——任何装了 `shennian` 的机器都会出现在同一个机器列表里，手机上像切 App 一样切换。Agent 跑在**那台电脑**上，不是云沙盒。

<p align="center">
  <img src="./docs/screens/screen-machines.png" alt="机器列表" width="260" />
  <img src="./docs/screens/screen-sessions.png" alt="跨机器的对话列表" width="260" />
</p>

### 带上你自己的 Agent
任何能从 stdin 读、向 stdout 输出 JSONL 的程序都能接入神念。实现 `/caps` 和 `/run`，用 `shennian agent add` 注册一下，就立即拿到中继、手机端、会话持久化和推送通知——自己不用再写前端。

详见下文的 [自定义 Agent 协议](#自定义-agent-协议)。

### 本机文件浏览器
直接在手机上浏览本机目录——树形视图、文件预览、上传下载、为某个 Agent 会话动态切换工作目录。无需 SSH，无需 iCloud 中转。

<p align="center">
  <img src="./docs/screens/screen-files.png" alt="手机上的文件浏览器" width="260" />
</p>

### 真正能用的语音
不只是语音转文字——端内模型会把零散的口语润色成可执行的指令，还会记住你的专业术语。走着路也能驱动 Agent。

<p align="center">
  <img src="./docs/screens/screen-voice.png" alt="语音输入" width="260" />
</p>

### 完成时，自己找你
Cron 触发、Hook 执行、长任务跑完——神念会推送到你手机。合上 App，走开，等到红点变绿再回来。

### 机器共享，权限你说了算
签发一张带时效和权限范围的邀请码，同事或客户可以临时接入某台机器，看不到你的凭证，随时一键撤销。

### 到处都是你熟悉的那个客户端
iOS、Android、Web 同一套代码，同一个账号，沙发上开始，笔电上接着敲。

---

## 快速开始

### 1. 在你想要操控的那台电脑上安装 CLI
```bash
npm install -g shennian
shennian
```
要求 Node.js ≥ 18。这一条命令会完成配对并启动后台 daemon。

### 2. 装一个客户端
- iOS —— [TestFlight](https://testflight.apple.com/join/shennian) *(内测)*
- Android —— [APK 下载](https://shennian.net/download)
- Web —— [shennian.ai](https://shennian.ai)（海外）· [shennian.net](https://shennian.net)（国内）

### 3. 扫码配对
CLI 第一次启动时会打印二维码，扫一次即绑定账号，后续打开 App 就能直接用。

---

## 自定义 Agent 协议

神念内置的 Agent 只是开胃菜，真正的能力是 **你自己的 Agent**。协议刻意做得很小：一个通过 stdin / stdout 讲 JSONL 的命令行程序就够。

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

两份 demo 都是纯 Node.js / 纯 Python，不依赖 Shennian SDK，直接对接 DeepSeek OpenAI 兼容接口，用本地文件持久化 session，并在神念里暴露 `deepseek-chat` 和 `deepseek-reasoner` 两个模型。

#### Node demo
```bash
cp examples/node/.env.example examples/node/.env
# 在 examples/node/.env 里填 LLM_API_KEY

shennian agent add demo-node --command "node $(pwd)/examples/node/agent.mjs"
shennian agent list
```

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

`agent add` 之后，它会在神念里以 `custom:demo-node` 或 `custom:demo-python` 的形式出现。正常选择、发送第一轮、继续发送第二轮，并通过 `agentSessionId` 持续续聊——demo 自己负责本地 session 管理。

完整协议规范：**[PROTOCOL.md](./PROTOCOL.md)**

---

## SDK

SDK 是可选项，不是接入前提。想完全手写协议，就直接用上面的 demo 即可。

| 语言 | 包 |
|---|---|
| Node.js | `npm install @shennian/agent` |
| Python | `pip install shennian-agent` |

## 更多示例

以下示例无需 SDK，零依赖即可运行：

| 语言 | 源码 |
|---|---|
| Node.js | [examples/node/hello-spawn.mjs](./examples/node/hello-spawn.mjs) |
| Python | [examples/python/agent.py](./examples/python/agent.py) |
| Bash | [examples/bash/agent.sh](./examples/bash/agent.sh) |

---

## 许可证

协议规范、SDK 及示例均以 [MIT License](./LICENSE) 开源。
