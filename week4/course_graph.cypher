// Week 4, Part 6 onwards: this course, as a graph.
//
//   python load_graph.py            loads it (run it twice: the counts do not change)
//   python load_graph.py --reset    empties the database first, then loads it
//
// Or paste it into Neo4j Browser at http://localhost:7474.
//
// The Cypher basics (Parts 2 to 5) use Neo4j's standard Movies graph. This graph
// is the one the vector index is built on, for two reasons. Every Topic carries a
// description written to be embedded, where the Movies graph has only one-line
// taglines. And it describes the same material as the Week 3 sample corpus, so
// vector and graph retrieval can be compared on one source. The domain is one
// every student already knows: weeks, the topics they cover, which topic builds
// on which, the deliverables that assess them, and the tools they use.
//
// How it is written, and why
// --------------------------
// 1. Constraints first. A uniqueness constraint on each key both enforces it and
//    gives MERGE an index to find an existing node by. Community edition supports
//    uniqueness constraints only; existence, type and key constraints are
//    Enterprise features.
// 2. Nodes next, each MERGEd on its key alone, with the other properties SET
//    afterwards. Running the file again finds every node instead of creating it.
// 3. Relationships last, MERGEd between nodes that already exist. Never MERGE a
//    whole pattern such as (w:Week {number: 3})-[:COVERS]->(t:Topic {name: ...}):
//    if the relationship is missing, MERGE creates the ENTIRE pattern, nodes
//    included -- duplicates without constraints, an error with them.
//
// The result is idempotent: load it once or ten times, the graph is the same.
// That is the property Week 5's re-seedable ingest.py depends on.
//
// Statements end with ';' at the end of a line. Keep semicolons out of strings.

// ---------------------------------------------------------------- constraints

CREATE CONSTRAINT week_number IF NOT EXISTS FOR (w:Week) REQUIRE w.number IS UNIQUE;
CREATE CONSTRAINT topic_name IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT deliverable_name IF NOT EXISTS FOR (d:Deliverable) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT tool_name IF NOT EXISTS FOR (t:Tool) REQUIRE t.name IS UNIQUE;

// ---------------------------------------------------------------- weeks

MERGE (w:Week {number: 1}) SET w.title = "Modern AI and the AI software stack";
MERGE (w:Week {number: 2}) SET w.title = "LLMs, tokens, context, reasoning, and prompting";
MERGE (w:Week {number: 3}) SET w.title = "Embeddings, semantic search, and RAG";
MERGE (w:Week {number: 4}) SET w.title = "Neo4j: graphs, Cypher, and vector search";
MERGE (w:Week {number: 5}) SET w.title = "Knowledge graphs and Neo4j for AI";
MERGE (w:Week {number: 6}) SET w.title = "Graph RAG";
MERGE (w:Week {number: 7}) SET w.title = "Agents, tools, and integration";
MERGE (w:Week {number: 8}) SET w.title = "Agent architectures, skills, and workflows";
MERGE (w:Week {number: 9}) SET w.title = "Memory";
MERGE (w:Week {number: 10}) SET w.title = "Advanced agentic systems";
MERGE (w:Week {number: 11}) SET w.title = "Reliable AI systems";
MERGE (w:Week {number: 12}) SET w.title = "Final AI systems";

// ---------------------------------------------------------------- topics
// The description is the text that Part 6 of the notebook embeds.

