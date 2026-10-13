# Guichet

Ask about French administrative procedures in English and get an answer drawn only from official French guidance, with links to the sources.

**[Try the live demo](https://huggingface.co/spaces/AfoDyDigitals/Guichet)**

**Headline result:** translating English questions into French before searching raised retrieval recall@5 from **45% to 57%**, matching native-French performance on the same 102 questions. Answers built from the retrieved passages were **fully supported by their sources 76% of the time**, rising to **88%** when retrieval found the right passage.

## The problem

International students in France need answers from administrative guidance that exists only in French. A keyword search fails across languages, and a general chatbot can invent rules. Guichet ("service counter") retrieves the relevant official passages and answers from them alone.

## How it works

```
English question
  → translated to French (opus-mt-en-fr)
  → hybrid search: BM25 + dense embeddings (multilingual-e5-small), merged with reciprocal rank fusion
  → top 30 reranked by a multilingual cross-encoder (mmarco-mMiniLMv2)
  → top 5 passages given to Qwen2.5-3B-Instruct
  → English answer with numbered citations and links to the official pages
```

## Data

- **Corpus:** 417 pages from Service-Public.gouv.fr relevant to student life (residence permits, housing, health cover, work, driving licences, banking), split into 7,551 sections.
- **Source:** Service-Public.gouv.fr / DILA, "Fiches pratiques et ressources de Service-Public.gouv.fr Particuliers", file `vosdroits-latest` downloaded 11 October 2026 from [data.gouv.fr](https://www.data.gouv.fr/datasets/fiches-pratiques-et-ressources-de-service-public-gouv-fr-particuliers), under Licence Ouverte v2.0.
- **Test set:** 102 questions I wrote in English, each tied to the passage that answers it, written before any retrieval code existed. A French version of each (translated with Claude, spot-checked). A separate set of 41 LLM-generated questions (written by Claude, filtered by hand) to compare against.

## Results

### Retrieval: recall@5 (exact passage in the top 5)

Best method (rerank), by chunking strategy:

| Questions | Section | Fixed-size | Sentence windows |
|---|---|---|---|
| English | 38.2% | 43.1% | 45.1% |
| English, translated to French first | 53.9% | 55.9% | **56.9%** |
| French | 57.8% | 60.8% | 56.9% |

All four methods on English questions (sentence windows):

| Method | Recall@5 |
|---|---|
| BM25 (keywords) | 3.9% |
| Dense (embeddings) | 36.3% |
| Hybrid (BM25 + dense) | 24.5% |
| Hybrid + rerank | **45.1%** |

### Answers: faithfulness to sources (50 answers, labelled by hand)

| | Supported | Partly | Unsupported | Declined |
|---|---|---|---|---|
| All 50 | 76% | 16% | 4% | 4% |
| Right passage retrieved (32) | 88% | 6% | 3% | 3% |
| Right passage missed (18) | 56% | 33% | 6% | 6% |

## Findings

1. **Translating the query closes most of the language gap.** The same English questions scored 12 to 20 points below their French versions; one translation step recovered 72% to 100% of that gap.
2. **Keyword search does not work across languages.** BM25 scored under 5% on English questions, and merging it into a hybrid made results worse than dense search alone. The reranker recovered from this.
3. **Reranking won in every configuration**, by 6 to 14 points over dense search.
4. **Chunking strategy made little difference.** The three strategies were within a few points of each other, below what 102 questions can reliably separate.
5. **Answer quality follows retrieval quality.** When retrieval missed, the model declined only once in 18 cases and instead answered from nearby passages, with partly supported answers rising from 6% to 33%. Teaching it to decline is the clearest next improvement.

## Limitations

- **Small test set.** With 102 questions, single scores carry a margin of about ±10 points. Comparisons on the same questions (English vs translated vs French) are more reliable than that.
- **One annotator.** I wrote the questions and labelled the answers myself.
- **"Supported" is not "correct".** Faithfulness labels check that claims appear in the cited passages, not that the passages fit the student's situation.
- **The French question set is machine-translated**, not written by native speakers.
- **The synthetic question set was inconclusive:** 41 questions on different passages cannot be compared cleanly with the human set.
- **The corpus is a snapshot** of 11 October 2026; the source changes daily.
- **The sentence splitter fails on long lists** without full stops, leaving a few chunks of up to 765 words.
- **Search is exact (brute-force) k-NN**, fine at 15,000 chunks; a larger corpus would need an approximate index such as FAISS or HNSW.
- **The demo** truncates each passage to 300 words to keep answers fast.

## Repository

```
data/          select_pages.py, build_corpus.py, make_chunks.py, corpus.jsonl
retrieval/     search.py: BM25, dense, hybrid, rerank
evaluation/    test questions, scoring, review-page builders
results/       retrieval scores, per-question ranks, answers, faithfulness labels
app/           rag.py (pipeline) and app.py (Gradio demo)
guichet_colab.ipynb   runs embedding, evaluation and generation on a free Colab GPU
```

## Reproduce

1. Download `vosdroits-latest` from the data.gouv.fr link above into `data/raw/`.
2. `python data/select_pages.py && python data/build_corpus.py && python data/make_chunks.py`
3. Open `guichet_colab.ipynb` in Colab on a T4 GPU and run the cells in order.

## Author

Temidayo James Afolabi, M.Sc. Computational Linguistics, Université Paris Cité · [GitHub](https://github.com/AfoDyDigitals)
