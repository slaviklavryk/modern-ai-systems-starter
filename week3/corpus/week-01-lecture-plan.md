# Modern AI Systems

**Session:** Week 1, session 1 of 2 (lecture)
**Duration:** 90 minutes **[ASSUMPTION: 90-minute slot]**
**Syllabus reference:** `Modern_AI_Systems_Syllabus_v2.md` §6 Week 1
**Paired with:** `week-01-practical-plan.md` (setup session, same week)

**Guiding question:**

> What changed in AI, and what does it mean for software developers?

---

## 1. What students leave with

By the end of this session a student can:

1. Say what the course is about in one sentence, and what it is *not* about.
2. Place foundation models in a historical line from classical AI, and name why the
   current boom happened rather than reciting that it did.
3. Explain the shift from *training a task-specific model* to *prompting a
   general-purpose model*, and why that changes the developer's job.
4. Name the layers of a modern AI application stack.
5. State what their semester project must contain to pass the Week 1 domain gate.

Contributes to outcome 1 (LLM principles). Assessed later via the oral walkthrough —
nothing in Week 1 is graded — the Milestone 0 proposal it sets up is due end of Week 2.

---

## 2. Topic budget

Per §5: **6–8 core topics plus one demonstration.** This session runs 6 core, 1 mention,
1 demo — deliberately at the low end, because Week 1 also carries course logistics and
the project pitch, which always overrun.

**Core**

1. Course structure, assessment, and the AI-use policy
2. The line from classical AI → ML → deep learning → transformers → foundation models
3. Why the boom happened: scale, data, compute, pretraining, general-purpose models, accessible APIs
4. Task-specific models versus prompting a general model
5. The modern AI application stack
6. The semester project and the domain approval gate

**Mention** (one slide, named and contextualised, not examinable in depth)

- Model families: language, vision, audio, multimodal, embedding

**Demo** — same model, different context (§4 below)

---

## 3. Run sheet

| Time | Segment | Notes |
|---|---|---|
| 0–10 | **Framing.** The central question; "we are not building another ChatGPT, we are building software that uses one as a component" | Set the tone: engineering course, not an ML theory course |
| 10–20 | **Course mechanics.** 12 weeks, two sessions a week, one semester project, four graded deliverables, weights, the oral walkthrough, the AI-use policy | Be explicit that AI assistance is *expected* but must be disclosed and explainable (§9.3) |
| 20–35 | **Historical line.** Classical AI → ML → deep learning → transformers → foundation models | Fast. The point is the shape of the curve, not dates |
| 35–45 | **Why now.** Scale, data, compute, pretraining, general-purpose models, accessible APIs | Land: *a single pretrained model now does many tasks depending on the context we give it* |
| 45–55 | **The paradigm shift.** Task-specific model vs. prompting a general model — what the developer's job becomes | This is the intellectual core of the session |
| 55–70 | **Demo: same model, different context** | §4. The anchor of the whole lecture |
| 70–78 | **The AI application stack**, and model families as a mention slide | Introduce the recurring architecture diagram (§10) — mostly empty, filled in weekly |
| 78–88 | **The semester project and the domain gate.** §3.1 criteria, stated as hard requirements | Students must leave knowing the five criteria |
| 88–90 | **Handoff to the practical session.** What to bring, what to do beforehand | See §7 |

---

## 4. The demo — same model, different context

One demo, run live, and it must be the same model both times. This is the seed of the
course's conceptual spine, so it is worth the fifteen minutes.

**Setup.** Ask the model a question about *this course* — something genuinely absent
from its training data:

> "In the Modern AI Systems course, what is assessed in Lab 2, and what is it worth?"

**Round 1 — no context.** The model produces something fluent, plausible, and wrong.
Do not editorialise yet; let the room read it. Ask: *how would you know this is wrong?*

**Round 2 — with context.** Paste the Lab 2 block from §6 Week 7 of the syllabus into
the prompt and ask again. Now it is correct, specific, and quotable.

