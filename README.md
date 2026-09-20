# Modern AI Systems — starter repo

Everything you need for Week 1. Later weeks add to this repo; nothing here gets
thrown away.

## Setup

Run these in order. **Start step 1 first and let it download while you do the rest.**

### 1. Clone somewhere with a SHORT path

```bash
cd C:\dev
git clone https://github.com/slaviklavryk/modern-ai-systems-starter.git modern-ai
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

### The layout

The material is organised by week. Run each week's commands from that week's folder,
and open its notebook from there too:

```
common/   shared across weeks — the provider client (llm_client.py)
week1/    hello.py, prompt_lab
week2/    tokens.py, thinking_levels.py, context_lab
week3/    chunking, embedding, the vector store, ingest, retrieval_lab, multimodal
```

Your `.env` stays at the repo root and is found from any week folder, so you fill it in
once. The full file list is at the bottom of this README.

### 4. First model call

```bash
cd week1
python hello.py
```

You should see `setup complete` followed by token counts.

### 5. The prompt lab

Open `week1/prompt_lab.ipynb` in VS Code. When it asks for a kernel, choose the one in
`.venv`.

Run the cells **one at a time**, and fill in the ✍️ notes cell under each experiment.
The notes are the point of the session — we use them in the discussion at the end.

If you would rather not use a notebook, `python prompt_lab.py` (from `week1/`) runs a
smoke test and the helpers work the same from a plain script.

You will hit `429` if you run them all at once: the free tier allows about 6 requests
per minute. That is expected, and `ask()` reports it in plain language rather than
crashing. If the limit becomes an obstacle rather than a minor wait, see
`LLM_CLIENT.md` — every notebook can be switched to run on Lightning AI instead with a
one-line change to `.env`, no code changes required.

### Week 3: the vector store

Chroma is where your embedded corpus lives.

**There is no Docker here, and no server to start.** `pip install` is the entire
installation. `vector_store.py` uses Chroma's `PersistentClient`, which runs *inside your
Python process* and keeps everything in a folder: SQLite for the metadata, plain files
for the vector index. The relationship is the same as SQLite against PostgreSQL — one is
a library your program calls, the other is a service you run and connect to. Chroma, as
this course uses it, is the library.

Do not confuse this with **Neo4j**, which arrives in Week 4 and genuinely does need
Docker. That is why `docker-compose.yml` has an entry for Neo4j and none for Chroma.

Chroma does also offer a server mode (`chroma run`, then `HttpClient`) and an official
Docker image. This course uses neither, and you do not need them for any lab.

Work from the `week3/` folder for everything below:

```bash
cd week3
```

**1. Install it.** With `.venv` active:

```bash
pip install -r requirements.txt
```

`chromadb` is in `requirements.txt`, so if you set up in Week 1 you already have it and
this is a no-op — run it anyway, it is safe to repeat. There is no model download and no
PyTorch; embeddings come from the API, so the install is small. On Windows the long-path
rule from step 1 still applies: if `pip` fails with `OSError` or "long path", your
project folder is too deep. Move it to `C:\dev\modern-ai` and recreate the venv.

Check it landed:

```bash
python -c "import chromadb; print(chromadb.__version__)"
```

**2. Embed your corpus, once.** Put your documents in a folder as `.txt` or `.md`, then:

```bash
python ingest.py corpus/
```

This is the slow step, and it is slow for a reason: embeddings are limited to about
**100 texts per minute**, counted per text rather than per request, so batching cannot
speed it up. A 3,000-chunk corpus takes roughly half an hour. `ingest.py` paces itself
and prints an estimate before it starts, so leave it running.

You only pay this once. The result is written to `week3/chroma/` and survives restarts,
reboots, and closing VS Code. That location is fixed relative to the code, so it does not
matter which folder you launched from — `ingest.py` and the notebook always agree.

**3. Use it.** From the `retrieval_lab.ipynb` notebook, or any script in `week3/`:

```python
from vector_store import VectorStore

store = VectorStore(name="chunks")        # opens what ingest.py built
print(store.count())                       # 0 means you have not ingested yet
for row in store.search("your question", n_results=5):
    src = row["metadata"].get("source", "?")   # which document it came from
    print(f'{row["distance"]:.3f}  [{src}]  {row["chunk"][:80]}')
