# External Dataset Catalog for Subchat Trees

Purpose: Provide a comprehensive set of publicly available datasets to evaluate hierarchical multi-threaded dialogue, context isolation, long-term memory retrieval, multi-query RAG, re-ranking, reasoning decomposition, tool use, and code + knowledge grounding.

## Category Index
1. Multi-Turn & Hierarchical / Threaded Dialogue
2. Ambiguity, Disentanglement & Entity Resolution
3. Knowledge-Grounded QA / Conversational QA
4. Retrieval Corpora (General, Heterogeneous, Domain-Specific)
5. Long-Context & Memory / Compression Evaluation
6. Re-Ranking & Hybrid Retrieval Benchmarks
7. Reasoning Chains / Trees / Decomposition
8. Tool Use, Function Calling & Agentic Interaction
9. Code & Technical QA / Programming Dialogue
10. Safety, Robustness & Context Pollution Stress Tests
11. Multimodal (Optional Future)
12. Synthetic Generation Frameworks (For Custom Scenarios)

---
## 1. Multi-Turn & Hierarchical / Threaded Dialogue
| Dataset | Link | Size/Stats | License | Relevance |
|---------|------|-----------|---------|-----------|
| MultiWOZ 2.2 | https://arxiv.org/abs/2104.00773 / https://github.com/budzianowski/multiwoz | 10K+ dialogues, multi-domain | MIT | Multi-domain state tracking; adapt domains as separate subchat branches. |
| TaskMaster | https://github.com/google-research-datasets/Taskmaster | ~13K task-oriented dialogues | Apache 2.0 | Branching task flows similar to subtask subchats. |
| DSTC8 Schema-Guided | https://github.com/google-research-datasets/dstc8-schema-guided-dialogue | ~22K dialogues | Apache 2.0 | Rich schema; each service slot can form isolated context branches. |
| Ubuntu Dialogue Corpus | https://arxiv.org/abs/1506.08909 | ~1M turns | Custom (research) | Noisy real support threads; test retrieval across long histories. |
| OASST (OpenAssistant Conversations) | https://open-assistant.io | 161K messages | Apache 2.0 | Human-curated multi-turn instructions; branch generation & isolation tests. |
| HC3 (Human ChatGPT Comparison) | https://arxiv.org/abs/2303.14416 | 36K QA pairs | CC BY-NC 4.0 | Distinguish human vs model responses in mixed branches. |
| ShareGPT (Filtered) | https://huggingface.co/datasets/sharegpt_alpaca | ~100K convs | Depends (user uploads) | Realistic multi-topic chats causing potential pollution. |
| OpenOrca | https://huggingface.co/datasets/Open-Orca/OpenOrca | ~1.3M examples | MIT | Diverse instruction-following contexts; branch specialization. |

## 2. Ambiguity, Disentanglement & Entity Resolution
| Dataset | Link | Focus | License | Relevance |
|---------|------|-------|---------|-----------|
| AmbigQA | https://arxiv.org/abs/2004.10645 | Ambiguous questions w/ multiple valid answers | MIT | Design multi-branch resolution nodes for each interpretation (context isolation). |
| CoNLL-YAGO / AIDA (Entity Linking) | https://downloads.cs.stanford.edu/nlp/data/entity-recognition/ | Entity disambiguation | Research | Evaluate disambiguation prompts inside branches. |
| QASPER (Scientific QA) | https://arxiv.org/abs/2104.10690 | Multi-answer, latent info | CC BY 4.0 | Requires structured retrieval across long doc windows; ambiguity in claim grounding. |
| WOZ ambiguity subsets (from MultiWOZ) | MultiWOZ sources | Domain slot ambiguity | MIT | Slot-specific subbranches preventing contamination. |
| FEVER (Fact verification) | https://fever.ai | 185K claims | Research | False vs true claims—branch for competing factual interpretations. |

