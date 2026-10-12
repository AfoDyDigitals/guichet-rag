import json
FIX = {
 "F31697#12": "In my rented flat, who has to unblock the water pipes, me or the landlord?",
 "F15402#9": "How do I apply for a residence permit as a stateless person?",
 "F33375#9": "What do I include in my quarterly declaration for the activity bonus as a student?",
 "F33375#11": "What happens if I'm overpaid the activity bonus as a student?",
 "F1460#7": "Who has to exchange a driving licence obtained in a non-European country?",
 "F33314#10": "What can disqualify me as a student from asylum seekers' benefits?",
 "F1350#9": "What does tenant insurance cover for a student?",
 "F929#60": "What notice period must my landlord give to end my lease?",
 "F34441#13": "How do I apply for a European Health Insurance Card?",
 "F12859#5": "How can my healthcare costs be covered during my studies?",
 "F1311#17": "How is my rent reviewed or increased?",
 "F31267#23": "If I share a flat, how does the lease cover each flatmate?",
 "F11891#1": "What can make me lose my right to stay in France?",
 "F21032#16": "What can I do if I lose my residence permit?",
 "F32131#9": "How is a workplace accident handled during my internship?",
 "F35807#0": "If I move within France, what should I do about the address on my documents?",
}
rows = [json.loads(l) for l in open("evaluation/questions.jsonl") if l.strip()]
for r in rows:
    r["question"] = FIX.get(r["section_id"], r["question"])
with open("evaluation/questions.jsonl", "w") as f:
    f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
print(len(rows), "questions,", sum(r["section_id"] in FIX for r in rows), "fixed")