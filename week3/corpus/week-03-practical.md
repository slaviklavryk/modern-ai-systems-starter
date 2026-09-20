---
title: Week 3 — Practical: From a Folder of Documents to a Grounded Answer
subtitle: Modern AI Systems · Practical 3
footer: Modern AI Systems · Week 3 Practical
theme: light
---

# Week 3 — Practical

**Building the thing that fills the `SOURCES` block, and then closing the loop**

<!-- notes:
≈90 min. Section intent in week-03-practical-plan.md.

Project this deck and leave it up. Students self-pace; do not try to keep 25 people in
lockstep. Print it as a handout (Ctrl+P) so nobody is blocked waiting for a slide.

Your job is to circulate, not to present.

THE CONSTRAINT THAT SHAPES THIS SESSION: embedding is limited to roughly 100 texts per
minute, measured 2026-09-14, and the quota counts texts rather than requests so batching
does not help. A real corpus is therefore half an hour of ingest, which does not fit in a
90-minute room.

So: everyone works on a SMALL sample in the session, and runs the full ingest on their own
corpus afterwards. Say this at the start. A student who points `ingest.py` at 3,000 chunks
at minute five will spend the session watching a progress line.

Step timings sum to ≈86 min and are guidance, not a script.
-->

---

## What you leave with today

- Your corpus **chunked, embedded, and searchable**
- **Ten gold-set queries** — the deliverable due this week
- A program that answers a question **from your own documents, with sources**

<!-- notes:
≈1 min. Read the list and start Step 1.

The third item is the one that surprises them: by the end of today they have built RAG,
which most of them expect to be a much larger thing than it is.
-->

---

## Before anything: ingest is slow, on purpose

Embedding is capped at about **100 texts per minute**. The quota counts *texts*, not
requests — **batching cannot speed it up.**

- **In the lab:** a small sample. Twenty or thirty chunks.
- **Tonight:** your real corpus, with `ingest.py` left running.

<!-- notes:
≈3 min. State this before anyone opens a terminal.

The measurement is the course's own, taken 2026-09-14: a cold batch of 100 succeeds and
50+50 is refused immediately. There is no trick that avoids it — only waiting, and
embedding once rather than repeatedly.

Which is why the store is persistent. Embeddings are written to ./chroma/ and survive a
kernel restart, so the cost is paid per corpus rather than per session. This is the
practical reason behind the ingest-once, query-every-call split the lecture drew.

TRIAGE: a student who has already started a large ingest should not kill it. Let it run in
its own terminal and work the session on a sample in a second collection with --name.
-->

---

## Step 1 — Install the vector store

Work from the **`week3/`** folder — that is where this week's code and your `./chroma`
store live.

```bash
cd week3
.venv\Scripts\activate
pip install -r requirements.txt
python -c "import chromadb; print(chromadb.__version__)"
```

No Docker, no server. Chroma runs **inside your Python process** and keeps its data in a
folder.

<!-- notes:
≈5 min.

Expect the question "where is the container?" — this course uses Docker for Neo4j from
Week 4, so the assumption is reasonable. Chroma's PersistentClient is embedded: SQLite for
metadata, files for the index. The comparison that lands is SQLite against PostgreSQL.

If `pip` dies with OSError or a long-path error, they cloned too deep. `C:\dev\modern-ai`,
recreate the venv. Same failure as Week 1, same fix.
-->

---

## Step 2 — Chunk your corpus

```python
from chunking import chunk_text

chunks = chunk_text(MY_CORPUS, chunk_size=60, overlap=15)
print(f"{len(MY_CORPUS.split())} words -> {len(chunks)} chunks")
```

Change `chunk_size`. Run it again. **Watch a sentence that sits on a boundary.**

<!-- notes:
≈8 min. Open `retrieval_lab.ipynb`, Part 1.

The trade-off has no correct answer and they must not be given one: too small loses the
context that gave a chunk meaning, too large dilutes relevance with unrelated material.
Overlap mitigates what a boundary cuts; it is not a free parameter.

Push for a number they can defend. "200 because the example said 200" is the answer to
refuse — they defend this choice in Lab 1.

Nothing here costs an API call. Chunking is pure string work.
-->

---

## Step 3 — Embed the sample

```python
from vector_store import VectorStore

store = VectorStore(name="lab_demo", reset=True)
store.add(chunks)
print(f"{store.count()} chunks indexed")
```

Twenty or thirty chunks. **Not your whole corpus — not yet.**

<!-- notes:
≈6 min.

`add()` is the ingestion-time half of the pipeline: embed once, store. `reset=True` clears
the collection first, which is what you want every time the chunk size changes and never
want otherwise.

Watch for someone whose sample is 500 chunks. That is five minutes of waiting and they
will think it has hung.
-->

