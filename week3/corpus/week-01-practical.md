---
title: Week 1 — Practical: First Calls and the Prompt Lab
subtitle: Modern AI Systems · Practical 1
footer: Modern AI Systems · Week 1 Practical
theme: light
---

# Week 1 — Practical

**Calling the model from Python, and finding out what a prompt actually does**

<!-- notes:
≈90 min. Run sheet in week-01-practical-plan.md §3.

Project this deck and leave it up. Students self-pace through the steps — do not try to
keep 25 people in lockstep. Print it as a handout too (Ctrl+P) so nobody is blocked
waiting for you to advance a slide.

Your job this session is to circulate, not to present.

Step timings sum to ≈88 min and are guidance, not a script. The prompt lab is the point
of the session; the setup steps exist to make it possible.

NOTE: Docker and Neo4j are deliberately NOT here. They belong to Week 5 and their setup
moves to the Week 4 practical — see week-01-practical-plan.md §9.
-->

---

## What you leave with today

- A working API key
- A Python script that calls a model and reads its token usage
- **Evidence, from your own experiments, that how you ask changes what you get**

<!-- notes:
≈1 min. Read the list, then start Step 1 immediately — the API key is the long pole.

The third item is the session's real content. Everything before it is plumbing.
-->

---

## Before anything: the corpus rule

Everything you send to the API is used to improve Google's products and models.

- **No personal data**
- **Nothing licence-restricted**
- **Nothing confidential**

<!-- notes:
≈3 min. Say this out loud; it is not a footnote.

Per §11.3: Ukraine is a supported region and the free tier is legitimate here, but the
paid-tier privacy exemption does **not** apply to us. Free-tier prompts and responses
are used for training.

This binds every prompt and every corpus all semester — including the project domain
they are about to choose. A student whose domain is their employer's internal
documentation has chosen wrong, and better to learn it now than in Week 4.
-->

---

## Step 1 — Cloud project and API key

1. Sign in to **Google AI Studio** with a **personal** Google account (or create new Google account)
2. Create a new Cloud project
3. Generate an API key in that project
4. Copy it somewhere temporary — you will move it in Step 3

<!-- notes:
≈17 min, and the highest-variance segment of the session. Start it first.

Not a university Workspace account: admins can disable AI Studio per organizational
unit, and we are not debugging that today (§11.1).

Quota is per **Cloud project**, not per key — extra keys in one project add nothing.
That is why everyone makes their own: 25 independent allowances rather than one shared
pool to exhaust.

TRIAGE: if a student stalls on phone or card verification, pair them with a working
neighbour so they can still do the prompt lab on that machine, and resolve the account
outside the session. Do not spend twenty minutes on one account while the room waits.
-->

---

## Step 2 — Python environment

```bash
cd C:\dev
git clone https://github.com/slaviklavryk/modern-ai-systems-starter.git modern-ai
cd modern-ai
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Clone somewhere with a short path.** Not inside OneDrive or Documents.

macOS / Linux: `source .venv/bin/activate`

<!-- notes:
≈6 min.

One prescribed approach for the whole course (§11.5) — plain `venv`, because it ships
with Python and there is nothing extra to install or fail today.

**The short-path warning is not fussiness — verified on this machine.** `ipykernel`
pulls in `jedi`, which ships files whose paths exceed Windows' 260-character limit. From
a deep folder the install dies with a bare `OSError` naming a django-stubs `.pyi` file,
which tells a student nothing. From `C:\dev\modern-ai` it installs cleanly in under a
minute. This machine has `LongPathsEnabled = 0`, and student laptops mostly will too.

Put "clone to a short path" on the board before they start. It costs one sentence now
and saves twenty minutes of triage.

If someone already uses uv or conda and it works, leave them alone.

Watch for: the prompt must show `(.venv)`.

REPO URL: contents are written and verified in `starter-repo/`; only the hosting URL is
outstanding.
-->

---

## Step 3 — Keys go in `.env`, never in code

```bash
copy .env.example .env
```

Then open `.env` and paste your key:

```
GEMINI_API_KEY=your-key-here
```

<!-- notes:
≈5 min.

Both `.env.example` and `.gitignore` are already in the repo; they are copying one and
trusting the other — but not before verifying it on the next slide.

The rule for the semester, stated once, plainly: **a key never appears in a source file,
a notebook, a screenshot, or a chat message.** Not even temporarily. Not even on a branch
you intend to delete.
-->

---

## Verify it before you continue

```bash
git status
```

`.env` must **not** appear in the output.

<!-- notes:
≈2 min. Make everyone actually run this.

If `.env` shows up, `.gitignore` is missing or in the wrong directory. Fix it here —
this thirty-second check is what prevents a leaked key in Week 6.

While you are here, the thing worth saying once: git history is permanent. A key
committed in one commit and deleted in the next is still in the first one, still in
every clone. So if a key ever leaks, **revoke it in AI Studio first** — the commit
cleanup is optional, the revocation is not.
-->

---

## Step 4 — Your first model call

```bash
python hello.py
```

```python
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Reply with exactly: setup complete",
)

