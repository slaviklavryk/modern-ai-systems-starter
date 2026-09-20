# Week 1 · Practical — First calls and the prompt lab

**Session:** Week 1, session 2 of 2 (practical / laboratory)
**Duration:** 90 minutes **[ASSUMPTION: 90-minute slot]**
**Syllabus reference:** `Modern_AI_Systems_Syllabus_v2.md` §6 Week 1, §11
**Paired with:** `week-01-lecture-plan.md`
**Worksheet:** `week-01-practical.md` → `slides/week-01-practical.html`

**Terminology.** "Practical" is the weekly hands-on session. **Lab 1–3** are the four
graded deliverables (Weeks 4 / 7 / 10 / 12). Nothing here is graded except the
Milestone 0 proposal it sets up.

**Purpose in one sentence:**

> Every student calls a model from Python, proves to themselves that what they put in
> front of it changes what comes back, and leaves with a domain that will survive Week 6.

The lecture asserts that context determines output. This session is where they get the
evidence themselves, on their own key, rather than watching the instructor demonstrate it.

---

## 1. What students leave with

1. A personal Google Cloud project with a working API key.
2. `.env` in place, verified invisible to `git status`, and the rule for a leaked key.
3. A Python script that calls a model and reads its token usage.
4. **Notes from five prompt experiments**, in their own words.
5. A drafted Milestone 0 proposal and a provisional domain approval.

Contributes to outcomes 3 (use a foundation-model API from Python) and 4 (design prompts
and construct model context deliberately).

---

## 2. Before the session

**Instructor** — see §10. The starter repo is now hosted and linked; nothing left blocking this session.

**Students** — assigned at the end of the lecture:

- Personal Google account created (**not** a university Workspace account — §11.1).
- Python, Git, and VS Code installed.
- Two or three candidate project domains in mind.
- Laptop and charger.

Send this in writing too.

---

## 3. Run sheet

| Time | Segment | Notes |
|---|---|---|
| 0–5 | **Framing and the corpus policy** (§4) | Mandatory, not advisory. Binds the domain they are about to choose |
| 5–22 | **Google Cloud project + API key** | Start immediately; the long pole. Triage plan in §8 |
| 22–28 | **Clone and Python environment** | Two packages, short download. Watch for `(.venv)` in the prompt |
| 28–35 | **Key hygiene.** `.env` from `.env.example`, then verify with `git status` | §11.5. The `git status` check is what prevents a leaked key in Week 6 |
| 35–42 | **First programmatic call.** `hello.py`, and find `thoughts_token_count` | The moment the course becomes real. Do not explain the thinking tokens — Week 2 does |
| 42–66 | **The prompt lab.** Five experiments in `prompt_lab.py`; students record what changed each time | §5. **This is the session** |
| 66–69 | **Synthesis.** Collect one line per student; sort their observations into the taxonomy without naming it first | Lands the context idea from their own evidence |
| 69–83 | **Domain clinic.** Test candidate domains against the five §3.1 criteria; circulate and redirect | §6. Longest consequences of anything in Week 1 |
| 83–88 | **Checklist sign-off** and what is due | §7 |

---

## 4. The corpus policy — say it out loud, in this session

Not a footnote. Per §11.3, Ukraine is a supported region and the free tier is legitimate
here, **but the paid-tier privacy exemption does not apply** — free-tier prompts and
responses *are* used to improve Google's products and models.

Stated as a rule that binds every corpus and every prompt for the whole semester:

- **No personal data.**
- **Nothing licence-restricted.**
- **Nothing confidential.**

Also state, because they will think of it within twenty minutes: **creating extra
accounts to farm quota violates the terms**, and a suspended account costs them their
personal email as well as their coursework.

Repeat this in the Lab 1 brief.

---

## 5. The prompt lab

The centrepiece. Students work through **`prompt_lab.ipynb`** in VS Code — one experiment
per section, each followed by a ✍️ notes cell they fill in: **what I changed, what changed
in the answer, why I think it changed.**

