"""Week 6 — run every retriever on a test set, and write the answers out for judging.

    python evaluate.py                       # all four retrievers and the router, once
    python evaluate.py --runs 2              # twice: generation is not deterministic
    python evaluate.py --only vector,hybrid  # some retrievers only
    python evaluate.py --test my_test.json   # your own test set, in the same format (Lab 2)

Writes `results/answers.md`: one table per question, the expected answer above it, and
each retriever's answer with an empty verdict column. Fill in the verdicts yourself:
correct, partly, wrong, or silent (no answer although one exists). Judging by a model
is Week 11's subject; here a person decides, with the cited chunks to hand.

Cost per run: one generation call per answer, plus one for each text-to-Cypher query
and each routing choice, on Lightning; one embedding per question for vector and hybrid.
Progress is saved after every answer to `results/answers.json`, and a rerun continues
where it stopped.
"""

import argparse
import json
import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from retrievers import answer  # noqa: E402  (also sets up the import paths)
from router import retrieve, route  # noqa: E402
from embedding_client import EmbeddingClient  # noqa: E402
from graph_db import connect  # noqa: E402
from llm_client import LLMClient  # noqa: E402

RETRIEVERS = ["vector", "name", "hybrid", "cypher"]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--test", type=pathlib.Path, default=_HERE / "test_set.json")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--only", default=",".join(RETRIEVERS),
                        help="Comma-separated retrievers to run")
    parser.add_argument("--no-router", action="store_true", help="Skip the routing choices")
    args = parser.parse_args()

    test_set = json.loads(args.test.read_text(encoding="utf-8"))["questions"]
    chosen = [r for r in args.only.split(",") if r in RETRIEVERS]
    out_dir = _HERE / "results"
    out_dir.mkdir(exist_ok=True)
    saved = out_dir / "answers.json"
    rows = json.loads(saved.read_text(encoding="utf-8")) if saved.exists() else []
    done = {(r["run"], r["id"], r["retriever"]) for r in rows}

    driver, emb, llm = connect(), EmbeddingClient(), LLMClient(provider="lightning")
    for run_no in range(1, args.runs + 1):
        for q in test_set:
            jobs = chosen + ([] if args.no_router else ["router"])
            for name in jobs:
                if (run_no, q["id"], name) in done:
                    continue
                if name == "router":
                    text = route(llm, q["question"])
                else:
                    got = retrieve(driver, emb, llm, q["question"], name)
                    text = answer(llm, q["question"], got["sources"])
                    if got.get("problem"):
                        text = f"(query refused or failed: {got['problem']})"
                rows.append({"run": run_no, "id": q["id"], "retriever": name, "answer": text})
                saved.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
                print(f"run {run_no} {q['id']:4} {name:7} {' '.join(text.split())[:140]}")
    driver.close()

    lines = [f"# Answers on `{args.test.name}`\n",
             "Verdicts: correct, partly, wrong, silent (no answer although one exists).\n"]
    for q in test_set:
        lines += [f"\n## {q['id']}. {q['question']}\n", f"**Expected:** {q['expected']}\n",
                  "| Run | Retriever | Answer | Verdict |", "|---|---|---|---|"]
        for r in sorted((r for r in rows if r["id"] == q["id"]), key=lambda r: (r["retriever"], r["run"])):
            lines.append(f"| {r['run']} | {r['retriever']} | {' '.join(r['answer'].split()).replace('|', '/')} | |")
    (out_dir / "answers.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nwritten: {out_dir / 'answers.md'}")


if __name__ == "__main__":
    main()
