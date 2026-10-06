// Week 5: one uniqueness constraint per key of the course knowledge graph.
//
// Each constraint enforces its key and gives MERGE an index to find a node by.
// Community edition supports uniqueness constraints only; existence, type and
// key constraints are Enterprise features.
//
// The entities: weeks, read from file names, and the three extracted types. Week 4's
// course graph declared the same four; IF NOT EXISTS makes running them again harmless.

CREATE CONSTRAINT week_number IF NOT EXISTS FOR (w:Week) REQUIRE w.number IS UNIQUE;
CREATE CONSTRAINT topic_name IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT deliverable_name IF NOT EXISTS FOR (d:Deliverable) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT tool_name IF NOT EXISTS FOR (t:Tool) REQUIRE t.name IS UNIQUE;

// The text layer.
CREATE CONSTRAINT document_name IF NOT EXISTS FOR (d:Document) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE;
