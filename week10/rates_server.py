"""An MCP server with one tool: the hryvnia exchange rate set by the National Bank of Ukraine.

    python week10/rates_server.py        # from the repository root; stop with Ctrl+C

It serves http://127.0.0.1:8001/mcp over streamable HTTP. The tool is the agent's
exchange_rate from week9/agent_stack.py, with the same description and the same body:
FastMCP's @mcp.tool takes the place of LangChain's @tool. It needs only an internet
connection.
"""

import logging
import datetime

import requests
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

NBU = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange"

# On Windows, asyncio logs every connection a client resets as an error with a long
# traceback. It is harmless, so it is kept out of the server's log.
logging.getLogger("asyncio").addFilter(
    lambda record: not (record.exc_info and record.exc_info[0] is ConnectionResetError))

mcp = FastMCP("rates", port=8001)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def exchange_rate(
    currency: str = Field(description="The currency's ISO 4217 code, such as EUR or USD"),
) -> str:
    """The official hryvnia exchange rate set by the National Bank of Ukraine for one
    currency, given its ISO 4217 code such as EUR or USD. Use it for any question about
    a current rate."""
    rows = requests.get(f"{NBU}?valcode={currency}&json", timeout=10).json()
    if not rows:                                # an unknown code returns an empty list
        return f"No NBU rate for {currency!r}."
    r = rows[0]
    return f"1 {r['cc']} = {r['rate']} UAH, set by the NBU for {r['exchangedate']}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
