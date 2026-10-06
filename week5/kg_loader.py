"""Week 5 — load the course knowledge graph, built from the documents alone, idempotently.

    from kg_loader import read_chunks, resolve_results, load_all
    chunks = read_chunks()                          # the Week 3 corpus, chunked as Week 3 did
    resolved = resolve_results(results)             # extracted names grouped into entities
    load_all(driver, chunks, resolved)              # the whole load, in the lecture's order

The load order is the lecture's (section 8): constraints, the text layer, entities
merged on their keys, the relationships between them, and MENTIONS last. Every
statement MERGEs on a key, so running the whole load twice leaves every count
unchanged -- including the length of every list of chunk ids.

Chunk ids are `<file>#<chunk index>`, e.g. `week-03-lecture-plan.md#4`. They are
the same on every machine, because chunking is deterministic: the corpus chunked
at 200 words with 40 of overlap reproduces exactly the 183 chunks Week 3 stored
in Chroma (checked 2026-10-04). Chroma's own ids ("0", "1", ...) depend on the
order of ingestion and are not used.
"""

import pathlib
import re
import sys
from collections import Counter

_HERE = pathlib.Path(__file__).resolve().parent
for _d in ("week3", "week4"):
    sys.path.insert(0, str(_HERE.parent / _d))

from chunking import chunk_text  # noqa: E402
from graph_db import run, run_script  # noqa: E402
from kg_model import DECLARED_TYPES, ENTITY_TYPES, EXTRACTED_TYPES, TYPES, key  # noqa: E402

CORPUS = _HERE.parent / "week3" / "corpus"

CONSTRAINTS = _HERE / "constraints.cypher"
CHUNK_SIZE, OVERLAP = 200, 40   # Week 3's defaults; changing them changes every chunk id

# The sample for the practical's extraction part: chunks that state relationships,
# chunks that tempt the model into wrong ones, and one from the corpus's single
# document that is not about the course, which should yield nothing.
#
# Chosen 2026-10-04 by reading the reference extraction (extractions/course_corpus.json):
SAMPLE_IDS = [
    "week-03-lecture-plan.md#3",      # cosine distance and ranking build on cosine similarity: stated
    "week-02-practical-plan.md#7",    # tool calling and cost work depend on structured output: stated
    "week-03-practical-plan.md#6",    # embedding and ingestion use Chroma: USES, stated
    "week-03-lecture.md#12",          # a pipeline diagram: its stages came back as a BUILDS_ON chain
    "week-02-lecture.md#14",          # a table of a context's parts: part-of, returned as BUILDS_ON
    "week-01-lecture.md#22",          # the stack diagram: nine ASSESSES, from labs to layers of the stack
    "week-01-lecture.md#23",          # the list of week titles: weeks returned as topics
    "week-02-lecture.md#9",           # a price table: three models returned as tools
    "week-01-practical.md#15",        # an example inside the material: Einstein -> Princeton
    "IDE-BCA001-heat-hold-cool-laplace-derivation.md#0",   # not about the course: should yield nothing
]


def read_chunks(corpus: pathlib.Path = CORPUS) -> list[dict]:
    """Chunk every .md/.txt file under a folder. Returns [{"id", "text", "source", "index"}].

    A document's name is its path relative to the folder, with forward slashes, so
    that two files of the same name in different subfolders stay two documents:
    `labs/intro.md#0` and `notes/intro.md#0`. In a flat folder it is the file name.
    """
    corpus = pathlib.Path(corpus)
    files = sorted(p for p in corpus.rglob("*") if p.suffix.lower() in {".md", ".txt"})
    chunks = []
    for path in files:
        source = path.relative_to(corpus).as_posix()
        pieces = chunk_text(path.read_text(encoding="utf-8"), chunk_size=CHUNK_SIZE, overlap=OVERLAP)
        for i, text in enumerate(pieces):
            chunks.append({"id": f"{source}#{i}", "text": text, "source": source, "index": i})
    return chunks


def _week_of(source: str):
    """week-03-lecture-plan.md -> 3. A file not named after a week -> None."""
    m = re.match(r"week-(\d+)-", source)
    return int(m.group(1)) if m else None


def _kind_of(source: str):
    """lecture, lecture plan, practical, or practical plan; None for anything else."""
    m = re.match(r"week-\d+-(lecture|practical)(-plan)?\.", source)
    return (m.group(1) + (" plan" if m.group(2) else "")) if m else None


