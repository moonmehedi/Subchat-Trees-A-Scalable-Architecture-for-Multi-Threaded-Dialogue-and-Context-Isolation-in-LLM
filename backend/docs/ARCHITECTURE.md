# Subchat Trees – Simple Architecture Overview

This project organizes conversations as a tree. The main conversation is the root, and each follow‑up creates a subnode (subchat) that inherits only the relevant memory from its parent while keeping contexts isolated. Retrieval (RAG) can be applied per node.

## 1) Conversation Tree
- Root node = main conversation (topic starter)
- Child nodes = follow‑ups or focused subtopics
- Each node has its own message buffer and metadata (title, path, parent/children)
- The path encodes the lineage (root → child → grandchild …)

## 2) Follow‑ups create subnodes (with parent awareness)
- A follow‑up is created by selecting text from the parent conversation and asking a question.
- API: POST `/api/conversations/{parent_id}/subchats`
  - Body fields used:
    - `title`: subchat title
    - `selected_text` (optional but recommended): exact fragment highlighted from the parent
    - `context_type`: defaults to `"follow_up"`
- Immediately after creation, the user sends their follow‑up question to the new subchat node.

## 3) Memory model and isolation
- Node buffer: stores only this node’s messages.
- Parent memory: the subnode can be aware of its parent via a small, explicit follow‑up context (not the full parent buffer).
- Isolation: messages from other branches (siblings/other topics) are not included, preventing cross‑context pollution.
- The system injects a system message for follow‑ups:
  - e.g., `FOLLOW‑UP CONTEXT: User selected "<selected_text>" from the previous conversation. Focus on this specific topic.`
- Result: The LLM focuses on the selected fragment and the user’s new question, not unrelated topics from elsewhere in the tree.

## 4) Retrieval (RAG)
- Retrieval can be enabled per message to augment the node’s context with external knowledge.
- Tests may disable RAG to measure behavior cleanly (baselines vs. system).

## 5) Minimal flow
- Step A (root): user asks a broad question → main node responds.
- Step B (create subchat): user highlights a fragment (e.g., "snake") and creates a follow‑up subchat with `selected_text: "snake"`.
- Step C (ask follow‑up): user sends a question to the new subchat. The LLM receives the follow‑up system context and answers narrowly.

## 6) Why this prevents context pollution
- Each node has its own buffer.
- Follow‑ups carry only a compact parent hint (selected_text), not all parent content.
- No sibling data is mixed into the subchat.
- Retrieval, when enabled, brings in external facts relevant to the new node—not other branches.

## Quick references
- Create subchat: `POST /api/conversations/{parent_id}/subchats` with `{ title, selected_text?, context_type? }`
- Send message: `POST /api/conversations/{node_id}/messages` with `{ message, disable_rag? }`
- Selected text (`selected_text`) is the primary signal for what the follow‑up should focus on.

This simple structure lets you branch conversations cleanly, inherit only what matters, and keep each thread focused and testable.