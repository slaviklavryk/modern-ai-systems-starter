"""Week 5 — extract a knowledge graph from chunks of text, with a schema.

    from extraction import extract, save_results, load_results
    rows = extract(llm, chunks)                          # chunks: [{"id", "text"}]

    python extraction.py --sample --provider lightning   # the ten sample chunks, 4 calls
    python extraction.py --all --provider lightning      # the whole corpus, 61 calls
    python extraction.py --all --per-call 10             # fewer, larger calls: see Cost
    python extraction.py --all --corpus ../my_docs       # any folder of .md/.txt files

The schema is the design (lecture, section 6)
---------------------------------------------
The classes `Mention`, `Relation` and `Extraction` below are the structured-output
schema. Their `type` fields are `Literal` types listing only the declared types,
so the model cannot return a type the design does not contain. Every mention and every
relationship carries the id of the chunk it came from: that id is what lets an
answer built on the relationship cite its chunk.

Cost, and what batching costs in quality
----------------------------------------
Several chunks go into each call (`per_call`). Fewer calls is cheaper, but the
model then reads more at once and finds less. Measured 2026-10-04 on the 183-chunk
corpus with openai/gpt-5-nano (the Lightning backend), extracting Topic, Tool and
Deliverable, BUILDS_ON, USES and ASSESSES:

    per call   calls   time    mentions   relationships   entities after resolution
       10        19    185 s      205           37                  172
        3        61    627 s      623          163                  388

The default is 3. `extractions/course_corpus.json` is the 3-per-call run and
`course_corpus_p10.json` the 10-per-call run, kept for that comparison. The
results are saved to a file, and every later step reads that file instead of
calling again.

Which model extracts
--------------------
`LLMClient` reads LLM_PROVIDER from .env; `--provider lightning` overrides it for
one run. The free Gemini tier allows only 20 generation requests per model per
day (measured 2026-10-04) as well as 6 per minute, which one full extraction of
even this small corpus exceeds, so extraction is the step to move to the second
provider. Every results file records the provider and model that produced it.

The command line saves progress after every call. If the model stays
unavailable through every retry (the free tier's 503s), it stops; run the same
command again and it continues from the first chunk not yet extracted.
"""

import datetime
import hashlib
import json
import pathlib
import sys
import time
from typing import Literal, Optional

from pydantic import BaseModel

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "common"))

from kg_model import ENTITY_TYPES, EXTRACTED_TYPES  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE / "extractions"

# Six requests per minute is one every ten seconds; the margin avoids the 429.
_MIN_SECONDS_BETWEEN_CALLS = 10.5

INSTRUCTION = """You extract a knowledge graph from chunks of course material.

Each chunk is introduced by its id in square brackets.

Return, as mentions, each with the id of the chunk it comes from:
- every Topic that a chunk discusses: a concept or technique the course teaches;
- every Tool that a chunk names: a specific software product, service, library
  or hosted model;
- every Deliverable that a chunk refers to: a graded piece of work, such as a lab.

Return also every relationship that a chunk states, with the id of that chunk:
- BUILDS_ON, from a Topic to a Topic it requires or depends on;
- USES, from a Topic to a Tool with which it is taught or done;
- ASSESSES, from a Deliverable to a Topic it assesses.

Rules:
- Use only the declared types.
- Extract a relationship only if the chunk states it. Do not add relationships
  that are merely plausible.
- Give every name in its canonical form: a short noun phrase, in the singular
  unless the term is normally plural.
- A chunk that discusses nothing of these kinds yields nothing."""


# The structured-output schema. The allowed labels are read from kg_model.py, so the
# design and the schema cannot disagree: tuple() of a dict gives its keys, and
# Literal[("Topic", "Tool", "Deliverable")] is the same as Literal["Topic", "Tool",
# "Deliverable"]. (An editor's type checker may flag these two lines, since it cannot
# see the values without running the code; Python and Pydantic accept them.)
EntityType = Literal[tuple(ENTITY_TYPES)]
RelationType = Literal[tuple(EXTRACTED_TYPES)]


