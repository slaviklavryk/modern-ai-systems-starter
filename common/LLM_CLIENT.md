# The LLM client: switching between Gemini and Lightning AI

This describes `llm_client.py`, the module `prompt_lab.py` and `context_lab.py` both
call instead of talking to a model provider directly. It exists because the Gemini
free tier's ceiling of roughly 6 requests per minute can stall a working session.
Lightning AI is a fallback for that situation, not a replacement for Gemini: the Week 2
material is written and measured against Gemini, and Lightning is a second, verified
place to run the same notebooks when the quota is the obstacle.

---

## 1. How to switch

Everything runs on Gemini unless `.env` says otherwise. To switch to Lightning, add two
lines to `.env`:

```
LLM_PROVIDER=lightning
LIGHTNING_API_KEY=your-key-here
```

Remove the `LLM_PROVIDER` line, or set it back to `gemini`, to switch back. No notebook
cell needs to change either way: `prompt_lab.ipynb` and `context_lab.ipynb` both import
`ask()` (and, in Week 2, `show()`, `counttokens()`, `calls()`) from their respective helper
modules, and those modules read the active provider once, when they are imported.

A Lightning API key is obtained from the Lightning AI dashboard, under Global Settings
→ Keys. No other credential is required: `LIGHTNING_USER_ID` and `LIGHTNING_TEAMSPACE`
were needed only by an earlier, abandoned approach and play no part in the current
implementation.

---

## 2. What `llm_client.py` provides

One class, `LLMClient`, with two methods.

```python
from llm_client import LLMClient

llm = LLMClient()                        # reads LLM_PROVIDER from .env
llm = LLMClient(provider="lightning")     # or choose one explicitly

result = llm.chat(
    "What is assessed in Lab 2?",
    system="Answer using only the sources given.",
    temperature=0,
    schema=list[SomeModel],
    max_tokens=200,
    thinking="low",
)
```

`chat()` returns a `ChatResult`, the same shape regardless of which provider answered:

| Field | Contents |
|---|---|
| `.text` | The answer, as a string |
| `.usage.prompt_tokens` | Tokens the request cost |
| `.usage.thinking_tokens` | Tokens spent reasoning, before the visible answer |
| `.usage.answer_tokens` | Tokens in the visible answer |
| `.parsed` | Populated only when `schema` was supplied: typed objects, not a string to parse |
| `.raw` | The untouched provider response, for debugging |

`count_tokens(text)` returns a token count for a string. On Gemini this is free and
exact. Lightning has no equivalent endpoint; see §4.

---

## 3. Where this is used

`prompt_lab.py` (Week 1) and `context_lab.py` (Week 2) both build their public
functions — `ask()`, `repeat()`, `show()`, `counttokens()`, `render()`, `calls()` — on top of
one shared `LLMClient` instance created when the module is imported. Neither module
calls a provider SDK directly any more. The notebooks call these functions exactly as
before; switching providers is a `.env` change, not a code change.

---

## 4. What is identical between providers, and what is not

Verified 2026-09-13, `gemini-3.5-flash` against `openai/gpt-5-nano` (Lightning's
default model in this client).

**Identical in effect.**

| Feature | Notes |
|---|---|
| A plain question, with or without a system instruction | |
| Temperature | |
| Structured output | Gemini accepts a bare `list[Model]` schema directly. Lightning requires the top-level schema to be an object (a bare array is rejected, HTTP 400), so `llm_client.py` wraps a list schema as `{"items": [...]}` before sending it and unwraps the result before returning `.parsed`. The call site sees no difference |
| A three-way token split (prompt / thinking / answer) on every call | Gemini's `usage_metadata` and Lightning's `usage.completion_tokens_details.reasoning_tokens` are different fields with the same meaning |
| Thinking-token variance between identical calls | Confirmed on both: two identical prompts to Lightning produced 0 and 64 reasoning tokens; this is the same phenomenon Week 2 measures on Gemini, not a defect introduced by the wrapper |

**Not identical.**

| Feature | Gemini | Lightning |
|---|---|---|
| Free token counting | `count_tokens()` does not draw on the request quota (measured: 10 calls in 2.1 seconds) | No equivalent endpoint exists. `counttokens()` falls back to an estimate of one token per four characters, printed as "(rough estimate)" rather than presented as a measured figure. Treat any total shown while `LLM_PROVIDER=lightning` as approximate |
| The thinking-level dial | `thinking="minimal"` through `"high"` produces a measured, reliable effect: the Week 2 deck's own table shows `MINIMAL` failing a multi-step problem and `LOW` correcting it | The equivalent parameter, `reasoning_effort`, is accepted without error but its effect was not observed reliably: `MINIMAL` and `LOW` produced the same answer and the same reasoning-token count in one run, and separate identical calls with no such parameter at all varied between 0 and 64 reasoning tokens regardless. Do not use Lightning to run the Week 2 thinking-dial demonstration in front of a class |

---

## 5. If Lightning stops authenticating

`litai`, Lightning's own Python package, was tried first and abandoned: its `LLM` class
sends `Authorization: Basic base64(user_id:api_key)`, which the server rejects
regardless of credentials, a confirmed bug in the versions tested (`litai` 0.0.10,
`lightning_sdk` 2026.4.23) rather than a configuration problem. `llm_client.py` instead
calls the documented REST endpoint directly:

```
POST https://lightning.ai/api/v1/chat/completions
Authorization: Bearer <LIGHTNING_API_KEY>
```

This is the same request shape shown in Lightning's own documentation, using the
`requests` library rather than `litai`. If this endpoint is renamed or its
authentication requirements change, `llm_client.py` is the only file that needs to be
updated: neither `prompt_lab.py` nor `context_lab.py` refers to Lightning directly.
