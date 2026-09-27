"""Week 4 — embeddings stored on nodes, and a vector index that finds the way in.

    python graph_vectors.py                               # embed the Topic nodes of the course graph
    python graph_vectors.py --from-chroma week3_chunks    # copy your Week 3 chunks in, vectors and all

    from graph_vectors import embed_nodes, vector_search
    embed_nodes(driver, emb)                              # once; skips nodes already embedded
    vector_search(driver, emb, "How do I find text by meaning?", k=3)

The idea in one line: a traversal must START from a node, and a user's question
names none. The vector index finds the starting nodes by meaning; the graph then
supplies what is connected to them. See the notebook, Part 6.

Nothing here is new machinery. The vectors come from Week 3's EmbeddingClient,
with the same document/query task types, and the index is the same kind of
approximate nearest-neighbour structure (HNSW) that Chroma uses.

Measured on the pinned neo4j:5.26-community, 2026-09-27
--------------------------------------------------------
- Community edition HAS the vector index, and it accepts our 3072 dimensions
  (the limit is 4096 from 5.18). Provider `vector-2.0`, quantisation ON by default.
- The score is NOT Chroma's number. Neo4j reports (1 + cos)/2, between 0 and 1,
  higher = closer, so orthogonal vectors score 0.5. Chroma reported the distance
  1 - cos, lower = closer. Checked against cos computed in Python: agreement to
  within 9e-4, the difference being quantisation. Do not compare raw numbers
  across the two stores; convert first.
- A WHERE placed AFTER queryNodes can only discard from the k nodes already
  found: k=4 then a filter returned 2 rows. Ask for more than you need.
- The search is APPROXIMATE, visibly so even on a small corpus. The 183-chunk
  sample corpus, identical vectors in both stores, 8 questions: asking Neo4j for
  k=5 found 85% of the exact top 5 (exact_search() below) in one build of the
  index and 87.5% in another -- the approximation depends on how the index was
  built. Asking for 50 and keeping the best 5 found 97.5% both times. Chroma
  returned the exact top 5 on every question checked. Turning quantisation off made the scores exact but did not
  change the k=5 misses -- those come from the approximate search itself. The
  remaining gap after over-fetching is quantisation reordering chunks whose
  scores differ by about 0.001.
- A vector of the WRONG LENGTH is stored without any error, and the index then
  silently leaves that node out of every search. `_store_vectors` checks the
  length before writing for that reason.
- `db.index.vector.queryNodes` is the only query interface on 5.26. Current
  Neo4j releases deprecate it (2026.04) in favour of Cypher 25's SEARCH clause,
  which is what you will find in today's documentation. SEARCH does not run here.
"""

import pathlib
import re
import sys
import time
from typing import Optional

# EmbeddingClient and VectorStore live in ../week3. Put that folder on the path so
# `from embedding_client import ...` works from this week's folder.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "week3"))

from embedding_client import EmbeddingClient  # noqa: E402
from neo4j import Driver  # noqa: E402

from graph_db import connect, run  # noqa: E402

DIMENSIONS = 3072  # gemini-embedding-001; must match the index, or nodes vanish from search

# Labels and property names cannot be passed as parameters in Cypher 5, so this is
# the one place in the course code that puts names into query text. They are
# checked against this pattern first -- never interpolate anything unchecked.
_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _checked(name: str) -> str:
    if not _IDENTIFIER.match(name):
        raise ValueError(f"not a safe Cypher identifier: {name!r}")
    return name


def ensure_vector_index(driver: Driver, index: str, label: str, prop: str = "embedding",
                        dimensions: int = DIMENSIONS) -> None:
    """Create a cosine vector index if it does not exist, and wait until it is ONLINE.

    If an index of that name already exists with a different dimension, refuse:
    the vectors would be stored and then silently ignored by every search.
    """
    label, prop = _checked(label), _checked(prop)
    existing = run(driver, "SHOW INDEXES YIELD name, options WHERE name = $index "
                           "RETURN options", index=index)
    if existing:
        have = existing[0]["options"]["indexConfig"]["vector.dimensions"]
        if have != dimensions:
            raise ValueError(f"index {index!r} is {have}-dimensional, vectors are {dimensions}")
    else:
        run(driver,
            f"CREATE VECTOR INDEX {_checked(index)} IF NOT EXISTS "
            f"FOR (n:{label}) ON n.{prop} "
            "OPTIONS {indexConfig: {`vector.dimensions`: $dims, "
            "`vector.similarity_function`: 'cosine'}}",
            dims=dimensions)
    run(driver, "CALL db.awaitIndex($index, 120)", index=index)


def _store_vectors(driver: Driver, label: str, key: str, rows: list[dict],
                   prop: str = "embedding") -> None:
    """Write one vector per node, matched on its key. rows: [{"key", "vector"}]."""
    for row in rows:
        if len(row["vector"]) != DIMENSIONS:
            raise ValueError(f"{row['key']!r}: vector has {len(row['vector'])} dimensions, "
                             f"expected {DIMENSIONS} -- it would be invisible to the index")
    run(driver,
        f"UNWIND $rows AS row "
        f"MATCH (n:{_checked(label)} {{{_checked(key)}: row.key}}) "
        f"CALL db.create.setNodeVectorProperty(n, $prop, row.vector)",
        rows=rows, prop=prop)


