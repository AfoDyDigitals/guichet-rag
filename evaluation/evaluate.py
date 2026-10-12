"""Score every (question set x chunking x method) combination."""
import json
import numpy as np

KS = [1, 5, 10]


def load(path):
    try:
        return [json.loads(l) for l in open(path) if l.strip()]
    except FileNotFoundError:
        return []


def first_hit(chunks, ranked, q, level):
    for rank, i in enumerate(ranked, 1):
        c = chunks[i]
        if (q["section_id"] in c["section_ids"]) if level == "section" else (c["page_id"] == q["page_id"]):
            return rank
    return None


def evaluate(retrievers, question_sets, methods, depth=10):
    rows, ranks = [], []
    for qs_name, qs in question_sets.items():
        for strat, r in retrievers.items():
            for m in methods:
                hits = {"section": [], "page": []}
                for q in qs:
                    ranked = r.search(m, q["question"], depth)
                    rec = {"questions": qs_name, "chunking": strat, "method": m,
                           "question": q["question"], "section_id": q["section_id"],
                           "top3": [r.chunks[i]["chunk_id"] for i in ranked[:3]]}
                    for lvl in hits:
                        rec[f"rank_{lvl}"] = first_hit(r.chunks, ranked, q, lvl)
                        hits[lvl].append(rec[f"rank_{lvl}"])
                    ranks.append(rec)
                for lvl, rk in hits.items():
                    row = {"questions": qs_name, "chunking": strat, "method": m, "level": lvl, "n": len(rk)}
                    for k in KS:
                        row[f"recall@{k}"] = round(float(np.mean([x is not None and x <= k for x in rk])), 3)
                    row["mrr@10"] = round(float(np.mean([1 / x if x else 0 for x in rk])), 3)
                    rows.append(row)
                print(f"done: {qs_name:9} {strat:8} {m}")
    return rows, ranks
