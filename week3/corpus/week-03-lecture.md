---
title: Week 3 — Embeddings, Semantic Search, and RAG
subtitle: Modern AI Systems · Lecture 3
footer: Modern AI Systems · Week 3
theme: light
---

# How can software find information by meaning, and hand what it finds to a model?

*Week 3 — embeddings, similarity, chunking, retrieval, and grounded generation*

<!-- notes:
≈90 min for the session. Run sheet: none. `week-03-lecture-plan.md` states each
section's intent only, the format this course's plans follow. The per-slide
timings below are the schedule.

Organising principle, from the plan: Week 2 closed by naming what its own prompt
skeleton could not remove — the sources block was still pasted in by hand, which
required the developer to already know which passage answered the question. This
session is not new material bolted onto that template. It is the automation of the
one block of a context the students already understand, followed by the step that
returns the filled template to the model.
-->

---

## Why keyword search is not enough

<!-- notes:
Section divider. Plan §1.

The goal of this block: students should leave able to produce, from their own
vocabulary, a case where exact-match search fails on a paraphrase or a synonym, and
to state that this is a property of matching symbols rather than meaning, not a
defect of any particular search engine.

This opens the session because it is the honest motivating question, not a
rhetorical one. Keyword search is not a weak technology awaiting replacement; it
remains better at exact identifiers and rare terms. The session does not return to
that point, since sparse retrieval and fusion are not part of this course. State the
limitation as a property of symbol matching and do not promise a later resolution.
-->

---

## The same idea, no shared words

> "How does the system find the right passage in a large document collection?"

> Corpus sentence: *"Neo4j stores information as nodes connected by edges."*
> Query: *"graph database"*

**Zero words in common. The same topic.**

<!-- notes:
≈3 min. Ask the class whether a plain keyword search would find this sentence.
It would not: no shared token between query and passage.

State the diagnosis precisely: this is not a bug in any particular search engine.
Any system that matches on symbols rather than on meaning will miss this pairing,
because the symbols genuinely do not overlap.
-->

---

## Matching symbols is not matching meaning

Exact-match search compares **strings**.

What a person means by a query is rarely the string they typed.

**Synonyms, paraphrase, and translation** all break a symbol match while leaving the
meaning untouched.

<!-- notes:
≈3 min. Land the reframing: the previous slide's failure generalises. Ask for one
more example from the class — a paraphrase in their own domain that a keyword
search would miss.

Do not resolve this yet. The session's answer is built up over the next six
sections; naming embeddings here would remove the reason to build the mechanism
carefully.
-->

---

## Text becomes a vector

<!-- notes:
Section divider. Plan §2. ≈13 min for this block, including a live demonstration.

This is the new mechanism the session introduces. Everything after it, from
similarity to indexing, presupposes this mental model.
-->

---

## One input, one fixed-length output

```
"The model can only work        [ embedding model ]      [-0.0175, 0.0323,
 with what is in its                  encoder        -->   0.0263, ...,
 context."                                                  -0.0091]

 any number of tokens                                    always the same length
```

An **embedding model** consumes a sequence of tokens — the same sub-word units from
Week 2 — and produces one fixed-length vector, typically several hundred to a few
thousand numbers, regardless of input length.

<!-- notes:
≈3 min. The diagram is the point: variable-length text in, fixed-length vector out.

Connect explicitly to Week 2: the input is still tokens, not raw text. Nothing new
happens at that stage. What is new is what comes out — one vector representing the
whole input, rather than a prediction for the next token.
-->

---

## Why the numbers mean anything

The vector is **not** arbitrary. The model is trained with a **contrastive
objective**: pairs of texts that share meaning are pushed toward nearby vectors;
unrelated pairs are pushed apart.

**"Nearby in this space" is a consequence of training, not an accident to be taken
on faith.**

<!-- notes:
≈4 min. This is the slide that prevents the rest of the session from sounding like
magic. State plainly: nothing about a neural network guarantees that meaning maps
to geometric closeness. That property exists because it was the explicit target of
training, using pairs of related and unrelated texts as supervision.

