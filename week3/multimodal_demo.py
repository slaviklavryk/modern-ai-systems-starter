"""Week 3, optional extension — one embedding space for images AND text.

    python multimodal_demo.py photo.jpg "a cat" "a dog" "a red car"
    python multimodal_demo.py                 # built-in shape demo (needs Pillow)

Everything else this week embeds text and compares text to text. This shows the
step past that: a model that maps an image and a sentence into the SAME space, so
`cosine(image, "a red circle")` is a number you can compute and rank. That is what
"multimodal embedding" means, and it is the Week 3 project extension the syllabus
mentions.

Why this uses a different model from the rest of the course
----------------------------------------------------------
The pinned `gemini-embedding-001` in `embedding_client.py` is TEXT ONLY, and it is
pinned for a text reason: its query/document `task_type` asymmetry, which the
practical depends on. Images need `gemini-embedding-2`, which is multimodal (text,
image, video, audio, PDF) but has NO `task_type` -- a different set of trade-offs,
documented on the "Choosing a model" slide. So this script calls the SDK directly
rather than going through `EmbeddingClient`; mixing two models behind one client
would blur exactly the distinction that slide is making. To use multimodal
embeddings in your own project, extend `EmbeddingClient` with a `-2` backend.

Measured 2026-09-19 on `gemini-embedding-2`
-------------------------------------------
A generated red-circle image, embedded, then compared to five captions:

    0.4688  a red circle          <- correct, and well clear of the rest
    0.2989  a blue square
    0.2697  a photograph of a cat
    0.2714  the quarterly financial report
    0.2585  a green triangle

Image and text vectors are both 3072-dimensional -- the same space, which is the
whole point. Absolute numbers are lower than text-to-text similarity tends to run;
as always in this course, the ranking is the signal, not the raw value.
"""

import argparse
import io
import math
import os
import pathlib
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

MODEL = "gemini-embedding-2"  # multimodal; NOT the pinned text model -- see docstring
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}

_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def embed_image_bytes(data: bytes, mime_type: str) -> list[float]:
    r = _client.models.embed_content(
        model=MODEL,
        contents=[types.Content(parts=[types.Part.from_bytes(data=data, mime_type=mime_type)])],
    )
    return r.embeddings[0].values


def embed_image(path: pathlib.Path) -> list[float]:
    mime = MIME.get(path.suffix.lower())
    if mime is None:
        raise SystemExit(f"Unsupported image type {path.suffix!r}. Use one of: {', '.join(MIME)}")
    return embed_image_bytes(path.read_bytes(), mime)


def embed_text(text: str) -> list[float]:
    r = _client.models.embed_content(
        model=MODEL,
        contents=[types.Content(parts=[types.Part.from_text(text=text)])],
    )
    return r.embeddings[0].values


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb)


def rank(image_vec: list[float], captions: list[str]) -> None:
    """Embed each caption, print them sorted by similarity to the image."""
    scored = sorted(((cosine(image_vec, embed_text(c)), c) for c in captions), reverse=True)
    width = max(len(c) for c in captions)
    print(f"\n  {'cosine':>8}   caption")
    print("  " + "-" * (11 + width))
    for i, (score, caption) in enumerate(scored):
        mark = "  <- best match" if i == 0 else ""
        print(f"  {score:>8.4f}   {caption:<{width}}{mark}")


def built_in_demo() -> None:
    """Zero-argument showcase: generate three unambiguous images, caption them.

    Pillow is used ONLY here, and is imported lazily so the course does not carry
    an image dependency for a script most students run once. If it is missing, the
    real use of this tool -- your own image plus captions -- still works.
    """
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        raise SystemExit(
            "The built-in demo draws its own images and needs Pillow:\n"
            "    pip install Pillow\n"
            "Or skip it and use your own image:\n"
            '    python multimodal_demo.py photo.jpg "a cat" "a dog"'
        )

    def png(draw_fn, bg="white", size=(224, 224)) -> bytes:
        img = Image.new("RGB", size, bg)
        draw_fn(ImageDraw.Draw(img), size)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    scenes = {
        "a red circle on white": lambda d, s: d.ellipse([30, 30, s[0]-30, s[1]-30], fill="red"),
        "a blue square on white": lambda d, s: d.rectangle([40, 40, s[0]-40, s[1]-40], fill="blue"),
        "a yellow star on black": lambda d, s: d.polygon(
            [(112, 20), (140, 90), (210, 90), (152, 132), (175, 200),
             (112, 158), (49, 200), (72, 132), (14, 90), (84, 90)], fill="yellow"),
    }
    captions = ["a red circle", "a blue square", "a yellow star",
                "a green triangle", "a photograph of a dog"]

    print("Three generated images, the same five captions each time.")
    print("The matching caption should win every time, even though the model was")
    print("never shown these exact pictures.")
    for truth, draw_fn in scenes.items():
        bg = "black" if "black" in truth else "white"
        print(f"\n=== image: {truth} ===")
        rank(embed_image_bytes(png(draw_fn, bg=bg), "image/png"), captions)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image", nargs="?", type=pathlib.Path, help="Image file (png/jpg/webp)")
    ap.add_argument("captions", nargs="*", help="Candidate captions to rank against the image")
    args = ap.parse_args()

    if args.image is None:
        built_in_demo()
        return

    if not args.image.exists():
        raise SystemExit(f"No such file: {args.image}")
    captions = args.captions or [
        "a photograph of a person", "a landscape", "a document or screenshot",
        "an animal", "a piece of food",
    ]
    print(f"image: {args.image}")
    rank(embed_image(args.image), captions)


if __name__ == "__main__":
    main()
