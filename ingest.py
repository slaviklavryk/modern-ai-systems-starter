"""Week 3 — embed a corpus once, into a store that survives the process.

    python ingest.py corpus/                 # every .txt and .md under corpus/
    python ingest.py corpus/ --reset         # re-chunk from scratch
    python ingest.py corpus/ --chunk-size 300 --overlap 60

Why this is a script and not a notebook cell
--------------------------------------------
Ingestion is a slow, one-off batch job; querying is interactive. They belong in
different places, which is the same "ingest once, query every call" split the
lecture draws.

The slowness is not incidental. `gemini-embedding-001` allows roughly 100 texts
per minute (measured 2026-09-14), counted per text rather than per request, so
batching cannot speed it up -- only waiting works. A 3,000-chunk corpus is about
half an hour. `EmbeddingClient` paces itself so this runs unattended.

Run it once, leave it running, and every notebook afterwards opens the finished
index in `./chroma/` instantly. Re-run with `--reset` only when you change the
chunk size, because that invalidates every chunk boundary you already stored.

Lab 2 requires a re-seedable `ingest.py`. This is that file's ancestor: keep it
working as your corpus grows.
"""

import argparse
import pathlib
import sys
import time

from chunking import chunk_text
from vector_store import VectorStore

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SUFFIXES = {".txt", ".md"}


def read_corpus(source: pathlib.Path) -> list[tuple[str, str]]:
    """Return [(filename, text)]. Accepts one file or a directory of them."""
    if source.is_file():
        return [(source.name, source.read_text(encoding="utf-8"))]
    files = sorted(p for p in source.rglob("*") if p.suffix.lower() in SUFFIXES)
    if not files:
        raise SystemExit(f"No .txt or .md files under {source}")
    return [(p.name, p.read_text(encoding="utf-8")) for p in files]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=pathlib.Path, help="A file, or a directory of .txt/.md")
    parser.add_argument("--chunk-size", type=int, default=200, help="Words per chunk")
    parser.add_argument("--overlap", type=int, default=40, help="Words repeated between chunks")
    parser.add_argument("--name", default="chunks", help="Chroma collection name")
    parser.add_argument("--reset", action="store_true", help="Clear the collection first")
    args = parser.parse_args()

    documents = read_corpus(args.source)
    chunks: list[str] = []
    for filename, text in documents:
        pieces = chunk_text(text, chunk_size=args.chunk_size, overlap=args.overlap)
        chunks.extend(pieces)
        print(f"  {filename:<40} {len(text.split()):>6} words -> {len(pieces):>4} chunks")

    if not chunks:
        raise SystemExit("Corpus produced no chunks -- is it empty?")

    store = VectorStore(name=args.name, reset=args.reset)
    already = store.count()
    if already and not args.reset:
        print(f"\nCollection {args.name!r} already holds {already} chunks.")
        print("Pass --reset to rebuild it, or --name to ingest alongside it.")
        return

    minutes = len(chunks) / 90
    print(f"\n{len(documents)} documents -> {len(chunks)} chunks")
    print(f"Embedding at ~90 texts/minute: expect roughly {minutes:.0f} minute(s).")
    print("Leave this running.\n")

    started = time.time()
    store.add(chunks)
    elapsed = time.time() - started

    print(f"\nDone. {store.count()} chunks indexed in {elapsed / 60:.1f} minutes.")
    print(f"Stored in ./chroma/ -- open it from a notebook with VectorStore(name={args.name!r}).")


if __name__ == "__main__":
    main()
