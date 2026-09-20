---
title: Week 2 — LLMs, Tokens, Context, and Prompting
subtitle: Modern AI Systems · Lecture 2
footer: Modern AI Systems · Week 2
theme: light
---

# What actually happens when we send a prompt?

*Week 2 Lecture — tokens, context, parameters, and thinking*

<!-- notes:
≈90 min for the session. Run sheet: none. `week-02-lecture-plan.md` records the
intent of each section and nothing further, which is the format that plan follows;
the per-slide timings below are the only schedule.

The organising principle for this session: last week the students had the experiences,
and this week those experiences receive names. Almost every topic today corresponds to
an experiment they ran themselves in the prompt lab.

Delivered that way, the session is a discussion. Delivered as new material, it becomes
the densest lecture of the term.
-->

---

## Tokens

<!-- notes:
Section divider. Plan §1.

The goal of this block: students should leave understanding that the model operates on
sub-word fragments rather than words, and that the vocabulary is the frozen result of
frequency counting over a training corpus. That one mechanism accounts for Ukrainian text
costing roughly a third more per page than English, for unreliable arithmetic, and for
exact identifiers fragmenting.

The block opens the session because everything after it is measured in tokens.
-->

---

## The model does not see words

It sees **tokens** — fragments, from a fixed vocabulary.