A notebook rather than a script, deliberately: the notes cell sits directly under the
student's own output. Asked to keep notes in a separate file most will not, and the
synthesis then has nothing to draw on. `prompt_lab.py` keeps the `ask()` and `repeat()`
helpers so there is one copy of them, not two.

| # | Experiment | What it shows |
|---|---|---|
| 1 | Vague → specific | The model did not get smarter; the answer got more determined by them and less guessed |
| 2 | No audience → child → auditor | Unstated things are not queried, they are silently assumed |
| 3 | Demand a JSON shape | Asking politely for a format is not a guarantee — the setup for Week 2's structured output |
| 4 | **A question it cannot answer, then paste the source** | The lecture demo, in their hands. Confident invention, then grounding |
| 5 | The same prompt three times | It is not a function. Sets up why Week 11 evaluates against a gold set |

**Experiment 4 is the one that matters.** If time slips, cut 2 or 3 — never 4.

### The synthesis, and why it is not optional

Go round the room and collect one observation per student. Sort what they say into
categories *without naming them first*: instructions, audience, output shape, source
material, examples.

They will have reconstructed most of Week 2's prompting taxonomy from their own evidence.
Then land the sentence: every experiment changed **what the model could see**, and
nothing else.

### Division of labour with Week 2

Deliberate, and worth protecting:

- **Week 1 practical — empirical.** Notice that how you ask changes what you get. No
  vocabulary, no framework, no parameters.
- **Week 2 lecture — systematic.** Names the components, adds system/developer/user
  roles, generation parameters, structured output, and thinking budgets.

Week 2's in-class exercise (§6 Week 2) should build on these notes rather than repeat
them — the students have already done the "add one thing at a time" discovery, so Week 2
starts from their findings and supplies the anatomy.

### Rate limits are part of the lesson

The lab is roughly a dozen calls per student. At the measured ~6 requests per minute they
**will** hit 429. `ask()` catches it and prints a plain-language message instead of a
stack trace. Warn them; do not treat it as a fault.

---

## 6. The domain clinic

The proposal is an **approval gate**, not a formality (§3.1), and this session is
**stage 1**. The failure mode it prevents: a student picks a structureless domain, cannot
build Lab 2 in Week 6, and has no time left to change.

| # | Criterion | The question that tests it |
|---|---|---|
| 1 | An accessible text source of reasonable size | Can you point at it right now, and is it legal to use (§4)? |
| 2 | Identifiable entities | Name five. |
| 3 | **At least three meaningful relationship types** | Name them as `A —VERB→ B`. This is the one that fails. |
| 4 | At least two plausible tool actions | What would the agent *do*, not just answer? |
| 5 | Some plausible per-user information worth remembering | What should it know about the user next week? |

**Criterion 3 is where domains die.** A student who can only produce "X is about Y" and
"X mentions Y" does not have a graph — they have a vector store with extra steps.
Redirect on the spot: the fix is usually narrowing to a domain with people,
organisations, events, and dependencies in it rather than a flat body of articles.

**Circulate the whole segment.** A domain that plainly fails is redirected here, today —
do not let the Week 2 written deadline soften this into drafting time. The redirect is
the part that protects them.

**Escape hatch, offered without penalty:** two or three curated fallback corpora exist
(§3.2). Corpus work can consume more hours than all the AI work in Lab 1 and teaches
nothing the course assesses. Say "unpenalised" out loud — students will not ask, they
will quietly burn a week.

---

## 7. Definition of done

Verified by the instructor or a paired classmate, not self-reported.

- [ ] Personal Google account and Cloud project created
- [ ] API key generated and **working** — a real response, not just a key string
- [ ] `.env` holds the key; `.gitignore` covers it; verified with `git status`
- [ ] Student can say what to do if the key leaks
- [ ] `hello.py` runs; student located `thoughts_token_count`
- [ ] All five experiments run, with written notes on what changed
- [ ] Milestone 0 proposal drafted, with evidence against all five §3.1 criteria
- [ ] **Domain provisionally approved, or redirected, by the instructor**

**Due end of Week 2:** Milestone 0 — Project Proposal. Graded within Lab 1; **Lab 1 is
not accepted without an approved proposal.**

