"""Week 4 — connect to Neo4j and run Cypher against it.

    from graph_db import connect, run, counts
    driver = connect()                         # reads NEO4J_* from .env
    rows = run(driver, "MATCH (t:Topic) RETURN t.name AS name LIMIT $n", n=5)
    print(counts(driver))

    python graph_db.py                         # is Neo4j up? which version?

This file is deliberately thin. The course uses the official `neo4j` driver
directly rather than a framework over it (syllabus §4, framework policy), so every
function below is a few lines around `driver.execute_query`, and the notebook
shows that call on its own in Part 5. Read these before you rely on them.

Parameters, always
------------------
Every value that reaches a query here goes in as a parameter (`$name`), never by
pasting it into the query string. A query built by concatenation breaks on the
first apostrophe in the data and is open to injection in exactly the way SQL is.
The risk grows later in the course, once text written by a model starts flowing
into queries (Week 5's LLM-assisted extraction) and into tools (Week 7).

The version is pinned, and it is Cypher 5
-----------------------------------------
`docker-compose.yml` pins `neo4j:5.26-community`, which runs Cypher 5 only
(verified 2026-09-27: server 5.26.31, community edition, driver 6.3.1). Most of
Neo4j's current online documentation is Cypher 25, which does not run here. Read
the Cypher 5 manual instead:

    https://neo4j.com/docs/cypher-manual/5/introduction/
"""

import os
import pathlib
import sys

from dotenv import load_dotenv
from neo4j import Driver, GraphDatabase

load_dotenv()  # finds the repo-root .env from any week folder; it walks upwards

# Defaults match docker-compose.yml, so a missing .env still reaches the local
# instance. Never reuse this password for anything real.
_DEFAULT_URI = "bolt://localhost:7687"
_DEFAULT_USER = "neo4j"
_DEFAULT_PASSWORD = "modernai"


def connect() -> Driver:
    """Open a driver to the course's Neo4j instance and check it answers.

    Fails immediately, with the reason, if the container is not running --
    rather than on the first query, where the error is harder to read.
    """
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", _DEFAULT_URI),
        auth=(
            os.environ.get("NEO4J_USER", _DEFAULT_USER),
            os.environ.get("NEO4J_PASSWORD", _DEFAULT_PASSWORD),
        ),
    )
    driver.verify_connectivity()
    return driver


def run(driver: Driver, query: str, **params) -> list[dict]:
    """Run one Cypher statement and return its rows as plain dicts.

    A query returns ROWS, not a picture of a graph -- the table view in Neo4j
    Browser, not the graph view. That is what a program receives, and in Week 6
    it is what has to be turned into text for a model's context.
    """
    records, _summary, _keys = driver.execute_query(query, parameters_=params)
    return [record.data() for record in records]


def statements(script: str) -> list[str]:
    """Split a .cypher script into statements.

    The rule is simple on purpose: a statement ends with `;` at the end of a
    line, and lines starting with `//` are comments. Keep semicolons out of
    string values in your own scripts, or put them mid-line.
    """
    found, current = [], []
    for line in script.splitlines():
        if line.strip().startswith("//"):
            continue
        current.append(line)
        if line.rstrip().endswith(";"):
            text = "\n".join(current).strip().rstrip(";").strip()
            if text:
                found.append(text)
            current = []
    tail = "\n".join(current).strip()
    if tail:
        found.append(tail)
    return found


def run_script(driver: Driver, path) -> int:
    """Run every statement in a .cypher file, in order. Returns how many ran."""
    text = pathlib.Path(path).read_text(encoding="utf-8")
    parts = statements(text)
    for statement in parts:
        driver.execute_query(statement)
    return len(parts)


def counts(driver: Driver) -> dict:
    """Nodes and relationships in the whole database.

    Run it before and after a load. If a load is idempotent -- built on MERGE
    with a key, as `course_graph.cypher` is -- running it twice leaves both
    numbers unchanged.
    """
    nodes = run(driver, "MATCH (n) RETURN count(n) AS n")[0]["n"]
    rels = run(driver, "MATCH ()-[r]->() RETURN count(r) AS n")[0]["n"]
    return {"nodes": nodes, "relationships": rels}


def breakdown(driver: Driver) -> dict:
    """Counts per node label and per relationship type -- what is actually in there."""
    labels = run(driver, """
        MATCH (n) UNWIND labels(n) AS label
        RETURN label, count(*) AS n ORDER BY label""")
    types = run(driver, """
        MATCH ()-[r]->()
        RETURN type(r) AS type, count(*) AS n ORDER BY type""")
    return {
        "labels": {row["label"]: row["n"] for row in labels},
        "relationships": {row["type"]: row["n"] for row in types},
    }


def server_info(driver: Driver) -> dict:
    """Server version and edition, straight from the database."""
    row = run(driver, "CALL dbms.components() YIELD versions, edition "
                      "RETURN versions[0] AS version, edition")[0]
    return row


if __name__ == "__main__":
    # Smoke test for the Week 4 practical, section 1: is the container up, and is
    # it the pinned version? Prints what is already stored, which is nothing on
    # a fresh volume.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        driver = connect()
    except Exception as exc:  # the usual cause is simply that Docker is not running
        raise SystemExit(
            f"Cannot reach Neo4j: {type(exc).__name__}: {exc}\n"
            "Is the container up? From the repo root: docker compose up -d"
        )
    info = server_info(driver)
    print(f"Neo4j {info['version']} ({info['edition']} edition) is running")
    if not info["version"].startswith("5.26"):
        print("  warning: the course pins 5.26 -- check docker-compose.yml")
    print(f"  {counts(driver)}")
    driver.close()
