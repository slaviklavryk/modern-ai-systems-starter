# Week 2 · Practical — Assembling a context, one part at a time

**Session:** Week 2, session 2 of 2 (practical)
**Duration:** 90 minutes
**Syllabus reference:** `Modern_AI_Systems_Syllabus_v2.md` §6 Week 2
**Paired with:** `week-02-lecture-plan.md`
**Notebook:** `starter-repo/week2/context_lab.ipynb`, with helpers in `starter-repo/week2/context_lab.py`

**Guiding question:** What does each part of a context contribute, and what does it cost?

**Organising principle:** the lecture named the parts of a context; this session builds one.
Every topic in the lecture has a cell the students run themselves, and the central exercise
adds a single part per step so that each part's contribution is attributable rather than
asserted. The session is the counterpart to Week 1, which established that context changes
the answer: this one establishes which part changed it.

---

## 1. Tokens, measured on their own corpus

Students run `tokens.py` against text from the domain they proposed in Week 1 rather than
against the lecture's prepared table, and record the tokens-per-word figure their own
material produces. The section exists so that the Ukrainian cost premium stops being a
number on a slide and becomes a property of their project, which matters because every
budget in Weeks 4, 10 and 11 is derived from it. It opens the session because
`count_tokens` does not consume the generation quota, so the class can be exploratory here
in a way the rest of the session cannot afford, and because the students need a token
figure in hand before any argument about context cost will land.

## 2. The three counters, and what thinking costs

Students call the model a small number of times and read `usage_metadata` directly,
including the `thoughts_token_count` that has been in their terminal output since Week 1
without explanation. The section should produce two observations from their own runs: that
thinking tokens are present on prompts requiring no reasoning, and that the count differs
between identical calls, which is what prevents it from being budgeted by assumption. It
sits second because everything the remainder of the session does is measured against these
three numbers. Students run `thinking_levels.py`, which sends the same trivial task and the same
multi-step task at each of the four `thinking_level` values and reports what each cost.
They should leave able to state, from their own output, that the level below the task's
threshold produces a confident wrong answer and the levels above it purchase nothing. This
is the section to shorten or run once on the projector if the session is behind, since it
is eight calls per student against a six-per-minute ceiling and the conclusion survives
being demonstrated collectively.

## 3. Temperature

Students repeat Week 1's Experiment 5 under their own control, first at the default and
then with `temperature=0`. The `context_lab.ipynb` demonstration switches to a closed-form
question for the `temperature=0` comparison, since an open-ended one is not guaranteed to
converge: floating-point non-determinism in Gemini's batched serving can still select
different tokens even at `temperature=0` when several candidates are near-tied, as an
open-ended question invites (measured 2026-09-14 on `gemini-3.5-flash`). Students who try
`temperature=0` against the open-ended Week 1 question on their own should expect the same
variation, not a broken demonstration. The purpose is to convert the lecture's mechanical
explanation into an observation they have made, and the section is not finished when the
demonstration succeeds: it ends with each student naming the parts of their own proposed
system that require a value near zero, which is the judgement the lab work will actually
require of them.

## 4. The context ladder

This is the centrepiece and the longest section. Beginning from a bare question, students
add one part of a context per step — system instruction, task, sources, output format,
examples — and observe both the answer and the token count change at each step. The
question is the one Week 1's Experiment 4 could not answer, so the ladder ends by answering
correctly, with citations, a question that produced confident invention a week earlier. Two
properties of the exercise are load-bearing and should not be traded away for time: the
assembled context is displayed before every call, so that students see the string their own
code produced rather than a result attributed to the model, and the token count is shown
beside it, so that the cost of each added part is visible at the moment it is added.

## 5. Requesting a shape against constraining it

Students reproduce Experiment 3's intermittent failure — a prompt asking politely for JSON
— and then replace the request with `response_schema`, and confirm by parsing the result
rather than by inspecting it. The section exists because the difference between a prompt
and a configuration is the prerequisite for tool calling in Week 7, and because a class
that has only been told about the distinction will continue to write the prompt version.
The parse step is not decoration: a student who checks by eye will accept a code fence.

## 7. Where it goes wrong, and the exit clause

Students ask the grounded system a question their sources do not answer, and observe the
standing rule from section 4 produce a refusal rather than an invention. They then remove
the exit clause and ask the same question again. The comparison is the section: one line of
standing instruction is the difference between a system that reports insufficient
information and one that fills the gap, and students who have watched their own system fail
without it are the ones who will keep it in Lab 1.

## 8. What they leave with

The session closes by having each student save their completed ladder as the prompt
skeleton they will submit with Lab 1, and by confirming the Milestone 0 proposal is
submitted, since it is due at the end of this week and Week 3 opens ingestion and the gold
set. The section also states what the ladder does not yet contain — no tools, no memory, no
conversation history, and sources still pasted in by hand — which is the bridge to Week 3
and the reason the remaining nine weeks exist.

---

## Notes for the syllabus

Three items, recorded for reconciliation.

**The superseded in-class exercise is reinstated here.** `week-02-lecture-plan.md` records
that §6 Week 2's prescribed exercise — building a prompt up one component at a time — was
dropped from the lecture because the Week 1 practical had absorbed the discovery. Section 4
above reinstates it in the practical, in code rather than in discussion. This is not a
reversal of that decision: the lecture harvests the students' Week 1 notes and supplies the
anatomy, and the practical builds the thing. The syllabus entry should be amended to place
the exercise in the practical session.

**Call budget against the rate limit.** The session as planned is approximately twenty-five
generation calls per student against the confirmed six-per-minute ceiling (§11.1), which is
several minutes of unavoidable waiting. The notebook prints a running call count so the
constraint is visible rather than mysterious, and sections 6 and 3 are the designated
reductions. A practical of this shape is close to the ceiling of what the free tier
supports in ninety minutes, and Weeks 4 and 10 should be planned with that in mind.

**Structured output and the thinking dial are in this session.** Both are named as Week 2
core in §6, and both are currently absent from the lecture deck after a revision. Sections 5
and 6 above carry them. If the deck is not restored, the syllabus should record that these
two topics are taught in the practical rather than the lecture, because Week 7 tool calling
and Week 11 cost work both depend on them having been covered somewhere.
