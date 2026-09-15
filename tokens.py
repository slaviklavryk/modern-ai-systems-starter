"""Week 2 — tokens are not words.

Counts tokens with the same model the course uses, so the numbers match what you
see in `usage_metadata`.

    python tokens.py                    # the prepared comparison table
    python tokens.py "your own text"    # try anything

Note: `count_tokens` does NOT consume the ~6 requests/minute generation quota
(measured: 10 calls in 2.1s, no rate limiting), so run it as often as you like.

Why tokens are pieces of words
------------------------------
A model's vocabulary is a fixed table with one row per token, so it cannot hold
every word in every language (plus names, typos, identifiers). One row per
*character* would avoid that, but sequences get long and attention cost grows
with roughly the square of length.

Sub-word pieces are the compromise. The vocabulary is built by starting from
characters, repeatedly merging the most frequent adjacent pair in a big training
corpus, and stopping when it is full. So common sequences earned their own
token; rare ones never did and stay in pieces. Nothing is ever unrepresentable,
because anything unfamiliar can be spelled out from smaller fragments.

That one mechanism explains the whole table below: Ukrainian costs more because
the merge counting was done on a mostly-English corpus, long numbers cost ~1
token per digit because arbitrary digit strings are too varied to earn merges,
and `gemini-3.5-flash` fragments because that identifier was never in the corpus.

What this can and cannot show
-----------------------------
It shows token *counts*, accurately, for our model. It cannot show you *where*
the boundaries fall — Gemini's `compute_tokens`, which returns the individual
token strings, is not available on the free Developer API tier. For a visual
of the split, use a web playground (see the Week 2 lecture plan, section 5a);
just remember those use a different tokeniser, so their numbers will not match
these.
"""

import os
import sys

from dotenv import load_dotenv
from google import genai

# Windows consoles default to a legacy code page (cp1252 here), which raises
# UnicodeEncodeError the moment you print Cyrillic. Your corpus is Ukrainian,
# so you will meet this again in Week 3 -- this is the fix.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

MODEL = "gemini-3.5-flash"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# (label, text) -- paired rows are meant to be compared against each other.
SAMPLES = [
    ("English", "The model can only work with what is in its context."),
    ("Ukrainian", "Модель може працювати лише з тим, що є в її контексті."),
    ("Common word", "context"),
    ("Rare word", "antidisestablishmentarianism"),
    ("A long number", "3.14159265358979323846"),
    ("An identifier", "gemini-3.5-flash"),
    ("Some code", 'response = client.models.generate_content(model=MODEL)'),
]


def counttokens(text: str) -> int:
    return client.models.count_tokens(model=MODEL, contents=text).total_tokens


def report(label: str, text: str) -> None:
    tokens = counttokens(text)
    words = len(text.split())
    chars = len(text)
    per_word = f"{tokens / words:.2f}" if words else "-"
    shown = text if len(text) <= 46 else text[:43] + "..."
    print(f"  {label:<14} {chars:>5} {words:>6} {tokens:>7} {per_word:>9}   {shown}")


if __name__ == "__main__":
    print(f"\nmodel: {MODEL}\n")
    print(f"  {'':<14} {'chars':>5} {'words':>6} {'tokens':>7} {'tok/word':>9}   text")
    print("  " + "-" * 78)

    if len(sys.argv) > 1:
        report("yours", " ".join(sys.argv[1:]))
        print()
    else:
        for label, text in SAMPLES:
            report(label, text)
        print(
            "\n  Look at the first two rows. Same sentence, same meaning —\n"
            "  and a different number of tokens. Your corpus is Ukrainian.\n"
        )