print(response.text)
print(response.usage_metadata)
```

<!-- notes:
≈7 min. The moment the course becomes real — make sure everyone sees a response.

**The model tier, not a version.** We say Flash and pin the exact ID in the starter repo
only, because IDs moved 3.0 → 3.8 within a year (§4) — `gemini-2.5-flash`, this course's
original pin, was **retired for new API keys** partway through writing this material;
Google's own 404 named `gemini-3.6-flash` as the replacement. We settled on
`gemini-3.5-flash` instead: active, not a preview build, and — unlike the `-lite` tier,
which returns no `thoughts_token_count` at all — it keeps the reasoning-token behaviour
this demo needs. Pro returns 429 on the free tier, confirmed by probe — this course is
Flash-only.

**Re-verify this pin at the start of each semester.** A model that works today can 404
by the next offering, exactly as it did here.

**That second print line.** Have them find `thoughts_token_count`, then say nothing more
about it. Measured on this course's key, `gemini-3.5-flash`, two runs of this identical
prompt:

    prompt=7  thinking=102  answer=2
    prompt=7  thinking=71   answer=2

A hundred-plus, then seventy-one tokens of thinking to emit two tokens of output — on a
prompt with nothing to reason about. Same answer both times; invisible cost moved by
nearly a third between runs. Week 2 explains it, and it lands far better once they have
seen it on their own account. Do not explain it today.

**Pre-empt the noise:** the SDK prints an "automatic function calling (AFC) is not
recommended" warning on every call. It is unrelated to anything they did.
-->

---

## The prompt lab

<!-- notes:
Section divider. ≈24 min, and this is the session.

**Open `prompt_lab.ipynb` in VS Code.** Kernel picker, top right, choose the interpreter
inside `.venv` — that is the one step that trips people, so say it once to the room.

Five experiments, one per section, each followed by a ✍️ notes cell they fill in.
Putting the notes *in the notebook next to the output* is deliberate: asked to keep notes
in a separate file, most students will not, and the synthesis then has nothing to draw on.
Here the empty cell is staring at them under their own result.

Check a few notes cells as you circulate. "I changed the prompt and it got better" is not
a note; push for what specifically changed in the answer.

RATE LIMITS: the lab is roughly a dozen calls per student. At ~6 requests per minute
they will hit 429 if they run everything at once. That is fine and it is instructive —
`ask()` catches it and prints a plain-language message rather than a stack trace. Tell
them to expect it.
-->

---

## Experiment 1 — vague, then specific

```python
ask("Tell me about Lviv.")

ask("In exactly 3 bullet points, describe Lviv's Old Town "
    "for a first-time visitor who has one afternoon. "
    "No history lecture — what to actually do.")
```

<!-- notes:
≈5 min.

The first returns an essay. Measured while writing this: roughly a thousand words of
history, architecture, and cuisine, none of it asked for.

The second returns something usable.

The question to put to the room: *the model did not get smarter between those two calls.
So what actually changed?* Push past "the prompt was better" — what changed is how much
of the answer was determined by them rather than guessed by the model.
-->

---

## Experiment 2 — who is it for?

```python
ask("Explain what an API key is.")
ask("Explain what an API key is to a 10-year-old.")
ask("Explain what an API key is to a security auditor.")
```

<!-- notes:
≈4 min.

Same topic, three audiences, three genuinely different answers — vocabulary, depth, and
what each one chooses to leave out.

The point: audience is information the model does not have unless you supply it. With no
audience it does not refuse, and it does not ask. It picks one silently. Every unstated
thing gets filled in with a guess.
-->

---

## Experiment 3 — ask for a shape

```python
ask("List 3 risks of committing an API key to a public "
    "repository. Return ONLY a JSON array of objects with "
    "keys 'risk' and 'severity'. No prose, no code fence.")
