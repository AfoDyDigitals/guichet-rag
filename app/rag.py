"""Guichet pipeline: translate the question -> retrieve French passages -> answer in English with citations."""
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM

SYSTEM = (
    "You help international students with French administrative procedures. "
    "Answer ONLY from the numbered French passages provided. "
    "Write in English, in 2 to 4 short sentences. "
    "After each claim, cite the passage it comes from, like [1] or [2]. "
    "If the passages do not answer the question, reply exactly: "
    "\"I couldn't find this in the official guidance.\""
)
NOT_FOUND = "I couldn't find this in the official guidance."
PAGE_URL = "https://www.service-public.gouv.fr/particuliers/vosdroits/{}"


class Translator:
    def __init__(self, name="Helsinki-NLP/opus-mt-en-fr", device="cpu"):
        self.tok = AutoTokenizer.from_pretrained(name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(name).to(device)

    def __call__(self, texts, bs=32):
        out = []
        for i in range(0, len(texts), bs):
            batch = self.tok(texts[i:i + bs], return_tensors="pt", padding=True, truncation=True).to(self.model.device)
            with torch.no_grad():
                ids = self.model.generate(**batch, max_new_tokens=128)
            out += self.tok.batch_decode(ids, skip_special_tokens=True)
        return out


class Generator:
    def __init__(self, name="Qwen/Qwen2.5-3B-Instruct", device="cpu"):
        self.tok = AutoTokenizer.from_pretrained(name)
        dtype = torch.float16 if device == "cuda" else torch.float32
        self.model = AutoModelForCausalLM.from_pretrained(name, dtype=dtype).to(device)

    def answer(self, question, passages, max_new_tokens=200):
        context = "\n\n".join(f"[{i}] {p['text']}" for i, p in enumerate(passages, 1))
        messages = [{"role": "system", "content": SYSTEM},
                    {"role": "user", "content": f"Passages:\n{context}\n\nQuestion: {question}"}]
        inputs = self.tok.apply_chat_template(messages, add_generation_prompt=True, return_dict=True,
                                              return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            out = self.model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
        return self.tok.decode(out[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def ask(question, retriever, translator, generator, k=5, method="rerank"):
    query_fr = translator([question])[0]
    passages = [retriever.chunks[i] for i in retriever.search(method, query_fr, k)]
    return {"question": question, "query_fr": query_fr, "passages": passages,
            "answer": generator.answer(question, passages),
            "sources": [PAGE_URL.format(p["page_id"]) for p in passages]}