---

## Checkpoint — look at what you stored

```python
for row in store.peek(3):
    print(f"[{row['id']}] {row['chunk'][:100]}...")
```

Read chunk `[0]` against your source text. **Did the boundary land mid-sentence?**

From a terminal: `chroma browse lab_demo --path ./chroma`

<!-- notes:
≈4 min. Do not skip this. It is the only moment in the session where a student sees their
own chunking as data rather than as a parameter.

`search()` answers "what is relevant to this question". It cannot answer "what is actually
in there", which is what a wrong chunk boundary requires. That distinction is worth saying
out loud, because it is the same distinction that makes Week 4's measurement necessary.

A mid-sentence split is invisible in the original document and obvious in the stored chunk.
That is the whole point of looking.

`peek()` is the reliable route and the one to demonstrate. `chroma browse` is a fuller
browser but it starts a server of its own and needs a real terminal; it was confirmed
present in the pinned chromadb 1.5.9 and was NOT confirmed to load records, because the
preparation environment had no terminal to test it in. Try it once on your own machine
before offering it to the room. It also leaves its server running after the command ends,
which locks ./chroma/ until that process is stopped.
-->

---

## Step 4 — Retrieve

```python
for row in store.search("your question here", n_results=3):
    print(f"distance={row['distance']:.4f}  {row['chunk'][:80]}...")
```

`distance` is **1 − cosine similarity**. Smaller is closer.

**Find one question it answers well, and one it gets wrong.** You need both.

<!-- notes:
≈10 min.

The failing question is the more valuable of the two and students will not look for it
unless told. Press for it: a question whose answer is spread across two chunks, or one that
turns on a word the corpus phrases differently.

Keep the pairing from the lecture in view — retrieval by meaning succeeds on paraphrase and
has no special claim on exact identifiers.

They will need the failing question again in Step 7.
-->

---

## The gold set

<!-- notes:
Section divider. ≈10 min. This is the deliverable due this week.
-->

---

## Step 5 — Ten queries, written before you tune anything

```python
GOLD = [
    {"query": "...", "expect": "a distinctive phrase the right chunk contains"},
    # ten of them, for YOUR corpus
]
```

A gold set written **afterwards**, to fit results you already have, measures nothing.

<!-- notes:
≈10 min. The order is the entire point and it is worth being blunt about.

It sits here — after retrieval works, before the first tunable decision — for that reason.
They have seen enough of their own results to write useful queries, and have not yet
changed anything to make those queries pass.

`expect` is a checkable phrase, not a full answer. This is deliberately cruder than
recall@k: Week 4 turns it into a real measurement, across several values of k and with the
failures diagnosed. Do not pre-empt that here.

This is the artefact every later improvement in the course is compared against. A student
who leaves without it cannot do Week 4.
-->

---

## Step 6 — Choosing a model, settled by a number *(optional)*

```python
alt = EmbeddingClient(provider="openrouter")
alt_store = VectorStore(embedder=alt, name="lab_demo_alt", reset=True)
alt_store.add(chunks)
```

`gemini-embedding-001` against `baai/bge-m3`, on **your** gold set.

<!-- notes:
≈8 min, and the first section to cut if the room is behind. Needs OPENROUTER_API_KEY.

A tie is the likely result on a small corpus, and a tie is an answer: it means the decision
belongs to the things that are not retrieval quality — rate limit, cost, dimensionality and
therefore storage.

One of those is decisive rather than a tiebreaker. `task_type` query/document asymmetry
works on Gemini and is a confirmed no-op through OpenRouter, even routing the same model.
Point them at the capability matrix in `embedding_client.py` rather than asserting it.

On a real corpus this costs a second full ingest, so it is a subset exercise. Say so.
-->

---

## Hand the chunks to the model

<!-- notes:
Section divider. ≈18 min. The loop closes here.

Everything from now on costs generation calls, which are the separate 6-per-minute limit.
Expect 429s and expect them to be fine — `ask()` reports the wait in plain language.
-->

---

## Step 7 — This is the whole of RAG

```python
def rag(question, *, k=3):
    retrieved = [row["chunk"] for row in store.search(question, n_results=k)]
    return ask(question, system=SYSTEM, task=TASK, fmt=FORMAT, sources=retrieved)
```

`SYSTEM`, `TASK`, `FORMAT` are **your Week 2 files, unchanged.** One line is new.

<!-- notes:
≈12 min. The payoff of the session and of the last two weeks.

Read the printed context before the answer. The SOURCES block was assembled by their own
code, from their own corpus, moments ago — and nothing else in the template moved since
Week 2.

Refuse the framing that this is a new architecture. It is one slot of a template they
already wrote, now filled by a function instead of by hand. A student who believes they are
learning a framework will go looking for complexity that is not there.

