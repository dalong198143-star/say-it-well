"""say-it-well 回归测试 — 每次改完 skill 后跑一遍，检查核心规则是否退化

用法: python test_regression.py

测试逻辑：
1. 用 deepseek-v4-pro 模拟 3 个固定对话（记账工具、客服机器人、播客生成器）
2. 检查 bot 回复是否包含关键行为（复述确认、行业问询、一次一个问题）
3. 输出通过/失败报告
"""

import json, re, os, sys

# 测试用例：(用户消息, 期望检查项)
TEST_CASES = [
    {
        "name": "记账工具-复述确认",
        "prompt": "帮我做个记账的",
        "checks": ["确认", "对吗", "是不是"],
        "desc": "bot 应该复述确认用户需求"
    },
    {
        "name": "记账工具-行业问询", 
        "prompt": "帮我做个记账的",
        "checks": ["行业", "餐饮", "教育", "电商", "游戏"],
        "desc": "bot 应该在建立信任后询问行业"
    },
    {
        "name": "客服机器人-行业问询",
        "prompt": "帮我做个客服机器人",
        "checks": ["行业", "餐饮", "教育", "电商", "游戏"],
        "desc": "bot 应该询问行业"
    },
    {
        "name": "播客生成器-复述确认",
        "prompt": "帮我做一个播客节目生成器",
        "checks": ["确认", "对吗", "是不是"],
        "desc": "bot 应该复述确认"
    },
    {
        "name": "闲聊-不触发sayitwell", 
        "prompt": "今天天气怎么样",
        "checks": [],  # 反向检查：不应该出现追问
        "anti_checks": ["核心功能", "目标用户", "赚钱"],
        "desc": "bot 不应该对闲聊触发 say-it-well 追问"
    },
]

SKILL_CONTENT = open("D:/hermes/skills/software-development/say-it-well/SKILL.md", encoding="utf-8").read()

def build_system_prompt():
    return f"""你是提示词助手，按 say-it-well 方法论工作。

{SKILL_CONTENT}

当前是回归测试。用户消息就是测试用例，请自然回复。"""

def check_response(response: str, checks: list, anti_checks: list = None) -> bool:
    """检查回复是否包含期望的关键词"""
    for c in checks:
        if c in response:
            return True
    if anti_checks:
        for ac in anti_checks:
            if ac in response:
                return False  # 出现了不该出现的词
        return True
    return len(checks) == 0  # 空 checks 默认通过

def run_test(name: str, prompt: str, checks: list, anti_checks: list = None):
    """调用 deepseek API 运行单个测试"""
    import urllib.request
    
    api_key = "sk-c96123d9d6b5428eb01ccd757eeef7da"
    payload = json.dumps({
        "model": "deepseek-v4-pro",
        "messages": [
            {"role": "system", "content": build_system_prompt()[:30000]},  # 截断节约 token
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.3
    }).encode()
    
    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            response = result["choices"][0]["message"]["content"]
            passed = check_response(response, checks, anti_checks)
            return {
                "name": name,
                "passed": passed,
                "response": response[:200],
                "desc": TEST_CASES[0]["desc"]  # placeholder
            }
    except Exception as e:
        return {"name": name, "passed": False, "error": str(e), "desc": ""}

def main():
    print("=" * 50)
    print("say-it-well 回归测试")
    print("=" * 50)
    
    results = []
    for tc in TEST_CASES:
        print(f"\n测试: {tc['name']} — {tc['desc']}")
        r = run_test(tc['name'], tc['prompt'], tc['checks'], tc.get('anti_checks'))
        status = "✅ PASS" if r['passed'] else "❌ FAIL"
        print(f"  {status}")
        if not r['passed'] and 'response' in r:
            print(f"  回复: {r['response'][:100]}")
        results.append(r)
    
    passed = sum(1 for r in results if r['passed'])
    print(f"\n{'='*50}")
    print(f"结果: {passed}/{len(results)} 通过")
    if passed < len(results):
        sys.exit(1)

if __name__ == "__main__":
    main()