def check_type(rel_type: str) -> str:
    """Refuse a relationship type the model does not declare.

    A relationship type cannot be a parameter in Cypher 5, so it is written into
    the query text. Model output is untrusted input: check it before it gets there.
    """
    if rel_type not in DECLARED_TYPES:
        raise ValueError(f"undeclared relationship type {rel_type!r}; "
                         f"the model declares {sorted(DECLARED_TYPES)}")
    return rel_type


def load_constraints(driver) -> int:
    """One uniqueness constraint per key. Community edition supports no other kind."""
    return run_script(driver, CONSTRAINTS)


def clear_other_graphs(driver) -> None:
    """Remove the Movies graph and Week 4's graphs, if they are there.

    Community edition has one database, and Week 4's course graph uses the same
    labels as this one (Topic, Tool, Deliverable, Week). Its nodes are recognised
    by the properties only its script sets: a description on topics and tools, a
    title on weeks and deliverables. Week 4's copied chunks carry a collection.
    """
    run(driver, "MATCH (n) WHERE n:Movie OR n:Person DETACH DELETE n")
    run(driver, "MATCH (c:Chunk) WHERE c.collection IS NOT NULL DETACH DELETE c")
    run(driver, "MATCH (n) WHERE n.description IS NOT NULL OR n.title IS NOT NULL "
                "DETACH DELETE n")


def load_text_layer(driver, chunks: list[dict]) -> dict:
    """Documents and chunks, in order. Built from the chunks alone: no API call."""
    docs = sorted({c["source"] for c in chunks})
    run(driver, """
        UNWIND $docs AS d
        MERGE (doc:Document {name: d.name})
        SET doc.kind = d.kind
        WITH doc, d WHERE d.week IS NOT NULL
        MERGE (w:Week {number: d.week})
        MERGE (doc)-[:FOR_WEEK]->(w)""",
        docs=[{"name": d, "week": _week_of(d), "kind": _kind_of(d)} for d in docs])
    run(driver, """
        UNWIND $rows AS row
        MERGE (c:Chunk {id: row.id})
        SET c.text = row.text, c.source = row.source, c.chunk_index = row.chunk_index
        WITH c, row
        MATCH (doc:Document {name: row.source})
        MERGE (doc)-[:HAS_CHUNK]->(c)""",
        rows=[{"id": c["id"], "text": c["text"], "source": c["source"],
               "chunk_index": c["index"]} for c in chunks])
    run(driver, """
        UNWIND $pairs AS p
        MATCH (a:Chunk {id: p.a}), (b:Chunk {id: p.b})
        MERGE (a)-[:NEXT]->(b)""",
        pairs=[{"a": a["id"], "b": b["id"]} for a, b in zip(chunks, chunks[1:])
               if a["source"] == b["source"]])
    return {"documents": len(docs), "chunks": len(chunks)}


def resolve_results(results: dict) -> dict:
    """Group the extracted names into entities. Returns the rows to load and what was merged.

    Two names are one entity when they have the same key (`kg_model.key`: lower
    case, tidied, then the alias list) and the same type. The type is the one the
    model gave, unless `kg_model.TYPES` settles it. Each entity is shown under the
    name the model used for it most often. A name still returned under two types
    becomes one node per type, and is listed under `type_conflicts` to be read. A
    relationship whose end has the wrong type for it is listed under
    `dropped_relations`. Nothing here touches the database, so the notebook can show
    it before anything is written.
    """
    forms = {}   # (label, key) -> how often each spelling was returned

    def entity(label, name):
        k = key(name)
        return (TYPES.get(k, label), k) if k else None

    def note(e, name):
        forms.setdefault(e, Counter())[" ".join(name.split())] += 1

    mentions, relations, dropped = set(), set(), []
    for m in results["mentions"]:
        if m["type"] not in ENTITY_TYPES:
            raise ValueError(f"undeclared entity type {m['type']!r}")
        e = entity(m["type"], m["name"])
        if e:
            note(e, m["name"])
            mentions.add((m["chunk"], e))
    for r in results["relations"]:
        frm, to = EXTRACTED_TYPES[check_type(r["type"])]
        a, b = entity(frm, r["source"]), entity(to, r["target"])
        if not (a and b) or a == b:
            continue
        if (a[0], b[0]) != (frm, to):
            dropped.append(r)
            continue
        note(a, r["source"])
        note(b, r["target"])
        relations.add((r["type"], a, b, r["chunk"]))

    # The most frequent spelling; among equals, the first in sorted order.
    name = {e: max(sorted(c), key=c.get) for e, c in forms.items()}
    labels_of_key = {}
    for label, k in forms:
        labels_of_key.setdefault(k, []).append(label)
    return {
        "entities": sorted((label, name[(label, k)]) for label, k in forms),
        "mentions": sorted((c, e[0], name[e]) for c, e in mentions),
        "relations": sorted((t, name[a], name[b], c) for t, a, b, c in relations),
        "merged": {name[e]: sorted(c) for e, c in sorted(forms.items()) if len(c) > 1},
        "type_conflicts": {name[(labels[0], k)]: sorted(labels)
                           for k, labels in sorted(labels_of_key.items()) if len(labels) > 1},
        "dropped_relations": dropped,
    }


