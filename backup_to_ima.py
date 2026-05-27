"""
backup_to_ima.py — 备份整个 ChromaDB 知识库到 Markdown，按 6 类 topic 分组

输出目录: D:/hermes-tools/kb-backup/
每个 topic 一个 .md 文件
"""

from chromadb import PersistentClient
import os
import json
from datetime import datetime

CHROMA_PATH = "D:/hermes-tools/kb-vector"
OUTPUT_DIR = "D:/hermes-tools/kb-backup"
TIMESTAMP = datetime.now().strftime("%Y%m%d-%H%M")

# 6 个输出分类标签
TOPIC_CATEGORIES = [
    "第二大脑架构",
    "最新架构更新",
    "Prompt Engineering",
    "Prompt Engineering Evolution 2022-2026",
    "AI Coding Agent Tools 2026",
    "LLM Price War Agentic Shift 2026",
]

# 分类映射规则：根据 metadata.topic + content keywords 确定输出类别
# 优先级: 精确匹配 > 内容关键词 > 默认分类
TOPIC_MAP = {
    # ChromaDB metadata.topic → output category
    "kb-system": "第二大脑架构",
    "第二大脑架构": "第二大脑架构",
    "knowledge-management": "第二大脑架构",
    "ai-models": "LLM Price War Agentic Shift 2026",
    "ai-coding": "AI Coding Agent Tools 2026",
    "prompt-engineering": "Prompt Engineering",
    "methodology": "最新架构更新",
}

# 内容关键词 → 细化分类覆盖
CONTENT_OVERRIDES = [
    # (keyword in document, override_category)
    ("Prompt Engineering 2022-2026", "Prompt Engineering Evolution 2022-2026"),
    ("Prompt Engineering Evolution", "Prompt Engineering Evolution 2022-2026"),
    ("学术分类", "Prompt Engineering Evolution 2022-2026"),
    ("全面分类法", "Prompt Engineering Evolution 2022-2026"),
    ("Prompt技术", "Prompt Engineering Evolution 2022-2026"),
    ("DSPy", "Prompt Engineering"),
    ("System Prompt设计", "Prompt Engineering"),
    ("中文Prompt", "Prompt Engineering"),
    ("告别vibe coding", "AI Coding Agent Tools 2026"),
    ("结构化方法", "AI Coding Agent Tools 2026"),
    ("AI编程最佳实践", "AI Coding Agent Tools 2026"),
    ("LLM API定价", "LLM Price War Agentic Shift 2026"),
    ("价格战", "LLM Price War Agentic Shift 2026"),
    ("永久降价", "LLM Price War Agentic Shift 2026"),
    ("降价75%", "LLM Price War Agentic Shift 2026"),
    ("Agent基准测试", "LLM Price War Agentic Shift 2026"),
    ("Agent工作流", "LLM Price War Agentic Shift 2026"),
    ("自主Agent", "LLM Price War Agentic Shift 2026"),
    ("Claude Code", "AI Coding Agent Tools 2026"),
    ("Codex", "AI Coding Agent Tools 2026"),
    ("Cursor", "AI Coding Agent Tools 2026"),
    ("Trae", "AI Coding Agent Tools 2026"),
    ("Aider", "AI Coding Agent Tools 2026"),
    ("Cline", "AI Coding Agent Tools 2026"),
    ("通义灵码", "AI Coding Agent Tools 2026"),
    ("文心快码", "AI Coding Agent Tools 2026"),
    ("AI编码工具", "AI Coding Agent Tools 2026"),
    ("AI编程工具", "AI Coding Agent Tools 2026"),
    ("编码工具选型", "AI Coding Agent Tools 2026"),
    ("反例", "最新架构更新"),
    ("反面教材", "最新架构更新"),
    ("anti-pattern", "最新架构更新"),
    ("Phase", "最新架构更新"),
    ("实施计划", "最新架构更新"),
    ("project-summary", "最新架构更新"),
    ("work-log", "最新架构更新"),
    ("agent-2026", "最新架构更新"),
    ("冷启动", "第二大脑架构"),
    ("cold-", "第二大脑架构"),
    ("kb-setup", "第二大脑架构"),
    ("arch-", "第二大脑架构"),
    ("kb-core", "第二大脑架构"),
    ("kb-security", "第二大脑架构"),
    ("kb-feed", "第二大脑架构"),
    ("kb-health", "第二大脑架构"),
    ("kb-protocol", "第二大脑架构"),
    ("kb-evolve", "第二大脑架构"),
    ("kb-calibrate", "第二大脑架构"),
    ("kb-graph", "第二大脑架构"),
    ("kb-brief", "第二大脑架构"),
    ("kb-research", "第二大脑架构"),
    ("知识库架构", "第二大脑架构"),
    ("第二大脑", "第二大脑架构"),
    ("ChromaDB", "第二大脑架构"),
    ("向量知识库", "第二大脑架构"),
    ("去重", "第二大脑架构"),
    ("知识库", "第二大脑架构"),
    ("规范文章", "第二大脑架构"),
    ("时效性维护", "第二大脑架构"),
    ("知识库内容标准", "第二大脑架构"),
    ("重复文章", "第二大脑架构"),
    ("信念修正", "第二大脑架构"),
]

