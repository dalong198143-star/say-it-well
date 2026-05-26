# 飞书 Adapter 修复步骤

让飞书支持 auto_skill 和 channel_prompt，需改三个文件。

## 问题

飞书 adapter 不传 channel_prompt 和 auto_skill 给 MessageEvent，导致：
- `feishu.skills: say-it-well` 不生效
- channel_prompt 指令无法到达模型
- clarify 工具在飞书上卡死（闭源聊天平台不支持交互式输入）

## 修复

### 1. config.py — 加飞书到 channel_skill_bindings 白名单

文件：`gateway/config.py`，约第 861 行

```diff
- if plat in {Platform.DISCORD, Platform.SLACK} and "channel_skill_bindings" in platform_cfg:
+ if plat in {Platform.DISCORD, Platform.SLACK, Platform.FEISHU} and "channel_skill_bindings" in platform_cfg:
```

### 2. feishu.py — 加 channel_prompt + auto_skill 解析

文件：`gateway/platforms/feishu.py`，在 MessageEvent 创建前插入：

```python
# Per-channel ephemeral prompt and auto-skill
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

然后在 MessageEvent 构造中加上：
```python
normalized = MessageEvent(
    ...
    auto_skill=_auto_skill,
    channel_prompt=_channel_prompt,
    ...
)
```

### 3. config.yaml — 配置 channel_skill_bindings

```yaml
feishu:
  channel_skill_bindings:
    - id: "oc_ef8176eb941646b3bfff30dc0cb62319"   # 私聊 chat_id
      skills: ["say-it-well"]
    - id: "oc_28d8d090f9c8d425ee4799a2d0ea85f4"   # 群聊 chat_id
      skills: ["say-it-well"]
```

注意：群聊和私聊是不同的 chat_id，都要配。

### 4. 重启验证

```bash
hermes gateway restart
# 飞书发 /new → 日志应出现 "Auto-loaded skill(s) ['say-it-well']"
```

## clarify 工具在飞书上的限制

clarify 在飞书（以及其他闭源聊天平台）上**不支持交互式输入**，调了会卡死在 "Still working... (running: clarify)"。

**解决**：飞书上不要用 clarify 工具。给用户选项时直接文字列出 1/2/3，让用户打字回复数字即可。

已在 say-it-well SKILL.md 中加了规则："飞书平台上不要用 clarify 工具。需要给用户选项时，直接文字列出来"。

## 双向兜底策略（血的教训）

skill 内容体量大（say-it-well 约 5000+ 字），模型可能漏掉某些关键规则（如"问行业"、"不用 clarify"）。

**解决**：最关键的铁律同时写在两处——SKILL.md 主体 + channel_prompt。channel_prompt 短小（~100 字），模型更难忽略。

当前 channel_prompt：
```
你是提示词助手。用户想做工具时按 say-it-well 方法论追问。铁律：确认需求后必须问行业，用户回答后自己判断——够细就过，不够细就再问一轮具体业务。一次只问一个问题。普通聊天不走追问。先追问，再动手。
```

## 群聊与私聊

飞书群聊和私聊使用不同的 chat_id，channel_skill_bindings 需要分别配置。每次拉机器人进新群后，需要把新群的 chat_id 加入 bindings 并重启 Gateway。
