---
title: Week 1 — Modern AI and the AI Software Stack
subtitle: Modern AI Systems · Lecture 1
footer: Modern AI Systems · Week 1
theme: light
---

# Modern AI Systems

*How do we build software that uses modern AI models as one component of a larger intelligent system?*

<!-- notes:
≈90 min. Run sheet in week-01-lecture-plan.md §3.

Open cold with the guiding question on screen. Take two or three answers from the
room before showing anything else — you want their current mental model out loud,
because most of the lecture is adjusting it.

Do not start with logistics. Start with the idea.
-->

---

## How did we get here?

<!-- notes:
Section divider. ≈15 min for this whole block — keep moving, this is the part most of
the room half-knows already.

The organising idea, which you should state before the slides: at every stage, ask
**what did "programming" mean?** That is the through-line, and it sets up the paradigm
shift later.
-->

---

## Classical Algorithm

Humans write the rules (code, program). The machine executes them.

```
if temperature > 38 and cough:
    diagnosis = "possible influenza"
```

**Programming meant:** writing the rules by hand.

<!-- notes:
≈3 min.

Worked where rules are knowable and few. Broke on anything with real-world variety —
the expert systems of the 1980s collapsed under the cost of maintaining rule bases.

Key failure: nobody can enumerate the rules for "is this a photo of a cat".
-->

---

## Machine learning

Humans supply labelled examples. The machine infers the rules.

**Example: is this email spam?**

- Show it 10,000 emails, each labelled `spam` or `not spam`
- For each one, count things a human picked in advance —
  *contains "free"?* · *number of exclamation marks* · *sender seen before?*
- The machine learns which combination of counts predicts the label

**Programming meant:** collecting labels, and hand-picking which counts to feed it.

<!-- notes:
≈4 min.

The shift from Classical AI: we stopped writing the *if/else* rules ourselves and
started supplying *examples of right answers* instead. The machine works out the rule
that fits them.

The catch, and the reason for the next slide: a human still had to decide in advance
which counts (features) were worth measuring. Nobody hand-designs "number of
exclamation marks" for a cat photo — that feature works for spam and nothing else.

This is called **feature engineering**, and for years it was most of the actual job.

Also: one model per task. This spam classifier knows nothing about sentiment, or cats,
or anything else. A new task meant starting over.
-->

---

## Deep learning

The machine learns the features too — not just the rule on top of them.

**Example: is this a photo of a cat?**

```
   pixels  →  edges  →  shapes  →  ears, whiskers  →  "cat"
```

Nobody wrote "detect an edge" or "detect a whisker." The network discovered that those
were the useful things to look for, on its own, from millions of labelled photos.

**Programming meant:** choosing an architecture and finding enough data — not deciding
what to measure.

<!-- notes:
≈4 min.

2012 onward. This is the one genuine leap in this slide's story: feature engineering,
the "most of the job" from the previous slide, mostly disappears. The network's early
layers learn to detect edges; later layers combine edges into shapes; later still into
parts like ears and whiskers; the last layer says "cat."

Say plainly: nobody programmed the edge detector. It emerged from data, because
detecting edges turned out to be a useful step toward the label.

Point at the diagram and note the shape of it — small pieces combining into bigger
ones — because next week's transformer slide and Week 3's embeddings both reuse this
same idea of "the machine finds its own useful representation."

But the economics did not change: still one model per task, still thousands of
labelled examples per task, still weeks of work before you know whether it works. A
cat-photo network knows nothing about spam.

This is the world most ML courses describe. The next two slides are why this course is
not that course.
-->

---

## Transformers, 2017

**Attention:** for each word, look at every other word in the sentence and decide
which ones matter most to it.

> *"The trophy didn't fit in the suitcase because **it** was too big."*
> What does *it* mean? Attention weighs *it* against every other word — *trophy*
> wins — and that is the mechanism, not a trick.

**And it does this for the whole sentence at once**, not one word after another —
which means training can happen **in parallel**, across many chips simultaneously.

Parallel training is what made scale affordable.

**This is the "T" in GPT** — Generative Pre-trained Transformer.

*Vaswani et al., "Attention Is All You Need," Google, 2017 — the paper that started it.*