def embed_nodes(driver: Driver, emb: EmbeddingClient, *, label: str = "Topic",
                key: str = "name", text: str = "description",
                index: str = "topic_embeddings", force: bool = False) -> int:
    """Embed each node's text property and store the vector on the node.

    Skips nodes that already have an embedding unless force=True, because every
    text embedded counts against the ~100 texts/minute quota. Returns how many
    nodes were embedded this time.
    """
    label, key, text = _checked(label), _checked(key), _checked(text)
    todo = run(driver,
               f"MATCH (n:{label}) WHERE n.{text} IS NOT NULL "
               f"AND ($force OR n.embedding IS NULL) "
               f"RETURN n.{key} AS key, n.{text} AS text ORDER BY key",
               force=force)
    if todo:
        # Stored passages are documents; questions are queries. Same asymmetry as Week 3.
        vectors = emb.embed_batch([r["text"] for r in todo], task_type="RETRIEVAL_DOCUMENT")
        _store_vectors(driver, label, key,
                       [{"key": r["key"], "vector": v} for r, v in zip(todo, vectors)])
    ensure_vector_index(driver, index, label)
    return len(todo)


def vector_search(driver: Driver, emb: EmbeddingClient, question: str, *,
                  index: str = "topic_embeddings", k: int = 5) -> list[dict]:
    """Embed the question and return the k nearest nodes with their scores.

    Returns [{"node": {...properties, without the vector}, "score": float}],
    highest score first. The score is (1 + cos)/2 -- see the module docstring.
    """
    vector = emb.embed(question, task_type="RETRIEVAL_QUERY")
    rows = run(driver,
               "CALL db.index.vector.queryNodes($index, $k, $vector) YIELD node, score "
               "RETURN node, score",
               index=index, k=k, vector=vector)
    for row in rows:
        row["node"].pop("embedding", None)  # 3072 numbers nobody wants printed
    return rows


def exact_search(driver: Driver, vector: list[float], *, label: str = "Chunk",
                 k: int = 5) -> list[dict]:
    """The EXACT k nearest nodes: compare the vector with every node, no index.

    `vector.similarity.cosine` returns the same (1 + cos)/2 the index reports
    (checked 2026-09-27), so the two are directly comparable. This is the
    reference the index approximates. It reads every node, so it is fine for a
    student corpus and far too slow for a large one -- which is why indexes exist.
    Returns [{"node": {...}, "score": float}], highest first.
    """
    rows = run(driver,
               f"MATCH (n:{_checked(label)}) WHERE n.embedding IS NOT NULL "
               "RETURN n AS node, vector.similarity.cosine(n.embedding, $v) AS score "
               "ORDER BY score DESC LIMIT $k",
               v=vector, k=k)
    for row in rows:
        row["node"].pop("embedding", None)
    return rows


def copy_chunks_from_chroma(driver: Driver, collection: str, *, limit: Optional[int] = None,
                            index: str = "chunk_embeddings", batch: int = 250) -> int:
    """Copy Week 3 chunks from Chroma into Neo4j as (:Chunk) nodes, vectors included.

    No embedding call is made: the vectors come straight out of Chroma, so this
    costs nothing against the quota. That also means both stores hold IDENTICAL
    vectors, which is what lets the notebook's Part 9 compare the two indexes
    and nothing else. Copies `batch` chunks at a time, so a large corpus never
    sits in memory whole.

    Neo4j holds ONE copied collection at a time: existing (:Chunk) nodes are
    deleted first. Chroma numbers chunk ids from 0 in every collection, so two
    collections copied side by side would collide -- and Part 9's comparison
    needs Neo4j to hold exactly what one Chroma collection holds.
    """
    from vector_store import VectorStore  # week3; imported here so Chroma loads only if used

    store = VectorStore(name=collection)
    total = store.count() if limit is None else min(limit, store.count())
    if total == 0:
        raise SystemExit(f"Chroma collection {collection!r} is empty. "
                         f"Collections there: {store.collections()}")
    run(driver, "MATCH (c:Chunk) DETACH DELETE c")
    run(driver, "CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE")
    copied = 0
    while copied < total:
        rows = store.export(limit=min(batch, total - copied), offset=copied)
        if not rows:
            break
        run(driver,
            "UNWIND $rows AS row MERGE (c:Chunk {id: row.id}) "
            "SET c.text = row.chunk, c.source = row.source, c.chunk_index = row.chunk_index, "
            "c.collection = $collection",
            rows=[{"id": r["id"], "chunk": r["chunk"],
                   "source": r["metadata"].get("source"),
                   "chunk_index": r["metadata"].get("chunk_index")} for r in rows],
            collection=collection)
        _store_vectors(driver, "Chunk", "id",
                       [{"key": r["id"], "vector": r["embedding"]} for r in rows])
        copied += len(rows)
    ensure_vector_index(driver, index, "Chunk")
    return copied


if __name__ == "__main__":
    import argparse

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--from-chroma", metavar="COLLECTION",
                        help="Copy this Week 3 Chroma collection into Neo4j instead")
    parser.add_argument("--limit", type=int, help="Copy at most this many chunks")
    parser.add_argument("--force", action="store_true", help="Re-embed nodes that already have a vector")
    args = parser.parse_args()

    driver = connect()
    started = time.time()
    if args.from_chroma:
        n = copy_chunks_from_chroma(driver, args.from_chroma, limit=args.limit)
        print(f"copied {n} chunks from Chroma '{args.from_chroma}' in {time.time() - started:.1f}s "
              "(no embedding calls: the vectors came with them)")
    else:
        emb = EmbeddingClient()
        n = embed_nodes(driver, emb, force=args.force)
        print(f"embedded {n} Topic nodes in {time.time() - started:.1f}s "
              f"({emb.texts_embedded} texts against the ~100/minute quota)")
        for row in vector_search(driver, emb, "How do I find text by meaning rather than keywords?", k=3):
            print(f"  {row['score']:.4f}  {row['node']['name']}")
    driver.close()
