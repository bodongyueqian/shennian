# 神念 Agent 协议

**用任意语言构建 AI Agent，随时随地从手机掌控它。**

[English](./README.md) · [协议规范](./PROTOCOL.md) · [shennian.ai](https://shennian.ai) · [shennian.net](https://shennian.net)

---

## 神念是什么？

**神念（Shennian）** 是一款 AI Agent 移动控制台。在本机运行一条命令，扫码配对，即可从手机、浏览器或桌面远程操控 Claude、Codex、Gemini、Cursor 等 AI Agent——内置文件浏览、推送通知、机器共享。

**立即体验：** [shennian.ai](https://shennian.ai) · [shennian.net](https://shennian.net)

**核心功能：**
- **多 Agent 支持** — 统一控制台切换 Claude、Codex、Gemini、Cursor、OpenClaw
- **内置文件系统** — 手机浏览目录、预览代码、上传下载，无需 SSH
- **推送通知** — 任务完成、告警触发，实时推送到手机
- **机器共享** — 生成带权限和有效期的分享码，授权给队友，随时撤销
- **自定义 Agent** — 通过本开放协议接入任意 Agent ← *你正在查看*

---

## 本仓库：自定义 Agent 协议

本仓库定义了让任意第三方 Agent 接入神念的**开放协议**。你的 Agent 只是一个 CLI 程序，从 stdin 读消息，向 stdout 写 JSON Lines，其余的网络中转、手机 UI、推送通知全由神念负责。

```
手机 / 浏览器 ←→ 神念云端 ←→ 神念 CLI ←→ stdin/stdout ←→ 你的 Agent
```

---

## 三步快速上手

### 1. 编写你的 Agent

最简 Agent 只需处理两个命令：`/caps` 和 `/run`。

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
    print(json.dumps({"state": "delta", "text": f"你说：{message}"}))
    print(json.dumps({"state": "final"}))
```

**Node.js**（使用 SDK）

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
  echo "{\"state\":\"delta\",\"text\":\"你说：$msg\"}"
  echo '{"state":"final"}'
fi
```

### 2. 安装神念 CLI，注册你的 Agent

```bash
# 安装 CLI（需要 Node.js 18+）
npx shennian

# 注册 Agent（CLI 自动运行 /caps 探测能力）
shennian agent add my-agent --command "python /path/to/my_agent.py"
```

### 3. 用手机控制

打开神念 App → 选择本机 → 选择 **My Agent** → 开始对话。

就这三步。

---

## 协议概览

### 两种生命周期模式

| 模式 | 工作方式 | 适用场景 |
|---|---|---|
| **spawn** | 每条消息新建子进程，stdin 写消息，stdout 读事件，进程退出即结束 | 简单脚本、无状态 Agent |
| **stdio** | 进程长驻，stdin/stdout 双向 JSON Lines 通信 | 有状态 Agent、主动推送 |

### 命令

| 命令 | 用途 |
|---|---|
| `my-agent /caps` | 声明能力（名称、模型、模式） |
| `my-agent /run --workdir=<path>` | 处理单条消息（spawn 模式） |
| `my-agent /start --workdir=<path>` | 启动长驻会话（stdio 模式） |

### 事件类型（stdout → 神念）

| state | 含义 |
|---|---|
| `delta` | 流式推送文本片段 |
| `final` | 本轮结束 |
| `error` | 报告错误，本轮结束 |
| `tool-call` | 在 UI 展示工具调用 |
| `tool-result` | 在 UI 展示工具结果 |
| `notify` | 主动推送到手机（stdio + proactive 模式） |

完整规范：**[PROTOCOL.md](./PROTOCOL.md)**

---

## 主动推送 Agent

**stdio** 模式 + `proactive: true` 的 Agent 可以主动向手机推送消息，无需用户触发——适合监控告警、定时任务、Webhook 回调：

```python
from shennian_agent import Agent

agent = Agent(name="Monitor", model="monitor-v1", mode="stdio", proactive=True)

@agent.on_send
def handle(text, **kwargs):
    agent.delta("监控已启动。")
    agent.final()

def on_alert(message):
    agent.notify(title="告警", text=message, source="monitor:cpu")

agent.run()
```

用户手机会立即收到推送通知，无需轮询。

---

## CLI 参考

```bash
# 注册自定义 Agent
shennian agent add <name> --command "<命令>"

# 示例
shennian agent add gpt      --command "python ~/agents/gpt_agent.py"
shennian agent add searcher --command "node ~/agents/search.mjs"
shennian agent add local    --command "/usr/local/bin/my-agent"

# 查看已注册的 Agent
shennian agent list

# 删除 Agent
shennian agent remove <name>
```

注册后，Agent 以 `custom:<name>` 的形式出现在神念 App 中，与内置的 Claude、Codex、Gemini 等完全并列。

---

## SDK

可选辅助库，帮你处理协议细节，专注实现 Agent 逻辑：

| 语言 | 包 | 源码 |
|---|---|---|
| Node.js | `npm install @shennian/agent` | [sdk/node/](./sdk/node/) |
| Python | `pip install shennian-agent` | [sdk/python/](./sdk/python/) |

---

## 示例

零依赖示例，纯 stdin/stdout，无需 SDK：

| 语言 | 模式 | 源码 |
|---|---|---|
| Node.js | spawn | [examples/node/hello-spawn.mjs](./examples/node/hello-spawn.mjs) |
| Node.js | stdio | [examples/node/agent.mjs](./examples/node/agent.mjs) |
| Python | spawn | [examples/python/agent.py](./examples/python/agent.py) |
| Bash | spawn | [examples/bash/agent.sh](./examples/bash/agent.sh) |

---

## 许可证

协议规范、SDK 及示例代码均以 [MIT License](./LICENSE) 开源。