MERGE (t:Topic {name: "Foundation models"}) SET t.description = "General-purpose models pretrained on broad data and adapted to a task by prompting rather than by retraining.";
MERGE (t:Topic {name: "The AI application stack"}) SET t.description = "The layers between a user and a model: the application, context and orchestration, knowledge, tools, memory, and the model itself.";
MERGE (t:Topic {name: "Tokens"}) SET t.description = "The sub-word fragments a language model reads and writes. Context size, cost, and rate limits are all measured in tokens.";
MERGE (t:Topic {name: "Context window"}) SET t.description = "Everything the model can see in one call. Every token in it is paid for on every call, and irrelevant material degrades the answer.";
MERGE (t:Topic {name: "Reasoning and thinking budgets"}) SET t.description = "Hidden reasoning tokens a model spends before answering, billed like output and controlled by a thinking level.";
MERGE (t:Topic {name: "Temperature"}) SET t.description = "The setting that rescales the probability distribution over next tokens before sampling, trading repeatability for variety.";
MERGE (t:Topic {name: "Prompt and context design"}) SET t.description = "Assembling the system instruction, task, format, examples, and sources that make up a model's context, most of it placed there by software.";
MERGE (t:Topic {name: "Structured output"}) SET t.description = "Constraining a model to return data in a declared schema rather than asking politely for JSON.";
MERGE (t:Topic {name: "Hallucination"}) SET t.description = "Fluent, confident output that is not supported by any source, with several distinct causes that need different remedies.";
MERGE (t:Topic {name: "Embeddings"}) SET t.description = "Fixed-length vectors that represent the meaning of a text, so that texts with similar meaning lie close together.";
MERGE (t:Topic {name: "Cosine similarity"}) SET t.description = "The cosine of the angle between two vectors, which compares their direction and ignores their length.";
MERGE (t:Topic {name: "Chunking"}) SET t.description = "Splitting documents into overlapping passages small enough to embed and retrieve one at a time.";
MERGE (t:Topic {name: "Vector search"}) SET t.description = "Finding the stored passages nearest in meaning to a question, rather than those that share its keywords.";
MERGE (t:Topic {name: "Retrieval-augmented generation"}) SET t.description = "Retrieving relevant passages and placing them in the model's context so that it answers from them.";
MERGE (t:Topic {name: "Grounding and citation"}) SET t.description = "Instructing the model to answer only from the supplied sources, cite them, and say when they do not contain the answer.";
MERGE (t:Topic {name: "Property graph model"}) SET t.description = "Nodes with labels, typed and directed relationships, and properties stored on both.";
MERGE (t:Topic {name: "Cypher"}) SET t.description = "Neo4j's declarative query language, in which a query is a pattern of nodes and relationships to be matched.";
MERGE (t:Topic {name: "Graph traversal"}) SET t.description = "Following relationships from node to node, including paths whose length is not known in advance.";
MERGE (t:Topic {name: "Idempotent loading"}) SET t.description = "Loading data with MERGE on a key so that running the same load twice produces the same graph.";
MERGE (t:Topic {name: "Vector index in Neo4j"}) SET t.description = "An approximate nearest-neighbour index over embeddings stored on nodes, which gives a query a starting point by meaning.";
MERGE (t:Topic {name: "Graph modelling"}) SET t.description = "Deciding whether a fact becomes a node, a relationship, or a property, working backwards from the questions the graph must answer.";
MERGE (t:Topic {name: "Knowledge graphs"}) SET t.description = "Graphs of the entities in a domain and the explicit relationships between them.";
MERGE (t:Topic {name: "Entity extraction"}) SET t.description = "Identifying entities and relationships in unstructured text, often with a model producing structured output.";
MERGE (t:Topic {name: "Graph RAG"}) SET t.description = "Retrieval that follows relationships in a graph as well as similarity, for questions whose answer spans connected facts.";
MERGE (t:Topic {name: "Hybrid retrieval"}) SET t.description = "Combining vector search and graph traversal in one retrieval step.";
MERGE (t:Topic {name: "Tool calling"}) SET t.description = "Letting a model request a function call with arguments in a declared schema, which the program executes.";
MERGE (t:Topic {name: "The agent loop"}) SET t.description = "The cycle in which the model decides, a tool executes, and the result returns to the context for the next decision.";
MERGE (t:Topic {name: "MCP"}) SET t.description = "The Model Context Protocol, a standard way to connect tools and data sources to a model without hand-wiring each one.";
MERGE (t:Topic {name: "Tool safety"}) SET t.description = "The risk that arises when an agent has private data, untrusted input, and a way to act or communicate outward: the lethal trifecta.";
MERGE (t:Topic {name: "Workflows versus agents"}) SET t.description = "Choosing between a fixed sequence of steps written in code and a loop in which the model chooses the steps.";
MERGE (t:Topic {name: "Skills"}) SET t.description = "Packaged procedures and instructions a model can load when a task calls for them, rather than a single function.";
MERGE (t:Topic {name: "Provider abstraction"}) SET t.description = "One interface over several model providers, so that a change of provider or an outage is a configuration change.";
MERGE (t:Topic {name: "Agent memory"}) SET t.description = "Information that persists across interactions, stored explicitly or retrieved, and what happens when it is wrong or stale.";
MERGE (t:Topic {name: "Multi-agent systems"}) SET t.description = "Several cooperating agents with separate roles, and when that structure is justified over a single agent.";
MERGE (t:Topic {name: "Evaluation with a gold set"}) SET t.description = "Measuring a system against a fixed set of queries with expected properties instead of inspecting individual outputs.";
MERGE (t:Topic {name: "LLM-as-judge"}) SET t.description = "Using a model to grade another model's outputs, and the measurable biases that grading introduces.";
MERGE (t:Topic {name: "Prompt injection"}) SET t.description = "Instructions hidden in retrieved documents or tool results that attempt to redirect the model.";
MERGE (t:Topic {name: "Cost and rate limits"}) SET t.description = "Token accounting, caching, latency, and per-minute quotas, which together form a system's operating envelope.";
MERGE (t:Topic {name: "Integrated AI system"}) SET t.description = "A complete application combining retrieval, graphs, tools, memory, and evaluation, with its design decisions justified.";

