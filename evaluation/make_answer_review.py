"""Build a review page for labelling generated answers. Usage: make_answer_review.py answers.jsonl out.html"""
import html, json, sys

src, out = sys.argv[1], sys.argv[2]
items = [json.loads(l) for l in open(src) if l.strip()]
LABELS = ["supported", "partly", "unsupported", "declined"]

cards = []
for n, a in enumerate(items):
    passages = "".join(f"<li><small>{html.escape(p['chunk_id'])}</small> {html.escape(p['text'][:900])}</li>"
                       for p in a["passages"])
    radios = "".join(f"<label><input type='radio' name='q{n}' value='{l}'> {l}</label>" for l in LABELS)
    badge = "found" if a["gold_found"] else "not found"
    cards.append(
        f"<div class='card' data-n='{n}'><p class='meta'>{n + 1} / {len(items)} · your passage {badge}</p>"
        f"<p translate='no'><b>Q:</b> {html.escape(a['question'])}</p>"
        f"<p class='ans' translate='no'><b>Answer:</b> {html.escape(a['answer'])}</p>"
        f"<div class='radios'>{radios}</div>"
        f"<details><summary>Passages the model saw</summary><ol>{passages}</ol></details></div>")

page = """<!doctype html><html lang="fr"><meta charset="utf-8"><title>Answer Review</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{max-width:860px;margin:auto;padding:16px;font:16px/1.5 system-ui,sans-serif;background:#fafafa;color:#1a1a1a}
.card{background:#fff;border:1px solid #ddd;border-radius:8px;padding:14px;margin:14px 0}
.card.done{border-color:#3b8;}.meta{color:#888;font-size:13px;margin:0}
.ans{background:#f3f6fb;padding:8px;border-radius:6px}.radios{display:flex;gap:16px;flex-wrap:wrap;margin:8px 0}
li{margin:6px 0;font-size:14px}small{color:#888}
.bar{position:sticky;top:0;background:#fafafa;padding:8px 0;border-bottom:1px solid #ddd;display:flex;gap:12px;align-items:center}
button{padding:10px 14px;font:inherit;cursor:pointer}.key{font-size:14px;color:#444}
</style>
<div class="bar"><button onclick="save()">Download labels</button><span id="n"></span></div>
<p class="key" translate="no"><b>supported</b>: every claim is in the cited passages ·
<b>partly</b>: some claims are, some aren't ·
<b>unsupported</b>: the main claim isn't in the passages ·
<b>declined</b>: it said it couldn't find the answer</p>
""" + "".join(cards) + """
<script>
const items = """ + json.dumps([{"question": a["question"], "section_id": a["section_id"],
                                "gold_found": a["gold_found"]} for a in items]) + """;
const cards=[...document.querySelectorAll('.card')];
function count(){let d=0;cards.forEach(c=>{const on=!!c.querySelector('input:checked');c.classList.toggle('done',on);d+=on});
 document.getElementById('n').textContent=d+' of '+cards.length+' labelled';}
cards.forEach(c=>c.querySelectorAll('input').forEach(i=>{
 try{if(localStorage['lab_'+c.dataset.n]===i.value)i.checked=true}catch(e){}
 i.onchange=()=>{try{localStorage['lab_'+c.dataset.n]=i.value}catch(e){};count();};}));
count();
function save(){
 const lines=cards.map((c,n)=>{const i=c.querySelector('input:checked');
  return JSON.stringify({...items[n],label:i?i.value:null});});
 const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([lines.join('\\n')+'\\n']));
 a.download='answer_labels.jsonl';a.click();}
</script>"""
open(out, "w").write(page)
print(len(items), "answers ->", out)