[Interactive transformer visualisation →](https://poloclub.github.io/transformer-explainer/)

<!-- notes:
≈2 min. One slide, conceptual only. Week 2 revisits attention at the level we need.

Read the trophy/suitcase sentence aloud and ask the room what "it" refers to before
explaining anything. They resolve it instantly and unconsciously — that instant,
whole-sentence weighing of "which word matters to which other word" is exactly what
attention does mechanically. This is a classic ambiguous-pronoun example, chosen
because a human resolves it by holding the whole sentence in mind at once, which is
the same thing the model does.

The older approach (before 2017) read one word at a time, in order, each step waiting
on the one before it — like one person reading a queue of instructions aloud, word by
word. Attention removes that ordering requirement: since every word can already see
every other word directly, there is nothing forcing the words to be processed one
after another. That is what "trains in parallel" means concretely — many words, many
chips, all at once, instead of one long queue.

The point to land is not the architecture. It is that this parallelism removed the
sequential bottleneck in training, which made "just make it much bigger" viable for
the first time.

Spell out GPT while you are here, since half the room uses the word daily without
knowing what it stands for:

  **G**enerative — it produces new text, not just a label or a score
  **P**re-trained — trained once, in advance, on a general corpus, before it ever sees
  a specific task
  **T**ransformer — this architecture, the one on this slide

Worth one sentence: "GPT" started as OpenAI's name for their model family, and has
since become a generic word the way "hoover" did for vacuum cleaners — this course
uses "foundation model" or "LLM" for the general case and reserves "GPT" for OpenAI's
actual models.

The citation is worth a sentence too: this came out of Google, not OpenAI — Google
published the mechanism, OpenAI built GPT on top of it a year later. Small piece of
trivia the room tends to enjoy: the title is a pun on the Beatles' "All You Need Is
Love," which is part of why a paper title is still being quoted by name a decade on.

If there's time, pull up the interactive visualiser live — watching attention weights
light up on a real sentence lands the trophy/suitcase point better than the slide alone.
-->

---

## What is an LLM?

**L**arge — billions of parameters, trained on a huge slice of the internet
**L**anguage — it works on text
**M**odel — a function that predicts what comes next

**The core mechanic, in one line:** given the words so far, predict the most likely
next word. Then feed that word back in, and predict the next one. Repeat.

> "The capital of France is ___" → **Paris** (very likely), not *banana* (very unlikely).

<!-- notes:
≈2 min. The missing bridge between the last two slides — attention explains *how* it
weighs words against each other; this slide says *what it's doing that for*.

Walk the France example literally: the model isn't "looking up" Paris. It is scoring
every possible next word by how likely it is to follow everything before it, and Paris
scores far higher than any alternative. Do that scoring once, output the winner, append
it to the sentence, and do it again — one word at a time. A whole essay is this loop,
run thousands of times.

This is deliberately the *floor* of the explanation, not the full mechanism —
tokenisation, the actual probability distribution, and sampling parameters are Week 2.
Today's job is just: attention (previous slide) is the mechanism *inside* each
prediction; this next-word loop is *what it's repeatedly doing*; foundation model (next
slide) is what you get when this training recipe is scaled up enormously. Three
different questions, three consecutive slides, on purpose.
-->

---

## Foundation LLMs (Large Language Models)

Pretrain **once**, on an enormous **general corpus**. Adapt to a task by **describing the
task**, not by retraining.

GPT · Gemini · Claude · Llama — one model family, many tasks, no retraining.

**Model families**: Language · vision · audio · multimodal · **embedding

**Programming means:** constructing the **right context and asking the right question.**

<!-- notes:
≈3 min. This is the hinge of the lecture. Slow down here.

The names on the slide are the point made concrete: four different companies, four
different model families, all foundation models in exactly this sense — pretrained
once, then adapted by prompting rather than retraining. Say each is a *family*, not one
fixed model — this is deliberately the family name with no version number, the same
reason §4 of the syllabus names a tier rather than an ID. This course builds on
Gemini's Flash tier, but the concept and everything we build applies to any of them.

Trace the line back explicitly: hand-written rules → labelled examples → learned
features → described tasks. Each step moved work away from the developer and into the
model, and this last one moved it further than the others combined.

