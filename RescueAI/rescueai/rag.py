from pathlib import Path
import re, math

class Retriever:
    def __init__(self, mode="auto"):
        self.mode = mode
        self.docs = []
        for p in sorted((Path(__file__).parent.parent / "rag" / "documents").glob("*.md")):
            for i, chunk in enumerate(re.split(r"\n\s*\n", p.read_text(encoding="utf-8"))):
                if chunk.strip():
                    self.docs.append({"id":f"{p.stem}-{i+1}","source":p.name,"text":chunk.strip()})

    def retrieve(self, query, k=5):
        q = set(re.findall(r"\w+", query.lower()))
        scored = []
        for d in self.docs:
            words = set(re.findall(r"\w+", d["text"].lower()))
            score = len(q & words) / math.sqrt(max(1, len(q) * len(words)))
            scored.append({**d,"score":score})
        return sorted(scored,key=lambda x:x["score"],reverse=True)[:k]
