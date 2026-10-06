"""Week 5 — rebuild the course knowledge graph in one command.

    python ingest.py                  # rebuild from saved results: no API call, seconds
    python ingest.py --reset          # empty the database first, then rebuild
    python ingest.py --extract        # re-run extraction first (61 calls, minutes)
    python ingest.py --no-vectors     # skip copying the chunk vectors from Chroma
    python ingest.py --corpus ../my_docs --reset   # another folder of documents

This is the re-seedable ingest the syllabus requires from this week, and the
template you adapt for your own domain in Lab 2. It has the lecture's four
stages (section 8):

    documents --> chunks --> embeddings --> extraction --> load --> Neo4j
                  free       quota:         quota:         free,
                  determ.    saved          saved          idempotent

Only the two middle stages spend API quota, and both write their results to
disk: the embeddings live in Week 3's Chroma store, and the extraction results
in `extractions/course_corpus.json`. A rebuild therefore re-runs the load from
saved results in seconds. A new extraction is a separate, deliberate step
(`--extract`), because at six requests per minute it is the slow part.

Run it twice: the counts printed the second time are the same.
"""

import argparse
import pathlib
import sys
import time

_HERE = pathlib.Path(__file__).resolve().parent
for _d in ("common", "week3", "week4"):
    sys.path.insert(0, str(_HERE.parent / _d))

from graph_db import breakdown, connect, run  # noqa: E402
from kg_loader import CORPUS, copy_vectors, load_all, read_chunks, resolve_results  # noqa: E402

import extraction  # noqa: E402



def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--reset", action="store_true", help="Empty the database first")
    parser.add_argument("--extract", action="store_true", help="Re-run extraction first")
    parser.add_argument("--provider", choices=["gemini", "lightning"], default="lightning",
                        help="Who extracts (default lightning: Gemini's free tier allows "
                             "20 requests a day, and extraction needs 61)")
    parser.add_argument("--no-vectors", action="store_true", help="Do not copy chunk vectors")
    parser.add_argument("--corpus", type=pathlib.Path, default=CORPUS,
                        help="Folder of .md/.txt documents (default: week3/corpus)")
    args = parser.parse_args()
    started = time.time()

    # Stage 1: documents to chunks. Deterministic, so the ids are the same everywhere.
    chunks = read_chunks(args.corpus)
    RESULTS = extraction.results_path(args.corpus)
    print(f"1. chunks:     {len(chunks)} from {len({c['source'] for c in chunks})} documents")

    # Stage 3 first, if asked: it is the only stage that may take minutes.
    if args.extract:
        from llm_client import LLMClient
        if RESULTS.exists():
            RESULTS.unlink()
        llm = LLMClient(provider=args.provider)
        results = extraction.extract(llm, chunks)
        extraction.save_results(results, chunks, RESULTS, complete=True, provider=llm.provider,
                                model=llm.model, per_call=3, thinking="default")
    results = extraction.load_results(RESULTS, chunks)
    if not results.get("complete"):
        raise SystemExit(f"{RESULTS.name} is incomplete: run "
                         f"`python extraction.py --all --corpus {args.corpus}` to finish it first.")
    print(f"3. extraction: {len(results['mentions'])} mentions, "
          f"{len(results['relations'])} relationships, read from {RESULTS.name}")

    driver = connect()
    if args.reset:
        run(driver, "MATCH (n) DETACH DELETE n")
        print("   database emptied (constraints and indexes kept)")

    # Stage 4: the load, in the lecture's order.
    resolved = resolve_results(results)
    load_all(driver, chunks, resolved)
    print(f"4. load:       {len(resolved['entities'])} entities, {len(resolved['mentions'])} mentions, "
          f"{len(resolved['relations'])} relationships; {len(resolved['merged'])} entities had "
          f"several spellings, {len(resolved['type_conflicts'])} names came under two types")

    # Stage 2 last: it only decorates nodes that the load has created.
    if not args.no_vectors:
        n = copy_vectors(driver, chunks)
        print(f"2. vectors:    {n} of {len(chunks)} chunks, copied from Chroma")

    detail = breakdown(driver)
    print("\n   nodes by label:        " + ", ".join(f"{k} {v}" for k, v in detail["labels"].items()))
    print("   relationships by type: " + ", ".join(f"{k} {v}" for k, v in detail["relationships"].items()))
    print(f"   {time.time() - started:.1f}s")
    driver.close()


if __name__ == "__main__":
    main()