And note what the new job is. It is not gone — it moved. It is now about what goes
into the context window, which is the whole rest of the semester.
-->

---

## Why now?

- **Scale** — parameters, and the training runs to match
- **Data** — a usable fraction of the public internet
- **Compute** — GPUs cheap enough to make it thinkable
- **Pretraining** — general capability before any specific task
- **General-purpose models** — one model, many tasks
- **Accessible APIs** — a developer can use one this afternoon

<!-- notes:
≈5 min.

Ask the room which of these they think mattered most before you give an opinion.

The honest answer is that no single one was sufficient. Transformers existed for three
years before GPT-3 made the shift obvious.

The last bullet is the one that makes this a software engineering course rather than a
research topic. Ten years ago, using a state-of-the-art model meant being a research
lab. Now it is an API key — which they will have by the end of this week.
-->

---

## We are not building another ChatGPT

We are learning to build **software that uses a model like ChatGPT as one component**.

<!-- notes:
≈2 min. This single sentence sets expectations for the whole semester and heads off
the two wrong assumptions in the room: that this is a maths course about transformers,
and that this is a course about being good at prompting.

Neither. It is a software engineering course.
-->

---

## Where AI earns its place

> AI adds value where a problem involves **ambiguity, unstructured input, or natural
> human interaction** — not because it's available.

| Conventional | AI-powered |
|---|---|
| Keyword search | Semantic search |
| FAQ pages | Natural-language Q&A |
| Manually classified tickets | Automatic classification |
| Fixed document parser | Intelligent extraction |
| Manual summarization | Automatic summarization |
| Rule-based recommendations | Personalized recommendations |

<!-- notes:
≈4 min.

The principle first, before the table: ask the room *why* each right-hand column beats
the left. The answer is always the same shape — the left column needed the input to
already be tidy (an exact keyword, a ticket someone hand-labelled); the right column
copes when it isn't.

Two worked examples, if there's time for one:

**Support system.** A normal system: FAQ search, submit a ticket. AI adds:
natural-language Q&A grounded in the company's docs (RAG — Week 4), automatic ticket
classification and routing, conversation summarisation, suggested responses drawn from
past cases. Why it's worth it: users don't need to know the exact terminology or where
in the knowledge base an answer lives — the system understands intent and retrieves.

**Document processing.** A normal system: an employee retypes an invoice into a
database. AI-enhanced: OCR/document AI extracts text, an LLM identifies which fields
mean what, results are validated against business rules, ambiguous documents get
flagged for a human. A real invoice might resolve to:

    Supplier: ABC Ltd.        Total: $4,275.50
    Invoice #: INV-10482      Currency: USD
    Date: 2026-09-01          PO: PO-8391

Why it's worth it: documents are not laid out consistently. A traditional rule-based
parser breaks the moment the layout changes; an LLM copes with a much wider range of
formats without being reprogrammed for each one.
-->

---

## Where it doesn't

> Use AI where the rules are hard to state precisely. Use ordinary code where they're
> **exact, deterministic, and must be auditable.**

| Function | Better approach | Why not AI |
|---|---|---|
| Calculate a total | Code / database | Arithmetic must be exact |
| Validate a password | Regex / validation rules | The rules are already explicit |
| Process a transaction | Conventional business logic | Unpredictable output is unacceptable |
| Authenticate a user | Cryptography + auth libraries | Must be deterministic and auditable |
| Sort records | Database `ORDER BY` | Exact, and already fast |
| Enforce permissions | RBAC / ABAC rules | Access decisions must be explicit |

<!-- notes:
≈4 min.

The full list this table is trimmed from also covers: checking a date is valid (standard
library, no reasoning needed), calculating tax from a known formula (AI can introduce
inconsistent results where none is acceptable), a simple threshold check (an `if`
statement, not a model), storing structured data (a database, not an LLM).

**The example that lands best: one system, both columns at once.** An online shop —
AI is genuinely useful for recommending products, understanding natural-language
search, generating descriptions, answering questions, catching unusual purchase
patterns. But nobody wants AI deciding the final price.

