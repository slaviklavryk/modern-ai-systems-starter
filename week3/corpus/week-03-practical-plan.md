# Week 3 · Practical — Building a retrieval pipeline

**Session:** Week 3, session 2 of 2 (practical)
**Duration:** 90 minutes
**Syllabus reference:** `Modern_AI_Systems_Syllabus_v2.md` §6 Week 3
**Paired with:** `week-03-lecture-plan.md`

**Guiding question:** Does the mechanism the lecture named actually retrieve the right
chunk, on the student's own corpus?

**Organising principle:** the lecture built the mechanism; this session builds the
pipeline and measures it. Every claim the lecture made about retrieval by meaning is
one students confirm on material they chose themselves, not on a prepared example.
The session ends with the same artefact every retrieval improvement for the rest of
the semester will be measured against.

---

## 1. Ingest and chunk the corpus

Each student brings the domain approved at the end of Week 2 and turns it into a set
of chunks. The section should produce a chunk size and overlap the student can
justify rather than one copied from an example, since the lecture's trade-off between
losing surrounding context and diluting relevance has no single correct answer. This
is necessary infrastructure for everything after it: retrieval operates on these
chunks, not on the raw corpus. Students should confirm the effect of their choice by
inspecting the records they actually stored — `store.peek()`, or `chroma browse` from a
terminal — rather than by re-reading the source text, since a boundary that falls
mid-sentence is invisible in the original and obvious in the chunk.

## 2. Dense retrieval: embed and search

Students embed every chunk once and store the result, then embed a handful of trial
questions and retrieve the nearest chunks. The goal is a working dense-retrieval path
end to end, and a first, informal impression of where it succeeds and where it
returns something plausible-looking but wrong. This is the ingest-once,
query-every-call distinction from the lecture, now in the student's own code rather
than on a slide.

## 3. The gold set

Each student writes ten representative queries for their own domain, with the
property expected of a correct answer, **before** tuning anything against them. The
section should state plainly why the order matters: a gold set written after
retrieval has been adjusted to satisfy it measures nothing. It sits here, immediately
after the first working retrieval and before any decision that could be tuned, for
exactly that reason — students have seen enough of their own results to write useful
queries, and have not yet changed anything to make those queries pass. This is the
evaluation seed every later retrieval or generation improvement in the course is
compared against, starting now rather than in Week 11.

## 4. Choosing an embedding model, measured

Students embed the same corpus with the local multilingual model and with
`gemini-embedding-001`, then compare both against the gold set they have just written.
This is the syllabus's "optional exercise, genuinely instructive" and is the first
decision in the course that a student settles with a measurement rather than a
preference, which is the transferable part. The lecture argued local versus hosted and
monolingual versus multilingual in the abstract; this section makes the argument
concrete on a Ukrainian corpus the student chose, where the multilingual question is
not academic. The outcome is worth discussing whichever way it lands, including when
the hosted model does not win, and this is the first section to drop if the session
runs long.

## 5. From retrieved chunks to a grounded answer

Students take the ranked chunks their own retrieval returns and pass them to the model
as the `sources=` block of the Week 2 context template, producing a grounded answer
from their own corpus. The section is deliberately short on new code: the template,
the system instruction, and the exit clause are all files the student already wrote in
Week 2, and the only genuinely new line is the one that substitutes retrieved text for
pasted text. That is the point worth making explicit — the week's work was building
the thing that fills a slot they already understood, not learning a new framework.
Students should finish with a program that takes a question and returns an answer with
its sources cited, and with at least one observed case where the answer is fluent and
the cited chunk does not support it.

## 6. Assembling the context: the decisions that are yours

Students vary how the retrieved chunks are assembled and observe what changes. The
lecture presented four decisions — how many chunks, in what order, truncated how, and
numbered how — and this section is where each stops being a slide and becomes a line
in the student's own code. The number of chunks is the one to press on, because it is
simultaneously a quality decision and a cost decision: every retrieved chunk is a
prompt token billed on every call, which is the Week 2 token arithmetic arriving in a
place students did not expect it. Numbering is the prerequisite for the citation
section 5 already produced, and is worth naming as the reason an answer can be checked
at all.

## 7. Close

The section confirms the week's deliverable — a working RAG program, question in and
grounded answer out, plus the ten-query gold set — and states what it still lacks: no
student yet knows how often their own system is right across the whole gold set,
because only the embedding-model choice has been measured that way. The
fluent-but-unsupported answer found in section 5 is the evidence that inspection alone
will not settle it. That gap, and the gold set this session produces, are exactly what
Week 4 consumes.

---

## Notes for the syllabus

**Embeddings are hosted, and rate-limited — 2026-09-14.** The local
sentence-transformers backend was removed (syllabus §13): it silently ignored
`task_type`, so the default backend did not implement the query/document asymmetry
this week teaches. `embedding_client.py` now defaults to `gemini-embedding-001`.