If asked what "related" means in training data: question-answer pairs, paraphrase
pairs, and translation pairs are typical sources. The specifics vary by model and
are not needed at this level of detail.
-->

---

## Two kinds of model

| | Consumes | Produces |
|---|---|---|
| **Generative model** | Tokens | The next token, repeatedly, producing text |
| **Embedding model** | Tokens | One static vector, once, for comparison |

**A generative model is read. An embedding is compared.**

<!-- notes:
≈3 min. This is the "embedding models versus generative models" distinction named
directly in the syllabus core list.

The comparison is deliberately one sentence per side. A generative model repeats
its core operation once per output token; an embedding model runs once per input
and stops. Neither is a restricted version of the other — they are built for
different jobs.
-->

---

## Our model, our numbers

```
cosine(relevant document, query)   = 0.7566
cosine(unrelated document, query)  = 0.6135
```

`python embedding_client.py`

<!-- notes:
≈4 min. Measured 2026-09-13 on `gemini-embedding-001`, using `embedding_client.py`
from the starter repository. Run it live.

The two documents: a sentence about context assembly (relevant to the query "what
does the model see?") and an unrelated sentence about baking bread. Both compare
against the same query.

The point is not that 0.61 looks low — cosine similarity for unrelated short
sentences from the same model is rarely close to zero, since general English or
Ukrainian sentences share considerable structure. The point is the **direction**:
relevant scores higher than unrelated, consistently, which is the property a
retrieval system depends on. Absolute thresholds are a tuning question for later;
relative ordering is the mechanism.
-->

---

## Measuring similarity between vectors

<!-- notes:
Section divider. Plan §3. ≈9 min.

Depends directly on the previous block and is the mechanism every later section's
ranking is built from.
-->

---

## Two ways to compare two vectors

**Euclidean distance** — the straight-line distance between two points. Sensitive
to each vector's **magnitude** as well as its direction.

**Cosine similarity** — the angle between two vectors, ignoring their length
entirely.

<!-- notes:
≈3 min. State both before arguing for one. Euclidean distance is the intuitive
case: literal distance in the space. It is not what this course uses, and the next
slide states why.
-->

---

## Cosine similarity, precisely

```
cosine similarity  =   A · B
                      -------
                     |A| · |B|
```

**Dot product, divided by the product of magnitudes.** Ranges:

- **1** — identical direction
- **0** — unrelated
- **−1** — opposite

<!-- notes:
≈4 min. Give the definition, then the reason to prefer it over Euclidean distance
as a consequence of that definition, not a rule to memorise: cosine similarity
discards magnitude and measures direction alone.

That matters because an embedding's magnitude can vary with properties such as
text length that have nothing to do with meaning, while its direction is exactly
what training made meaningful. Two vectors pointing the same way but of different
lengths are, for this course's purposes, the same result.

If the class asks why magnitude varies at all: it is a side effect of how the
network processes longer or shorter inputs, not a signal the training objective
targets. Direction is the trained signal; magnitude is not.
-->

---

## "Cosine distance"

Some vector stores report **distance** rather than similarity:

```
cosine_distance = 1 − cosine_similarity
```

**Smaller number, closer match.** The same quantity, inverted.

<!-- notes:
≈2 min. A terminology note, not a new concept. Students will meet both conventions
across different tools and should not be surprised by the inversion.
-->

---

## Choosing a model

| | `gemini-embedding-001` | `gemini-embedding-2` |
|---|---|---|
| **Multilingual** | not stated in the docs | **over 100 languages** |
| **Multimodal** | text only | **text, image, video, audio, PDF** |
| **Vector size** | 128–3072 | 128–3072 |
| **Input limit** | 2,048 tokens | 8,192 tokens |
| **`task_type`** | **supported** | not supported |

[ai.google.dev/gemini-api/docs/embeddings](https://ai.google.dev/gemini-api/docs/embeddings)

<!-- notes:
Section divider. Plan §4. ≈9 min.

The goal: students leave able to justify a choice of embedding model for their own
project rather than treat the default as unexplained.

Read the table as an engineering judgement rather than a feature list. The newer
model wins on four rows out of five — more languages, more modalities, four times
the context — and this course pins the older one anyway, on the strength of the
last row alone. Ask the class why before explaining it.

`task_type` is the query/document asymmetry this week teaches. It exists on `-001`
and not on `-2`, where the documentation says to put the task in the prompt instead.
A default that silently ignored the parameter would teach a mechanism the student's
own code did not implement, which is the whole reason for the pin.

Two honest qualifications. "Not stated in the docs" for `-001` means exactly that --
Google's page does not give a language count, but the course's own measurements run
on Ukrainian throughout and retrieve correctly, so treat it as multilingual on
evidence rather than on documentation. And the multimodal row is the one likely to
age this decision: syllabus §6 Week 3 lists multimodal embeddings as an optional
project extension, and `-2` is what would make that possible.

That extension is runnable now: `starter-repo/week3/multimodal_demo.py` embeds an image
and text captions with `-2` into one space and ranks them. Measured 2026-09-19, a
red-circle image scored 0.47 against "a red circle" and 0.26-0.30 against every
distractor. Worth showing on the projector for a minute if the class is curious;
it is not examinable.
-->

---

## Chunking a corpus

<!-- notes:
Section divider. Plan §5. ≈6 min.

Necessary infrastructure before the pipeline section, since chunk size is a
pipeline design decision rather than a detail of storage.
-->

---

## Why not embed the whole document?

One vector represents one document, however long. A 40-page corpus file and a
one-sentence answer would compress to the **same-sized description.**

**Retrieval needs to point at the part that answers the question**, not confirm
that the whole document is somewhat relevant.

<!-- notes:
≈3 min. The failure mode to name: a single embedding for an entire document can
only say "this document, broadly" is relevant. It cannot say which paragraph.
Retrieval requires addressing pieces, not whole files, which is the entire reason
a corpus is chunked before anything is embedded.
-->

---

## The chunk-size trade-off

**Too small** — a chunk loses the surrounding context that gave it meaning.

**Too large** — relevant material is diluted by unrelated text in the same chunk.

**Overlap** is a mitigation for information lost at a boundary, not a free
parameter to maximise.

<!-- notes:
≈3 min. State this as a genuine trade-off with no universally correct answer,
rather than a parameter with one right value. The practical asks students to
choose a chunk size for their own corpus and observe the effect, rather than
supplying one.
-->

---

## The retrieval pipeline

<!-- notes:
Section divider. Plan §6. ≈7 min.
-->

---

## Once, or on every call?

| Stage | When | Cost model |
|---|---|---|
| Ingest, chunk, embed, store | **Once** | Paid once, ever |
| Embed the query, search the index | **Every call** | Paid on every question |

<!-- notes:
≈3 min. Name this explicitly rather than let it pass as an incidental detail: Week
2's "changes every call versus never" table for context assembly is the identical
idea. Static work is done once and can be reviewed; dynamic work runs per call and
is where cost and correctness bugs actually live.
-->

---

## The whole path, end to end

```
INGEST (once)
  corpus --> chunk --> embed --> store in a vector index

QUERY (every call)
  question --> embed --> search the index --> ranked chunks
```

<!-- notes:
≈4 min. Walk this left to right. Everything above the line runs once, when the
corpus changes. Everything below runs for every question a user asks.

This diagram is the skeleton the practical builds in code this week.
-->

---

## Where the vector index actually lives

| | Examples | What you get |
|---|---|---|
| **Dedicated vector databases** | Chroma, Qdrant, Weaviate, Milvus | Built for this one job — persistence, metadata filtering, an API |
| **General databases, vector added** | PostgreSQL + `pgvector`, Redis, Elasticsearch, MongoDB | Vectors beside the data you already hold; one system to operate |
| **Index libraries** | FAISS, `hnswlib` | The search algorithm alone — no server, no persistence, no API |

<!-- notes:
≈4 min. The purpose of this slide is that students choose a store for their own project
rather than adopting this course's default without examining it. Keep this one to the
taxonomy; the next slide unpacks HNSW, and the one after takes the middle row in detail.

Give a decision heuristic rather than a ranking: start from the data platform the
project is already committed to. A project already running PostgreSQL should reach for
`pgvector` before adding a second system to operate. A project with no database at all
and a corpus that fits in memory does not need a server in the first place.

State plainly why this course uses Chroma: least operational overhead for a teaching
setting, runs in-process with no server to administer, and is positioned by its own
authors for prototyping rather than production scale. That is a reason, not an
endorsement, and a student whose project outgrows it should say so in the Lab 1
discussion.

The last line is the one to land. These products differ operationally — durability,
filtering, who runs the server — far more than they differ mathematically, since most
build the same graph index over the same distance metrics. Point at the line students
already have in `vector_store.py`: `hnsw:space` is that algorithm named in their own
code, and the reason it must be set explicitly is the measured finding that Chroma's
unconfigured default is squared Euclidean rather than the cosine this course teaches.

Deliberately no benchmark figures on this slide. Published vector-database comparisons
are largely vendor-adjacent, and the numbers move between releases; a figure quoted
here would be wrong by the next offering.
-->

---

## The database you already may use

|                     | Vector search today                                                           |
| ------------------- | ----------------------------------------------------------------------------- |
| **SQL Server 2025** | Native `VECTOR` type and `VECTOR_DISTANCE()` — cosine, Euclidean, dot product |
| **MariaDB 11.7+**   | `VECTOR INDEX` using a modified HNSW; cosine or Euclidean                     |
| **Neo4j**           | `CREATE VECTOR INDEX`, cosine or Euclidean                                    |
| **DynamoDB**        | Native vector search; up to 4096 dimensions, with filtering                   |

<!-- notes:
≈4 min. Two points to land, and the second is the one that changes a student's design.

First: capability does not follow from a data type. MySQL Community can store a vector
and parse one from a string, and offers no distance function, no index, and no
nearest-neighbour query — so a project on MySQL that needs retrieval still needs
something else. MariaDB, its fork, ships a genuine `VECTOR INDEX`. Two databases that
look interchangeable on a CV are not interchangeable here, and reading the manual
rather than the announcement is the transferable lesson.

Second, and worth pausing on: **Neo4j is on this list.** The graph database this course
installs in Week 5 and uses for Lab 2 holds vector indexes natively, with the same
cosine metric taught today. A student whose project ends up on Neo4j can keep the
embeddings and the graph in one system rather than operating two, and Week 6's
vector-versus-graph comparison can then be made inside a single database rather than
across two. Do not develop it here — Week 5 introduces the database and Week 6 makes
the comparison — but name it, because students who have already chosen Chroma should
know the option exists before Lab 2.

Dates, for the instructor rather than the slide: SQL Server 2025 reached GA in November
2025, with its DiskANN approximate index still in preview at that point; MariaDB added
vector indexes in 11.7; DynamoDB's vector search reached GA in August 2026, six weeks
before this deck was written. This row of the landscape moves faster than any other
material in the course. Re-check every entry before each offering, and expect at least
one to have changed.

No benchmark figures here either, for the reason given on the previous slide.
-->

---

## Why a ranked list is not an answer

<!-- notes:
Section divider. Plan §7. ≈12 min.

The pivot of the session. Everything up to here produced a ranking; nothing has
produced prose. State that plainly rather than letting generation arrive as an
obvious next step nobody had to argue for.
-->

---

## What the pipeline actually returns

```
QUESTION:  "What is assessed in Lab 2, and what is it worth?"

RETURNED:
  [0.81]  "Lab 2 marking: graph model quality 20%, Neo4j/Cypher..."
  [0.74]  "Lab 2 - Knowledge graph and Graph RAG - due end of Week 7..."
  [0.52]  "Lab 3 marking: agent correctness 25%, tool schema..."
```

A ranked list of chunks. **Nobody asked for this.** They asked a question.

<!-- notes:
≈3 min. Put the question and the output side by side and let the mismatch stand for
a moment before naming it.

The list is not a failure — it is exactly what the previous six sections set out to
build, and the third result being wrong is normal rather than a defect. The point is
narrower: a ranking is the input to what the user wanted, not the thing itself. No
part of this session so far produces a sentence.
-->

---

## Week 2's template, one slot now filled by software

```
SYSTEM      standing rules            written once, by you
EXAMPLES    demonstrations            written once, by you
TASK        what to do                written once, by you
FORMAT      shape of the answer       written once, by you
SOURCES     the passages          <-- RETRIEVAL FILLS THIS, every call
QUESTION    what the user asked       supplied by the user
```

**This is the whole of RAG.** The rest of the template is unchanged from Week 2.

**RAG = Retrieval Augmented Generation**

<!-- notes:
≈4 min. This is the payoff slide of the session and should be presented as such.

Week 2 closed by naming the one block students could not automate: the sources, which
had to be pasted in by someone who already knew which passage answered the question.
Six sections of this session were spent building the thing that fills it.

Resist presenting RAG as a new architecture. It is one slot of a template the class
already wrote, now populated by a function instead of by hand. Students who believe
they are learning a framework will look for complexity that is not there.
-->

---

## The whole path, now with an answer at the end

```
INGEST (once)
  corpus --> chunk --> embed --> store in a vector index

QUERY (every call)
  question --> embed --> search --> ranked chunks
                                        |
                                        v
                              assemble into SOURCES
                                        |
                                        v
                            model --> grounded answer
```

<!-- notes:
≈4 min. The same diagram from earlier in the session with three boxes appended. Show
it as a continuation rather than redrawing it, so the class sees that retrieval was
always the larger part of the work.

Name what is cheap and what is not: ingestion runs once per corpus change, and the
query path runs per question and is what the user waits for.
-->

---

## Assembling the context is a design decision

| Decision | Why it matters |
|---|---|
| **How many chunks** | Every one is paid for on every call, and Week 2 measured that |
| **In what order** | Position affects what the model attends to |
| **Truncated how** | A token budget cuts something; choose what |
| **Numbered how** | `[1]`, `[2]` is what makes a citation checkable |

<!-- notes:
≈4 min. Each row is a decision the practical forces students to make in their own
code, so present them as choices with consequences rather than as configuration.

The first row connects directly to the token arithmetic of Week 2: retrieved chunks
are prompt tokens, they are billed on every call, and retrieving ten chunks where
three would do is a cost decision made by accident.

The last row is the prerequisite for the next slide. Without numbering there is no
mechanism by which an answer can be checked against its source.
-->

---

## Grounding is requested, not guaranteed

The system instruction and the exit clause from Week 2 are what keep the model inside
the supplied sources:

> *"Answer using only the sources given. If the sources do not answer the question,
> reply exactly: not stated."*

**This is a request. The model can still answer beyond its sources, and sometimes
does.**

<!-- notes:
≈5 min. The honest slide of the section, and the one that sets up Week 4.

Students have already seen both halves of this. In Week 2 they watched the exit clause
work, and they watched the same question without it produce a fluent, formatted, cited
answer that was invented. Nothing about retrieval removes that failure mode; retrieval
makes it less likely by supplying the fact, and grounding instructions make it less
likely again, but neither is a guarantee.

Do not resolve this. The unresolved version is the motivation for Week 4: the only way
to know how often the request is honoured is to measure it against a gold set, which
is why the gold set is due at the end of this week rather than later.
-->

---

## Due this week

**Ten representative queries, with expected properties, for your own domain.**

This is the **evaluation seed** — the gold set every later retrieval improvement
will be measured against, starting now rather than in Week 11.

<!-- notes:
≈2 min. State why this begins here rather than later: a later improvement can only
be measured against a gold set that already exists. Writing it after the fact
would let every claim of improvement go unchecked.
-->

---