class Mention(BaseModel):
    name: str
    type: EntityType
    chunk_id: str


class Relation(BaseModel):
    source: str
    type: RelationType
    target: str
    chunk_id: str


class Extraction(BaseModel):
    mentions: list[Mention]
    relations: list[Relation]


def instruction() -> str:
    """The system instruction sent with every call."""
    return INSTRUCTION


def _prompt(chunks: list[dict]) -> str:
    return "\n\n".join(f"[{c['id']}]\n{c['text']}" for c in chunks)


def _chunk_id(returned: str) -> str:
    """The id as the model returned it, without the brackets the prompt puts around it.

    The model sometimes copies `[week-01-lecture.md#22]` with its brackets (seen
    2026-10-04: 26 of one sample run's mentions), and an exact comparison then
    drops a correctly attributed mention as if its chunk were invented.
    """
    return returned.strip().strip("[]").strip()


def extract(llm, chunks: list[dict], *, per_call: int = 3, thinking: Optional[str] = None,
            verbose: bool = True, resume: Optional[dict] = None, on_call=None) -> dict:
    """Extract mentions and relationships from chunks, several chunks per call.

    chunks: [{"id", "text"}]. Returns {"mentions", "relations", "calls", "done"},
    where every mention and relation carries its chunk id, "calls" records the
    tokens each call spent, and "done" lists the chunks already extracted. A chunk
    id the model invents (one not in the call) is dropped and counted, since it
    could never be cited.

    `resume` is an earlier, unfinished result: its chunks are skipped. `on_call`
    is called with the result so far after every call, which is how the command
    line saves progress -- the free tier's 503s can outlast every retry, and a
    long extraction should not have to start again from nothing.
    """
    schema = Extraction
    system = instruction()
    out = resume or {"mentions": [], "relations": [], "calls": [], "done": [],
                     "dropped_unknown_chunk": 0}
    todo = [c for c in chunks if c["id"] not in set(out["done"])]
    last = 0.0
    for start in range(0, len(todo), per_call):
        batch = todo[start:start + per_call]
        wait = _MIN_SECONDS_BETWEEN_CALLS - (time.time() - last)
        if last and wait > 0 and llm.provider == "gemini":   # 6 requests/minute
            time.sleep(wait)
        last = time.time()
        result = llm.chat(_prompt(batch), system=system, schema=schema, thinking=thinking)
        ids = {c["id"] for c in batch}
        parsed = result.parsed
        for m in parsed.mentions:
            chunk = _chunk_id(m.chunk_id)
            if chunk in ids:
                out["mentions"].append({"name": m.name, "type": m.type, "chunk": chunk})
            else:
                out["dropped_unknown_chunk"] += 1
        for r in parsed.relations:
            chunk = _chunk_id(r.chunk_id)
            if chunk in ids:
                out["relations"].append({"source": r.source, "type": r.type,
                                         "target": r.target, "chunk": chunk})
            else:
                out["dropped_unknown_chunk"] += 1
        out["calls"].append({"chunks": len(batch), "seconds": round(time.time() - last, 1),
                             "prompt": result.usage.prompt_tokens,
                             "thinking": result.usage.thinking_tokens,
                             "answer": result.usage.answer_tokens})
        out["done"].extend(c["id"] for c in batch)
        if on_call:
            on_call(out)
        if verbose:
            c = out["calls"][-1]
            print(f"  call {len(out['calls'])}: {c['chunks']} chunks, {c['seconds']}s, "
                  f"thinking {c['thinking']}, answer {c['answer']} tokens")
    return out


def fingerprint(chunks: list[dict]) -> str:
    """A hash of every chunk id and text. If the corpus or the chunking changes, it changes."""
    h = hashlib.sha256()
    for c in chunks:
        h.update(c["id"].encode("utf-8") + b"\0" + c["text"].encode("utf-8") + b"\0")
    return h.hexdigest()[:16]


