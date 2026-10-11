import glob, json
import xml.etree.ElementTree as ET
from collections import Counter

DC = "{http://purl.org/dc/elements/1.1/}"
KEYWORDS = ["étudiant", "séjour", "visa", "loyer", "bail", "locataire",
            "dépôt de garantie", "caution", "aide au logement", "apl",
            "assurance maladie", "carte vitale", "complémentaire santé",
            "médecin traitant", "compte bancaire", "permis de conduire",
            "stage", "bourse", "smic"]

rows = []
for path in sorted(glob.glob("data/raw/vosdroits-latest/F*.xml")):
    root = ET.parse(path).getroot()
    title = " ".join(root.findtext(DC + "title", "").split())
    subject = root.findtext(DC + "subject", "")
    if "Étranger" in subject or any(k in title.lower() for k in KEYWORDS):
        rows.append({"id": root.get("ID"), "title": title,
                     "subject": subject, "url": root.get("spUrl")})

with open("data/selected.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(len(rows), "pages selected")
for subject, n in Counter(r["subject"] for r in rows).most_common(10):
    print(n, subject)