Circle back to the very first slide's central question here: *one component of a larger
system.* This is the whole point stated concretely — a real system is both columns at
once, and the engineering judgement is knowing which parts are which.
-->

---

## What this course is, and is not

| Not this course                             | This course                  |
| ------------------------------------------- | ---------------------------- |
| Building neural networks, custom ML systems | Using existing LLMs          |
| Training foundation models                  | Using them as components     |
| AI-powered development                      | AI-powered software          |

<!-- notes:
≈3 min.

The "not" column matters as much as the "is" column. Several students will have
expected the left-hand side and should know now.

If asked "will we learn how transformers work?" — conceptually in Week 2, in one
slide, and that is all we need to build with them.
-->

---

## Course mechanics

- **12 weeks** · two sessions a week — one lecture, one practical
- **One semester project**, grown across the whole course
	- Make this worth putting in your CV
- **Four graded deliverables**, not weekly homework
- No exam

<!-- notes:
≈2 min. Keep this brisk — details are in the syllabus and they can read.

Emphasise the project is *one* project. Everything they build in Lab 1 is what Lab 2
extends. Choosing badly in Week 1 is expensive; that is why the practical session has
a domain clinic.
-->

---
## Assessment

| Deliverable                         | Due     | Points |
| ----------------------------------- | ------- | -----: |
| Lab 1 — Vector RAG                  | Week 4  |     20 |
| Lab 2 — Knowledge graph / Graph RAG | Week 7  |     25 |
| Lab 3 — Agent, tools, memory        | Week 10 |     35 |
| Final integrated project            | Week 12 |     20 |
Passing score: 51
<!-- notes:
≈2 min.

Point out the spacing: four weeks, three weeks, three weeks, two weeks. Lab 2 is the
hardest and has been given room deliberately.
-->

---

## AI assistance is OK

Using coding agents and assistants on this course is **permitted.

1. **Disclose it** — a short note in every README
2. **Own it** — you can explain any line you submit
3. **Know the boundary** — writing your pipeline with an agent is fine; not
   understanding your own retrieval is not

<!-- notes:
≈3 min.

This is a course about building with these tools; pretending otherwise would be
incoherent. Say that.

The honest framing: condition 2 is the real one, and the oral walkthrough is where it
is checked. Undisclosed use, or inability to explain your own work, goes through normal
academic integrity procedure.

Expect a question about "how much is too much" — the answer is there is no percentage,
there is only whether you can explain it.
-->

---

## Context - a demonstration

Same model. Same question. Twice.

> In the Modern AI Systems course, what is assessed in Lab 2, and what is it
> worth?

<!-- notes:
Section divider. ≈15 min for the demo — the anchor of the session. Protect this time;
if you are running late, cut the history block, never this.

Full script in week-01-lecture-plan.md §4. Recording is ready if the live call fails.
-->

---

## Round 1 — no context

Most likely outputs:
1. Could not locate the details of what you're asking.
2. Searched and found something similar on the Internet and provided an answer.
3. Replies "I don't know" (less likely).

<!-- notes:
≈4 min.

Run it live. Do not editorialise while it generates — let the room read it.

Then ask: *how would you know this is wrong?* Sit in the silence. The answer is that
from the text alone, you could not. It invented a plausible course.

Do not call this a bug yet. That is the next slide, and it is worth its own beat.
-->

---

## Round 2 — with context

Paste the Lab 2 section of the syllabus into the prompt. Ask again.

Correct. Specific. **Quotable.**

<!-- notes:
≈3 min.

Run it. Point out it now cites specifics — the 25% weight, the re-seedable ingest, the
measured comparison — because they were in front of it.

Then the three points, in this order:
  1. Same model, same weights, same question. Only the context changed.
  2. Round 1 was not a malfunction (previous slide — refer back).
  3. So the engineering question is the one on the next slide.
-->

---

## Which leaves one question

How does the right information get into that window — at the right moment, without a
human pasting it in by hand?

<!-- notes:
≈1 min. Ask it, then leave it hanging for a beat before the reveal slide.

Every remaining week of this course is an answer to this question.
-->

---

## So what is the developer's job now?

Not training the model.
Not writing the rules.

**Deciding what the model sees, what it can reach, what it may do, and what it
remembers.**