// ---------------------------------------------------------------- deliverables

MERGE (d:Deliverable {name: "Lab 1"}) SET d.title = "Vector RAG", d.weight = 20;
MERGE (d:Deliverable {name: "Lab 2"}) SET d.title = "Knowledge graph and Graph RAG", d.weight = 25;
MERGE (d:Deliverable {name: "Lab 3"}) SET d.title = "Agent, tools, and memory", d.weight = 25;
MERGE (d:Deliverable {name: "Final project"}) SET d.title = "Integrated AI system and presentation", d.weight = 30;

// ---------------------------------------------------------------- tools

MERGE (t:Tool {name: "Gemini API"}) SET t.description = "The course's model interface, used through the Google Gen AI SDK on the Flash tier.";
MERGE (t:Tool {name: "Gemini embeddings"}) SET t.description = "The hosted, multilingual embedding model behind embedding_client.py.";
MERGE (t:Tool {name: "Chroma"}) SET t.description = "An embedded vector store that runs inside the Python process and persists to a folder.";
MERGE (t:Tool {name: "Neo4j"}) SET t.description = "A graph database, run locally in Docker and queried in Cypher.";
MERGE (t:Tool {name: "Docker"}) SET t.description = "Runs services such as Neo4j in containers from one shared compose file.";
MERGE (t:Tool {name: "DeepEval"}) SET t.description = "A pytest-based framework for evaluating model outputs.";
MERGE (t:Tool {name: "Groq"}) SET t.description = "A second, OpenAI-compatible model provider behind the provider abstraction.";
MERGE (t:Tool {name: "Ollama"}) SET t.description = "Runs a small model locally, as an offline fallback.";

// ---------------------------------------------------------------- COVERS: which week teaches which topic

MATCH (w:Week {number: 1}) MATCH (t:Topic) WHERE t.name IN ["Foundation models", "The AI application stack"] MERGE (w)-[:COVERS]->(t);
MATCH (w:Week {number: 2}) MATCH (t:Topic) WHERE t.name IN ["Tokens", "Context window", "Reasoning and thinking budgets", "Temperature", "Prompt and context design", "Structured output", "Hallucination"] MERGE (w)-[:COVERS]->(t);
MATCH (w:Week {number: 3}) MATCH (t:Topic) WHERE t.name IN ["Embeddings", "Cosine similarity", "Chunking", "Vector search", "Retrieval-augmented generation", "Grounding and citation"] MERGE (w)-[:COVERS]->(t);
MATCH (w:Week {number: 4}) MATCH (t:Topic) WHERE t.name IN ["Property graph model", "Cypher", "Graph traversal", "Idempotent loading", "Vector index in Neo4j"] MERGE (w)-[:COVERS]->(t);
MATCH (w:Week {number: 5}) MATCH (t:Topic) WHERE t.name IN ["Graph modelling", "Knowledge graphs", "Entity extraction"] MERGE (w)-[:COVERS]->(t);
MATCH (w:Week {number: 6}) MATCH (t:Topic) WHERE t.name IN ["Graph RAG", "Hybrid retrieval"] MERGE (w)-[:COVERS]->(t);
MATCH (w:Week {number: 7}) MATCH (t:Topic) WHERE t.name IN ["Tool calling", "The agent loop", "MCP", "Tool safety"] MERGE (w)-[:COVERS]->(t);
MATCH (w:Week {number: 8}) MATCH (t:Topic) WHERE t.name IN ["Workflows versus agents", "Skills", "Provider abstraction"] MERGE (w)-[:COVERS]->(t);
MATCH (w:Week {number: 9}) MATCH (t:Topic) WHERE t.name IN ["Agent memory"] MERGE (w)-[:COVERS]->(t);
MATCH (w:Week {number: 10}) MATCH (t:Topic) WHERE t.name IN ["Multi-agent systems"] MERGE (w)-[:COVERS]->(t);
MATCH (w:Week {number: 11}) MATCH (t:Topic) WHERE t.name IN ["Evaluation with a gold set", "LLM-as-judge", "Prompt injection", "Cost and rate limits"] MERGE (w)-[:COVERS]->(t);
MATCH (w:Week {number: 12}) MATCH (t:Topic) WHERE t.name IN ["Integrated AI system"] MERGE (w)-[:COVERS]->(t);

