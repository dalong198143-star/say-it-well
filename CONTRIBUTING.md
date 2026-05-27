# 贡献指南 — say-it-well

> 怎么给"话说清楚"项目添砖加瓦

## 项目结构

```
say-it-well/
├── SKILL.md                    # 核心技能文件（Hermes 加载入口）
├── INCIDENTS.md                # 事故记录（每个 bug 的前因后果）
├── references/
│   ├── industries.md           # 行业画像库（25 个行业，bot 自动加载）
│   ├── feishu-troubleshooting.md   # 飞书部署排查
│   └── feishu-adapter-fix.md       # 飞书 adapter 源码修改指南
├── README.md
└── CONTRIBUTING.md
```

## 怎么加一个维度

say-it-well 的 12 维追问表格在 SKILL.md 的第三步。新增维度：

1. 在追问表格里加一行（维度名 + 追问示例 + 目的）
2. 在追问策略的"识别关键分叉点"里加一条触发条件
3. 如果维度很关键，在"什么时候停"的"核心维度"列表里加上
4. 在 INCIDENTS.md 里记一笔为什么要加

## 怎么加一个上路指南分类

上路指南在 SKILL.md 的第六步。新增分类：

1. 按 `**如果是XXX类：**` 格式插入
2. 包含：具体工具名 + 操作步骤 + ⚠️ 注意事项（审批/备案/费用）
3. 在 industries.md 里找到对应的行业，确认技术栈建议和上路指南一致

## 怎么记录事故

每次修 bug 后，在 INCIDENTS.md 里加一条：

```markdown
### N. 问题名称
- **症状**: 用户看到什么
- **根因**: 为什么发生
- **修复**: 改了什么
- **经验**: 以后记住什么
```

同时在 SKILL.md 对应规则旁边加注释：`<!-- 事故: xxx(N日) → 修复: xxx -->`

## 怎么验证改动

1. 改完 SKILL.md → 复制到 `D:/hermes/skills/software-development/say-it-well/`
2. `hermes gateway restart`
3. 飞书发 `/new` → 测试对话 → 检查是否按预期执行

## Commit 规范

```
<type>: <简短描述>
```

类型：`feat`（新功能）、`fix`（修 bug）、`docs`（文档）、`refactor`（重构）

示例：
```
fix: 行业判断改为硬规则，不再依赖模型主观感受
feat: 上路指南新增手机游戏/App 分类
docs: INCIDENTS.md 记录 13 条事故
```