## 3. Knowledge-Grounded QA / Conversational QA
| Dataset | Link | Size | License | Relevance |
|---------|------|------|---------|-----------|
| Natural Questions (NQ) | https://ai.google.com/research/NaturalQuestions | 307K | CC BY-SA 3.0 | Retrieve factual spans; branch follow-ups for clarifications. |
| HotpotQA | https://hotpotqa.github.io | 113K | CC BY-SA 4.0 | Multi-hop reasoning → child branches for each hop chain. |
| TriviaQA | https://arxiv.org/abs/1705.03551 | 650K | CC BY-SA 4.0 | Large-scale recall stress-tests. |
| WebQuestions | https://github.com/danielfrendrich/WebQuestions | 6K | CC BY-SA 3.0 | Simple baseline single-hop QA; compare vs multi-branch complexity. |
| ELI5 | https://arxiv.org/abs/1907.09190 | 270K Q/Long answers | MIT | Long context summarization vs granular branch decomposition. |
| QuAC | https://arxiv.org/abs/1808.07036 | 14K dialogs | CC BY-SA 3.0 | Sequential follow-up QA modeling multi-turn context updates. |
| CoQA | https://arxiv.org/abs/1808.07042 | 127K turns | CC BY-SA 4.0 | Conversational comprehension; branch per answer type. |
| QAConv / DialDoc | https://arxiv.org/abs/2110.08555 | Doc-grounded dialogs | Apache 2.0 | Branch turns mapped to doc sections (localized retrieval windows). |

## 4. Retrieval Corpora (General, Heterogeneous, Domain-Specific)
| Corpus | Link | Benchmark | License | Relevance |
|--------|------|----------|---------|-----------|
| BEIR | https://arxiv.org/abs/2104.08663 | 18 datasets | MIT | Unified eval for heterogeneous retrieval—plug multi-query + branch weighting. |
| MS MARCO | https://microsoft.github.io/msmarco/ | Large-scale passages | Custom (academic) | Test re-ranking, dense vs lexical hybrid search. |
| KILT | https://arxiv.org/abs/2009.02252 | Unified knowledge tasks | CC BY 4.0 | Multi-task retrieval enabling branch-type adaptive strategies. |
| OpenWebText / C4 | https://huggingface.co/datasets | Web-scale | Various | Stress test indexing scale for long-term memory retrieval. |
| Arxiv / PubMed QA | https://huggingface.co/datasets/pubmed_qa | Biomedical + scientific | Custom | Domain-specific retrieval requiring precise isolation. |
| LegalBench (docs) | https://arxiv.org/abs/2308.11462 | Legal tasks | MIT | Domain-specific hierarchical decompositions (statute vs case vs concept). |

## 5. Long-Context & Memory / Compression Evaluation
| Dataset | Link | Focus | License | Relevance |
|---------|------|-------|---------|-----------|
| PG19 | https://arxiv.org/abs/1911.06353 | Long books | MIT | Test summarization nodes + selective context inheritance. |
| BookSum | https://arxiv.org/abs/2206.07327 | Chapter/book summaries | MIT | Multi-level summarization tree evaluation. |
| LongFormQA | https://arxiv.org/abs/2203.07984 | Long answers grounded in docs | Research | Branch for retrieval vs synthesis separation. |
| NarrativeQA | https://arxiv.org/abs/1712.07040 | Long story comprehension | MIT | Multi-branch character/topic isolation. |
| GovReport | https://arxiv.org/abs/2106.06134 | Long formal reports | MIT | Structured summarization branches (executive summary vs details). |
| QMSum | https://arxiv.org/abs/2104.08469 | Meeting summarization | CC BY 4.0 | Branch per topic/agenda item; evaluate memory gating. |
| SAMSum | https://arxiv.org/abs/1911.12237 | Chat summarization | CC BY-NC-SA 4.0 | Evaluate summarization precision for branch condensation. |