// ---------------------------------------------------------------- BUILDS_ON: a topic points at what it builds on

MATCH (a:Topic {name: "The AI application stack"}) MATCH (b:Topic) WHERE b.name IN ["Foundation models"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Tokens"}) MATCH (b:Topic) WHERE b.name IN ["Foundation models"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Context window"}) MATCH (b:Topic) WHERE b.name IN ["Tokens"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Reasoning and thinking budgets"}) MATCH (b:Topic) WHERE b.name IN ["Tokens", "Foundation models"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Temperature"}) MATCH (b:Topic) WHERE b.name IN ["Foundation models"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Prompt and context design"}) MATCH (b:Topic) WHERE b.name IN ["Context window", "The AI application stack"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Structured output"}) MATCH (b:Topic) WHERE b.name IN ["Prompt and context design"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Hallucination"}) MATCH (b:Topic) WHERE b.name IN ["Foundation models", "Context window"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Embeddings"}) MATCH (b:Topic) WHERE b.name IN ["Tokens"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Cosine similarity"}) MATCH (b:Topic) WHERE b.name IN ["Embeddings"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Chunking"}) MATCH (b:Topic) WHERE b.name IN ["Embeddings", "Context window"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Vector search"}) MATCH (b:Topic) WHERE b.name IN ["Cosine similarity", "Chunking"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Retrieval-augmented generation"}) MATCH (b:Topic) WHERE b.name IN ["Vector search", "Prompt and context design", "Hallucination"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Grounding and citation"}) MATCH (b:Topic) WHERE b.name IN ["Retrieval-augmented generation"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Cypher"}) MATCH (b:Topic) WHERE b.name IN ["Property graph model"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Graph traversal"}) MATCH (b:Topic) WHERE b.name IN ["Cypher"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Idempotent loading"}) MATCH (b:Topic) WHERE b.name IN ["Cypher"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Vector index in Neo4j"}) MATCH (b:Topic) WHERE b.name IN ["Vector search", "Cypher"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Graph modelling"}) MATCH (b:Topic) WHERE b.name IN ["Property graph model"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Knowledge graphs"}) MATCH (b:Topic) WHERE b.name IN ["Graph modelling"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Entity extraction"}) MATCH (b:Topic) WHERE b.name IN ["Knowledge graphs", "Structured output"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Graph RAG"}) MATCH (b:Topic) WHERE b.name IN ["Retrieval-augmented generation", "Graph traversal", "Vector index in Neo4j", "Knowledge graphs"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Hybrid retrieval"}) MATCH (b:Topic) WHERE b.name IN ["Graph RAG", "Vector search"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Tool calling"}) MATCH (b:Topic) WHERE b.name IN ["Structured output"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "The agent loop"}) MATCH (b:Topic) WHERE b.name IN ["Tool calling", "Context window"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "MCP"}) MATCH (b:Topic) WHERE b.name IN ["Tool calling"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Tool safety"}) MATCH (b:Topic) WHERE b.name IN ["Tool calling", "Retrieval-augmented generation"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Workflows versus agents"}) MATCH (b:Topic) WHERE b.name IN ["The agent loop"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Skills"}) MATCH (b:Topic) WHERE b.name IN ["Tool calling", "Prompt and context design"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Provider abstraction"}) MATCH (b:Topic) WHERE b.name IN ["The AI application stack"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Agent memory"}) MATCH (b:Topic) WHERE b.name IN ["The agent loop", "Vector search"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Multi-agent systems"}) MATCH (b:Topic) WHERE b.name IN ["Workflows versus agents", "Agent memory"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Evaluation with a gold set"}) MATCH (b:Topic) WHERE b.name IN ["Retrieval-augmented generation"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "LLM-as-judge"}) MATCH (b:Topic) WHERE b.name IN ["Evaluation with a gold set", "Structured output"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Prompt injection"}) MATCH (b:Topic) WHERE b.name IN ["Tool safety"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Cost and rate limits"}) MATCH (b:Topic) WHERE b.name IN ["Tokens", "Reasoning and thinking budgets"] MERGE (a)-[:BUILDS_ON]->(b);
MATCH (a:Topic {name: "Integrated AI system"}) MATCH (b:Topic) WHERE b.name IN ["Multi-agent systems", "Hybrid retrieval", "Evaluation with a gold set", "Prompt injection", "Cost and rate limits"] MERGE (a)-[:BUILDS_ON]->(b);

