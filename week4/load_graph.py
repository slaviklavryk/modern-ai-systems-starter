"""Week 4 — load a .cypher script into Neo4j, and show that loading it twice changes nothing.

    python load_graph.py --movies                 # Neo4j's standard Movies graph (Parts 2 to 5)
    python load_graph.py                          # course_graph.cypher (Part 6, vector search)
    python load_graph.py --reset                  # empty the database first
    python load_graph.py my_graph.cypher          # any script written the same way

Run it twice. The counts printed the second time are the same as the first,
because both scripts MERGE every node on a key and every relationship between
nodes that already exist. That property -- idempotence -- is what makes a load
safe to re-run, and Week 5 requires a re-seedable `ingest.py` built on it.

The Movies graph is Neo4j's own example: 38 films, 133 people, and who acted in,
directed, produced, wrote, or reviewed what. `--movies` loads `week4/movies.cypher`,
an unmodified copy of `scripts/movies.cypher` from neo4j-graph-examples/movies at
commit 51cf90d18c1a7f74bce7a77083543697dfb0139d. No network is needed. Neo4j
Browser's own `:play movies` guide runs the same script.

The two graphs take turns: Community edition has one database, and loading one
deletes the other first (`switch_to` below). Only the other graph is deleted, so
the run-it-twice check above still works. Moving to the Movies graph also deletes
the course graph's topic embeddings, so run `graph_vectors.py` again after moving
back; it embeds the 39 topics, well within the quota.

`--reset` deletes every node and relationship (DETACH DELETE) but keeps the
constraints and indexes, which the scripts re-create with IF NOT EXISTS anyway.
It does NOT delete the Docker volume. `docker compose down -v` does that, and
takes the whole graph with it -- which is exactly why a load must be re-runnable.
"""

import argparse
import pathlib
import sys
import time

from graph_db import breakdown, connect, counts, run, run_script

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_SCRIPT = HERE / "course_graph.cypher"

# Copied unchanged from one commit of neo4j-graph-examples/movies, so every student
# loads the same 171 nodes and 253 relationships (verified 2026-09-27 on Neo4j 5.26.31).
MOVIES_SCRIPT = HERE / "movies.cypher"

# Community edition has one database, so the two graphs take turns in it. Loading
# one first deletes the other, found by its labels. Chunk belongs with the course
# graph: Part 9 copies chunks in beside it.
MOVIES_LABELS = ["Movie", "Person"]
COURSE_LABELS = ["Week", "Topic", "Deliverable", "Tool", "Chunk"]


def remove_labels(driver, labels: list[str]) -> int:
    """Delete every node carrying any of these labels, with its relationships.

    Returns how many nodes were deleted. Constraints and indexes are kept.
    """
    return run(driver,
               "MATCH (n) WHERE any(l IN labels(n) WHERE l IN $labels) "
               "DETACH DELETE n RETURN count(n) AS n",
               labels=labels)[0]["n"]


def switch_to(driver, script: pathlib.Path) -> int:
    """Delete the other graph before loading this one. Returns nodes deleted.

    Only the OTHER graph is deleted, never the one being loaded, so loading the
    same script twice still shows the counts unchanged. Any other script leaves
    the database as it is.
    """
    other = {MOVIES_SCRIPT.resolve(): COURSE_LABELS,
             DEFAULT_SCRIPT.resolve(): MOVIES_LABELS}.get(script.resolve())
    return remove_labels(driver, other) if other else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("script", nargs="?", type=pathlib.Path, default=None,
                        help="A .cypher file (default: course_graph.cypher)")
    parser.add_argument("--movies", action="store_true",
                        help="Load Neo4j's standard Movies graph instead")
    parser.add_argument("--reset", action="store_true",
                        help="Delete every node and relationship first")
    args = parser.parse_args()
    script = MOVIES_SCRIPT if args.movies else (args.script or DEFAULT_SCRIPT)

    driver = connect()
    if args.reset:
        run(driver, "MATCH (n) DETACH DELETE n")
        print("database emptied (constraints and indexes kept)")
    removed = switch_to(driver, script)
    if removed:
        print(f"removed the other graph first: {removed} nodes")

    before = counts(driver)
    started = time.time()
    n = run_script(driver, script)
    after = counts(driver)

    print(f"{script.name}: {n} statements in {time.time() - started:.1f}s")
    print(f"  before: {before}")
    print(f"  after:  {after}")
    if before == after and before["nodes"] > 0:
        print("  unchanged -- the load is idempotent")

    detail = breakdown(driver)
    print("\n  nodes by label:        " + ", ".join(f"{k} {v}" for k, v in detail["labels"].items()))
    print("  relationships by type: " + ", ".join(f"{k} {v}" for k, v in detail["relationships"].items()))
    driver.close()


if __name__ == "__main__":
    main()