## 6. Re-Ranking & Hybrid Retrieval Benchmarks
| Dataset/Resource | Link | Purpose | License | Relevance |
|------------------|------|---------|---------|-----------|
| MS MARCO Passage Ranking | https://microsoft.github.io/msmarco/ | Cross-encoder vs bi-encoder | Academic | Integration of re-ranking node-level improvements. |
| TREC Deep Learning | https://trec.nist.gov | Passage/document ranking | Various | Evaluate hierarchical retrieval + intent-aware multi-query. |
| BEIR (with MonoT5 / ColBERT results) | https://github.com/beir-cellar/beir | Baseline metrics | MIT | Compare integrated hybrid pipeline vs published baselines. |
| MTEB | https://arxiv.org/abs/2210.07316 | Embedding tasks | Apache 2.0 | Choose embedding models for vector index performance. |
| SPLADE v2 | https://arxiv.org/abs/2109.10086 | Sparse expansion | MIT | Combine lexical expansion + semantic search for pollution avoidance. |
| ColBERT / ColBERTv2 | https://arxiv.org/abs/2004.12832 / https://arxiv.org/abs/2112.01488 | Late interaction | MIT | Token-level similarity for precise branch-relevant retrieval. |

## 7. Reasoning Chains / Trees / Decomposition
| Dataset | Link | Focus | License | Relevance |
|---------|------|-------|---------|-----------|
| GSM8K | https://arxiv.org/abs/2110.14168 | Grade-school math reasoning | MIT | Test branch-based step isolation (each arithmetic step). |
| MultiArith / AQUA | https://arxiv.org/abs/1911.01547 | Math word problems | Research | Evaluate CoT vs tree-of-subchat decomposition. |
| SVAMP | https://arxiv.org/abs/2108.04327 | Robust math semantics | Research | Ambiguity resolution via branches. |
| StrategyQA | https://arxiv.org/abs/2101.02235 | Implicit multi-hop reasoning | MIT | Branch hidden premises; evaluate retrieval enrichment. |
| HotpotQA (multi-hop) | https://hotpotqa.github.io | Multi-hop | CC BY-SA 4.0 | Subchat per supporting fact chain. |
| ProofWriter | https://arxiv.org/abs/2010.03429 | Logical entailment chains | MIT | Formal reasoning trace nodes. |
| FOLIO | https://arxiv.org/abs/2210.10749 | First-order logic understanding | MIT | Structured symbolic branch evaluation. |
| ALFWorld / ScienceWorld | https://arxiv.org/abs/2010.03768 / https://arxiv.org/abs/2211.16771 | Embodied reasoning | MIT | Branch for environment states & action plans. |

## 8. Tool Use, Function Calling & Agentic Interaction
| Dataset | Link | Focus | License | Relevance |
|---------|------|-------|---------|-----------|
| ToolBench | https://arxiv.org/abs/2307.16789 | Real API tool calls | Apache 2.0 | Map each tool decision to isolated reasoning subchat. |
| Gorilla / APIBench | https://arxiv.org/abs/2305.15334 | API invocation | Apache 2.0 | Branch for parameter planning vs execution. |
| ReAct synthetic traces | https://arxiv.org/abs/2210.03629 | Action + reasoning | Research | Convert each thought/action pair into node chain. |
| WebShop | https://arxiv.org/abs/2305.00666 | Tool/navigation environment | MIT | Branch for navigation vs purchase reasoning. |
| OpenAI Function Calling examples (synthetic) | docs/openai | Structured JSON calls | Various | Evaluate structured context isolation inside/tool vs outside/tool reasoning. |

## 9. Code & Technical QA / Programming Dialogue
| Dataset | Link | Focus | License | Relevance |
|---------|------|-------|---------|-----------|
| CodeSearchNet | https://arxiv.org/abs/1909.09475 | Code retrieval | Apache 2.0 | Branch: problem → API retrieval → solution synthesis. |
| StackOverflow (BigQuery dump) | https://archive.org/details/stackexchange | Q/A code tasks | CC BY-SA 4.0 | Multi-topic contamination stress ("Java" ambiguity examples). |
| HumanEval | https://arxiv.org/abs/2107.03374 | Code generation tests | MIT | Branch per test function reasoning & verification. |
| MBPP | https://arxiv.org/abs/2108.07732 | Python tasks | MIT | Branch for problem understanding vs solution vs refactor. |
| LeetCode (synthetic scraped sets) | unofficial | Algorithm tasks | Various | Build scenario trees: problem → approach → complexity → edge cases. |
| CodeAlpaca / OpenCoder | https://github.com/sahil280114/codealpaca | Instruction/code | Apache 2.0 | Mixed code + natural language retrieval evaluation. |

