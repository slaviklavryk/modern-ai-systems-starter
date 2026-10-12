"""Week 6 — rebuild the course graph, cleaned, ready for retrieval. One command.

    python build_graph.py

It empties the database and loads Week 5's reference extraction with the Week 6
cleaning applied (`cleaning.py`), copies Week 3's chunk vectors onto the chunks, gives
every extracted entity the extra label `Entity` so that one query can reach all three
types, and checks that the stored vectors come from the embedding model the client uses
(`vector_check.py`). No generation call; one embedding, for the check.
"""

import pathlib
import sys
import time

_HERE = pathlib.Path(__file__).resolve().parent
for _d in ("common", "week3", "week4", "week5"):
    sys.path.insert(0, str(_HERE.parent / _d))
sys.path.insert(0, str(_HERE))

import cleaning  # noqa: E402
from embedding_client import EmbeddingClient  # noqa: E402
from extraction import RESULTS, load_results  # noqa: E402
from graph_db import breakdown, connect, run  # noqa: E402
from kg_loader import copy_vectors, load_all, read_chunks, resolve_results  # noqa: E402
from vector_check import check_and_record  # noqa: E402


def build(driver) -> dict:
    """The whole rebuild. Returns the resolution, for reading what it merged and dropped."""
    cleaning.apply()
    chunks = read_chunks()
    resolved = resolve_results(load_results(RESULTS / "course_corpus.json", chunks))
    run(driver, "MATCH (n) DETACH DELETE n")
    load_all(driver, chunks, resolved)
    vectors = copy_vectors(driver, chunks)
    run(driver, "MATCH (n) WHERE n:Topic OR n:Tool OR n:Deliverable SET n:Entity")
    model = check_and_record(driver, EmbeddingClient())
    print(f"{len(resolved['entities'])} entities ({len(resolved['type_conflicts'])} names still "
          f"under two types, {len(resolved['dropped_relations'])} relationships dropped); "
          f"{vectors} chunk vectors from {model}")
    return resolved


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    started = time.time()
    driver = connect()
    build(driver)
    detail = breakdown(driver)
    print("nodes by label:        " + ", ".join(f"{k} {v}" for k, v in detail["labels"].items()))
    print("relationships by type: " + ", ".join(f"{k} {v}" for k, v in detail["relationships"].items()))
    print(f"{time.time() - started:.1f}s")
    driver.close()
