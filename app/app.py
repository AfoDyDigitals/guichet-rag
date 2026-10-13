"""Guichet demo: ask in English, get an answer from official French guidance, with sources."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "retrieval")]

import gradio as gr
import numpy as np
import torch
from sentence_transformers import SentenceTransformer, CrossEncoder
from search import Retriever
from rag import Translator, Generator, PAGE_URL

CHUNKS = os.environ.get("GUICHET_CHUNKS", "chunks_sentence.jsonl")
EMB = os.environ.get("GUICHET_EMB", "emb_sentence.npy")
try:
    import spaces
    gpu_task = spaces.GPU(duration=60)
except ImportError:
    gpu_task = lambda f: f

DEVICE = "cuda" if (os.environ.get("SPACES_ZERO_GPU") or torch.cuda.is_available()) else "cpu"
LLM = os.environ.get("GUICHET_LLM", "Qwen/Qwen2.5-3B-Instruct" if DEVICE == "cuda" else "Qwen/Qwen2.5-1.5B-Instruct")

chunks = [json.loads(l) for l in open(CHUNKS)]
emb = np.load(EMB)
assert len(chunks) == len(emb), "chunks and embeddings don't match"
retriever = Retriever(chunks,
                      SentenceTransformer("intfloat/multilingual-e5-small", device=DEVICE), emb,
                      CrossEncoder("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1", max_length=512, device=DEVICE))
translator = Translator(device=DEVICE)
generator = Generator(LLM, device=DEVICE)


def short(p, words=300):
    return {**p, "text": " ".join(p["text"].split()[:words])}


def sources_md(passages, query_fr):
    lines = [f"**Searched in French:** {query_fr}"]
    for i, p in enumerate(passages, 1):
        lines.append(f"**[{i}]** {p['text'][:160]}… [official page]({PAGE_URL.format(p['page_id'])})")
    return "\n\n".join(lines)


@gpu_task
def respond(question):
    question = (question or "").strip()
    if not question:
        yield "Type a question first.", ""
        return
    query_fr = translator([question])[0]
    passages = [short(chunks[i]) for i in retriever.search("rerank", query_fr, 5)]
    sources = sources_md(passages, query_fr)
    yield "_Writing the answer…_", sources
    text = ""
    for piece in generator.stream(question, passages):
        text += piece
        yield text, sources


with gr.Blocks(title="Guichet") as demo:
    gr.Markdown("# Guichet\nAsk about French admin procedures for students (residence permits, housing, "
                "health cover, work) in English. Answers come only from official "
                "[Service-Public.gouv.fr](https://www.service-public.gouv.fr) guidance, with sources.\n\n"
                "_Unofficial demo: answers can be wrong. Always check the linked official page._")
    question = gr.Textbox(label="Your question", placeholder="Where can I buy a tax stamp?")
    ask = gr.Button("Ask", variant="primary")
    answer = gr.Markdown(label="Answer")
    with gr.Accordion("Sources", open=True):
        sources = gr.Markdown()
    gr.Examples(["Where can I buy a tax stamp?",
                 "How many hours can a non-European student work in France?",
                 "How do I get my security deposit back from my landlord?",
                 "How do I apply for the APL housing benefit?"], inputs=question)
    ask.click(respond, question, [answer, sources])
    question.submit(respond, question, [answer, sources])

if __name__ == "__main__":
    demo.launch()
