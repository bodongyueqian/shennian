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

### 快速接入

**Python**

```python
#!/usr/bin/env python3
import sys, json

if sys.argv[1] == "/caps":
    print(json.dumps({"name": "我的 Agent", "model": "gpt-4o", "mode": "spawn"}))
    sys.exit(0)

if sys.argv[1] == "/run":
    message = sys.stdin.read()
    print(json.dumps({"state": "delta", "text": f"你说: {message}"}))
    print(json.dumps({"state": "final"}))
```

**Node.js**

```bash
npm install @shennian/agent
```

```typescript
import { Agent } from '@shennian/agent'

const agent = new Agent({ name: '我的 Agent', model: 'gpt-4o' })

agent.onSend(async ({ text }) => {
  for await (const chunk of callMyLLM(text)) {
    agent.delta(chunk)
  }
  agent.final()
})

agent.run()
```

### 注册到 CLI

```bash
shennian agent add my-agent --command "python /path/to/my_agent.py"
shennian agent list
shennian agent remove my-agent
```

注册后，自定义 Agent 会与 Claude、Codex 等内置 Agent 一同出现在神念 App 中。

### 会话恢复

支持跨重启多轮对话的 Agent，需要在 `/caps` 中声明 `resume: true`，在 `final` 事件中返回 `agentSessionId`，并在 `/run` 中接受 `--resume <id>` 参数。神念负责持久化和回传 session ID，Agent 只需根据 ID 恢复自身状态。

完整协议规范：**[PROTOCOL.md](./PROTOCOL.md)**

---

## SDK

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
