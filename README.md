# Modern AI Systems — starter repo

Everything you need for Week 1. Later weeks add to this repo; nothing here gets
thrown away.

## Setup

Run these in order. **Start step 1 first and let it download while you do the rest.**

### 1. Clone somewhere with a SHORT path

```bash
cd C:\dev
git clone <STARTER-REPO-URL> modern-ai
cd modern-ai
```

**Windows: this matters.** Clone to something like `C:\dev\modern-ai`, **not** a deep
folder inside OneDrive or Documents. One of the notebook dependencies ships file paths
longer than Windows' 260-character limit, and installing from a deep folder fails with
an `OSError` that does not explain itself.

### 2. Python environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

About 30 packages, under a minute on a decent connection.

macOS / Linux: `source .venv/bin/activate`

Your prompt should now show `(.venv)`. If it does not, the next steps will fail
with import errors.

### 3. Your API key

Get one from [Google AI Studio](https://aistudio.google.com/apikey), signed in
with a **personal** Google account, in a Cloud project you created.

```bash
copy .env.example .env
```

Open `.env` and replace `your-key-here` with your key.

Then confirm it is not about to be committed:

```bash
git status
```

`.env` must **not** appear. If it does, `.gitignore` is missing or in the wrong
directory — fix that before continuing.

### 4. First model call

```bash
python hello.py
```

You should see `setup complete` followed by token counts.

### 5. The prompt lab

Open `prompt_lab.ipynb` in VS Code. When it asks for a kernel, choose the one in
`.venv`.

Run the cells **one at a time**, and fill in the ✍️ notes cell under each experiment.
The notes are the point of the session — we use them in the discussion at the end.

If you would rather not use a notebook, `python prompt_lab.py` runs a smoke test and the
helpers work the same from a plain script.

You will hit `429` if you run them all at once: the free tier allows about 6 requests
per minute. That is expected, and `ask()` reports it in plain language rather than
crashing.

### Later: Neo4j

`docker-compose.yml` is here and ready, but it is not needed until **Week 4**. Leave it
alone for now.

## Rules for the whole semester

**Keys never leave `.env`.** Not into a source file, a notebook, a screenshot,
or a chat message. If one leaks, revoke it in AI Studio *first* — deleting the
file in a later commit does not remove it from git history.

**Nothing personal, licence-restricted, or confidential** goes into a prompt or
a corpus. Free-tier prompts and responses are used to improve Google's products
and models.

**Do not create extra accounts to get around rate limits.** It violates the
terms, and a suspended account costs you your personal email too.

## Troubleshooting

| Symptom | Cause |
|---|---|
| `OSError` / "long path" during `pip install` | You cloned into too deep a folder. Move the project to `C:\dev\modern-ai` and recreate the venv |
| Notebook has no kernel, or the wrong one | In VS Code, click the kernel picker top-right and choose the interpreter inside `.venv` |
| `ModuleNotFoundError: prompt_lab` in the notebook | The notebook must be opened from inside the repo folder, next to `prompt_lab.py` |
| `ModuleNotFoundError` | The venv is not active — no `(.venv)` in your prompt |
| `KeyError: 'GEMINI_API_KEY'` | `.env` missing, misspelled variable, or `load_dotenv()` not called |
| `API key not valid` | Trailing space on the key, or the key belongs to a different Cloud project |
| `429 RESOURCE_EXHAUSTED` | Per-minute limit. It is a fixed window — wait a minute, do not hammer it |
| `503 UNAVAILABLE` | Transient server load. Just run it again |
| AFC warning on every call | Harmless SDK noise. Ignore it |
| Port 7474 or 7687 in use | Something else is running — usually Neo4j Desktop. Stop it, then `docker compose up -d` |
| Machine becomes unusable | Do not raise the heap caps in `docker-compose.yml`; they are low on purpose |

## What is here

```
requirements.txt     Week 1 dependencies, pinned
.env.example         Copy to .env and fill in
.gitignore           Keeps .env out of git
hello.py             Your first model call
prompt_lab.ipynb     The five Week 1 experiments — start here
prompt_lab.py        ask() and repeat(), used by the notebook
docker-compose.yml   Neo4j, pinned and memory-capped — not needed until Week 4
```
