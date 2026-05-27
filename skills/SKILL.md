---
name: multi-agent-dispatcher
description: "Multi-agent task dispatcher — 自动按任务类型分派给克劳德/扣带思/爱马仕。系统级调度规则，全项目通用。"
---

# 多 Agent 调度系统

三个 agent 的分工铁律，系统级，任何任务先过这张表。

## 分派矩阵

| 任务特征 | 派给谁 | 命令 |
|---------|--------|------|
| 复杂重构、多文件逻辑、架构设计、debug | 克劳德 | `claude -p "任务" --max-turns 20` |
| 批量并行、CI 自动化、大批量编辑、PR | 扣带思 | `codex exec "任务" --max-turns 15` |
| 规划、审核、say-it-well 对话、飞书运维 | 爱马仕 | 主 session 直接做 |
| 简单独立子任务 | delegate_task Flash | `delegate_task(goal=...)` |

## 并行规则

- 克劳德和扣带思可以同时跑（互不依赖的任务）
- 爱马仕审核必须在两者都完成后
- 同一文件不能同时派给两个 agent

## 禁止

- ❌ 图省事全用 Flash 替克劳德和扣带思
- ❌ 同一个文件同时交给两个 agent 改
- ❌ 克劳德扣带思跑完后不审核直接告诉用户"搞定了"

## 工作流模板

### 标准开发流程
```
1. 爱马仕规划 → 拆成子任务
2. 克劳德做复杂部分 + 扣带思做批量部分 → 并行
3. 两者都完成 → 爱马仕审核代码质量
4. 审核通过 → 告诉用户
```

### 快速修复流程
```
1. 爱马仕诊断 → 判断归属
2. 单人执行（克劳德或扣带思）
3. 完成后爱马仕验证
```

## 环境变量

克劳德：
```bash
export ANTHROPIC_AUTH_TOKEN="sk-c96..."
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
export ANTHROPIC_MODEL="deepseek-v4-pro"
```

扣带思：
```bash
# 通过本地代理 (LiteLLM :1234)
codex exec "任务" --dangerously-bypass-approvals-and-sandbox --max-turns 15
```

## 监控

- 克劳德进度：`tmux capture-pane -t <session> -p -S -30`
- 扣带思进度：`process poll <session_id>`
- 任务状态：`hermes agents` 或 `/agents`
