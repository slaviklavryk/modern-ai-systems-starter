"""An MCP server for the course: three tools that read the course graph, the assistant's
instruction as a resource, and a prompt that asks for a topic to be explained.

    python week10/course_server.py       # from the repository root; stop with Ctrl+C

It serves http://127.0.0.1:8002/mcp over streamable HTTP. The tools are the agent's from
week9/agent_stack.py, with the same descriptions and the same bodies: FastMCP's @mcp.tool
takes the place of LangChain's @tool, and search_course uses the hybrid retriever. They
share one Neo4j driver and one embedding client, opened when the server starts: Neo4j must
be running, with the graph that week6/build_graph.py builds, and GEMINI_API_KEY must be in
.env.
"""

import logging
import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "week6"))

from mcp.server.fastmcp import FastMCP  # noqa: E402
from mcp.server.fastmcp.prompts import base  # noqa: E402
from mcp.types import ToolAnnotations  # noqa: E402
from pydantic import Field  # noqa: E402

from retrievers import by_name, hybrid, read  # noqa: E402  (puts the other folders on the path)
from embedding_client import EmbeddingClient  # noqa: E402
from graph_db import connect  # noqa: E402
from vector_check import require_same_model  # noqa: E402

INSTRUCTION = ("You are the assistant of the Modern AI Systems course. Answer only from the "
               "conversation, the SOURCES and the results of the tools you call, and cite "
               "sources as [n]. Call a tool only when the question needs it. If none of "
               "these contains the answer, reply: not stated.")
DOCUMENTS_MENTIONING = """
MATCH (d:Document)-[:HAS_CHUNK]->(:Chunk)-[:MENTIONS]->(e:Entity {name: $name})
RETURN DISTINCT d.name AS document ORDER BY document"""
READ_ONLY = ToolAnnotations(readOnlyHint=True)

# On Windows, asyncio logs every connection a client resets as an error with a long
# traceback. It is harmless, so it is kept out of the server's log.
logging.getLogger("asyncio").addFilter(
    lambda record: not (record.exc_info and record.exc_info[0] is ConnectionResetError))

driver = connect()
emb = EmbeddingClient()
require_same_model(driver, emb)          # refuses to search with another embedding model

mcp = FastMCP("course", port=8002)


# Tools: the model decides when to call them.

@mcp.tool(annotations=READ_ONLY)
def search_course(
    query: str = Field(description="What to search the course materials for"),
) -> str:
    """Search the course materials (lectures, practicals and plans) for passages and
    facts relevant to the query. Use it for any question about the course."""
    return "\n".join(hybrid(driver, emb, query)) or "Nothing found."


@mcp.tool(annotations=READ_ONLY)
def facts_by_name(
    query: str = Field(description="A question or phrase that names tools, topics or labs"),
) -> str:
    """Facts from the course graph about tools, topics and labs named in the query.
    Returns nothing if the query names none."""
    facts = by_name(driver, query)
    return "\n".join(facts) if facts else "No facts: the query names nothing in the graph."


@mcp.tool(annotations=READ_ONLY)
def documents_mentioning(
    name: str = Field(description="The name as the course graph spells it, such as 'Chroma'"),
) -> str:
    """List the course documents that mention a tool, topic or lab, given its name as
    the course graph spells it, for example 'Chroma'."""
    rows = read(driver, DOCUMENTS_MENTIONING, name=name)
    return "\n".join(r["document"] for r in rows) or f"No documents mention {name!r}."


# A resource: the application decides when to read it.

@mcp.resource(
    "course://instruction",
    name="instruction",
    title="The course assistant's instruction",
    description="The standing instruction of the course assistant: answer only from the "
                "sources and the tools' results, and cite them.",
    mime_type="text/plain",
)
def instruction() -> str:
    return INSTRUCTION


# A prompt: the user decides when to use it.

@mcp.prompt(
    name="explain_topic",
    title="Explain a course topic",
    description="Ask for one course topic to be explained from the course materials, with "
                "sources.",
)
def explain_topic(
    topic: str = Field(description="The course topic to explain, such as 'chunking'"),
) -> list[base.Message]:
    return [base.UserMessage(f"Explain {topic} from the course materials, citing each source.")]


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