<!-- notes:
≈2 min. This is the thesis of the course in one slide.

Pause after it. This is the sentence you want them repeating in Week 12.
-->

---

## The rest of the semester

| Week | Mechanism |
|---|---|
| 2 | Shape the context by hand — prompting |
| 3–4 | Fetch text into it — retrieval and RAG |
| 5–6 | Fetch relationships into it — knowledge graphs |
| 7–8 | Let the model *act* and put results back — tools, agents |
| 9 | Carry it across sessions — memory |
| 11 | Find out whether any of it works — evaluation |

<!-- notes:
≈3 min.

The reveal: these are not six unrelated technologies. They are six mechanisms for
constructing context, which is why the syllabus calls context engineering the spine of
the course.

Say it: if you remember one thing from today, it is that this table is one idea, not
six.
-->

---

## The AI Application Stack

```
   ┌───────────────────────────────────┐
   │  Application  ·  interface, UX    │   
   ├───────────────────────────────────┤
   │  Orchestration  ·  agents, flows  │  
   ├───────────────────────────────────┤
   │  Context  ·  prompts, memory      │   
   ├───────────────────────────────────┤
   │  Knowledge  ·  vectors, graph     │   
   ├───────────────────────────────────┤
   │  Model access  ·  API / SDK       │   
   ├───────────────────────────────────┤
   │  Foundation model                 │   
   └───────────────────────────────────┘
```

<!-- notes:
≈5 min. Two lists, one slide, deliberately paired row-for-row: the stack layer on the
left, the weeks that build it on the right.

**Present it bottom-up, against the reading order of the diagram.** We start at the
foundation — given, not built, Week 1 is just learning to call it — and by Week 12 we
are at the top, a full application. The diagram's own shape does the work: bottom of
the image is the beginning of the semester, top of the image is the end of it.

Note we build every layer except the bottom one — the only layer most people think
about when they hear "AI."

The one row worth a sentence of caveat: **Context spans Weeks 2 and 9**, not because it
is revisited but because it is never *not* being built — prompting (Week 2) and memory
(Week 9) are both context mechanisms, just constructed at different points. This is the
same wrinkle the syllabus's own phase table has; do not over-explain it, one sentence is
enough.

Map the labs onto it too: Lab 1 finishes the knowledge layer, Lab 2 deepens it, Lab 3
adds orchestration. By the final project, all six layers are theirs.

Individual week-by-week topics (not just ranges) are on the earlier "rest of the
semester" slide if a student wants that level of detail — this slide's job is the shape
of the climb, not the roadmap.
-->

---
## Weekly topics

1. **Modern AI and the AI software stack** — history to foundation models; project domain selection
2. **LLMs, tokens, context, reasoning, prompting** — tokenization, structured output
3. **Embeddings and semantic search** — chunking, vector stores
4. **Retrieval-Augmented Generation** — RAG architecture, evaluation with a gold set → **Lab 1 due**
5. **Knowledge graphs and Neo4j for AI** — graph modeling, Cypher, vector vs. graph retrieval
6. **Graph RAG** — combining vector and graph retrieval, when Graph RAG is (un)necessary
7. **Agents, tools, and integration** — tool schemas, agent loop, MCP, prompt-injection/tool safety → **Lab 2 due**
8. **Agent architectures, skills, and workflows** — tools vs. skills vs. workflows vs. agents;
9. **Memory** — short/long-term, explicit/retrieved memory, failure modes
10. **Advanced agentic systems** — multi-agent patterns, architecture review → **Lab 3 due**
11. **Reliable AI systems** — evaluation methodology, LLM-as-judge, prompt injection, cost/rate limits
12. **Final AI systems** — integrated project, lab-fair demo → **Final project due**
---

## The semester project

```
Domain → Knowledge → Embeddings → RAG
       → Knowledge graph → Graph RAG → Tools → Agent → Memory
       → Evaluation → Complete AI system
```

Pick a domain **you actually care about.**

<!-- notes:
≈3 min.

Every practical session and every lab moves this one project forward. Nothing is
throwaway.

The "care about" part is not sentimental — it is a twelve-week commitment, and interest
is what carries them through Lab 2, which is the hard one.

