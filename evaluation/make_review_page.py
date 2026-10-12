import json, random, html

subject = {json.loads(l)["id"]: json.loads(l)["subject"] for l in open("data/selected.jsonl")}
done = {json.loads(l)["section_id"] for l in open("evaluation/questions.jsonl")}
rows = [json.loads(l) for l in open("data/corpus.jsonl")]
rows = [r for r in rows
        if len(r["text"].split()) >= 30 and r["heading"] != "Introduction"
        and r["id"] not in done
        and not subject[r["page_id"]].startswith(("Famille", "Justice"))]
random.seed(0)
cards = "".join(
    f"<h3>{html.escape(r['title'])}</h3><b>{html.escape(r['heading'])}</b>"
    f"<p>{html.escape(r['text'][:1200])}</p>"
    f"<input data-id='{r['id']}' placeholder='Your question in English (leave empty to skip)'><hr>"
    for r in random.sample(rows, 400))
page = """<!doctype html><html lang="fr"><meta charset="utf-8">
<style>body{max-width:800px;margin:auto;font:16px sans-serif}
input{width:100%;padding:8px}button{position:fixed;top:10px;right:10px;padding:10px}</style>
<button onclick="save()">Download questions</button>""" + cards + """
<script>
const boxes = [...document.querySelectorAll("input")];
boxes.forEach(b => { b.value = localStorage[b.dataset.id] || "";
                     b.oninput = () => localStorage[b.dataset.id] = b.value; });
function save() {
  const lines = boxes.filter(b => b.value.trim()).map(b => JSON.stringify(
    {question: b.value.trim(), lang: "en", section_id: b.dataset.id,
     page_id: b.dataset.id.split("#")[0]}));
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([lines.join("\\n") + "\\n"]));
  a.download = "new_questions.jsonl"; a.click();
  boxes.forEach(b => { if (b.value.trim()) { delete localStorage[b.dataset.id]; b.value = ""; b.disabled = true; } });
}
</script>"""
open("evaluation/review.html", "w").write(page)
print("Page rebuilt: 400 new passages,", len(done), "already used")