def classify_item(topic, doc_text, item_id):
    """根据 metadata.topic + content keywords 确定输出分类"""
    # Step 1: metadata.topic 映射
    base = TOPIC_MAP.get(topic, None)
    
    # Step 2: 内容关键词覆盖
    for keyword, override_cat in CONTENT_OVERRIDES:
        if keyword.lower() in doc_text.lower():
            return override_cat
    
    # Step 3: 默认
    if base:
        return base
    
    # Step 4: 末级默认
    if "model" in doc_text.lower() or "GPT" in doc_text or "Claude" in doc_text or "Gemini" in doc_text or "DeepSeek" in doc_text or "Qwen" in doc_text or "Grok" in doc_text or "Mistral" in doc_text:
        return "LLM Price War Agentic Shift 2026"
    if "code" in doc_text.lower() or "编程" in doc_text or "IDE" in doc_text:
        return "AI Coding Agent Tools 2026"
    if "prompt" in doc_text.lower() or "Prompt" in doc_text:
        return "Prompt Engineering"
    
    return "最新架构更新"


def main():
    client = PersistentClient(path=CHROMA_PATH)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 收集所有条目
    all_items = []
    stats = {"total": 0, "collections": {}}
    
    for col in client.list_collections():
        data = col.get()
        count = len(data['ids'])
        stats["collections"][col.name] = count
        stats["total"] += count
        
        for i in range(count):
            meta = data['metadatas'][i] if data['metadatas'] else {}
            all_items.append({
                "id": data['ids'][i],
                "document": data['documents'][i],
                "metadata": meta,
                "collection": col.name,
            })
    
    # 分类
    categorized = {cat: [] for cat in TOPIC_CATEGORIES}
    
    for item in all_items:
        topic = item["metadata"].get("topic", "")
        cat = classify_item(topic, item["document"], item["id"])
        if cat in categorized:
            categorized[cat].append(item)
        else:
            categorized["最新架构更新"].append(item)
    
    # 写入 Markdown 文件
    output_files = []
    
    for cat in TOPIC_CATEGORIES:
        items = categorized[cat]
        if not items:
            continue
        
        safe_name = cat.replace(" ", "-").replace("/", "-")
        filename = f"local-kb-{safe_name}-{TIMESTAMP}.md"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# 📂 {cat}\n\n")
            f.write(f"> 备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} | 共 {len(items)} 条知识\n\n")
            f.write("---\n\n")
            
            for idx, item in enumerate(items, 1):
                meta = item["metadata"]
                confidence = meta.get("confidence", "?")
                source_label = meta.get("source", "")
                topic_tag = meta.get("topic", "")
                
                # 置信度标签
                conf_map = {1.0: "用户确认", 0.7: "AI推断", 0.6: "外部引用", 0.5: "交叉验证"}
                conf_label = conf_map.get(float(confidence) if confidence and confidence != "?" else 0, str(confidence))
                
                f.write(f"### {idx}. [{conf_label}] 置信度 {confidence}\n")
                f.write(f"> ID: `{item['id']}` | 集合: {item['collection']}")
                if topic_tag:
                    f.write(f" | 原标签: {topic_tag}")
                if source_label:
                    f.write(f" | 来源: {source_label}")
                f.write("\n\n")
                f.write(f"{item['document']}\n\n")
                f.write("---\n\n")
        
        output_files.append(filepath)
        size_kb = os.path.getsize(filepath) / 1024
        print(f"✅ {cat}: {len(items)} 条 → {filename} ({size_kb:.1f} KB)")
    
    # 汇总
    print(f"\n📊 总计: {stats['total']} 条知识 | {len(output_files)} 个文件")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    
    # 写入 manifest
    manifest = {
        "timestamp": TIMESTAMP,
        "stats": stats,
        "categories": {cat: len(categorized[cat]) for cat in TOPIC_CATEGORIES},
        "files": [os.path.basename(f) for f in output_files],
    }
    manifest_path = os.path.join(OUTPUT_DIR, f"manifest-{TIMESTAMP}.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"📋 Manifest: {manifest_path}")

if __name__ == "__main__":
    main()
