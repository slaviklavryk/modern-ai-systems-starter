# Week 2 · Lecture — LLMs, tokens, context, and prompting

**Session:** Week 2, session 1 of 2 (lecture)
**Duration:** 90 minutes
**Syllabus reference:** `Modern_AI_Systems_Syllabus_v2.md` §6 Week 2
**Deck:** `week-02-lecture.md`

**Guiding question:** What actually happens when we send a prompt to an LLM?

**Organising principle:** almost every topic in this session was encountered as an
experience in the Week 1 prompt lab. The session names those experiences rather than
introducing them. Delivered that way it is a discussion; delivered as new material it is
the densest lecture of the term.

---

## 1. Tokens

Students should leave understanding that the model operates on sub-word fragments rather
than words, and that the vocabulary is the frozen result of frequency counting over a
training corpus. That single mechanism accounts for several behaviours encountered later
in the course: Ukrainian text costing roughly a third more per page than English,
unreliable arithmetic, and exact identifiers fragmenting into many pieces. The section
opens the session because everything after it is measured in tokens, and because it is the
most unexpected material available this week.

## 2. How reasoning models emerged

The goal is to explain why a response now carries three token counters rather than two.
The section traces three stages: a plain model with visible input and output,
chain-of-thought as a prompting technique that produced reasoning the user had to request
and read past, and reasoning models in which that loop moved inside the model and became
hidden. Students should recognise that no new mechanism was invented, only relocated. It
sits directly after tokens because thinking tokens are a third category of the same unit,
and it depends on the Week 1 statement that a model predicts a token and repeats.

## 3. What thinking costs

This section makes an invisible cost visible, which is its entire purpose. Students should
leave knowing that reasoning tokens are billed at output rates, that output costs four to
five times input at every major provider, and that the count varies substantially between
identical runs. Measured figures from this course's own key belong in the deck rather than
here. The section is deliberately not a cost lecture, which is Week 11; it needs only to
establish that the cost exists and was present in their own Week 1 terminal output without
anyone noticing.

## 4. Temperature

Students should be able to explain that the model produces a probability distribution over
next tokens and that temperature rescales it before sampling, and should be able to
identify which parts of their own systems require a value near zero. The section exists to
resolve Week 1's Experiment 5, where the same prompt produced three different answers. The
principal risk is mystification: temperature must be presented as a mechanical control
rather than as creativity.

## 5. Building a good context

This is the longest section of the session and the one students will apply every week for
the remainder of the course. It establishes what the context window contains, that every
token in it is paid for on every call, that irrelevant material actively degrades an
answer, and then what a context is assembled from in practice. The concrete outcome is a
prompt skeleton the students can copy into Lab 1. The section should land the course's
central claim: almost every part of a context is placed there by software the developer
wrote, which is why the course uses the term context engineering rather than prompting.

## 6. Controlling what comes out

The goal is the distinction between requesting an output shape and constraining it.
Students saw a prompt asking politely for JSON fail intermittently in Week 1; this section
replaces that request with configuration, and states why the same mechanism is the
prerequisite for tool calling in Week 7. It also covers reasoning as an adjustable
setting, establishing that both under-supplying and over-supplying it are costly in
different ways.

## 7. Where it goes wrong

Students should leave able to name several distinct causes of hallucination and to
recognise that they require different remedies. The section exists to prevent the common
conclusion that hallucination is one undifferentiated defect awaiting a better model.
Absent context is addressed by retrieval, incorrectly retrieved material by better
retrieval and evaluation, and well-formed invention of citations and method names barely
at all. It closes by stating the honest position: no setting disables the behaviour, and
the available measures are grounding, constraint, an explicit exit clause, and
measurement.

## 8. Close

Milestone 0 is due at the end of this week, and the section states why the deadline sits
there: Week 3 opens ingestion and the gold set, after which a redirected student loses
completed work. The session then bridges to Week 3 by pointing at Experiment 4 —
supplying the source manually worked and does not scale.

---

## Notes for the syllabus

Three divergences from §6 Week 2, recorded for later reconciliation.

**The listed in-class exercise is superseded.** The syllabus prescribes building a prompt
up one component at a time. That exercise was moved into the Week 1 practical when that
session became a prompt lab, and repeating it would waste time and cover known ground.
This session harvests the students' existing notes instead.

**Next-token prediction is no longer new here.** Week 1's lecture gained slides covering
what an LLM is, attention, and foundation models during preparation. The syllabus's Week 2
core list still presents this material as new, and should be reworded so that only
training versus inference and learned representations remain.

**The demonstration figures are stale.** §6 Week 2 cites `prompt=1061 / thinking=252 /
answer=35`, measured on `gemini-flash-latest` before the course pinned
`gemini-3.5-flash`. Current measurements are in the deck's speaker notes.
