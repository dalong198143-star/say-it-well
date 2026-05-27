"""Inspect ChromaDB data structure for backup script generation."""
from chromadb import PersistentClient

client = PersistentClient(path="D:/hermes-tools/kb-vector")
cols = client.list_collections()

for col in cols:
    data = col.get()
    print(f"=== {col.name}: {len(data['ids'])} items ===")
    if data['ids']:
        print(f"  Sample IDs: {data['ids'][:5]}")
        if data['metadatas']:
            topics = set()
            keys = set()
            for m in data['metadatas']:
                if m:
                    keys.update(m.keys())
                    if 'topic' in m:
                        topics.add(m['topic'])
            print(f"  Topic values: {topics}")
            print(f"  All metadata keys: {keys}")
            for i in range(min(3, len(data['documents']))):
                doc_preview = data['documents'][i][:120].replace('\n', ' ')
                print(f"  [{data['ids'][i]}] topic={data['metadatas'][i].get('topic','?') if data['metadatas'][i] else '?'}: {doc_preview}")
        else:
            for i in range(min(3, len(data['documents']))):
                print(f"  [{data['ids'][i]}]: {data['documents'][i][:120]}")
    print()
