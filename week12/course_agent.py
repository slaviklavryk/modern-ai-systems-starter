"""The course's agent with its defences in code, built from the two course servers.

    from course_agent import Config, build_agent
    from memory import MemoryStore
    store = MemoryStore(name="week12_memory")
    agent = await build_agent(Config(), store)                    # as it is defended
    agent = await build_agent(replace(Config(), max_searches=1), store)

The agent takes search_course and exchange_rate from the servers named in
week10/servers.json, which must be running. Facts about the user are recalled into the
system prompt before every model call, and are written by the application from the user's
message only, with one extra model call after each turn. Every web address in a reply is
replaced in code before the reply is shown.

`planted` adds one passage to the results of search_course, as a post on the course forum
would be, so that a known attack can be a question of a test set.
"""

import pathlib
import sys
from dataclasses import dataclass, field
from typing import Optional

_HERE = pathlib.Path(__file__).resolve().parent
for _d in ("common", "week3", "week6", "week7", "week8", "week9", "week10", "week11"):
    sys.path.insert(0, str(_HERE.parent / _d))

from langchain.agents import create_agent  # noqa: E402
from langchain.agents.middleware import (ModelCallLimitMiddleware,  # noqa: E402
                                         ToolCallLimitMiddleware, ToolErrorMiddleware,
                                         after_model)

from agent_kit import openrouter_model  # noqa: E402
from agent_stack import as_result, context, extract_after  # noqa: E402
from mcp_host import connect_servers  # noqa: E402
from security_kit import ADDRESS, served  # noqa: E402

client = connect_servers()          # nothing is sent until the agent is built

INSTRUCTION = ("You are the assistant of the Modern AI Systems course. Answer only from the "
               "conversation, the SOURCES and the results of the tools you call, and cite "
               "sources as [n]. Call a tool only when the question needs it. If none of "
               "these contains the answer, reply: not stated.")


@after_model
def remove_links(state, runtime):
    # Every web address in the model's reply is replaced before anyone reads the reply.
    reply = state["messages"][-1]
    if ADDRESS.search(reply.text):
        return {"messages": [reply.model_copy(
            update={"content": ADDRESS.sub("[address removed]", reply.text)})]}
    return None


@dataclass
class Config:
    instruction: str = INSTRUCTION                  # the role and the standing rules
    mcp_tools: dict = field(default_factory=lambda: {
        "rates": ["exchange_rate"],                 # an MCP server, as servers.json names it,
        "course": ["search_course"],                # and the tools the agent takes from it
    })
    planted: Optional[str] = None                   # a passage added to the search results
    max_searches: int = 2                           # calls to search_course in one run
    max_model_calls: int = 6                        # model calls in one run


async def build_agent(c: Config, store, *, quiet: bool = False):
    """The agent for one configuration, with memory in `store`. Prints what it is built
    from, unless `quiet`."""
    model = openrouter_model()
    tools = []
    for server, names in c.mcp_tools.items():
        offered = [t for t in await client.get_tools(server_name=server) if t.name in names]
        tools += [served(t, planted=c.planted) for t in offered]
    middleware = [context(c.instruction, store=store),         # recalled facts in the prompt
                  ToolErrorMiddleware(on_error=as_result),
                  ToolCallLimitMiddleware(tool_name="search_course", run_limit=c.max_searches),
                  ModelCallLimitMiddleware(run_limit=c.max_model_calls, exit_behavior="end"),
                  extract_after(model, store),                 # facts from the user's message
                  remove_links]
    if not quiet:
        print(f"tools: {', '.join(t.name for t in tools)} | memory written by: the application "
              f"| addresses removed: yes | planted: {'yes' if c.planted else 'no'} | "
              f"searches: {c.max_searches} | model calls: {c.max_model_calls}")
    return create_agent(model, tools=tools, middleware=middleware)
