import json, random

subject = {json.loads(l)["id"]: json.loads(l)["subject"] for l in open("data/selected.jsonl")}
done = {json.loads(l)["section_id"] for l in open("evaluation/questions.jsonl") if l.strip()}
rows = [json.loads(l) for l in open("data/corpus.jsonl")]
rows = [r for r in rows
        if len(r["text"].split()) >= 30 and r["heading"] != "Introduction"
        and r["id"] not in done
        and not subject[r["page_id"]].startswith(("Famille", "Justice"))]
random.seed(42)
with open("evaluation/synthetic_source.jsonl", "w") as f:
    for r in random.sample(rows, 60):
        f.write(json.dumps({"id": r["id"], "title": r["title"], "heading": r["heading"],
                            "text": r["text"][:1500]}, ensure_ascii=False) + "\n")
print("60 passages written")