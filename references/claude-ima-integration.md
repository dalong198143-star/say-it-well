# Claude Code ↔ IMA 知识库对接

> IMA（腾讯 IMA Copilot）是云端知识库，Claude Code 通过 MCP 协议调用

## 架构

```
Claude Code → MCP (HTTP) → IMA MCP Server (127.0.0.1:8081) → 腾讯 IMA API → 你的知识库
```

## 1. 确认 IMA MCP 服务在运行

```bash
# 检查端口
netstat -ano | findstr ":8081"

# 如果没在监听，手动启动
cd D:\maozhua\ima-mcp
D:\hermes-tools\python\Python311\Scripts\fastmcp.exe run ima_server_simple.py:mcp --transport http --host 127.0.0.1 --port 8081
```

> ⚠️ IMA MCP 有自动健康检查 cron（每 5 分钟），挂了会自动重启。不需要手动管。

## 2. Claude Code 添加 IMA MCP

在 Claude Code 对话中或终端执行：

```bash
claude mcp add ima --transport http --url http://127.0.0.1:8081/mcp
```

验证连接：

```bash
claude mcp list
# 应该看到 ima（HTTP，已连接）
```

## 3. 使用

在 Claude Code 对话中直接说：

```
"帮我查 IMA 知识库里关于 say-it-well 的内容"
"把这段总结存到 IMA 的知识库"
"用 IMA 查一下上次聊的无人机配送方案"
```

Claude 会自动调用 IMA 的 `ask` 工具。

## 4. IMA vs 本地 KB 使用场景

| 场景 | 用什么 |
|------|--------|
| 查项目技术经验、方法论、规则 | 本地 KB（`query_kb.py`） |
| 查云端知识库、对外输出内容 | IMA（MCP `ask` 工具） |
| 存项目决策、bug 修复经验 | 本地 KB（`add_to_kb.py`） |
| 存对外发布的内容、素材 | IMA（手动拖入） |

## 5. 常见问题

**Q: IMA MCP 连接失败？**
检查服务是否在运行，或等 cron 自动重启（每 5 分钟）

**Q: Claude 说找不到 IMA 工具？**
重新添加 MCP：`claude mcp remove ima && claude mcp add ima --transport http --url http://127.0.0.1:8081/mcp`

**Q: IMA 和本地 KB 都存了同一份知识？**
设计如此。本地 KB 是热数据（秒级查询），IMA 是冷存储+对外发布。

## 6. 依赖

| 组件 | 位置 | 状态 |
|------|------|:--:|
| IMA MCP Server | D:\maozhua\ima-mcp\ima_server_simple.py | cron 自动重启 |
| IMA 环境变量 | D:\maozhua\ima-mcp\.env | IMA_X_IMA_COOKIE + IMA_X_IMA_BKN |
| Claude Code | v2.1.150 | 已安装 |