// ---------------------------------------------------------------- deliverables: when due, what they assess

MATCH (d:Deliverable {name: "Lab 1"}) MATCH (w:Week {number: 4}) MERGE (d)-[:DUE_IN]->(w);
MATCH (d:Deliverable {name: "Lab 2"}) MATCH (w:Week {number: 7}) MERGE (d)-[:DUE_IN]->(w);
MATCH (d:Deliverable {name: "Lab 3"}) MATCH (w:Week {number: 10}) MERGE (d)-[:DUE_IN]->(w);
MATCH (d:Deliverable {name: "Final project"}) MATCH (w:Week {number: 12}) MERGE (d)-[:DUE_IN]->(w);

MATCH (d:Deliverable {name: "Lab 1"}) MATCH (t:Topic) WHERE t.name IN ["Embeddings", "Chunking", "Vector search", "Retrieval-augmented generation", "Grounding and citation"] MERGE (d)-[:ASSESSES]->(t);
MATCH (d:Deliverable {name: "Lab 2"}) MATCH (t:Topic) WHERE t.name IN ["Graph modelling", "Knowledge graphs", "Cypher", "Idempotent loading", "Graph RAG", "Hybrid retrieval"] MERGE (d)-[:ASSESSES]->(t);
MATCH (d:Deliverable {name: "Lab 3"}) MATCH (t:Topic) WHERE t.name IN ["Tool calling", "The agent loop", "Tool safety", "Agent memory", "Provider abstraction"] MERGE (d)-[:ASSESSES]->(t);
MATCH (d:Deliverable {name: "Final project"}) MATCH (t:Topic) WHERE t.name IN ["Integrated AI system", "Evaluation with a gold set", "Prompt injection", "Cost and rate limits"] MERGE (d)-[:ASSESSES]->(t);

// ---------------------------------------------------------------- tools: which topic uses which

MATCH (t:Topic) WHERE t.name IN ["Tokens", "Reasoning and thinking budgets", "Structured output", "Retrieval-augmented generation", "Tool calling"] MATCH (x:Tool {name: "Gemini API"}) MERGE (t)-[:USES]->(x);
MATCH (t:Topic) WHERE t.name IN ["Embeddings", "Vector index in Neo4j"] MATCH (x:Tool {name: "Gemini embeddings"}) MERGE (t)-[:USES]->(x);
MATCH (t:Topic) WHERE t.name IN ["Vector search"] MATCH (x:Tool {name: "Chroma"}) MERGE (t)-[:USES]->(x);
MATCH (t:Topic) WHERE t.name IN ["Property graph model", "Cypher", "Idempotent loading", "Vector index in Neo4j"] MATCH (x:Tool {name: "Neo4j"}) MERGE (t)-[:USES]->(x);
MATCH (t:Topic) WHERE t.name IN ["Evaluation with a gold set", "LLM-as-judge"] MATCH (x:Tool {name: "DeepEval"}) MERGE (t)-[:USES]->(x);
MATCH (t:Topic) WHERE t.name IN ["Provider abstraction"] MATCH (x:Tool) WHERE x.name IN ["Groq", "Ollama"] MERGE (t)-[:USES]->(x);
MATCH (a:Tool {name: "Neo4j"}) MATCH (b:Tool {name: "Docker"}) MERGE (a)-[:RUNS_IN]->(b);
