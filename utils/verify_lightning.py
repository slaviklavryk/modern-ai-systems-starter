"""Does Lightning AI work with our key?

    .venv\\Scripts\\python utils\\verify_lightning.py

Put your key in `.env` next to GEMINI_API_KEY:

    LIGHTNING_API_KEY=...

Why this calls the REST API directly instead of using `litai`
---------------------------------------------------------------
`litai` (and the `lightning_sdk` it wraps) could not authenticate at all in
testing on 2026-09-13: its own `LLM(...)` class sends
`Authorization: Basic base64(user_id:api_key)`, and the server rejects that
with 401 regardless of what LIGHTNING_USER_ID is set to. The key itself is
fine -- this script's plain `Authorization: Bearer <api_key>` against the
documented endpoint below works first try. This is a bug in the installed
package (litai 0.0.10, lightning_sdk 2026.4.23), not a setup problem.

This uses `/api/v1/chat/completions` -- the documented, OpenAI-compatible
endpoint -- rather than the internal one `lightning_sdk` calls, which also
needed a teamspace/billing-project id and a hardcoded per-model assistant id
neither of which are necessary here.
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("LIGHTNING_API_KEY")
if not API_KEY:
    raise SystemExit("No LIGHTNING_API_KEY in .env  (Lightning AI -> Global Settings -> Keys)")

MODEL = "openai/gpt-5-nano"

response = requests.post(
    url="https://lightning.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={
        "model": MODEL,
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": "Reply with exactly: lightning ok"}]}
        ],
    },
)
response.raise_for_status()
result = response.json()

print(f"model:  {result['model']}")
print(f"answer: {result['choices'][0]['message']['content']!r}")
print(f"usage:  {result['usage']}")

# Same three-way split Week 2 teaches for Gemini's usage_metadata:
#   prompt_tokens  == prompt_token_count
#   completion_tokens_details.reasoning_tokens  == thoughts_token_count
#   completion_tokens - reasoning_tokens  == candidates_token_count
reasoning = result["usage"]["completion_tokens_details"]["reasoning_tokens"]
print(f"reasoning tokens: {reasoning}")
print("  Run this twice: two identical calls, same trivial prompt, produced 0 and 64 in")
print("  testing on 2026-09-13 -- the same run-to-run variance Week 2 measures on Gemini.")