[https://platform.openai.com/tokenizer](https://platform.openai.com/tokenizer)

<!-- notes:
≈3 min. Use one of:

  https://platform.openai.com/tokenizer          (also shows token IDs)
  https://tiktokenizer.vercel.app/
  https://huggingface.co/spaces/Xenova/the-tokenizer-playground

State explicitly that these use a different tokeniser from Gemini, so their counts will
not match the students' own `usage_metadata`. They serve to show the split. The figures
that apply to the students' work appear on the next slide.

The OpenAI tool additionally displays token IDs. Mention this briefly: it demonstrates
that a token is ultimately a row number in a lookup table, which the explanation of
sub-word vocabularies depends on.
-->

---

## Why tokens and not words?

**One token per word?** The vocabulary is a fixed table with one row per token. It cannot
hold every word, name, typo and identifier in every language. Anything absent becomes
*unrepresentable.*

**One token per character?** Nothing is ever absent, but sequences become long, and
attention compares every token with every other, so cost grows with approximately the
**square** of length.

<!-- notes:
≈3 min. Present this as a design problem with two evident answers, both of which fail.
The compromise appears on the following slide.

The per-word approach also wastes the table: `run`, `runs` and `running` would occupy
three unrelated rows sharing nothing.

The per-character approach also consumes model capacity on reconstructing that
c-o-n-t-e-x-t spells a word, before any reasoning can begin.

Remain at this level of detail. BPE internals and vocabulary sizes are unnecessary detail,
and nothing later in the course depends on them.
-->

---

## Sub-word pieces — the compromise

> Start from characters. Repeatedly merge the **most frequent adjacent pair** in a large
> training corpus. Stop when the vocabulary is full.

**Common sequences earned their own token. Rare ones did not.**

Nothing is ever unrepresentable, since anything unfamiliar is spelled out from smaller
pieces.

<!-- notes:
≈3 min. This is byte-pair encoding, although the mechanism matters more than the name.

The significant word is **frequent**. The vocabulary is the fixed result of a counting
exercise over a particular training corpus.

That single fact accounts for every row of the table on the following slide.
-->

---


## Our model, our numbers

```
                 chars  words  tokens  tok/word
  English           52     11      13      1.18
  Ukrainian         54     11      17      1.55
  Common word        7      1       2      2.00
  Rare word         28      1       6      6.00
  A long number     22      1      23     23.00
  An identifier     16      1       9      9.00
```

`python tokens.py "anything you like"`

<!-- notes:
≈4 min. Measured on `gemini-3.5-flash` using `tokens.py` from the starter repository.

Run this live and accept suggestions from the class. `count_tokens` does not draw on the
approximately 6 requests per minute generation budget: 10 calls completed in 2.1 seconds
with no rate limiting. It can therefore be called repeatedly without consequence.

The two sentences are the course's recurring statement, in English and in Ukrainian.

Three rows to identify, in this order:
  1. Ukrainian 17 against English 13. The same meaning and a near-identical character
     count produce 31% more tokens.
  2. The long number: 23 tokens for 22 characters, approximately one per digit.
  3. The identifier: `gemini-3.5-flash` divides into 9 tokens.

Return to the number row once the cause has been given. A digit sequence is rare in the
corpus, so it survives as many small pieces rather than one, and the model performs
arithmetic over those fragments rather than over a quantity. That is the mechanism behind
the unreliable arithmetic the students will meet later, and it is the same mechanism as
the Ukrainian and identifier rows rather than a separate defect.

Do not explain the cause yet. Allow the table to remain unexplained for a short period.
-->

---

## Three counters, not two

```python
print(response.usage_metadata)

prompt_token_count      = 7      # what you sent
thoughts_token_count    = 95     # ???
candidates_token_count  = 2      # what you got back
```

Two of these are self-explanatory. **The third requires an explanation.**

<!-- notes:
≈2 min. This slide opens the reasoning block by posing the question the next three slides
answer. Display it, ask the question, and move on to Stage 1 rather than explaining it
here.

The students saw this output in Week 1, Step 4, without explanation. Identify that: it has
been present in their terminal since last week and nobody asked about it.

The question to pose: a plain language model requires two figures to describe a call, and
this response requires three. What is the third one for?

This also connects the block to the preceding one. The section just completed established
what a token is; this establishes that there are three distinct categories of them.
-->

---

## Stage 1 — tokens in, tokens out

```
prompt ─────────────────────────▶ answer
 (in)                              (out)
```

Two counters. The whole transaction is visible.

**This is the model introduced in Week 1.**

<!-- notes:
≈2 min. Establish the baseline deliberately, since the contrast carries the lesson.

A single pass: the model predicts the answer directly, token by token, and everything it
produces is readable.
-->

---

## Stage 2 — "think step by step"

Asking a model to **reason before answering** improves its performance on difficult
problems.

*Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models,"
Google, 2022*

**The reasoning was ordinary visible output.** The user requested it, paid output rates
for it, and read past it to reach the answer.

<!-- notes:
≈3 min. arXiv 2201.11903.

Note the pattern: this originated at Google, as did the attention paper discussed last
week. Both mechanisms were published openly and subsequently built upon across the
industry.

The framing required for the next slide: chain-of-thought was a prompting technique. The
user was responsible for requesting it, and the reasoning obscured the answer.

Then pose the question and pause: if this reliably improves results, why require the user
to ask for it?
-->

---

## Stage 3 — the loop moved inside

```
prompt ──▶ [ internal reasoning ] ──▶ answer
 (in)        (thinking — hidden)       (out)
```

Three counters. The thinking is **absent from `response.text`**, billed at output rates,
and, unlike the prompting technique, **controllable**.

<!-- notes:
≈3 min. This resolves the sequence.

The formulation to deliver:

  Chain-of-thought moved from something the user types into the prompt to something the
  model performs independently and does not display. The mechanism is unchanged; its
  location and visibility are not.

Connect this to Week 1, which prevents the material from appearing to introduce new
machinery: last week established that a model predicts the next token, appends it, and
repeats. A reasoning model runs that same loop twice, once privately to reason and once
publicly to answer.

"Test-time compute" is the term for expending compute at answer time rather than during
training.
-->

---

## What it actually costs

Four runs. Identical trivial prompt — *"reply with exactly: setup complete"*:

```
prompt=7   thinking=71    answer=2
prompt=7   thinking=80    answer=2
prompt=7   thinking=95    answer=2
prompt=7   thinking=102   answer=2
```

**35–50× more thinking than answer**, on a prompt requiring no reasoning.

<!-- notes:
≈4 min. Measured on this course's key using `gemini-3.5-flash`. Run it live as well.

Three points, in order:

  1. These tokens are billed. They were present last week and went unnoticed.
  2. They are invisible by default; `response.text` contains none of them.
  3. The count varies by approximately one third between identical runs, so it cannot be
     budgeted by assumption.

Have a recorded run available. `503 UNAVAILABLE` responses are frequent enough on this
API to warrant their own troubleshooting slide in the Week 1 practical, and should not be
allowed to disrupt the central demonstration of the session.
-->

---

## Billed as output

| Provider | Input | Output |
|---|---|---|
| Gemini 3.8 Flash | $0.75 / 1M | **$3.75 / 1M** |
| Claude Sonnet 5 | $2 / 1M | **$10 / 1M** |
| GPT-4o | $2.50 / 1M | **$10 / 1M** |

Google's price list labels that column: *"Output price **(including thinking tokens)**."*

<!-- notes:
≈3 min. Open a price list during the session if connectivity permits:

  https://ai.google.dev/gemini-api/docs/pricing
  https://claude.com/pricing
  https://developers.openai.com/api/docs/pricing

Two observations:

Output costs four to five times input at every provider. This is the standard shape of
LLM pricing, and thinking tokens are billed as output.

Google states this explicitly. The other two providers do not mention reasoning tokens on
their pricing pages. State this: it repeats the lesson of the demonstration at a higher
level, in that the cost is absent from the response and largely absent from the
documentation. A developer who never inspects `usage_metadata` has little reason to
discover it before receiving an invoice.

If the class requests an order of magnitude: approximately 1,500 calls per student per
semester across 25 students is on the order of $10–15 of invisible reasoning at Flash
rates. The figure is small, which is why the cost goes unnoticed. Week 11 treats it as a
cost problem; today it requires only visibility.
-->

---

## Temperature — Experiment 5, explained

The model produces a **probability distribution** over next tokens. Temperature rescales
that distribution before sampling.

- **Low** → sharpened. The top candidate is selected reliably.
- **High** → flattened. Greater variety, greater risk.
- **0** → effectively always the most likely token.

<!-- notes:
≈4 min.

Re-run the students' Experiment 5 live, but not with the open-ended fact question. An
open-ended prompt leaves several near-tied candidate tokens at each step, and
floating-point non-determinism in Gemini's batched serving can still select different
tokens at `temperature=0` (measured 2026-09-14 on `gemini-3.5-flash`: two `temperature=0`
calls to "name one interesting fact about graph databases" returned different text). Use
a closed-form prompt instead, one with a single correct answer, such as an arithmetic
question. Run it three times at the default, then three times with `temperature=0`.

    config=types.GenerateContentConfig(temperature=0)

The conclusion: last week's observation that the model is not a function described
sampling, and sampling is adjustable. State the caveat explicitly if a student asks why
their own open-ended re-run did not converge; it is not a broken demonstration.

Keep the explanation mechanical. Avoid characterising temperature as creativity. It does
not make the model imaginative; it makes the model less likely to select its highest-ranked
candidate. Presenting it otherwise is the principal failure mode of this slide.

Then pose the engineering question: which parts of a Lab 3 system require this value near
zero? Classification, extraction and routing, and anything whose output will be parsed.
-->

---

## Building a good context

<!-- notes:
Section divider. **≈30 min, the longest block in the session, deliberately so.**

The preceding material covered mechanism: the nature of a token and the cost of
reasoning. This block covers material the students will apply every week for the
remainder of the course, and on which Lab 1 depends directly.

The sequence: what the window is, what it costs, what belongs in it, and a template that
can be copied.

This connects to Experiment 4. The syllabus extract the students pasted in was context,
assembled manually. This block concerns assembling it deliberately.
-->

---

## The context window is everything it can see

System instructions · your question · conversation history · retrieved documents ·
tool results · memory

**All of it, re-sent, on every call.**

<!-- notes:
≈3 min.

The re-sending is unexpected to most students. The model maintains no session. A
conversation functions because the entire history is transmitted on each turn, which is
also why extended conversations become slower and more expensive.

Connect this to Experiment 4: pasting in the syllabus was manual retrieval. Weeks 3 and 4
automate precisely that operation and nothing further.

State the constraint: the window is finite. When it fills, material must be removed, and
determining what to remove is the engineering problem the remainder of the course
addresses.
-->

---

## Context is not free

Every token in the window is **paid for on every call.**

- Longer prompt → higher cost, higher latency
- Irrelevant context is actively harmful, since it competes for attention

<!-- notes:
≈3 min.

Correct the assumption that a large window should simply be filled. This must happen
before Week 3, when the students build retrieval and are inclined to supply as much
material as possible.

The second point is the less obvious one and merits emphasis: additional context can
degrade an answer, because the relevant passage now competes with irrelevant material.
Week 4 addresses this properly as a RAG failure mode. Today it is sufficient to establish
that more is not better.

Long context against retrieval is an unresolved engineering trade-off, and students will
ask about it.
-->

---

## What a good context is assembled from

| Part | Changes | Built in |
|---|---|---|
| **System instructions** — role, standing rules | Never | Today |
| **Examples** — demonstrations of the task | Never | Today |
| **Tool definitions** — what it may call | Never | Week 7 |
| **Retrieved knowledge** — passages for *this* question | Every call | Weeks 3–4 |
| **Memory** — what is known about *this* user | Per user | Week 9 |
| **Conversation history** — what was already said | Per turn | Week 9 |
| **The request** — what the user asked | Every call | — |

> Only the lower rows change. Most of a context is determined once, by the developer.

<!-- notes:
≈5 min. This slide explains the purpose of the remainder of the course.

Read the right-hand column downwards: almost every row corresponds to a different week.
Retrieval, tools and memory are not separate subjects. They are different parts of this
one assembly, and each receives its own week because each is difficult to build well.

State this directly: the table is the syllabus.

Two points to develop:

- The "Changes" column is the engineering distinction. Static parts are written once and
  tested. Dynamic parts are assembled per call by code, and that code is what the students
  will spend the semester writing. An error in a static part is a typographical error; an
  error in the assembly produces a system that passes testing and fails in production.
- None of this is performed by the model. Every row is placed there by software the
  developer wrote. This is why the course uses the term context engineering rather than
  prompting.

If asked whether ordering matters: it does, to a measurable degree rather than as a matter
of preference. That is a Week 11 evaluation question.
-->

---

## Context template example

```
System     You answer questions about {domain} using only the
           sources below. If they do not answer it, reply
           exactly: not stated.

Sources    [1] {retrieved passage}
           [2] {retrieved passage}

Task       Answer the question using only the sources above.

Format     Three bullets maximum. Cite [n] after each claim.

Question   {whatever the user typed}
```

<!-- notes:
≈5 min. The most directly applicable slide in the session. Advise the students to
photograph it.

This is the preceding table instantiated. Work through it block by block, naming the part
each one represents.

This is the Lab 1 prompt skeleton. In Week 3 the `Sources` block ceases to be pasted
manually and is populated by retrieval, which is the only change. State this now, since it
presents retrieval as the automation of one block of a prompt the students already
understand rather than as a new subject.

Three details to identify:

- "using only the sources below" — without this instruction the model combines its
  training data with the supplied sources, and the two become indistinguishable.
- "reply exactly: not stated" — the exit clause from Experiment 4. A single line
  distinguishes a system that reports insufficient information from one that invents an
  answer.
- Numbered sources with "cite [n]" — this makes the answer auditable. A claim without a
  citation becomes visibly suspect, both to the user and to the tests written in Week 11.

Identify what is absent: no tools, no memory, no conversation history. This is the
smallest context that performs useful work, and the course spends ten weeks adding the
remainder.
-->

---

## The System block — the standing brief

Everything true of every call, written once by the developer and never per request:

- **Role and scope** — what the system is for, and what it declines to do
- **Standing rules** — use only the sources; cite every claim
- **Output policy** — format, length, and the exit clause
- **Tone and audience** — who reads the answer

**Not here:** the question, the retrieved passages, or anything else that differs between
one call and the next.

<!-- notes:
≈3 min. This expands the first block of the template on the preceding slide, and the first
row of the assembly table before that — the row whose "Changes" column reads *Never*.

The definition to give: the system instruction is the part of the context that does not
depend on what the user asked. If a line would have to be rewritten for the next question,
it is not a standing rule and belongs in the request.

The common error is placing per-request material here and regenerating the instruction on
every call. That defeats the static and dynamic distinction the assembly table
established, and it also defeats provider-side prompt caching, which requires a stable
prefix. Week 11 treats caching as a cost mechanism; today it is a reason to keep this
block fixed.

Note where the exit clause sits. "If the sources do not answer, reply: not stated" is a
standing policy rather than a property of any one question, so it belongs here rather than
in the user turn, and it then applies to every call the system makes.

The engineering consequence to state: a system instruction is written once and can be
reviewed and tested like any other artefact the developer controls. The remainder of the
context cannot be, since it is assembled at run time by code.

Then bridge to the next slide. This slide covers what the block contains; where it is
actually set is not the prompt text.
-->

---

## Zero-shot and few-shot

**Zero-shot** — describe the task, demonstrate nothing.
**Few-shot** — place several solved instances in the context before the request.

| | Cost | Appropriate when |
|---|---|---|
| **Zero-shot** | Lower | The task is stated adequately in a sentence |
| **Few-shot** | Higher, on every call | The rule, its edge cases, or the output format are awkward to state |

*A "shot" is one worked example. Three examples is 3-shot.*

<!-- notes:
≈3 min. The terms are introduced here because the students have used one of them without
the name. Every one of the five Week 1 experiments was zero-shot: each described a task
and supplied no example.

The misconception to address directly, since it is the common one: few-shot is not
training. No weights change, nothing is learned, and the examples are discarded with the
rest of the context when the call returns. They are ordinary context, re-sent and re-paid
for on every call. The standard term is *in-context learning*, and the word "learning" in
it is misleading.

That is also the cost argument. Three short examples are inexpensive. Twenty long ones are
a permanent addition to every request the system ever makes, which is the same point the
"Context is not free" slide established, applied to a technique that appears free.

If asked how many examples: more assists up to a point and then ceases to. The ordering of
the examples and the balance of categories among them both affect the result measurably.
That is a Week 11 evaluation question rather than a matter of preference.

Then bridge to the next slide, which is the worked instance: why demonstrating the rule is
more effective than describing it.
-->

---

## Examples beat descriptions

Describing the rule is difficult. Demonstrating it is straightforward.

```
Classify this support ticket.

  "card declined"        → billing
  "can't log in"         → account
  "app crashes on save"  → technical

  "invoice shows wrong VAT" →
```

**Decomposition:** request the outline first, then each section, rather than the whole
report at once.

<!-- notes:
≈3 min. These are the two components the students could not have discovered in Week 1,
since neither appeared in the five experiments.

The preceding slide defined the technique; this one is the instance. Attempting to state
in prose the rule separating those three categories is awkward, and a model reading such a
rule would have to infer the edge cases. Three examples accomplish it without explanation.
This is the highest-value technique for classification and extraction, which constitutes
most of what the Lab 3 tools will perform.

Note that the examples also fix the output format: one word, lower case, no sentence. That
requirement was never stated.

Decomposition. Long single-pass outputs lose structure. Several smaller calls each address
a limited task, can be checked individually, and fail visibly rather than subtly. The cost
is additional calls, which at approximately 6 requests per minute is a constraint the
students will encounter in Lab 3.

Both techniques are practised in this week's practical. Today the students need only know
that they exist.
-->

---

## Hallucination has causes

> **Hallucination** — a fluent, confidently stated claim that is not supported by the
> sources or by fact. It is indistinguishable in form from a correct answer, so it cannot
> be identified by inspecting the output alone.

| Cause                          | What it looks like                                                     |
| ------------------------------ | ---------------------------------------------------------------------- |
| **Nothing in context**         | Confident invention, as in Experiment 4, round one                     |
| **Wrong material retrieved**   | A fluent answer grounded in the wrong source                           |
| **Stale training data**        | Formerly true, no longer                                               |
| **Conflicting sources**        | One is selected, the conflict is not reported                          |
| **Plausible-shape completion** | A citation, URL or method name that appears correct and does not exist |
No setting disables hallucination.
<!-- notes:
≈5 min.

Give the definition before the table, and state what it does not say. It does not say the
model lied, and it does not say the model was mistaken in the way a person is mistaken.
The output is unsupported rather than dishonest, and the mechanism behind that is the
closing slide of this block.

The second sentence carries the weight. If a false statement announced itself, the problem
would be trivial. Every remedy on the next slide exists because it does not: grounding
supplies something to check the answer against, citation makes the check possible, and
measurement performs it over a sample.

Terminology, if it is raised: the word is contested, and *confabulation* is argued to be
the more accurate term since nothing is perceived. Answer in one sentence and continue.
The causes matter here; the label does not.

The final row is the one this audience recognises from experience, having encountered a
model inventing a library method that appears as though it should exist. Explain it
mechanically: the model has learned the shape of an API call, a DOI and a URL. Producing a
well-formed instance is precisely what next-token prediction performs well. Producing a
correct instance requires information the model was never given.

The reframing to establish: these are distinct problems with distinct remedies. Absent
context is addressed by retrieval in Week 3. Incorrectly retrieved material is addressed by
improved retrieval and evaluation in Weeks 4 and 11. Plausible-shape completion is barely
addressed at all, and requires verification against a genuine source.

Treating hallucination as a single undifferentiated defect is what leads people to expect
that a better model will resolve it.
-->