The operational consequence shapes the session. Measured 2026-09-14:
**~100 texts per minute, counted per text rather than per request**, so batching does
not help and a 3,000-chunk corpus is roughly half an hour of ingest. Two things follow.
The store is persistent (`./chroma/`), and corpus ingestion happens in `ingest.py` from
a terminal rather than in a notebook cell — which is also the lecture's ingest-once,
query-every-call split made literal. Section 1 works on a small sample in the notebook;
students point `ingest.py` at their real corpus and let it run.

**Section 4's comparison changed accordingly.** It was local against hosted; it is now
`gemini-embedding-001` against OpenRouter's `baai/bge-m3`, and on a real corpus it must
be run over a subset, since each comparison costs a second full ingest.

**Resolved — the scripts this practical needs now exist in `starter-repo/`:**
`chunking.py` and `vector_store.py` (Chroma, configured for cosine distance — its
unconfigured default is Euclidean). Each was verified against a real, measured
result, recorded in `CLAUDE.md`, not assumed to work from the library's
documentation alone.

**Sparse retrieval removed and RAG construction moved in, 2026-09-14.** Sections on
BM25, lemmatisation, and Reciprocal Rank Fusion were withdrawn along with the
corresponding lecture block, and section 3 was added in their place when RAG
construction moved from Week 4 into Week 3. See the two syllabus §13 entries of the
same date. Section 3 depends on each student still having their Week 2 context
template to hand; students who did not keep it will need it reconstructed before the
session.

**The deck now exists: `weeks/week-03-practical.md`, 2026-09-14.** Nine numbered steps
against the seven sections below, in the project-and-circulate format Week 1's practical
established, plus six troubleshooting reference slides. Timings sum to 84 of 90 minutes.
It assumes the room works on a small sample and students run the full ingest afterwards,
for the reason given in the rate-limit note above.

**The notebook now exists: `starter-repo/week3/retrieval_lab.ipynb`, 2026-09-14.** Seven parts
matching the seven sections below, written against the student's own corpus throughout.
Two lecture points are exercised inside it rather than as sections of their own: Part 2
has students confirm that a one-word input and a whole corpus embed to the same number
of dimensions, and that a relevant chunk outscores an unrelated one on their own text.

**Run end to end, 2026-09-15.** A four-paragraph Ukrainian and English corpus through
`ingest.py --chunk-size 40 --name e2e --reset`, then reopened in a separate process:
`count()`, `collections()`, `peek()` and `search()` all correct, cosine distances in
range, persistence across processes confirmed. `rag()` returned a grounded, correctly
cited answer — *"Lab 2 is worth 25% of the final grade. [1] It is due at the end of Week
7. [1]"* — and the section 6 token-cost loop showed 102 / 233 / 319 prompt tokens at
k = 1 / 3 / 5. The embedding throttle was verified separately against the live quota,
embedding 120 texts across a window boundary without a 429. Section 4 still needs
`OPENROUTER_API_KEY` and was not exercised.

**One bug found and fixed by that run.** `vector_store.py` created its collection without
`embedding_function=None`, so Chroma recorded its own 384-dimension default in the
collection config while the stored vectors were 3072 from `gemini-embedding-001`. Our own
code never noticed, since it always passes vectors explicitly, but the declared function
contradicted the data for anything else opening the collection. Recorded in `CLAUDE.md`.

**`chroma browse` is present but unconfirmed.** The command exists in the pinned
`chromadb==1.5.9` and its `--path` syntax matches what the README documents; the TUI
starts and draws its header. It reported "Failed to load records" here, both before and
after the embedding-function fix, which points at the preparation environment — it spawns
its own server and had neither a real terminal nor, probably, a free port. Confirm it on a
real machine before offering it to a class. It is deliberately documented second, behind
`store.peek()`, so nobody is blocked if it misbehaves. Note also that it leaves its server
running after the command exits, which holds `./chroma/` open until that process ends.

**Coverage against the lecture, checked 2026-09-14.** Sections 4 and 6 were added after
an audit found two lecture sections with no practical counterpart: §4 "Choosing a
model", whose comparison exercise §6 Week 3 of the syllabus specifies and which was
absent entirely, and §8's four context-assembly decisions, which were taught as the
student's own and then never practised. Lecture §1 has no practical counterpart by
design, being motivational. Lecture §2 and §3 are exercised inside the notebook rather
than as sections of their own, since inspecting a vector and confirming that a relevant
chunk outscores an unrelated one are each a matter of minutes.

**Section 3 moved earlier in the same revision.** The gold set previously sat second
from last, after the sections whose decisions it is meant to adjudicate. It now
precedes the embedding-model comparison, which is the first thing in the session a
student could tune.
