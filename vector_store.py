"""Week 3 — dense retrieval: store chunk embeddings, search them by similarity.

    from vector_store import VectorStore
    store = VectorStore()
    store.add(chunks)                      # embeds and stores every chunk, once
    results = store.search("a question")   # embeds the question, searches the index

This is the "ingest once, query every call" half of the retrieval pipeline from
week-03-lecture-plan.md §6: `add()` is the ingestion-time work, `search()` is what
runs on every question.

The store is PERSISTENT, and that matters more than it looks
--------------------------------------------------------------
Embeddings are written to `./chroma/` on disk and survive the process. Embed a
corpus once, with `python ingest.py`, and every notebook and script afterwards
opens the same index without paying for it again.

This is not a performance nicety. `gemini-embedding-001` allows roughly 100 texts
per minute (measured 2026-09-14), so a 3,000-chunk corpus is about half an hour of
ingest. An in-memory store would spend that again on every kernel restart.

`reset=True` clears the collection first -- which is what you want after changing
chunk size, and never want otherwise.

Chroma's default distance is NOT cosine
-----------------------------------------
Confirmed 2026-09-13: an unconfigured Chroma collection uses squared Euclidean
distance. This course teaches and measures cosine similarity, so the collection
below is created with `metadata={"hnsw:space": "cosine"}` explicitly. Without that
line, `search()`'s scores would not be the metric taught in the lecture, silently.
"""

from typing import Optional

import chromadb

from embedding_client import EmbeddingClient


class VectorStore:
    def __init__(
        self,
        embedder: Optional[EmbeddingClient] = None,
        name: str = "chunks",
        *,
        path: str = "./chroma",
        reset: bool = False,
    ):
        self.embedder = embedder or EmbeddingClient()
        self._client = chromadb.PersistentClient(path=path)
        if reset:
            try:
                self._client.delete_collection(name)
            except Exception:
                pass  # nothing stored under that name yet
        self._collection = self._client.get_or_create_collection(
            name,
            # Explicitly NONE. We pass our own vectors to add() and search(),
            # so Chroma must not record an embedding function of its own --
            # left unset it stores "default", meaning its 384-dimension ONNX
            # model, while the vectors here are 3072 from gemini-embedding-001.
            # Nothing in this file notices, because it never asks Chroma to
            # embed anything; an outside tool opening the collection does.
            embedding_function=None,
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        """How many chunks are already indexed. Zero means you need ingest.py."""
        return self._collection.count()

    def peek(self, n: int = 5) -> list[dict]:
        """The first n stored chunks, without searching for anything.

        `search()` answers "what is relevant to this question". This answers
        "what is actually in there" -- which is the one you want when a chunk
        boundary looks wrong, or when a retrieved chunk is not what you expected.
        """
        got = self._collection.get(limit=n)
        return [{"id": i, "chunk": d} for i, d in zip(got["ids"], got["documents"])]

    def collections(self) -> list[str]:
        """Every collection name stored at this path.

        Run this when count() is 0 but ingest.py said it succeeded: almost
        always the name here and the name passed to `ingest.py --name` differ.
        """
        return [c.name for c in self._client.list_collections()]

    def add(self, chunks: list[str]) -> None:
        """Embed every chunk once and store it. Ingestion-time work.

        Slow and rate-limited on first run -- see the module docstring. Call it
        from `ingest.py`, not from a notebook cell you will re-run.
        """
        vectors = self.embedder.embed_batch(chunks, task_type="RETRIEVAL_DOCUMENT")
        start = self._collection.count()
        ids = [str(start + i) for i in range(len(chunks))]
        self._collection.add(ids=ids, embeddings=vectors, documents=chunks)

    def search(self, query: str, *, n_results: int = 5) -> list[dict]:
        """Embed the question and search the index. Query-time work.

        Returns a list of {"chunk": str, "distance": float} ordered nearest
        first, where distance is 1 − cosine similarity (0 = identical, larger
        = less similar -- see week-03-lecture-plan.md §3 for the definition).
        """
        query_vector = self.embedder.embed(query, task_type="RETRIEVAL_QUERY")
        result = self._collection.query(query_embeddings=[query_vector], n_results=n_results)
        return [
            {"chunk": doc, "distance": dist}
            for doc, dist in zip(result["documents"][0], result["distances"][0])
        ]


if __name__ == "__main__":
    # Smoke test: three chunks, one clearly relevant to the question, one not.
    # Its own collection, reset each run, so it never pollutes a real corpus.
    store = VectorStore(name="smoke_test", reset=True)
    store.add([
        "The model can only work with what is in its context.",
        "Everything in the context window is paid for on every call.",
        "A recipe for making bread starts with mixing flour and water.",
    ])
    for row in store.search("what does the model see?", n_results=3):
        print(f"  distance={row['distance']:.4f}  {row['chunk']}")
