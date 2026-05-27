"""克劳德记忆 → 本地知识库同步脚本

遍历所有 Claude Code 项目的 memory 文件，提取知识并存入 ChromaDB。
按文件内容的 heading 分段，每段作为独立文档。
已存在的文件（相同 project + filename）跳过，避免重复导入。

用法: python sync_claude_memory.py
"""

import os, json, hashlib
from pathlib import Path
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

CLAUDE_PROJECTS = os.path.expanduser("~/.claude/projects")
KB_PATH = "D:/hermes-tools/kb-vector"
COLLECTION = "general"

def extract_sections(text: str):
    """按 ## heading 分段，每段作为独立知识"""
    sections = []
    current_title = ""
    current_body = []
    for line in text.split("\n"):
        if line.startswith("## "):
            if current_body:
                sections.append((current_title, "\n".join(current_body).strip()))
            current_title = line.strip("# ").strip()
            current_body = []
        else:
            current_body.append(line)
    if current_body:
        sections.append((current_title, "\n".join(current_body).strip()))
    if not sections:
        sections.append(("", text.strip()))
    return sections

def infer_topic(filename: str) -> str:
    """从文件名推断 topic 标签"""
    name = filename.lower()
    if any(k in name for k in ["codex", "proxy", "api", "bug", "fix"]):
        return "ai-coding"
    if any(k in name for k in ["kb", "knowledge", "memory", "data"]):
        return "kb-system"
    if any(k in name for k in ["method", "rule", "principle", "lesson"]):
        return "methodology"
    if any(k in name for k in ["prompt", "skill", "say-it"]):
        return "prompt-engineering"
    if any(k in name for k in ["model", "llm", "ai", "gpt", "claude"]):
        return "ai-models"
    return "knowledge-management"

def main():
    client = PersistentClient(path=KB_PATH)
    collection = client.get_or_create_collection(COLLECTION)
    model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

    # 获取已有文档 ID 列表，避免重复导入
    existing = set(collection.get().get("ids", []))

    added = 0
    for proj_name in os.listdir(CLAUDE_PROJECTS):
        mem_dir = os.path.join(CLAUDE_PROJECTS, proj_name, "memory")
        if not os.path.isdir(mem_dir):
            continue

        for filename in os.listdir(mem_dir):
            if not filename.endswith(".md"):
                continue
            filepath = os.path.join(mem_dir, filename)
            content = Path(filepath).read_text(encoding="utf-8", errors="ignore")
            if not content.strip():
                continue

            # 生成唯一 ID
            file_hash = hashlib.md5(content.encode()).hexdigest()[:12]
            topic = infer_topic(filename)
            sections = extract_sections(content)

            for i, (title, body) in enumerate(sections):
                if len(body) < 30:  # 太短跳过
                    continue
                doc_id = f"claude-{proj_name}-{filename.replace('.md','')}-{file_hash}-{i}"
                if doc_id in existing:
                    continue

                embedding = model.encode([body], normalize_embeddings=True)
                collection.add(
                    documents=[body],
                    embeddings=embedding.tolist(),
                    ids=[doc_id],
                    metadatas=[{
                        "topic": topic,
                        "source": "claude-code",
                        "project": proj_name,
                        "section": title or filename,
                    }]
                )
                added += 1

    print(f"同步完成: {added} 条新知识入库。集合总数: {collection.count()}")

if __name__ == "__main__":
    main()
