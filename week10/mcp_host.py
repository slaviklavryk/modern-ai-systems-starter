"""The notebook's side of MCP: the connection to the servers, and one turn of the agent.

    from mcp_host import connect_servers, ask
    client = connect_servers()                    # a client for each server in servers.json
    tools = await client.get_tools()              # every server's tools, as LangChain tools
    agent = create_agent(model, tools=tools)
    history = await ask(agent, "What distance does Chroma use by default?")

Tools taken from a server have no synchronous form: the agent runs with `ainvoke`, so
`ask` is awaited. In a notebook, `await` works at the top level of a cell.
"""

import json
import pathlib
import sys
import time
from typing import Optional

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "week8"))

from langchain_core.messages.utils import count_tokens_approximately  # noqa: E402
from langchain_mcp_adapters.client import MultiServerMCPClient  # noqa: E402

from agent_kit import COUNTER, answer, show  # noqa: E402

SERVERS = _HERE / "servers.json"       # the file MCP Inspector reads as well


def connect_servers(path: pathlib.Path = SERVERS) -> MultiServerMCPClient:
    """A client for every server listed in the file, by name. Nothing is sent yet: each
    request opens its own session with the server it is addressed to."""
    servers = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))["mcpServers"]
    return MultiServerMCPClient({name: {"transport": "streamable_http", "url": s["url"]}
                                 for name, s in servers.items()})


async def ask(agent, question: str, history: Optional[list] = None, *,
              quiet: bool = False) -> list:
    """One turn: prints its steps, its answer, its model calls and the time it took, and
    returns the whole conversation, to pass back as `history`."""
    sent = list(history or []) + [{"role": "user", "content": question}]
    before, started = COUNTER.calls, time.perf_counter()
    messages = (await agent.ainvoke({"messages": sent}))["messages"]
    seconds = time.perf_counter() - started
    if not quiet:
        *steps, last = messages[len(sent) - 1:]
        show(steps)
        answer(last)
        calls = COUNTER.calls - before
        print(f"{calls} model call{'' if calls == 1 else 's'} in this turn ({seconds:.0f} s), "
              f"{COUNTER.calls} since the kernel started")
        if last.type == "ai" and last.response_metadata.get("model_name"):
            print(f"answered by: {last.response_metadata['model_name']}")
        print(f"history: {len(messages)} messages, about "
              f"{count_tokens_approximately(messages):,} tokens")
    return messages