```

Did you get exactly what you asked for?

<!-- notes:
≈4 min.

Often yes. Sometimes it wraps the JSON in a code fence anyway, or adds a sentence before
it — despite being told twice not to.

Both outcomes teach. If it complied, ask how they would *know* it complied without
reading it. If it did not, they have just met the reason Week 2 covers structured output
as a first-class feature rather than a prompting trick: asking politely for JSON is not
a guarantee, and code that parses the reply will crash on the day it is not.
-->

---

## Experiment 4 — something it cannot know

```python
ask("What is assessed in Lab 2 of the Modern AI Tools "
    "and Systems course, and what is it worth?")
```

Then paste a few lines of the syllabus in and ask again.

<!-- notes:
≈7 min. The most important experiment of the session — it is the lecture demo, now in
their own hands and on their own key.

Round one: fluent, specific, confident, invented. Ask them how they would have known it
was wrong if it had been about a course they had not taken.

Round two: correct, and it quotes the text.

Then the point, which they should say rather than you: **the model did not learn
anything between those two calls.** The only difference was what it could see.

Note the `ask` call in the file also instructs it to reply "not stated" if the text does
not answer. Worth pointing at: that instruction is the difference between a system that
admits ignorance and one that fills the gap. Week 4 makes it a requirement.
-->

---

## Experiment 5 — the same prompt, three times

```python
repeat("Name one interesting fact about graph databases.", n=3)
```

<!-- notes:
≈4 min.

The answers differ. Usually the token counts differ too, sometimes substantially.

This unsettles people, and it should. Every test they write for the rest of the semester
has to cope with a component that does not return the same thing twice — which is
exactly why Week 11 evaluates against a gold set of many queries rather than by eyeballing
one output.

Tie it back to Step 4 if they noticed the thinking tokens move between runs there: same
prompt, same answer, different invisible cost.
-->

---

## So what did you actually change?

Not the model. Not its knowledge.

**You changed what it could see when it answered.**

<!-- notes:
≈3 min. Close the block here, and make them do the work.

Go round the room and collect one line per student from their notes. Then sort what they
say into the categories without naming them first — instructions, audience, output shape,
source material, examples. They will have discovered most of the taxonomy Week 2 puts
names to.

Land it: every one of those five experiments changed the *context*, and nothing else. That
is the whole course in one sentence, and they now have their own evidence for it rather
than a claim from a slide.
-->

---

## The domain clinic

<!-- notes:
Section divider. ≈14 min, and the segment with the longest consequences in Week 1.

Protect this time. If you are running late, the prompt lab can lose an experiment —
this cannot be cut.
-->

---

## Pick a domain you actually care about

You will live with it for twelve weeks. Interest is what carries you through Lab 2.

<!-- notes:
≈2 min.

Push back on the safe-but-dull choice. A student who picks something to please you will
resent it by Week 7.

If they have no idea: a hobby, a field of study, a game, a sport, music, literature,
travel, a fictional universe. The requirement is structure, not seriousness.
-->

---

## Write evidence against all five

| # | Criterion | The test |
|---|---|---|
| 1 | An accessible text source | Point at it now. Is it legal to use? |
| 2 | Identifiable entities | Name five. |
| 3 | **Three relationship types** | Write them as `A —VERB→ B`. |
| 4 | Two plausible tool actions | What would it *do*, not just answer? |
| 5 | Per-user information worth remembering | What should it know about you next week? |

<!-- notes:
≈6 min of writing, then circulate for the rest.

Hand out the criteria sheet. They write in sentences, not in their heads — a domain that
fails criterion 3 looks fine until someone tries to write the arrows down.

Circulate the entire segment. This is the highest-value use of your attention in Week 1.
-->

---

## Criterion 3 is where domains die

`Einstein —DEVELOPED→ Relativity`
`Einstein —WORKED_AT→ Princeton`

Not: *"this article is about Einstein."*

<!-- notes:
≈4 min. Say the consequence out loud.

If the only relationships you can name are "is about" and "mentions", you do not have a
graph — you have a vector store with extra steps, and **Lab 2 becomes impossible.** You
would find out in Week 6, with no time to change.

That is the entire reason this clinic is in Week 1 rather than Week 5.

The usual fix is narrowing to a domain containing people, organisations, events, or
dependencies. Flat bodies of articles usually fail. Redirect on the spot — do not let a
failing domain leave the room with a provisional approval.
-->

---

## If the corpus fights you, drop it

Curated fallback corpora are available, **unpenalised**.

<!-- notes:
≈2 min. Offer this explicitly, more than once.

Sourcing, licensing, and cleaning a corpus can eat more hours than all the AI work in
Lab 1, and it teaches nothing this course assesses (§3.2).

Students will not ask — they will quietly burn a week and arrive at Lab 1 with nothing.
Say the word "unpenalised" out loud.
-->

---

## Before you leave

- [ ] Personal Google account and Cloud project created
- [ ] API key working — a real response, not just a key string
- [ ] `.env` holds the key; `git status` does not show it
- [ ] You can say what to do if a key leaks
- [ ] `hello.py` runs; you found `thoughts_token_count`
- [ ] All five experiments run, with notes on what changed
- [ ] Proposal drafted, with evidence against all five criteria
- [ ] **Domain provisionally approved, or redirected, by me**

<!-- notes:
≈3 min. Verified by you or a paired classmate — not self-reported.

The last line is the one that matters. A student leaving with an unchecked domain has
gained nothing from the clinic.
-->

---

## Due end of Week 2

**Milestone 0 — Project Proposal.** One page: domain, intended users, the problem,
candidate AI functionality, knowledge sources, evidence against all five criteria.

> Lab 1 is not accepted without an approved proposal.

<!-- notes:
≈2 min.

Be explicit about the two stages so the later deadline is not misread: their domain was
approved or redirected **today**. Next week's deadline is for the written page, not for
finding out whether the domain works.

Graded within Lab 1.
-->

---

## Troubleshooting

<!-- notes:
Section divider. Do not present these — jump to one when someone hits it, or point at
the printed handout.
-->

---

## `OSError` during `pip install`

You cloned into too deep a folder. Windows path limit.

```bash
cd C:\dev
git clone https://github.com/slaviklavryk/modern-ai-systems-starter.git modern-ai
```

Then recreate the venv.

<!-- notes:
Verified on this machine: `ipykernel` → `jedi` ships django-stubs paths past 260
characters, and with `LongPathsEnabled = 0` the install dies naming a `.pyi` file that
means nothing to a student.

Moving the repo is faster and safer than enabling long paths, which needs admin rights
and a reboot. Do not go down that road mid-session.
-->

---

## Notebook has no kernel

VS Code, kernel picker top right → the interpreter inside `.venv`.

<!-- notes:
The single most common notebook problem, and it looks like a broken install rather than
an unselected kernel. Say it to the room once before they open the notebook.

If `import prompt_lab` fails, they opened the notebook from outside the repo folder.
-->

---

## `ModuleNotFoundError`

Your prompt is missing `(.venv)`.

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

<!-- notes:
Installed into system Python while running inside the venv, or the reverse.
-->

---

## `KeyError` or `API key not valid`

- The variable in `.env` is not spelled `GEMINI_API_KEY`
- The key was copied with a trailing space
- `load_dotenv()` was never called
- The key belongs to a different Cloud project

<!-- notes:
The first two account for most of it.

The whole class uses one spelling — `GEMINI_API_KEY` — matching the starter repo.

For the trailing space, have them print `len(os.environ["GEMINI_API_KEY"])`; it is
invisible otherwise.
-->

---

## `429 RESOURCE_EXHAUSTED`

You have hit the per-minute ceiling: about **6 requests per minute**.

It is a fixed window, not a backoff. Waiting five seconds does nothing.

<!-- notes:
Measured directly on this course's account: 6 requests per minute, confirmed twice —
2026-09-03 on `gemini-flash-latest`, and again 2026-09-05 on `gemini-3.5-flash` after
the course switched off the rolling alias. Same ceiling both times; it looks like an
account-level limit, not a per-model one.

`ask()` catches this and waits 25s rather than crashing. Expect to see the message
during the prompt lab — it is not a mistake, it is the free tier.

On Pro: a 429 on the very first call is expected. Pro is not on the free tier. Use Flash.
-->

---

## `503 UNAVAILABLE`

> This model is currently experiencing high demand.

Not your fault, not your key, not your quota. `ask()` backs off and retries.

<!-- notes:
Hit repeatedly while building this session on 2026-09-04: six attempts and ~2 minutes of
exponential backoff before the call succeeded. Earlier the same day, first attempt worked.
Load fluctuates hard.

Distinguish it from the 429 explicitly, because they look alike and the responses differ:
**429 means wait for the minute window; 503 means the model is busy for everyone.**

If the room hits sustained 503s, do not let 25 students hammer it — pause the lab, run
one experiment together on the projector, and continue when it clears. See
week-01-practical-plan.md §8.
-->