---

## 8. Risks and triage

| Risk | Mitigation |
|---|---|
| **Sustained `503 UNAVAILABLE`** — the model is busy for everyone | Measured 2026-09-04: six attempts and ~2 min of exponential backoff before one call succeeded; earlier the same day, first attempt worked. Load fluctuates hard. If the room is stuck, **stop 25 machines hammering it** — pause, run one experiment together on the projector, resume when it clears. `ask()` already backs off |
| Account creation stalls on phone or card verification | Pair the blocked student with a working neighbour so they still do the prompt lab; resolve the account outside the session. Do not spend twenty minutes on one account |
| A student's Google account is a university Workspace account | Admins can disable AI Studio per organizational unit. Personal account, no exceptions (§11.1) |
| Everyone hits 429 at once during the lab | Expected, and instructive. Per-student Cloud projects mean 25 independent allowances; `ask()` reports it in plain language |
| The prompt lab overruns and eats the domain clinic | Cut experiments 2 and 3, never 4. The clinic has semester-long consequences; an experiment does not |
| **`pip install` dies with an opaque `OSError`** | Verified: `ipykernel` → `jedi` ships paths beyond Windows' 260-character limit, and most laptops have `LongPathsEnabled = 0`. From `C:\dev\modern-ai` it installs cleanly; from a deep OneDrive/Documents folder it fails. **Put "clone to a short path" on the board before they start.** Moving the repo beats enabling long paths, which needs admin rights and a reboot |
| Notebook shows no kernel, or the wrong one | VS Code kernel picker → the interpreter inside `.venv`. Looks like a broken install but is not. Say it to the room once before they open the notebook |
| Students poke at prompts without recording anything | The ✍️ notes cells sit in the notebook directly under each result, which is why the lab is a notebook rather than a script. Still check a few as you circulate — "it got better" is not a note |
| Students pick a domain to please the instructor | The project runs twelve weeks; interest is what carries them through Lab 2. Push back on the safe-but-dull choice |

---

## 9. Notes for the syllabus

Two divergences from the canonical document, both needing reconciliation before the
remaining weeks are planned:

**Two sessions per week.** §1 still reads *"one lecture per week · four substantial labs
rather than a weekly lab."* The actual schedule is two sessions weekly. The four graded
deliverables are unchanged; there are now twelve practical sessions of supervised time
toward them.

**Docker and Neo4j have moved out of Week 1.** §6 Week 1 and §11.2 place the image pull
and `docker compose up` in this session. They are gone from it — Week 1 now teaches the
course's central idea instead of installing infrastructure for Week 5.

The §11.2 rationale does not disappear, though: *"a student discovering an un-pulled
image during an outage has lost the evening."* **Recommendation: move Docker setup to the
Week 4 practical.** Neo4j is taught in Week 5, so it arrives just in time, and early
October is still comfortably ahead of the winter outage season the argument is really
about. Needs adding to the Week 4 practical plan when that week is written.

---

## 10. Instructor prep and hard blockers

| # | Item | Syllabus ref | Blocking? |
|---|---|---|---|
| ~~1~~ | ~~Starter repo hosted.~~ **Done — pushed 2026-09-05.** `requirements.txt`, `.env.example`, `.gitignore`, `hello.py`, `prompt_lab.py`, `prompt_lab.ipynb`, README, all verified against the live API before pushing. Public at `https://github.com/slaviklavryk/modern-ai-systems-starter`, confirmed reachable logged-out. Clone URL is filled in everywhere it was a placeholder | §12 item 4 | No longer blocking |
| 2 | Domain-approval criteria sheet, printed, one per student | §12 item 7 | **Yes** |
| 3 | Fallback corpora, ready to name aloud | §12 item 5, §3.2 | Yes, for the escape hatch |
| 4 | Written setup instructions for Windows | §11.5 | Covered by the starter-repo README |
| 5 | Run all five experiments yourself once, on the day, to gauge current 503 load | §11.1 | No, but do it |
| 6 | `docker-compose.yml` — **done**, but no longer needed until Week 4 | §12 item 2, §11.2 | Not for this session |
