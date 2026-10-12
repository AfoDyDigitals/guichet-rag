import json, re, statistics, sys

CORPUS = sys.argv[1] if len(sys.argv) > 1 else "data/corpus.jsonl"
OUT = sys.argv[2] if len(sys.argv) > 2 else "data"
rows = [json.loads(l) for l in open(CORPUS) if l.strip()]

def ctx(r):
    return f"{r['title']}. {r['heading']}. " if r["heading"] else f"{r['title']}. "

pages = {}
for r in rows:
    pages.setdefault(r["page_id"], []).append(r)

def split_sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Ý0-9])", text) if s.strip()]

section, fixed, sentence = [], [], []

for r in rows:
    section.append({"chunk_id": r["id"], "page_id": r["page_id"],
                    "section_ids": [r["id"]], "text": ctx(r) + r["text"]})

    sents = split_sentences(r["text"])
    for n, i in enumerate(range(0, max(len(sents) - 1, 1), 2)):
        sentence.append({"chunk_id": f"{r['id']}~s{n}", "page_id": r["page_id"],
                         "section_ids": [r["id"]], "text": ctx(r) + " ".join(sents[i:i + 3])})

SIZE, STEP = 150, 120
for pid, secs in pages.items():
    words, owner = [], []
    for r in secs:
        w = r["text"].split()
        words += w
        owner += [r["id"]] * len(w)
    title = secs[0]["title"]
    for n, start in enumerate(range(0, max(len(words) - (SIZE - STEP), 1), STEP)):
        ids = list(dict.fromkeys(owner[start:start + SIZE]))
        fixed.append({"chunk_id": f"{pid}~f{n}", "page_id": pid, "section_ids": ids,
                      "text": f"{title}. " + " ".join(words[start:start + SIZE])})

for name, chunks in [("section", section), ("fixed", fixed), ("sentence", sentence)]:
    with open(f"{OUT}/chunks_{name}.jsonl", "w") as f:
        f.writelines(json.dumps(c, ensure_ascii=False) + "\n" for c in chunks)
    lens = [len(c["text"].split()) for c in chunks]
    print(f"{name:9} {len(chunks):6} chunks   median {statistics.median(lens):5} words   max {max(lens)}")