```

`search()` returns `[{"chunk": str, "distance": float, "metadata": dict}]`, nearest first,
where `distance` is 1 − cosine similarity. The collection is created with
`hnsw:space="cosine"` deliberately — Chroma's default is squared Euclidean, which is not
the metric this course teaches.

**`metadata` is the provenance.** `ingest.py` records, for each chunk, the `source`
document it came from, its `chunk_index` within that document, and the `start_word` offset
— so an answer can cite where each passage came from, which is what Lab 1's grounded-
answer requirement wants. Chunks indexed before this existed return `metadata = {}`;
re-ingest with `--reset` to populate it.

**4. Re-ingest only when the chunking changes.**

```bash
python ingest.py corpus/ --chunk-size 300 --overlap 60 --reset
```

`--reset` clears the collection first. Use it when you change chunk size, because that
invalidates every boundary already stored. Without it, new chunks are added alongside
the old ones.

`week3/chroma/` is in `.gitignore`. Do not commit it — it is rebuildable, and it is large.

### Looking at what you stored

`search()` tells you what is *relevant to a question*. It cannot tell you what is
actually in the collection — which is what you need when a chunk boundary looks wrong or
a retrieved chunk is not what you expected.

**From Python.** This is the route to use, and the one the notebook uses:

```python
from vector_store import VectorStore

store = VectorStore(name="chunks")
print(store.count())          # how many chunks are indexed
print(store.collections())    # every collection at this path
for row in store.peek(3):     # the first few, without searching
    print(row["id"], row["chunk"][:80])
