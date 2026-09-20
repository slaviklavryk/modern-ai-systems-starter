# Week 3 · Lecture — Embeddings, semantic search, and RAG

**Session:** Week 3, session 1 of 2 (lecture)
**Duration:** 90 minutes
**Syllabus reference:** `Modern_AI_Systems_Syllabus_v2.md` §6 Week 3

**Guiding question:** How can software find information by meaning, and hand what it
finds to a model?

**Organising principle:** Week 2 closed by naming the limitation its own prompt
skeleton could not remove: the sources block was still pasted in by hand, which
required the developer to already know which passage answered the question. This
session removes that assumption and then completes the loop. It is not new material
bolted onto the template; it is the automation of the one block of a context the
students already understand, followed by the step that returns the filled template to
the model.

---

## 1. Why keyword search is not enough

Students should leave able to produce, from their own vocabulary, a case where an
exact-match search fails on a paraphrase or a synonym, and to state that this is a
property of matching on symbols rather than meaning, not a defect of any particular
search engine. The section opens the session because it is the honest motivating
question rather than a rhetorical one: keyword search is not a weak technology to be
replaced, and it remains better at exact identifiers and rare terms. The session does
not return to that point, since sparse retrieval and fusion are not part of this
course, so the limitation is stated as a property of symbol matching without promising
a later resolution.

## 2. What an embedding is

Students should leave able to state the mechanism precisely, not merely gesture at
it. An embedding model consumes a sequence of tokens, the same sub-word units Week 2
introduced, and an encoder network maps that sequence to one fixed-length vector,
typically several hundred to a few thousand numbers, regardless of how many tokens
the input contained. The numbers are meaningful rather than arbitrary because of how
the model was trained: a contrastive objective pushes pairs of texts that share
meaning toward nearby vectors and pushes unrelated pairs apart, so "nearby in this
space" is a direct consequence of training rather than an emergent property to be
taken on faith. The distinction between an embedding model and a generative model
follows from this in one sentence: a generative model consumes tokens and repeatedly
predicts the next one, producing text; an embedding model consumes the whole input
once and produces a single static vector, made for comparison rather than for
reading. This is the new mechanism the session introduces, and every later section,
from similarity to indexing, presupposes it.

## 3. Measuring similarity between vectors

Students should leave able to state, not merely wave at, how two embeddings are
compared. Euclidean distance is the straightforward case: the straight-line distance
between two points in the space, sensitive to each vector's magnitude as well as its
direction. Cosine similarity is the metric this course actually uses, and students
should be able to give its definition: the dot product of two vectors divided by the
product of their magnitudes, which is precisely the cosine of the angle between them,
ranging from −1 for opposite vectors through 0 for unrelated ones to 1 for vectors
pointing in an identical direction. The reason to prefer it over Euclidean distance
should be stated as a consequence of that definition rather than a rule to memorise:
cosine similarity discards magnitude and measures direction alone, which matters
because an embedding's magnitude can vary with properties such as text length that
have nothing to do with meaning, while its direction is what training made
meaningful. Students should also recognise "cosine distance," reported by some vector
stores as one minus the similarity, as the same quantity inverted so that a smaller
number means a closer match. This depends directly on section 2 and is the mechanism
every later section's ranking is built from.

## 4. Choosing a model

Students should leave able to justify a choice of embedding model for their own
project rather than treat the default as unexplained: local versus hosted, where a
model that runs on a laptop is the reasonable default and where a hosted model earns
its cost; monolingual versus multilingual, a genuine decision in a course conducted in
Ukrainian rather than an academic aside; and Matryoshka truncation, why a model's
full dimensionality can be cut down at little cost when storage or latency matters.
Multimodal embeddings are named only as a possible project extension, not developed
here.

## 5. Chunking a corpus

Students should leave understanding why an entire document cannot be embedded as one
vector without losing the ability to retrieve any one part of it, and should be able
to reason about the trade-off a chunk boundary creates: too small and a chunk loses
the context that gave it meaning, too large and it dilutes relevance with unrelated
material. Overlap is presented as a mitigation for information lost at a boundary,
not as a free parameter. This section is necessary infrastructure before section 6,
since chunk size is a pipeline design decision rather than a detail of storage.