A student who did not keep their Week 2 template needs it reconstructed now. Pair them with
someone who did.
-->

---

## Step 8 — Now run the question it got wrong

Retrieval failing means the model is grounded in **the wrong passage** — and a wrong
passage does not announce itself.

**Find one answer that reads well and is not supported by its own cited chunk.**

<!-- notes:
≈6 min. The most important thing they take to Week 4.

Make them read the cited chunk, not just the answer. The failure they are hunting is
fluent, formatted, cited, and wrong — which is exactly what Week 2's hallucination section
described, now arriving through retrieval instead of through absent context.

Ask which stage failed: chunking, retrieval, or generation. They will not be able to tell
reliably, and that is the honest answer — diagnosing it is Week 4's subject.

Anyone who cannot produce one should try a question whose answer needs two chunks at once.
-->

---

## The decisions that are yours

<!-- notes:
Section divider. ≈8 min.
-->

---

## Step 9 — What `k` costs

```python
for k in (1, 3, 5, 10):
    retrieved = [r["chunk"] for r in store.search(QUESTION, n_results=k)]
    prompt = render(QUESTION, task=TASK, fmt=FORMAT, sources=retrieved)
    print(f"k={k:>2} -> {counttokens(prompt):>5} prompt tokens, every call")
```

Then compare `rag(q, k=1)` against `rag(q, k=10)` — **the answers, not just the price.**

<!-- notes:
≈8 min. Week 2's token arithmetic arriving where they did not expect it.

Every retrieved chunk is a prompt token billed on every call. Retrieving ten where three
would do is a cost decision made by accident unless someone looks.

And more context is not reliably better: at k=10 the relevant passage competes with
material that is merely nearby. This is the context-rot point from Week 2, now reproducible
in their own pipeline.

The other three decisions — ordering, truncation, numbering — are named on the slide in the
lecture and belong to Lab 1. Numbering is the one worth a sentence: `render()` writes [1],
[2], which is the only reason a citation can be checked at all.
-->

---

## Before you leave

1. **Ten gold-set queries**, written before you tuned anything
2. A `rag()` that answers from your corpus, **with sources**
3. One **fluent, wrong, cited** answer — bring it to Week 4

Then tonight: `python ingest.py corpus/` on the real thing.

<!-- notes:
≈2 min.

Item 3 is the one they will forget and the one Week 4 opens with. Have them paste it into
their notes now, not from memory next week.

Remind them ./chroma/ is the artefact that makes the project work offline. Ingest while
connectivity is good and keep the folder — re-ingesting is the expensive operation,
querying is not.
-->

---

## Due end of this week

**Ten representative queries with expected properties, for your own domain.**

This is the **evaluation seed**. Every retrieval improvement for the rest of the semester
is measured against it.

<!-- notes:
≈1 min. Milestone 0 was Week 2; this is the first evaluation artefact of the course.

Next session measures their system against this set and takes it apart. Nobody arrives at
Week 4 usefully without it.
-->

---

## Troubleshooting

<!-- notes:
Section divider. Reference slides — do not present these. Jump to one when it is needed,
or let students find them in the printed handout.
-->

---

## `ModuleNotFoundError: chromadb`

`.venv` is not active, or Week 3 dependencies are not installed.

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

<!-- notes:
No `(.venv)` in the prompt is the tell.
-->

---

## `store.count()` returns 0

The collection name you opened is not the one you ingested into.

```python
print(store.collections())
```

<!-- notes:
Nearly always a mismatch between `VectorStore(name=...)` and `ingest.py --name`. The
default on both sides is "chunks".
-->

---

## `429` while embedding

The per-minute text quota. About 100 texts a minute, counted per text.

**Wait.** `ingest.py` paces itself; a notebook cell does not.

<!-- notes:
Seeing this in a notebook means they are embedding a corpus in a cell rather than through
ingest.py. Move it to the script.
-->

---

## Chunk size changed, results did not

You did not pass `--reset`, so the old chunks are still there beside the new ones.

```bash
python ingest.py corpus/ --chunk-size 300 --reset
```

<!-- notes:
Same in the notebook: `VectorStore(..., reset=True)`.
-->

---

## The ingest looks frozen

It is waiting out the quota, and it prints how long for.

A large corpus is genuinely tens of minutes. **Leave it running.**

<!-- notes:
Point at the "[embedding quota: ... waiting Ns]" line. This is the failure mode most likely
to make a student kill a job that was working.
-->

---

## `429` while generating

The separate **6 calls per minute** generation limit. Expected, not a fault.

`ask()` waits and retries, and says so.

<!-- notes:
Two different quotas in one session, and students will conflate them. Embedding is ~100
texts/min; generation is ~6 calls/min. Different limits, different causes.
-->