```

`collections()` is the one to reach for when `count()` returns 0 after a successful
ingest: the name you opened and the name you ingested under are almost certainly
different.

**From the terminal**, if you want to page through the whole collection rather than the
first few:

```bash
chroma browse chunks --path ./chroma
```

`chunks` is the collection name — the default used by both `ingest.py` and
`VectorStore`. You get a table of record IDs and documents: arrow keys to move, `Return`
to expand a cell, `s` to open a query editor, `q` to quit.

Two things to know. It starts a Chroma server behind the scenes pointed at your folder,
so it needs a real terminal — and that server can outlive the command, which is why a
second run sometimes reports the folder is busy. Quit with `q` rather than closing the
window, and if a later command complains the path is in use, end any stray `chroma`
process. `store.peek()` above needs none of this.

**There is no admin GUI in this course.** The ones that exist — chromadb-admin,
chroma-peek, VectorAdmin — all connect over HTTP and therefore need you to run and manage
a Chroma server. The CLI above covers the same need with nothing to set up.

**Do not edit `./chroma/chroma.sqlite3` by hand.** It opens in any SQLite browser, but the
schema is Chroma's own and the vectors live in separate binary files beside it. Look if
you are curious; change it and you will corrupt the index. Rebuild with `ingest.py`
instead.

### Optional: images and text in one space

Everything above compares text to text. `multimodal_demo.py` shows the step past that —
`gemini-embedding-2` maps an image and a sentence into the *same* space, so you can rank
captions by how well they match a picture:

```bash
python multimodal_demo.py photo.jpg "a cat" "a dog" "a red car"
python multimodal_demo.py                 # built-in shape demo (needs Pillow)
```

This is a different model from the one the practical pins — `gemini-embedding-2` is
multimodal but has no `task_type`, the trade-off on the "Choosing a model" slide. The
script calls the SDK directly rather than through `EmbeddingClient` for that reason, and
is a starting point for the multimodal project extension, not part of the core labs.

### Later: Neo4j

`docker-compose.yml` is here and ready, but it is not needed until **Week 4**. Leave it
alone for now.

## Slides

Every lecture and practical deck is published from this repository:

**https://slaviklavryk.github.io/modern-ai-systems-starter/**

They are ordinary web pages — no install, and they work on a phone. Inside a deck:
<kbd>→</kbd> next, <kbd>O</kbd> overview, <kbd>L</kbd> slide list, <kbd>S</kbd> speaker
notes, <kbd>T</kbd> light or dark, <kbd>F</kbd> fullscreen, <kbd>Ctrl</kbd>+<kbd>P</kbd>
to print a PDF handout.

The speaker notes are published too, deliberately. They carry the reasoning behind each
slide, the measured figures, and what the session was trying to achieve — useful when you
are revising something that made sense in the room and does not on paper.

### Publishing (instructor)

The site is the `docs/` folder on `main`, served by GitHub Pages. Decks are built from the
planning repository, not from here:

```bash
python publish_slides.py          # build every deck into starter-repo/docs/
python publish_slides.py --check  # list what would be published, write nothing
```

That regenerates `docs/index.html` from whatever decks exist, so publishing a new week is
one command plus a commit — there is no index to edit by hand. Then commit `docs/`.

One-time setup: **Settings → Pages → Source: Deploy from a branch → `main` → `/docs`**.
`docs/.nojekyll` is committed so Pages serves the files as-is rather than running Jekyll
over them.

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
| `ModuleNotFoundError: prompt_lab` (or `context_lab`, `chunking`, …) | Open the notebook from its own week folder, so it sits next to the modules it imports. `retrieval_lab.ipynb` reaches into `week2/` and `common/` via a path cell at its top — run that cell first |
| `ModuleNotFoundError` | The venv is not active — no `(.venv)` in your prompt |
| `KeyError: 'GEMINI_API_KEY'` | `.env` missing, misspelled variable, or `load_dotenv()` not called |
| `API key not valid` | Trailing space on the key, or the key belongs to a different Cloud project |
| `429 RESOURCE_EXHAUSTED` | Per-minute limit. It is a fixed window — wait a minute, do not hammer it. To stop hitting it altogether, see `LLM_CLIENT.md` |
| `503 UNAVAILABLE` | Transient server load. Just run it again |
| `ModuleNotFoundError: chromadb` | Week 3 dependencies not installed. `pip install -r requirements.txt` with `.venv` active |
| `store.count()` returns 0 | Nothing ingested yet, or you opened a different collection. `store.collections()` lists what is actually at that path |
| `chroma: command not found` | `.venv` is not active, or `chromadb` is not installed |
| `chroma browse` will not open the path | Something still holds the store: a notebook kernel, or a stray `chroma` server left by an earlier browse. Restart the kernel, and end any leftover `chroma` process |
| `chroma browse` shows "Failed to load records" | It needs a real terminal and a free port for the server it starts. Use `store.peek()` instead — it needs neither |
| `429` while embedding | You are embedding outside `ingest.py`, which paces itself. The limit counts texts, not requests: about 100 a minute. Wait a minute |
| Changed `--chunk-size`, results unchanged | You did not pass `--reset`, so the old chunks are still in the collection alongside the new ones |
| Ingest looks frozen | It is waiting out the per-minute quota. It prints how long it is waiting; a large corpus takes tens of minutes |
| Want to start the corpus over | `python ingest.py corpus/ --reset`, or delete the `week3/chroma/` folder |
| Looking for a Chroma container or `chroma run` | There is none. Chroma runs inside your Python process; only Neo4j uses Docker |
| AFC warning on every call | Harmless SDK noise. Ignore it |
| Port 7474 or 7687 in use | Something else is running — usually Neo4j Desktop. Stop it, then `docker compose up -d` |
| Machine becomes unusable | Do not raise the heap caps in `docker-compose.yml`; they are low on purpose |

## What is here

```
requirements.txt          Dependencies, pinned. Install once, covers all weeks
.env.example              Copy to .env (at the repo root) and fill in
.gitignore               Keeps .env and week3/chroma/ out of git
docker-compose.yml       Neo4j, pinned and memory-capped — not needed until Week 4

common/
  llm_client.py          Switches every notebook between Gemini and Lightning AI
  LLM_CLIENT.md          How that switch works, and what does and does not carry over

week1/
  hello.py               Your first model call
  prompt_lab.ipynb       The five Week 1 experiments — start here
  prompt_lab.py          ask() and repeat(), used by the notebook

week2/
  tokens.py              How text splits into tokens
  thinking_levels.py     How much reasoning a task actually needs
  context_lab.ipynb      Building a context one part at a time
  context_lab.py         ask(), show() and counttokens(), used by that notebook

week3/
  retrieval_lab.ipynb    Corpus to grounded answer, on your own material
  ingest.py              Embed a corpus once into week3/chroma/. Run this first
  embedding_client.py    Embeddings: Gemini (default) or OpenRouter
  chunking.py            Splitting a corpus into overlapping chunks
  vector_store.py        Dense retrieval, persistent Chroma, cosine
  multimodal_demo.py     Optional — image and text in one embedding space
```

Week 3 reuses `week2/context_lab.py`, and both weeks use `common/llm_client.py`; a short
path line at the top of the files that reach across folders makes those imports resolve
from any working directory.
