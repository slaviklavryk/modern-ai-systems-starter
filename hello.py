"""Week 1, Step 4 — your first model call.

Run it:  python hello.py

Expected output: the words `setup complete`, then a block of token counts.
Look at `thoughts_token_count`. We will come back to it in Week 2.
"""

import os

from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-flash-latest",
    contents="Reply with exactly: setup complete",
)

print(response.text)
print(response.usage_metadata)