## 10. Safety, Robustness & Context Pollution Stress Tests
| Dataset | Link | Focus | License | Relevance |
|---------|------|-------|---------|-----------|
| TruthfulQA | https://arxiv.org/abs/2109.07958 | Avoiding hallucinations | MIT | Evaluate isolation prevents cross-branch misinformation leakage. |
| AdvBench / Jailbreak prompts | https://github.com/llm-attacks | Adversarial prompts | MIT | Branch quarantining for unsafe topic handling. |
| ToxicChat / CivilComments | https://arxiv.org/abs/2209.11225 | Toxicity detection | CC BY | Branch containment of unsafe dialogue streams. |
| Multi-Domain Red Team sets | community | Mixed adversarial | Various | Evaluate selective inheritance shielding. |

## 11. Multimodal (Optional Future)
| Dataset | Link | Modalities | Relevance |
|---------|------|-----------|-----------|
| VQA v2 | https://visualqa.org | Image + QA | Subchat per ambiguous visual question. |
| VizWiz | https://vizwiz.org | Accessibility QA | Branch for user intent vs description retrieval. |
| DocVQA / ChartQA | https://arxiv.org/abs/2211.15378 | Document/Chart reasoning | Branch for region-level retrieval. |

## 12. Synthetic Generation Frameworks
| Resource | Link | Purpose | Relevance |
|---------|------|---------|-----------|
| Self-Instruct | https://arxiv.org/abs/2212.10560 | Generate diverse instructions | Expand scenario diversity automatically. |
| Evol-Instruct | https://arxiv.org/abs/2304.12244 | Progressive instruction mutation | Generate deeper branch chains. |
| Program-of-Thought (PoT) | https://arxiv.org/abs/2211.12588 | Program-based reasoning | Deterministic branch validation. |
| PAL (Program-Aided LM) | https://arxiv.org/abs/2211.10435 | Code execution reasoning | Execution trace → branch nodes with results caching. |

---
## Prioritization for This Project
High-value immediate integration subsets:
- Context Isolation: AmbigQA, MultiWOZ ambiguity slices, custom Python/Rust/Java scenarios (already partially in repo) → extend with AmbigQA patterns.
- Retrieval & Re-Ranking: BEIR (subset: FiQA, DBPedia, Quora), MS MARCO Passage; integrate ColBERT / SPLADE hybrid.
- Long Memory: PG19 (sampled chapters), QMSum (meetings), BookSum (chapter-level). Use them for buffer eviction + cross-branch summarization tests.
- Reasoning Trees: GSM8K + StrategyQA to test branch-per-step vs linear CoT.
- Tool Use: ToolBench minimal subset for follow-up branch reasoning separation vs execution logs.
- Code QA: MBPP + CodeSearchNet small slice to test retrieval + branch specialization of problem vs solution.

---
## Integration Mapping
| Capability | Dataset(s) | Scenario Conversion | Metric |
|------------|------------|---------------------|--------|
| Ambiguity resolution | AmbigQA, custom Java/Rust/Mercury | One JSON per ambiguous question with subchats per interpretation | Accuracy per branch, FP contamination rate |
| Multi-domain slot isolation | MultiWOZ, DSTC8 | Domain → root, slot/value clarifications → subchats | Slot retrieval F1, cross-branch leak rate |
| Long-term memory | PG19, QMSum | Chapter/segment → archived messages; summarization subchat nodes | Retrieval recall @k after eviction |
| Multi-hop QA | HotpotQA, StrategyQA | Each supporting fact → child node; final synthesis at parent | Support fact coverage %, synthesis correctness |
| Re-ranking quality | MS MARCO, BEIR | Query → candidate retrieval → re-ranked list stored in node | NDCG@10, MRR, relevance isolation |
| Reasoning decomposition | GSM8K, PoT synthetic | Step-per-node chain; program output stored | Step accuracy, final answer accuracy |
| Tool planning vs execution | ToolBench, PAL | Plan node → execution subnode → result summary | Tool success rate, branch purity |
| Code retrieval aiding solution | CodeSearchNet, MBPP | Problem root → retrieval candidates subchat → final solution branch | Pass@k vs retrieval baseline |
| Safety isolation | TruthfulQA, AdvBench | Unsafe prompt → quarantined branch (no inheritance) | Containment rate, hallucination reduction |

