"""Week 6 — make sure every vector in a search comes from one embedding model.

    from vector_check import check_and_record, require_same_model
    check_and_record(driver, emb)          # once, after the chunk vectors are loaded
    require_same_model(driver, emb)        # before every search

Two embedding models can produce vectors of the same size in unrelated spaces. Measured
2026-10-06: Week 3's stored chunk vectors are from `gemini-embedding-2`; a fresh
`gemini-embedding-001` vector of the same text has a cosine of about 0.00 with them,
while a fresh `gemini-embedding-2` vector has 1.000000 (measured 2026-10-09). Both have
3072 dimensions, so a search mixing them raises no error: it ranks by noise.

A recorded model name alone is not enough, since the store itself did not record one.
So the check re-embeds one stored chunk with the client and compares: only a match is
recorded, on a single (:Meta {name: 'chunk_embeddings'}) node.
"""

import math

INDEX = "chunk_embeddings"
SAME_MODEL = 0.99     # cosine between a stored vector and a fresh one of the same text


def _cosine(a, b):
    return sum(x * y for x, y in zip(a, b)) / (math.sqrt(sum(x * x for x in a)) *
                                               math.sqrt(sum(y * y for y in b)))


def check_and_record(driver, emb) -> str:
    """Re-embed one stored chunk; if it matches, record the client's model. One embedding."""
    with driver.session() as s:
        row = s.run("MATCH (c:Chunk) WHERE c.embedding IS NOT NULL "
                    "RETURN c.text AS text, c.embedding AS vector ORDER BY c.id LIMIT 1").single()
    if row is None:
        raise RuntimeError("no chunk has a vector: load them first (build_graph.py)")
    fresh = emb.embed(row["text"], task_type="RETRIEVAL_DOCUMENT")
    similarity = _cosine(row["vector"], fresh)
    if similarity < SAME_MODEL:
        raise RuntimeError(f"the stored chunk vectors are not from {emb.model}: a fresh vector "
                           f"of the same text has cosine {similarity:.4f} with the stored one. "
                           "Re-embed the corpus with this model, or switch the client back.")
    with driver.session() as s:
        s.run("MERGE (m:Meta {name: $index}) SET m.embedding_model = $model",
              index=INDEX, model=emb.model)
    return emb.model


def require_same_model(driver, emb) -> None:
    """Refuse a search whose client model is not the one the stored vectors came from."""
    with driver.session() as s:
        row = s.run("MATCH (m:Meta {name: $index}) RETURN m.embedding_model AS model",
                    index=INDEX).single()
    if row is None:
        raise RuntimeError("no embedding model is recorded for the chunk vectors: "
                           "run build_graph.py, which checks and records it")
    if row["model"] != emb.model:
        raise RuntimeError(f"the chunk vectors are from {row['model']}, but the client embeds "
                           f"with {emb.model}: the search would compare unrelated vectors")
