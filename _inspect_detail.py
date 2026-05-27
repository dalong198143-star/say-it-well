"""Detailed inspection: all items by topic."""
from chromadb import PersistentClient

client = PersistentClient(path="D:/hermes-tools/kb-vector")

for col in client.list_collections():
    data = col.get()
    print(f"\n=== {col.name}: {len(data['ids'])} items ===")
    
    by_topic = {}
    for i in range(len(data['ids'])):
        meta = data['metadatas'][i] if data['metadatas'] else {}
        topic = meta.get('topic', '(none)')
        if topic not in by_topic:
            by_topic[topic] = []
        by_topic[topic].append((data['ids'][i], data['documents'][i][:80], meta.get('confidence', '?')))
    
    for topic, items in sorted(by_topic.items()):
        print(f"\n  [{topic}] ({len(items)} items)")
        for id_, preview, conf in items:
            print(f"    {id_} (c={conf}): {preview.replace(chr(10),' ')}")