## 6. The retrieval pipeline

Students should leave able to draw the full path from a raw corpus to a ranked list
of chunks: ingest, chunk, embed, and store in a vector index at one point in time,
then embed the query and search that index on every call. The distinction between
what happens once and what happens on every call echoes the "changes every call
versus never" distinction Week 2 drew for context assembly, and should be named
explicitly as the same idea applied to retrieval. The section then surveys where that
index actually lives in practice, so that students choose a store for their own project
rather than adopting the course's default unexamined: dedicated vector databases such
as Chroma, Qdrant, Weaviate and Milvus; general-purpose databases that have acquired
vector search, including PostgreSQL through `pgvector`, SQL Server 2025, MariaDB,
DynamoDB and — the one that matters for this course — Neo4j; and index libraries such
as FAISS, which supply the search algorithm without persistence or an API around it.
Two things in that middle group earn the time. MySQL Community stores a `VECTOR` and
cannot search it, while its fork MariaDB ships a working `VECTOR INDEX`, which makes
the point that a data type is not a capability and that the manual settles it rather
than the announcement. And Neo4j, the database installed in Week 5 and required for
Lab 2, holds vector indexes natively under the same cosine metric taught here, so a
student may keep embeddings and graph in one system instead of two; the option is named
here and developed in Weeks 5 and 6 rather than pursued now. The
point to land is that most of these implement the same underlying index, so the choice
is an operational question about durability, filtering and scale rather than a
mathematical one — and that the `hnsw:space` parameter students pass to Chroma in the
practical names that algorithm in their own code. Published comparisons of these
products are largely vendor-adjacent and their figures move between releases, so the
section gives a decision heuristic rather than a ranking.

## 7. Why a ranked list is not an answer

Students should leave able to state what retrieval has and has not achieved. A ranked
list of chunks is not what a user asked for; it is the input to the thing they asked
for, and nothing so far in the session produces prose. The section names the limits of
an LLM-only application directly — knowledge frozen at training time, no access to a
private corpus, and confident invention when asked beyond it, all of which Week 1's
Experiment 4 already demonstrated to these students — and positions retrieval as the
supply of exactly what the model lacks. This is the section that earns the
demonstration: the same question asked of the model alone and of the model given
retrieved chunks, where the difference is visible without interpretation.

## 8. Assembling a context and grounding the answer

Students should leave able to draw the complete RAG path and to place it against
something they have already built. The retrieved chunks become the `sources=` block of
the Week 2 context template, now filled by software rather than by hand, which is the
payoff of this session's organising principle and should be named as such rather than
left for students to notice. The section covers what assembly involves — ordering,
truncation to a token budget, and the numbering that makes citation possible — and then
grounding: the system instruction and exit clause from Week 2 are what keep the model
inside the supplied sources, and source attribution is what makes an answer checkable
rather than merely fluent. Students should leave understanding that grounding is
requested rather than guaranteed, which is the thread Week 4 picks up when it measures
how often the request is honoured.

## 9. Close

The section states what is due this week: ten representative queries with expected
properties, written for each student's own domain, and why evaluation practice begins
here rather than in Week 11 — a later improvement can only be measured against a gold
set that already exists. It closes by naming what the week's working system still
lacks: nothing yet establishes whether it answers correctly, since a pipeline that runs
is not a pipeline that works, and no student has yet measured their own. That is the
subject of Week 4 and the reason the gold set is due before it.

---

## Notes for the syllabus

**`gemini-embedding-001`, named in §6 Week 3's optional exercise, is verified current
(2026-09-13, recorded in `CLAUDE.md`) and its choice over the newer `gemini-embedding-2`
is deliberate, not an oversight worth flagging away.** Measurement found that `-001`
produces different vectors for a document and a query embedding of identical text,
while `-2` and `-2-preview` do not: cosine similarity of exactly 1.0000 between the
two. Since query/document asymmetry is core retrieval material, `-001` is the correct
pin despite `-2`'s longer input window. Re-verify before each offering regardless,
per this course's standing practice: `-2` may gain the same behaviour in a later
revision, at which point its larger context window would make it the better default.