You are not required to use every technique. Choosing deliberately, and justifying what
you left out, is assessed in the final project.
-->

---

## The domain gate — five criteria

1. An accessible text source of reasonable size
2. Identifiable entities
3. **At least three meaningful relationship types**
4. At least two plausible tool actions
5. Some per-user information worth remembering

<!-- notes:
≈4 min.

State plainly: this is an approval gate, not a formality. A proposal failing any
criterion gets redirected before Week 3.

Walk each one with the test question from the practical plan §5 — "name five entities",
"name three relationships as A —VERB→ B", "what would it *do*, not just answer".
-->

---

## A couple of domains that work

| Domain | Three relationships | A tool action | Worth remembering |
|---|---|---|---|
| A football club's history | `PLAYED_FOR` · `MANAGED` · `TRANSFERRED_TO` | *Compare two seasons' stats* | Your favourite club — personalise answers |
| A book series or game universe | `ALLIED_WITH` · `RULES` · `LOCATED_IN` | *Timeline up to book 3* | Which books you've read — never spoil book 4 |
| Your university's course catalogue | `PREREQUISITE_OF` · `TAUGHT_BY` · `PART_OF` | *Do I meet the prerequisites for X?* | Courses you've already completed |

<!-- notes:
≈3 min. Added so the clinic isn't the first time they see what "good" looks like.

Walk one row properly — the book/game universe tends to land best, because the memory
column is concrete rather than generic: "remember what you've read so it never spoils
you" is a reason a real person would want that feature, not a textbook example of
"personalisation."

Point out that the *source* differs across all three — a stats site, a fan wiki or the
books themselves, the university's own catalogue — but each one still produces real
entities and real verbs between them. That is the only thing the five criteria are
actually testing.

If a student's own idea doesn't fit any of these shapes, that is not automatically a
problem — but it is worth working through against the criteria in the clinic rather than
assuming it is fine.
-->

---

## Milestone 0 — Project Proposal

One page, due **end of Week 2**:

domain · intended users · the problem · candidate AI functionality · knowledge sources ·
**evidence against all five criteria**

> Lab 1 is not accepted without an approved proposal.

<!-- notes:
≈2 min.

Drafted in the practical session *this* week, with the criteria sheet in hand and me
circulating — so nobody writes it alone and discovers a problem in Week 6. Then a week
to write it up properly.

Be clear that the clinic is not merely drafting time: a domain is provisionally approved
or redirected on the day. The Week 2 deadline is for the written page, not for finding
out whether the domain works.

Graded as part of Lab 1. The last line is not a threat, it is a schedule fact: an
unapproved domain means Lab 1 has nothing to build on.
-->

---

## Before the practical session

- Create a **personal** Google account — not a university Workspace account
- Install Docker Desktop, VS Code, Python, Git
- Bring a laptop **and the charger**
- Come with two or three candidate domains in mind

<!-- notes:
≈2 min. Send this in writing too.

Personal accounts matter: Workspace admins can disable AI Studio per organizational
unit, and we are not debugging that in a 90-minute session.

A student arriving without Docker installed cannot be fixed inside the session — the
download is the slow part, which is exactly what the practical exists to get done on
university bandwidth.
-->

---

## Next session: we build the environment

Accounts · API keys · key hygiene · Docker · first model call · the domain clinic

<!-- notes:
≈1 min. Close here.

Preview Week 2 in one line: what a token actually is, what the context window really
costs, and why the model spent seven times more effort thinking than answering.

That last detail is a real measurement from this course's own account, and it makes
them curious. Save the number for Week 2.
-->

## The diagram we will keep returning to

```
              User
               ↓
        AI Application
               ↓
     Context / Orchestration
               │
   ┌───────────┼───────────┐
   ↓           ↓           ↓
Knowledge    Tools      Memory
   │        / Skills       │
   └───────────┼───────────┘
               ↓
              LLM
               ↓
            Response
```

<!-- notes:
≈2 min.

Today only the outline is real; the branches fill in week by week. Tell them it will
reappear most weeks and that by Week 12 it is their own architecture diagram.

This week: everything except User → LLM → Response is empty. That is the honest
starting point.
-->

---

