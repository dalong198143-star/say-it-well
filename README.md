# 提示词炼金炉（say-it-well / 话说清楚）

> 让完全不懂代码、不懂英语、不懂 AI 的普通人，通过聊天把模糊想法炼成精准编程提示词。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 这是什么

你在飞书群里跟一个机器人聊天，说"帮我做个记账的"。它不会直接写代码，而是像朋友一样一步步问你——什么行业、给谁用、怎么赚钱、长什么样……

聊完之后，它给你一份**中英双语的精准编程提示词**，你拿去丢给 Trae / Codex / Claude Code，AI 就能帮你写出能跑的代码。

**不是写代码的工具，是帮你说清楚话的工具。**

## 为什么需要它

普通人跟 AI 编程工具对话的典型困境：

```
用户："帮我做个记账的"
AI：  （直接写了 4 个 .py 文件，全是错的）
```

问题不是 AI 不行，是用户没说清楚。但普通人不知道怎么说清楚——他们不懂技术术语、不懂英语、不知道 AI 能做什么不能做什么。

这个项目做的事：把"说不清楚 → 写不对"的死循环，变成"聊清楚 → 出 prompt → 拿去用"的流水线。

## 核心能力

- **11 维追问框架**：行业、目标用户、使用场景、核心功能、盈利方式、内容来源……每个维度一次只问一个问题
- **反思推理引擎**：不是机械填表，每一轮先理解用户的话意味着什么，再决定下一个问什么
- **行业深挖**：先问大类（餐饮/教育/游戏），判断不够细就再追问具体业务
- **真伪需求判断**：能做的说能做，部分能做的说替代方案，不能做的坦诚告知
- **去 AI 味润色**：自动清除"在当今时代"、"值得注意的是"等 AI 套话
- **中英双语输出**：一份中文 prompt + 一份 English prompt，适配所有主流 AI 编程工具

## 安装与使用

### 前置条件

- 安装了 [Hermes Agent](https://github.com/NousResearch/hermes-agent)
- 配置了飞书 Bot（或 Telegram / Discord / CLI）

### 安装技能

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/say-it-well.git

# 安装到 Hermes
cp say-it-well/SKILL.md ~/.hermes/skills/software-development/say-it-well/SKILL.md
cp -r say-it-well/references/ ~/.hermes/skills/software-development/say-it-well/references/
```

### 飞书配置

```bash
# 绑定技能到飞书频道
hermes config set feishu.channel_skill_bindings '[{"id":"你的飞书chat_id","skills":["say-it-well"]}]'

# 注入引导提示
hermes config set feishu.channel_prompt "你是提示词助手。用户想做工具时按 say-it-well 方法论追问..."

# 重启
hermes gateway restart
```

详细飞书部署指南见 `references/feishu-troubleshooting.md`。

## 对话流程

```
用户："帮我做个记账的"
  ↓
第一步：建立信任（自我介绍、能力透明）
  ↓
第二步：初始捕获（复述确认、可行性判断）
  ↓
第三步：问行业（什么行业？够不够细？）
  ↓
第四～N步：11 维递进追问（一次只问一个）
  ↓
第五步：回头确认（完整摘要，用户核验）
  ↓
第六步：双语输出（中文 + English + 建议工具 + 注意事项）
```

## 项目结构

```
say-it-well/
├── SKILL.md                        # Hermes 技能主文件
├── PROMPT_REFINERY_PLAN.md         # 项目规划文档
├── references/
│   ├── feishu-troubleshooting.md   # 飞书部署排查清单
│   ├── feishu-adapter-fix.md       # 飞书适配器源码修改指南
│   └── ima-skill-clone-criteria.md # IMA 技能克隆评估标准
└── README.md
```

## 路线图

| 阶段 | 内容 | 状态 |
|------|------|:----:|
| Phase 0 | 核心需求炼化（11维追问 + 双语输出） | ✅ 已完成 |
| Phase 1 | 输出末尾加"上路指南"（部署路径推荐） | 🚧 规划中 |
| Phase 2 | deployment-guide skill（卡住了怎么办） | 📋 待定 |
| Phase 3 | launch-coach skill（主动引导模式） | 📋 待定 |

## 常见问题

**Q: 用户完全不懂技术，能用吗？**
A: 能。这个工具就是为这样的人设计的。全程中文、不用术语、选项式追问。

**Q: 输出能直接给 Codex / Trae 用吗？**
A: 能。输出包含中英双语 prompt，直接复制粘贴。

**Q: 飞书上怎么用？**
A: 配置好飞书 Bot 后，在群里 @机器人 说你的想法即可。群聊和私聊都支持。

**Q: 能在其他平台用吗？**
A: 能。Telegram、Discord、CLI 都支持。飞书完整功能需要额外配置（见 references/feishu-adapter-fix.md）。

## 贡献

欢迎提 Issue 和 PR。核心改进方向：

- 更多行业的追问模板
- 更精准的模糊词→精准词映射
- 更好的去 AI 味规则
- 更多平台的部署指南

## License

MIT