def save_results(results: dict, chunks: list[dict], path: pathlib.Path, **settings) -> None:
    """Save extraction results with what produced them, so a rebuild needs no API call."""
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"created": datetime.date.today().isoformat(), "chunks": len(chunks),
              "corpus_fingerprint": fingerprint(chunks), **settings, **results}
    path.write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")


def results_path(corpus: pathlib.Path) -> pathlib.Path:
    """Where a corpus's extraction is saved: extractions/<folder name>.json.

    The course's own corpus, week3/corpus, keeps the name of its shipped reference,
    course_corpus.json, so that another corpus can never overwrite it.
    """
    from kg_loader import CORPUS
    corpus = pathlib.Path(corpus).resolve()
    name = "course_corpus" if corpus == CORPUS.resolve() else corpus.name
    return RESULTS / f"{name}.json"


def load_results(path: pathlib.Path, chunks: Optional[list[dict]] = None) -> dict:
    """Read saved results. Given the current chunks, refuse results made from other ones."""
    record = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if chunks is not None and record["corpus_fingerprint"] != fingerprint(chunks):
        raise ValueError(f"{path.name} was extracted from different chunks than the corpus "
                         "now produces. Re-extract, or restore the corpus and chunk size.")
    return record


if __name__ == "__main__":
    import argparse

    from llm_client import LLMClient

    from kg_loader import CORPUS, SAMPLE_IDS, read_chunks

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sample", action="store_true", help="The ten sample chunks")
    group.add_argument("--all", action="store_true", help="The whole corpus")
    parser.add_argument("--corpus", type=pathlib.Path, default=CORPUS,
                        help="Folder of .md/.txt documents (default: week3/corpus)")
    parser.add_argument("--per-call", type=int, default=3, help="Chunks per call")
    parser.add_argument("--thinking", choices=["minimal", "low", "medium", "high"])
    parser.add_argument("--out", type=pathlib.Path, help="Where to save the results")
    parser.add_argument("--provider", choices=["gemini", "lightning"],
                        help="Override LLM_PROVIDER from .env for this run")
    args = parser.parse_args()

    if not args.corpus.is_dir():
        raise SystemExit(f"no such folder: {args.corpus}")
    chunks = read_chunks(args.corpus)
    if not chunks:
        raise SystemExit(f"no .md or .txt files under {args.corpus}")
    if args.sample:
        chunks = [c for c in chunks if c["id"] in SAMPLE_IDS]
    out = RESULTS / "sample.json" if args.sample else results_path(args.corpus)
    if args.thinking:
        out = out.with_name(f"{out.stem}_{args.thinking}.json")
    out = args.out or out
    print(f"{len(chunks)} chunks from {args.corpus} -> {out}")

    llm = LLMClient(provider=args.provider)
    settings = dict(provider=llm.provider, model=llm.model, per_call=args.per_call,
                    thinking=args.thinking or "default")

    resume = None
    if out.exists():
        earlier = load_results(out, chunks)
        if earlier.get("complete"):
            raise SystemExit(f"{out.name} is already complete. Delete it to extract again.")
        resume = {k: earlier[k] for k in ("mentions", "relations", "calls", "done",
                                          "dropped_unknown_chunk")}
        print(f"resuming {out.name}: {len(resume['done'])} of {len(chunks)} chunks already done")

    def progress(partial):
        save_results(partial, chunks, out, complete=False, **settings)

    started = time.time()
    try:
        results = extract(llm, chunks, per_call=args.per_call, thinking=args.thinking,
                          resume=resume, on_call=progress)
    except (RuntimeError, OSError) as exc:   # unavailable through every retry, or a dropped connection
        raise SystemExit(f"stopped: {exc}\nProgress is saved in {out}. "
                         "Run the same command again to continue.")
    save_results(results, chunks, out, complete=True, **settings)
    print(f"{len(chunks)} chunks, {len(results['calls'])} calls, "
          f"{time.time() - started:.0f}s this run: {len(results['mentions'])} mentions, "
          f"{len(results['relations'])} relations -> {out}")
