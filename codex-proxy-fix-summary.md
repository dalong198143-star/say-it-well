# Codex 本地代理修复总结

> 修复日期：2026-05-26
> 执行：Claude Code（克劳德）
> 项目目录：D:/maozhua/Codex

## 问题诊断

Codex 的本地代理启动脚本（LiteLLM 代理 + 国产模型接入）存在多处损坏，导致启动失败或行为异常。

## 修复清单

### 1. 移除 chcp 65001（影响 5 个文件）

`chcp 65001 >nul` 在 Windows .bat 文件中将控制台编码切换为 UTF-8，但副作用严重：
- 破坏 pipe（|）符号
- 破坏 label（:label）语法
- 导致 Unicode 字符显示异常

影响文件：
- `启动代理.bat`
- `start_proxy.bat`
- `simple-start.bat`
- `test_proxy.bat`
- `诊断并启动.bat`

修复：全部移除 `chcp 65001 >nul` 行。

### 2. 修复 curl 命令引号

`启动代理.bat` 第 76 行 curl 命令存在未闭合引号，导致命令解析失败。

### 3. 修复 provider 名称

`启动代理.bat` 第 88 行显示的接入命令中 provider 写成了 `ollama`，应为 `local-deepseek`。

### 4. 更新 Codex 默认配置

`~/.codex/config.toml`:
- `model = "gpt-4o"` → `model = "deepseek-v4"`
- `model_provider = "openai"` → `model_provider = "local-deepseek"`

### 5. 标记废弃脚本

`start_proxy.bat` 添加废弃提示，引导用户使用 `启动代理.bat`（功能更完整的版本）。

### 6. ASCII 化全部输出

将 .bat 文件中所有 Unicode 符号替换为纯 ASCII：
- `✓` → `[OK]`
- `❌` → `[ERROR]`
- `⚠️` → `[WARN]`
- 框线字符（╔╗╚╝║═）→ `+---` 和 `|`

### 7. 健康检查验证

```bash
curl http://127.0.0.1:1234/health
```

代理服务正常运行。

## 经验教训

1. **Windows .bat 文件不要用 chcp 65001**——副作用远大于好处，用纯 ASCII 输出即可
2. **Unicode 符号在 .bat 中不可靠**——使用 `[OK]`、`[ERROR]`、`[WARN]` 等 ASCII 标签
3. **Codex 配置优先指向本地代理**——`model_provider = "local-deepseek"` 配合 `启动代理.bat`