**The three points to land, in order:**

1. Same model, same weights, same question. Only the context changed.
2. Round 1 was not a malfunction — the model did exactly what it does. It had nothing
   to work with and produced its best guess anyway. That is worth being afraid of.
3. Therefore the engineering question for the rest of the semester is: **how does the
   right information get into that window, at the right moment, without a human
   pasting it in by hand?**

Then name the answers as a preview: prompting (W2), retrieval (W3–4), graphs (W5–6),
tools (W7–8), memory (W9), evaluation (W11). Every one of them is a mechanism for
constructing context.

> The model can only work with what is in its context.

**Fallbacks.** Have a pre-recorded screen capture of both rounds ready (§11.4 — the
course plans around outages, and this applies to your own lecture). If the live model
is unavailable, the recording carries the point without loss.

---

## 5. Deliberately *not* in this session

Worth writing down, because the instinct is to cover it here and it belongs in Week 2:

- What a token is; tokenisation; context windows as a number
- What an LLM is mechanically; next-token prediction; transformers and attention
- Prompting *vocabulary* — named components, prompt structure, system/developer/user roles
- Generation parameters, structured output, reasoning/thinking budgets
- Hallucination as a topic in its own right

Note the one qualification: the **practical session this week does hands-on prompt
experimentation**, because it is the natural extension of this lecture's demo. That is
deliberate and it does not breach the split — the practical is purely empirical (*notice
that how you ask changes what you get*), while Week 2 supplies the anatomy and the
vocabulary. Do not pre-empt Week 2 by naming the components here.

Week 1 establishes *that* context determines output. Week 2 explains *what context is
made of and how to shape it*. Keeping the split clean is what stops Week 1 from
becoming the nineteen-topic lecture that §5 exists to prevent. If a student asks about
tokens, answer in one sentence and say "next week".

---

## 6. Materials and instructor prep

| Item | Status | Blocks |
|---|---|---|
| Slides for this session | Needed | §12 item 8 |
| Recording of the demo, both rounds | Needed | Insurance against an outage mid-lecture |
| Domain-approval criteria sheet (§3.1), one page per student | Needed | §12 item 7 — also used in the practical |
| Fallback corpora list, so it can be named aloud | Needed | §12 item 5 |
| Recurring architecture diagram, blank version | Needed | Reused every week |

The practical session later this week has harder dependencies (starter repo, compose
file) — see `week-01-practical-plan.md` §6.

---

## 7. Student handoff

**Before the practical session this week — do this, it is not optional:**

- Create a **personal** Google account (not a university Workspace account — §11.1),
  if you do not already have one you are willing to use for coursework.
- Install Docker Desktop, VS Code, Python, and Git if you have not already.
- Bring a laptop and the charger.

**Think about, do not write yet:** two or three candidate project domains. The
practical session includes a clinic to test them against the gate criteria.

**Milestone 0 — Project Proposal** is drafted in the practical session this week and
**due end of Week 2**. One page: domain, intended users, initial problem, candidate AI
functionality, knowledge sources, and evidence against each of the five §3.1 criteria.
Graded as part of Lab 1; **Lab 1 is not accepted without an approved proposal.**

The gate is two-stage (§3.1): the Week 1 clinic gives a provisional approval and
redirects failing domains immediately, so the later deadline costs nothing in safety.

---

## 8. Risks

| Risk | Mitigation |
|---|---|
| Logistics and the project pitch eat the lecture; the demo gets cut | The demo is the point of the session. If time is short, cut segment 3 (history) to five minutes — not the demo |
| Students treat the domain gate as a formality | State plainly that a domain without three real relationship types makes Lab 2 impossible, and they would discover it in Week 6 with no time to change |
| The room already knows the history and disengages early | Keep segment 3 fast and pivot to segment 5, which is the part they have not thought about |
| Live model call fails in front of the class | Pre-recorded demo, ready to play |
