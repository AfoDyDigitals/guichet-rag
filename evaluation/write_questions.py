import json, random
from deep_translator import GoogleTranslator
tr = GoogleTranslator(source="fr", target="en")

rows = [json.loads(l) for l in open("data/corpus.jsonl")]
rows = [r for r in rows if len(r["text"].split()) >= 30 and r["heading"] != "Introduction"]
out = open("evaluation/questions.jsonl", "a")
n = sum(1 for _ in open("evaluation/questions.jsonl"))
while True:
    r = random.choice(rows)
    print(f"\n[{n} written] {r['title']}\n{r['heading']}\n\n{r['text'][:1200]}\n")
    try:
        print("--- EN ---\n" + tr.translate(f"{r['title']}. {r['heading']}. {r['text'][:1200]}") + "\n")
    except Exception:
        print("--- EN --- (translation unavailable, use your own translator)\n")    
    q = input("Question (Enter = skip, q = quit): ").strip()
    if q == "q":
        break
    if not q:
        continue
    lang = input("Language (en/fr): ").strip()
    out.write(json.dumps({"question": q, "lang": lang, "section_id": r["id"],
                          "page_id": r["page_id"]}, ensure_ascii=False) + "\n")
    out.flush()
    n += 1