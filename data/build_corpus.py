import json, re, statistics
import xml.etree.ElementTree as ET

RAW = "data/raw/vosdroits-latest/"

def text(e):
    s = " ".join(" ".join(e.itertext()).split())
    return re.sub(r" ([.,)])", r"\1", s)

PASS = ("ListeSituations", "Texte", "BlocCas")
TITLED = ("Situation", "Chapitre", "SousChapitre", "Cas")

def walk(e, path, out):
    start, loose = len(out), []
    for c in e:
        if c.tag in PASS:
            walk(c, path, out)
        elif c.tag in TITLED:
            t = c.find("Titre")
            walk(c, path + ([text(t)] if t is not None else []), out)
        elif c.tag != "Titre":
            loose.append(text(c))
    if any(loose):
        out.insert(start, (path, " ".join(loose)))

rows, empty = [], []
for line in open("data/selected.jsonl"):
    page = json.loads(line)
    root = ET.parse(RAW + page["id"] + ".xml").getroot()
    out = []
    intro = root.find("Introduction")
    if intro is not None:
        out.append((["Introduction"], text(intro)))
    for tag in ("Texte", "ListeSituations"):
        for c in root.findall(tag):
            walk(c, [], out)
    out = [(p, t) for p, t in out if t]
    if not out:
        empty.append(page["id"])
    for n, (path, t) in enumerate(out):
        rows.append({"id": f"{page['id']}#{n}", "page_id": page["id"],
                     "title": page["title"], "url": page["url"],
                     "heading": " > ".join(path), "text": t})

with open("data/corpus.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

words = [len(r["text"].split()) for r in rows]
print(len(rows), "sections from", len({r["page_id"] for r in rows}), "pages")
print("pages with no text:", empty)
print("words per section: median", statistics.median(words), "max", max(words))

import random
for r in random.sample(rows, 3):
    print(r["id"], "|", r["heading"], "|", r["text"][:200])
for i in empty[:3]:
    r = ET.parse(RAW + i + ".xml").getroot()
    print(i, r.get("type"), [c.tag for c in r if not c.tag.startswith("{")])