---
## Suggested Folder Layout Additions
```
backend/dataset/external/
  multi_turn/
  ambiguity/
  retrieval/
  long_context/
  reasoning/
  tool_use/
  code/
  safety/
  synthetic/
```
Each subfolder: raw/ (original), processed/ (normalized JSON), scenarios/ (final evaluation JSON like existing ones).

---
## JSON Scenario Template (External Conversion)
```json
{
  "scenario_name": "AmbigQA_Q123",
  "source": "AmbigQA",
  "task_type": "ambiguous_question",
  "question": "Where was Newton born?",
  "branches": [
    {
      "interpretation": "Isaac Newton (scientist)",
      "expected_answer": "Woolsthorpe Manor, Lincolnshire, England",
      "evidence_refs": ["doc_id_42"],
      "messages": [ ... ]
    },
    {
      "interpretation": "Newton (unit of force)",
      "expected_answer": "Not applicable (unit)",
      "messages": [ ... ]
    }
  ],
  "evaluation": {
    "metrics": ["branch_accuracy", "cross_branch_leak_rate"]
  }
}
```

---
## Licensing Considerations
- Prefer MIT / Apache 2.0 sets for redistribution.
- For CC BY-SA: retain attribution in headers of processed JSON.
- For datasets with usage restrictions (MS MARCO): keep them in scripts that download rather than committing raw data.

---
## Quick Start Prioritized Imports
1. BEIR subset downloader → convert top 3 datasets into ChromaDB collections.
2. GSM8K → generate reasoning branch JSON (one step per node). 
3. AmbigQA → build ambiguity isolation scenarios.
4. QMSum meeting topics → hierarchical summarization depth evaluation.
5. MS MARCO passage ranking → implement re-ranking test harness using integrated pipeline.

---
## Metric Extensions To Implement
| Metric | Description | Implementation Hint |
|--------|-------------|---------------------|
| Cross-Branch Leak Rate | % of responses containing tokens from unintended branch | Extend `context_classifier.py` with branch-specific lexicons |
| Branch Purity Score | Intra-branch semantic coherence vs contamination | Embedding clustering separation (silhouette) |
| Retrieval Isolation Precision | Precision excluding buffer + unrelated branches | Augment vector_index with branch filters |
| Decomposition Coverage | % reasoning steps represented as nodes | Count vs oracle step list (GSM8K solution parse) |
| Summarization Fidelity | Similarity between parent summary and union of child content | Rouge-L / BERTScore parent vs concatenated children |
| Tool Planning Accuracy | Plan node vs execution result alignment | Compare tool arg JSON vs actual response fields |

---
## Future Expansion
- Add multimodal disambiguation (image of "Java" coffee bag vs code snippet).
- Integrate streaming evaluation on long-context PG19 chapter ingestion.
- Introduce synthetic adversarial contamination tests (insert misleading cross-branch message). 
- Add program-generated trees (PoT + PAL) for deterministic verification.

---
## References
All dataset papers are cited in `LITERATURE_REVIEW.md` extensions section where relevant (Re-Ranking, Program Execution, Retrieval).

---
## Summary
This catalog equips Subchat Trees with a roadmap for robust, diverse evaluation across ambiguity handling, context isolation, retrieval precision, reasoning structure, tool execution, and long-memory resilience. Begin with BEIR, AmbigQA, GSM8K, and QMSum for maximum architectural stress coverage, then layer in tool use (ToolBench) and code retrieval (CodeSearchNet) to expand scope.
