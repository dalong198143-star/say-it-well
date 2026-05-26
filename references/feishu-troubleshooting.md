# 飞书部署排查清单

say-it-well 在飞书上不追问、直接写代码的常见原因和修复步骤。

## 症状 1：Bot 不追问，直接创建文件/写代码

**原因**：say-it-well 虽然在系统提示词里，但 Bot 可能不主动加载它。

**修复（workaround — 不完美）**：

```bash
hermes config set feishu.channel_prompt "你是一个提示词助手。用户说的任何需求，都要先用 skill_view('say-it-well') 加载话说清楚技能，然后按技能里的追问流程一步步引导用户，不要直接写代码。切记：先追问，再动手。"
hermes gateway restart
```

**限制**：channel_prompt 只是自然语言指令，Bot 可能不听从。且飞书 adapter 有 bug（见症状 6），channel_prompt 不会自动传递。

## 症状 2：飞书会话全用 qwen3-max，配置的 deepseek-v4-pro 不生效

**根因分析**：

1. `feishu.model` / `feishu.provider` 配置项**不被 Gateway 代码读取**。Gateway 的 `_resolve_gateway_model()` 只读全局 `model.default`，不看平台级配置。
2. DeepSeek API key 缺在 `.env` 里会导致静默 fallback 到 `fallback_providers`（qwen3-max）。custom_providers 里的 key 可能不被 Gateway 的某些代码路径读取。

**修复**：

```bash
# 1. 确保全局 model.default 是 deepseek-v4-pro（已经是的跳过）
hermes config set model.default deepseek-v4-pro
hermes config set model.provider deepseek

# 2. 补 DEEPSEEK_API_KEY 到 .env（custom_providers 里的 key 可能不被 Gateway 读到）
echo "DEEPSEEK_API_KEY=sk-..." >> D:/hermes/.env

# 3. 重启 + 开新会话（旧会话模型锁定）
hermes gateway restart
# → 飞书发 /new → 发测试消息
```

## 症状 3：飞书不支持 /skill 和 /new 斜杠命令

**现象**：日志显示 `Unrecognized slash command /skill from feishu`

**结论**：飞书网关适配器不支持这些斜杠命令。但 `/new` 走确认流程可以用——Bot 会弹出 Approve 按钮。

## 症状 4：clarify 工具在飞书上卡死（\"Still working... running: clarify\"）

已在 say-it-well SKILL.md 里加了两条规则：
- 飞书平台上不要用 clarify 工具。clarify 在飞书上不支持交互式输入，调了会卡死。需要给用户选项时，直接文字列出来。
- 调用 clarify 之前必须先说一句过渡话（仅适用于 CLI 等支持 clarify 的平台）。

## 症状 4b：clarify 前 assistant 消息为空

旧症状——assistant 调 clarify 时没说话，直接弹按钮。已修复：SKILL.md 加了"调用 clarify 之前必须先说一句过渡话"。

## 症状 7：群聊里 say-it-well 不生效

**原因**：飞书群聊的 chat_id 和私聊不同（如 `oc_28d8d...` vs `oc_ef8176...`）。`channel_skill_bindings` 只配了私聊的 chat_id，群聊没配，所以 say-it-well 不会自动加载。

**修复**：把群聊 chat_id 也加到 config.yaml：

```yaml
feishu:
  channel_skill_bindings:
    - id: "oc_ef8176eb941646b3bfff30dc0cb62319"   # 私聊
      skills: ["say-it-well"]
    - id: "oc_28d8d090f9c8d425ee4799a2d0ea85f4"   # 群聊
      skills: ["say-it-well"]
```

改完重启 Gateway。新增群聊时都要补上。

## 症状 5：上下文频繁压缩（compacting context）

修复：`hermes config set compression.threshold 0.8`

## 症状 6（**源码级根因**）：channel_prompt 和 auto_skill 完全不生效

**根本原因**：飞书 adapter（`feishu.py`）创建 `MessageEvent` 时**没有**传入 `channel_prompt` 和 `auto_skill`。对比 Telegram/Discord——它们在 MessageEvent 构造前调用了 `resolve_channel_prompt()` 和 `resolve_channel_skills()`，飞书缺失这两步。

同时 `config.py` 第 861 行的 `channel_skill_bindings` 白名单只包含 `{DISCORD, SLACK}`，飞书被排除。

**源码级修复（一劳永逸）**：

### 1. `gateway/config.py` 第 861 行

```python
# 改前：
if plat in {Platform.DISCORD, Platform.SLACK} and "channel_skill_bindings" in platform_cfg:

# 改后：
if plat in {Platform.DISCORD, Platform.SLACK, Platform.FEISHU} and "channel_skill_bindings" in platform_cfg:
```

### 2. `gateway/platforms/feishu.py` MessageEvent 构造处（约第 3020 行）

在 `normalized = MessageEvent(` 之前插入：

```python
from gateway.platforms.base import resolve_channel_prompt, resolve_channel_skills
_chat_id_str = str(chat_id)
_channel_prompt = resolve_channel_prompt(
    self.config.extra,
    _chat_id_str,
    thread_id,
)
_auto_skill = resolve_channel_skills(
    self.config.extra,
    _chat_id_str,
    thread_id,
)
```

然后在 `MessageEvent(...)` 构造中加上：

```python
normalized = MessageEvent(
    ...
    auto_skill=_auto_skill,
    channel_prompt=_channel_prompt,
    timestamp=datetime.now(),
)
```

### 3. `config.yaml` feishu 段

```yaml
feishu:
  channel_skill_bindings:
    - id: "oc_ef8176eb941646b3bfff30dc0cb62319"  # 你的飞书频道 ID
      skills: ["say-it-well"]
```

### 效果

改完后，飞书用户每次发 `/new` 开新会话，Gateway 会：
1. 根据 `channel_skill_bindings` 自动加载 say-it-well 的完整 SKILL.md 内容
2. 将 `channel_prompt` 注入为 ephemeral system prompt
3. say-it-well 的 11 维方法论、反思推理、追问策略全部内化到 Bot 的上下文中

不再依赖 channel_prompt 那句模糊指令赌 Bot 会不会调用 `skill_view()`。

## 其他中国平台对比（QQ/微信）

QQ 和飞书情况相同——adapter 有但缺 channel_prompt/auto_skill 传递。同样的改法适用。Telegram 是唯一开箱即用支持完整 skill 自动加载的平台，但中国用户需翻墙。

## 验证 say-it-well 是否生效

1. 飞书发 `/new` → 点 Approve → 开新会话
2. 发 "帮我做个记账的"
3. 期望行为：Bot 先自我介绍，然后按 11 维方法论逐轮追问（一次一个问题），不是直接写代码
4. 检查 agent.log：`grep "auto_skill\|say-it-well" D:/hermes/logs/agent.log`