def load_extraction(driver, resolved: dict) -> None:
    """Write the resolved entities, their relationships, and MENTIONS.

    `resolved` is what `resolve_results` returned: the loader writes exactly the
    entities and relationships that were inspected, and resolves nothing itself.

    Each relationship is merged ONCE between two entities, and the chunk that states
    it is added to its `chunks` list only if absent. A relationship stated by three
    chunks is one relationship with three ids, not three parallel relationships --
    and a second load adds nothing. Labels and relationship types cannot be query
    parameters in Cypher 5, so they are written into the query text, from the
    declared model only.
    """
    for label in ENTITY_TYPES:
        run(driver, f"UNWIND $names AS name MERGE (:{label} {{name: name}})",
            names=[n for lab, n in resolved["entities"] if lab == label])
    for rel_type, (frm, to) in EXTRACTED_TYPES.items():
        rows = [{"a": a, "b": b, "chunk": c}
                for t, a, b, c in resolved["relations"] if t == rel_type]
        run(driver, f"""
            UNWIND $rows AS row
            MATCH (a:{frm} {{name: row.a}}), (b:{to} {{name: row.b}})
            MERGE (a)-[r:{check_type(rel_type)}]->(b)
            SET r.chunks = CASE
                WHEN r.chunks IS NULL THEN [row.chunk]
                WHEN row.chunk IN r.chunks THEN r.chunks
                ELSE r.chunks + row.chunk END""",
            rows=rows)
    for label in ENTITY_TYPES:
        run(driver, f"""
            UNWIND $rows AS row
            MATCH (c:Chunk {{id: row.chunk}}), (e:{label} {{name: row.name}})
            MERGE (c)-[:{check_type('MENTIONS')}]->(e)""",
            rows=[{"chunk": c, "name": n} for c, lab, n in resolved["mentions"] if lab == label])


def load_all(driver, chunks: list[dict], resolved: dict) -> None:
    """The whole load, in the lecture's order, from the output of `resolve_results`."""
    load_constraints(driver)
    clear_other_graphs(driver)
    load_text_layer(driver, chunks)
    load_extraction(driver, resolved)


def copy_vectors(driver, chunks: list[dict], collection: str = "week3_chunks") -> int:
    """Put Week 3's chunk vectors on the Chunk nodes. No embedding call.

    Chroma's ids differ from ours, so each stored chunk is matched on its source
    file and position, and its text is compared before the vector is used: a
    vector copied onto a different text would be a silent error.
    """
    from graph_vectors import _store_vectors, ensure_vector_index
    from vector_store import VectorStore

    store = VectorStore(name=collection)
    if store.count() == 0:
        print(f"  Chroma collection {collection!r} is empty; skipping vectors "
              "(run week3/ingest.py corpus/ --name week3_chunks to create it)")
        return 0
    ours = {(c["source"], c["index"]): c for c in chunks}
    rows = []
    for row in store.export():
        key = (row["metadata"].get("source"), row["metadata"].get("chunk_index"))
        chunk = ours.get(key)
        if chunk and chunk["text"] == row["chunk"]:
            rows.append({"key": chunk["id"], "vector": row["embedding"]})
    if rows:
        _store_vectors(driver, "Chunk", "id", rows)
        ensure_vector_index(driver, "chunk_embeddings", "Chunk")
    return len(rows)
