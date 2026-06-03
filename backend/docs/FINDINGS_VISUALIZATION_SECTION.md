# Findings and Visualization Draft

This document is a working results-section draft. It does not edit `paper/Conversation_Forest/sn-article.tex`. It organizes the current merged results, proposes the main visualizations, and appends all merged result tables for 7B, 14B, and 32B.

## Result Story in One Paragraph

The merged results show that conversation-tree isolation improves topic tracking across all tested model sizes and buffer sizes, but the optimal buffer depends strongly on model capacity. The 7B model is too weak for the strict topic-prefix instruction when long, mixed contexts accumulate: its baseline and system F1 both fall as the buffer grows, although the system still retains more topic content in the recall probes. The 14B model shows the cleanest mid-size tradeoff: performance improves from buffer 5 to 10/20, then drops at buffer 40 when the prompt becomes too long and mixed. The 32B model reaches the strongest absolute performance, with system F1 peaking at 85.2% at buffer 20 and still remaining high at buffer 40. Across models, these results support the central claim that context organization matters independently of context length: more context is not always better unless it is routed, summarized, and scoped to the correct conversational branch.

## Evaluation Prompt Used for Topic Isolation

The topic-isolation metric is intentionally strict. A response can be semantically relevant but still be counted as incorrect if it fails to start with the expected topic prefix. The instruction given to the model was:

```text
I'm going to ask you questions across multiple topics. Here's how the test works:

When I introduce a new topic, I will use this pattern:
topic_name : user query

Example:
medical_treatments : how does one remove tumors with electromagnetism?

Once a topic is introduced, you MUST keep using that topic name in ALL your answers, even if I don't repeat it in follow-up questions.

Example:
User: what about pancreatic tumors?
You must answer starting with:
medical_treatments: ...

Sub-topics may also appear using this pattern:
topic_name_subtopic_name : user query

REQUIRED FORMAT for EVERY response:
Start your answer with the active topic or sub-topic name, followed by a colon, then give your actual answer.

IMPORTANT: This is a long conversation covering many different topics. I may switch between topics frequently and return to earlier topics. You must track which topic is currently active and always prefix your response with the correct topic name.

Do you understand these instructions?
```

This matters most for the 7B model. In several cases, the 7B model preserved useful semantic content but failed the exact prefix contract after many previous turns, summaries, and retrieved snippets. Therefore, the low 7B context-isolation F1 should be interpreted as a combined measure of context memory and instruction-following reliability, not pure semantic understanding.

## Recall Probe Used for Memory Evaluation

The recall probe was designed as a summarization-only memory test. For each eligible topic, the model was asked:

```text
Summarize everything we have discussed about {topic}. Include all key points, details, and questions that were raised.
```

The run injected 43 recall probes. These probes are more meaningful for visualizing RAG than normal conversation turns because they explicitly ask the model to recover all prior topic information. If the active buffer is insufficient, the model has a clear reason to request retrieval. Normal turns are noisier because many are local follow-ups, new topic introductions, or short clarifications that do not need retrieval even when older context has been lost.

## Recommended Main Figures

### Figure 1. Context Isolation F1 vs Buffer Size

Use a line chart with buffer size on the x-axis and F1 on the y-axis. Use one subplot for each model: 7B, 14B, and 32B. Each subplot should contain two lines: baseline and system.

Recommended caption:

> Context isolation F1 across buffer sizes. The tree-based system improves F1 over the linear baseline across every tested model and buffer. Smaller models degrade sharply as buffer size grows, while larger models tolerate longer contexts better. The best observed system F1 is 85.2% for the 32B model at buffer 20.

Data to plot:

| Model | Buffer | Baseline F1 | System F1 | Improvement |
|---|---:|---:|---:|---:|
| 7B | 5 | 24.3 | 62.9 | +38.6 |
| 7B | 10 | 44.7 | 55.2 | +10.5 |
| 7B | 20 | 18.7 | 45.6 | +26.9 |
| 7B | 40 | 9.8 | 39.3 | +29.5 |
| 14B | 5 | 51.2 | 73.9 | +22.7 |
| 14B | 10 | 64.3 | 83.4 | +19.1 |
| 14B | 20 | 62.5 | 83.1 | +20.6 |
| 14B | 40 | 59.8 | 73.1 | +13.3 |
| 32B | 5 | 68.6 | 83.2 | +14.6 |
| 32B | 10 | 71.1 | 83.7 | +12.6 |
| 32B | 20 | 69.6 | 85.2 | +15.6 |
| 32B | 40 | 65.7 | 78.2 | +12.5 |

### Figure 2. F1 Improvement Heatmap

Use a heatmap where rows are model sizes and columns are buffer sizes. The cell value should be `System F1 - Baseline F1`.

Recommended caption:

> Absolute F1 gain from conversation-tree isolation. The proposed system improves topic isolation under every model-buffer configuration. The largest relative rescue occurs for the weakest 7B model, while the strongest absolute performance occurs for 32B at buffer 20.

This figure should be compact and very easy for reviewers to read.

### Figure 3. Context Pollution Rate vs Buffer Size

Use a line chart or grouped bar chart. Plot baseline and system pollution rate for each model.

Recommended caption:

> Context pollution rate across buffer sizes. The tree system consistently reduces topic pollution by separating unrelated conversation branches. At buffer 20, pollution drops from 84.1% to 61.5% for 7B, from 39.8% to 18.1% for 14B, and from 32.7% to 16.5% for 32B.

This is one of the most important figures because it directly matches the paper's thesis: the problem is not only forgetting, but also mixing unrelated conversational state.

### Figure 4. Recall Quality vs Buffer Size

Use three line charts or one multi-panel chart for ROUGE-1, ROUGE-L, and BLEU-2. If space is limited, show only ROUGE-1 in the main paper and put ROUGE-L/BLEU-2 in the appendix.

Recommended caption:

> Recall-probe similarity across buffer sizes. The recall probes ask the model to summarize all prior content for a topic. The system consistently produces summaries with higher overlap against the topic reference, showing that topic-local buffers preserve semantically relevant information even when strict prefix-following F1 is lower.

ROUGE-1 values:

| Model | Buffer | Baseline ROUGE-1 | System ROUGE-1 |
|---|---:|---:|---:|
| 7B | 5 | 0.2448 | 0.4240 |
| 7B | 10 | 0.2369 | 0.4094 |
| 7B | 20 | 0.1811 | 0.4056 |
| 7B | 40 | 0.1557 | 0.3545 |
| 14B | 5 | 0.3428 | 0.3896 |
| 14B | 10 | 0.3378 | 0.4201 |
| 14B | 20 | 0.2476 | 0.4187 |
| 14B | 40 | 0.1745 | 0.3725 |
| 32B | 5 | 0.2687 | 0.4328 |
| 32B | 10 | 0.3674 | 0.4206 |
| 32B | 20 | 0.3338 | 0.4283 |
| 32B | 40 | 0.1503 | 0.3918 |

### Figure 5. Tokens Per Correct Answer

Use a line chart with a log-scale y-axis or grouped bars. This metric is more informative than average input tokens alone because it accounts for correctness.

Recommended caption:

> Token efficiency measured as tokens per correct answer. Although the tree system sometimes uses slightly more input/output tokens, it usually requires fewer tokens per correct response because it produces more correct topic-tracking answers. This indicates that organized context can improve effective efficiency even when raw prompt length increases.

Key examples:

| Model | Buffer | Baseline Tokens per Correct | System Tokens per Correct |
|---|---:|---:|---:|
| 7B | 20 | 35451 | 15389 |
| 7B | 40 | 102923 | 25899 |
| 14B | 20 | 8036 | 6853 |
| 32B | 20 | 7775 | 6600 |

### Figure 6. Recall-Probe RAG Retrieval Rate

Use the summarization probe RAG decisions, not the normal-turn RAG decisions, as the main RAG visualization. Plot probe retrieval rate vs buffer size for baseline and system.

Recommended caption:

> RAG retrieval during recall probes. The recall probes explicitly ask the model to summarize prior topic content, so retrieval decisions are interpretable as a memory sufficiency signal. For the 14B model, baseline retrieval is high at small buffers and falls as buffer grows, while the system becomes almost entirely buffer-sufficient by buffer 10-40. The 7B model is an exception: it over-triggers RAG in the system setting, suggesting that the smaller model is less reliable at deciding whether local context is sufficient.

Probe retrieval rates:

| Model | Buffer | Baseline Probe RAG | System Probe RAG |
|---|---:|---:|---:|
| 7B | 5 | 2.3% | 39.5% |
| 7B | 10 | 4.7% | 20.9% |
| 7B | 20 | 4.7% | 9.3% |
| 7B | 40 | 0.0% | 2.3% |
| 14B | 5 | 58.1% | 23.3% |
| 14B | 10 | 44.2% | 2.3% |
| 14B | 20 | 37.2% | 4.7% |
| 14B | 40 | 16.3% | 0.0% |
| 32B | 5 | 53.5% | 88.4% |
| 32B | 10 | 93.0% | 53.5% |
| 32B | 20 | 60.5% | 18.6% |
| 32B | 40 | 72.1% | 2.4% |

Normal-turn RAG should be kept as a secondary or appendix figure because ordinary turns often do not require retrieval. The recall-probe view better represents the memory problem the system is designed to solve.

### Figure 7. Error Count vs Buffer Size

Use a grouped bar chart. This should be an appendix or short supporting figure.

Recommended caption:

> RAG decision or vLLM errors by buffer size. Errors are concentrated at larger buffers, especially buffer 40 for the 14B model. This supports the claim that simply increasing buffer length can destabilize the pipeline and does not guarantee better context handling.

Important error counts from Table 4:

| Model | Buffer | Baseline Errors | System Errors |
|---|---:|---:|---:|
| 7B | 40 | 7 | 0 |
| 14B | 40 | 25 | 18 |
| 32B | 40 | 9 | 3 |

## Draft Result Narrative

### 7B Model

The 7B model demonstrates the failure mode of using a small instruction-tuned model for a long, interleaved, multi-topic conversation. In Table 1, the system improves over the baseline at every buffer size, but both baseline and system F1 degrade as the buffer grows. The system reaches 62.9% F1 at buffer 5, then falls to 55.2%, 45.6%, and 39.3% at buffers 10, 20, and 40 respectively. The baseline is even less stable, falling to only 9.8% F1 at buffer 40.

This pattern should be described as model-capacity limited behavior. The task requires the model to maintain a hidden formatting rule while answering semantically diverse questions across many topics. The model must remember that every response must begin with the active topic name. For the 7B model, this instruction becomes fragile once it is buried above many turns of mixed context, summaries, and possible retrieval snippets. Therefore, some failures are not necessarily failures of semantic relevance; they are failures of strict topic-prefix compliance.

The recall matrix changes the interpretation. Even though 7B F1 declines with larger buffers, the recall-probe scores show that the system retains more topical content than the baseline. For ROUGE-1, the system scores 0.4240, 0.4094, 0.4056, and 0.3545 across buffers 5, 10, 20, and 40, while the baseline drops from 0.2448 to 0.1557. This means the tree structure is preserving semantically relevant content, but the weak model cannot always convert that retained content into a correctly prefixed answer.

The performance matrix also contradicts the initial assumption that system input tokens would always be lower. Average input tokens rise with buffer size for both methods, and the system is sometimes slightly larger than baseline. This happens because the baseline often receives disorganized, mixed context and responds with short, safe, or clarifying answers. In contrast, the system often gives the model cleaner topic-local context, allowing it to produce more detailed answers. Thus, higher system token count is partly a side-effect of better context understanding and longer useful responses, not necessarily worse context management.

The latency result is especially interesting. In the 7B runs, the system is often faster or comparable even when it produces more useful answers. This suggests that latency is affected not only by raw token count but also by how coherently the context is organized. A model may spend more generation and reasoning effort resolving a messy baseline prompt than answering from a scoped branch.

For 7B RAG, the recall-probe retrieval plot should be interpreted carefully. The system triggers RAG more than the baseline in the probes, especially at buffer 5. This is not the same clean memory-sufficiency signal observed in 14B. Instead, it suggests the 7B model is less calibrated in deciding whether local context is sufficient. The important 7B result is therefore not lower RAG use, but higher recall quality despite weak instruction-following.

### 14B Model

The 14B model provides the clearest evidence for the proposed architecture. Table 1 shows strong improvement from 7B to 14B in context isolation. The system F1 rises from 73.9% at buffer 5 to 83.4% at buffer 10 and 83.1% at buffer 20. At buffer 40, performance drops to 73.1%, showing that more context eventually becomes harmful even for a stronger model.

This drop at buffer 40 is important. Buffers 5, 10, and 20 summarize and evict content earlier, so older context is compressed into a more standardized form. At buffer 40, many more raw user and assistant turns remain in the prompt before summarization occurs. The model receives long raw conversation history, summaries, system instructions, and possibly retrieval output. The result is not better memory; it is a heavier and noisier prompt. This supports the paper's central argument that context engineering is not only about storing more messages, but about organizing them into the correct scope.

The recall-probe matrix reinforces the same story. System ROUGE-1 is 0.3896, 0.4201, 0.4187, and 0.3725 across buffers 5, 10, 20, and 40, while baseline declines from 0.3428 to 0.1745. The gap widens at larger buffers because the baseline stores more irrelevant topic mixture, while the system stores more relevant topic-local context.

The 14B performance matrix shows the same token pattern as 7B. Average input tokens generally increase as buffer size increases. The system is not always smaller in raw token count; at buffer 20 and 40 it is larger than baseline. However, the system uses fewer tokens per correct answer across all buffer sizes. For example, at buffer 20, baseline requires 8036 tokens per correct answer, while the system requires 6853. This is the cleaner efficiency story: the tree system may spend slightly more tokens, but it spends them on more correct answers.

Latency is also instructive. The 14B model has higher inference time than 7B because the model itself is larger. However, system latency is lower than baseline at buffer 5 and 10, nearly equal at buffer 40, and higher at buffer 20. This mixed pattern suggests that latency depends jointly on model size, prompt length, output length, and context organization. The important observation is that a more organized prompt can reduce latency in some cases even when the system output is richer.

The 14B recall-probe RAG decisions provide the cleanest retrieval evidence. Baseline probe retrieval is high at small buffers and decreases as buffer size grows: 58.1%, 44.2%, 37.2%, and 16.3%. System probe retrieval is much lower: 23.3%, 2.3%, 4.7%, and 0.0%. This is exactly the expected behavior. In the baseline, older topic content is evicted or mixed with unrelated turns, so the model frequently asks for retrieval. In the system, the relevant branch already contains the topic-local context, so the model increasingly judges the buffer sufficient.

### 32B Model

The 32B model shows the strongest absolute performance. Table 1 shows that the baseline is already strong compared with 7B and 14B, but the system still improves it at every buffer size. The system reaches 83.2% F1 at buffer 5, 83.7% at buffer 10, 85.2% at buffer 20, and 78.2% at buffer 40. The best overall setting is therefore 32B with buffer 20.

This result suggests that model capacity and context architecture are complementary. A stronger model can better tolerate long, mixed prompts, but the tree system still improves performance by reducing topic pollution. At buffer 40, the 32B system drops less severely than 7B and 14B, which indicates that larger models can process long conversations more robustly. However, the drop still exists, which means long-context capacity alone does not remove the need for branch-aware context management.

The recall matrix again shows strong system advantage. The 32B system maintains ROUGE-1 around 0.42 at buffers 5, 10, and 20, and still scores 0.3918 at buffer 40. The baseline collapses at buffer 40 to 0.1503. This is one of the strongest signs that the linear baseline becomes overwhelmed by topic mixture, while the tree system keeps the relevant branch recoverable.

The performance matrix shows that 32B is slower than 7B and 14B, as expected. The system sometimes increases average input and output tokens, but tokens per correct answer remain lower for the system at every buffer size. At buffer 20, baseline needs 7775 tokens per correct answer while the system needs 6600. Thus, the system is more effective per successful answer even when raw token use is slightly higher.

The 32B RAG results show a more mature version of the memory-sufficiency behavior. At buffer 5, the system retrieves more during probes than baseline, suggesting that even a strong model may judge short branch-local buffers as insufficient for summarization. But at buffers 10, 20, and 40, system probe retrieval falls below baseline, reaching only 2.4% at buffer 40 compared with 72.1% for baseline. This indicates that once the system has enough branch-local context, it no longer needs to retrieve as aggressively during recall probes.

Recent long-context LLMs such as OpenAI GPT-4.1, which supports a 1 million token context window, and Google Gemini 1.5 Pro, which introduced 1 million token and later 2 million token contexts, show that longer windows are becoming practical. However, these systems also make the central issue more visible: a long window is a storage mechanism, not an organization mechanism. Our results suggest that as models become stronger, the optimal design problem shifts from merely fitting more history into the prompt to deciding which branch of conversation should be visible for a particular turn.

### Cross-Model Interpretation

Across 7B, 14B, and 32B, the same core pattern appears. The tree system reduces context pollution and improves topic-prefix F1. The gain is largest for smaller models because they are more easily confused by linear context mixing. The strongest absolute performance comes from the 32B model because it combines higher instruction-following ability with branch-local context isolation.

The buffer-size result is equally important. Buffer 5 can be too small because relevant recent context is evicted early. Buffer 40 can be too large because raw conversation history becomes too noisy and expensive. Buffers 10 and 20 appear to be the most useful range in the current dataset, with 14B peaking at buffer 10 and 32B peaking at buffer 20. Therefore, buffer size should be treated as a model-dependent configuration parameter rather than a fixed constant.

The initial expectation was that tree-structured context would always reduce input tokens. The experiments show a more subtle result. The system often increases raw token use because it gives the model enough relevant information to answer fully. The baseline can appear cheaper because it answers briefly, asks for clarification, or fails to identify the correct topic. A better efficiency metric is tokens per correct answer, where the system is consistently stronger.

The recall-probe RAG view is the best retrieval visualization. Normal-turn RAG is noisy because many user turns do not need older context. The probe task directly asks the model to summarize a topic, so retrieval decisions reflect whether the model believes local memory is sufficient. The 14B and larger-buffer 32B results show the expected pattern clearly: baseline relies on retrieval more often, while the tree system becomes buffer-sufficient.

## Discussion Direction for the Paper

These results motivate conversation trees as a missing interface and memory abstraction for long-running LLM interaction. Current chat interfaces mostly preserve a single linear transcript. Even branching interfaces often behave like copy-paste forks: a new branch inherits a snapshot and then diverges, but the interface does not fully support nested conversational state, topic-local memory, or multiple interacting agents with partially shared context.

Conversation trees support a richer structure. A parent conversation can preserve broad context; child nodes can isolate detailed follow-ups; sibling nodes can explore alternatives without contaminating one another. This is useful not only for ordinary chat, but also for multi-agent systems, parallel task exploration, and embodied agents. In robotics, LLM-based systems such as SayCan and Inner Monologue show that language models can be used for planning, grounding, and multi-step embodied reasoning. Those settings naturally require separating task plans, subgoals, environmental observations, user corrections, and agent-specific memory. A tree-structured conversational substrate could make those contexts explicit instead of forcing them into one linear prompt.

The larger implication is that context quality depends on structure. Long context windows help, but they do not decide which previous turns are relevant, which should be isolated, and which should be inherited. Conversation-tree architectures offer a way to make this structure visible and operational.

## Suggested Paper Figure Order

1. Context Isolation F1 vs Buffer Size.
2. F1 Improvement Heatmap.
3. Pollution Rate Reduction.
4. Recall-Probe ROUGE-1 vs Buffer Size.
5. Tokens Per Correct Answer.
6. Recall-Probe RAG Retrieval Rate.
7. Error Count vs Buffer Size as appendix or limitations figure.

## Notes and Cautions

- Do not claim that baseline probe RAG is always greater than system probe RAG. That is true for 14B and for 32B at buffers 10, 20, and 40, but not for 7B and not for 32B at buffer 5.
- Do not claim lower raw input tokens as the primary system benefit. The stronger claim is lower context pollution, better F1, stronger recall scores, and fewer tokens per correct answer.
- Treat 7B as evidence that the architecture helps memory but cannot fully overcome weak instruction following.
- Treat buffer 40 as evidence that larger buffers are not automatically better.
- Keep normal-turn RAG as appendix material. Use recall-probe RAG in the main result narrative.

## External References for Framing

- OpenAI introduced GPT-4.1 with a 1 million token context window: https://openai.com/index/gpt-4-1/
- OpenAI GPT-4.1 model documentation lists a 1M token context window: https://platform.openai.com/docs/models/gpt-4.1
- Google introduced Gemini 1.5 Pro with long context up to 1 million tokens in preview and later consumer/API availability: https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024/
- Google announced Gemini 1.5 Pro availability with a 2 million token context window via waitlist for developers/API customers: https://blog.google/technology/ai/google-gemini-update-flash-ai-assistant-io-2024/
- Anthropic's documentation explains context windows as working memory and notes a 200K token context capacity for Claude, with long-context pricing documentation describing 1M context availability for Claude Sonnet 4: https://docs.anthropic.com/en/docs/about-claude/pricing
- SayCan grounds language models in robotic affordances for embodied planning: https://arxiv.org/abs/2204.01691
- Inner Monologue uses language models for embodied reasoning and planning with environmental feedback: https://arxiv.org/abs/2207.05608

# Appended Merged Result Tables

The following sections append all merged result tables from the model-specific `merge` folders. These are included here as manuscript-ready working material; rows can be removed later after deciding which results belong in the main paper and which belong in the appendix.


---

## Source Table: `backend/dataset/7b/merge/TABLE_1_CONTEXT_ISOLATION_MERGED.md`

# TABLE 1: MERGED CONTEXT ISOLATION METRICS (7B)

Merged from buffer-specific `TABLE_1_CONTEXT_ISOLATION.md` / `raw_metrics.json` files.

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Precision</td>
      <td>44.7%</td><td>84.0%</td>
      <td>71.5%</td><td>88.7%</td>
      <td>34.9%</td><td>80.7%</td>
      <td>21.5%</td><td>76.2%</td>
    </tr>
    <tr>
      <td>Recall</td>
      <td>21.1%</td><td>58.1%</td>
      <td>39.6%</td><td>46.1%</td>
      <td>15.6%</td><td>38.3%</td>
      <td>7.8%</td><td>33.4%</td>
    </tr>
    <tr>
      <td>F1</td>
      <td>24.3%</td><td>62.9%</td>
      <td>44.7%</td><td>55.2%</td>
      <td>18.7%</td><td>45.6%</td>
      <td>9.8%</td><td>39.3%</td>
    </tr>
    <tr>
      <td>Accuracy</td>
      <td>21.4%</td><td>58.3%</td>
      <td>39.8%</td><td>46.3%</td>
      <td>15.9%</td><td>38.5%</td>
      <td>8.1%</td><td>33.7%</td>
    </tr>
    <tr>
      <td>Pollution Rate</td>
      <td>78.6%</td><td>41.7%</td>
      <td>60.2%</td><td>53.7%</td>
      <td>84.1%</td><td>61.5%</td>
      <td>91.9%</td><td>66.3%</td>
    </tr>
    <tr>
      <td>Macro Precision</td>
      <td>48.5%</td><td>74.4%</td>
      <td>70.9%</td><td>85.6%</td>
      <td>41.7%</td><td>76.0%</td>
      <td>29.0%</td><td>72.8%</td>
    </tr>
    <tr>
      <td>Macro Recall</td>
      <td>33.7%</td><td>59.6%</td>
      <td>49.4%</td><td>59.7%</td>
      <td>24.7%</td><td>50.5%</td>
      <td>17.8%</td><td>41.4%</td>
    </tr>
    <tr>
      <td>Macro F1</td>
      <td>35.2%</td><td>60.8%</td>
      <td>53.6%</td><td>65.3%</td>
      <td>27.2%</td><td>55.6%</td>
      <td>19.0%</td><td>46.5%</td>
    </tr>
  </tbody>
</table>


---

## Source Table: `backend/dataset/7b/merge/TABLE_2_RECALL_SCORES_MERGED.md`

# TABLE 2: MERGED TOPIC RECALL SCORES (7B)

Merged from buffer-specific `TABLE_2_RECALL_SCORES.md` / `raw_metrics.json` files.

## Aggregate Scores and Probe Cost

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Avg ROUGE-1 (F1)</td>
      <td>0.2448</td><td>0.4240</td>
      <td>0.2369</td><td>0.4094</td>
      <td>0.1811</td><td>0.4056</td>
      <td>0.1557</td><td>0.3545</td>
    </tr>
    <tr>
      <td>Avg ROUGE-L (F1)</td>
      <td>0.1270</td><td>0.3004</td>
      <td>0.1349</td><td>0.3097</td>
      <td>0.1016</td><td>0.3194</td>
      <td>0.0861</td><td>0.2574</td>
    </tr>
    <tr>
      <td>Avg BLEU-2</td>
      <td>0.0364</td><td>0.1581</td>
      <td>0.0324</td><td>0.1259</td>
      <td>0.0205</td><td>0.1325</td>
      <td>0.0172</td><td>0.1142</td>
    </tr>
    <tr>
      <td>Topics Probed</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
    </tr>
    <tr>
      <td>Total Probe Tokens</td>
      <td>158043</td><td>121521</td>
      <td>252519</td><td>188722</td>
      <td>336942</td><td>284817</td>
      <td>472634</td><td>403852</td>
    </tr>
    <tr>
      <td>Avg Tokens per Probe</td>
      <td>3675</td><td>2826</td>
      <td>5873</td><td>4389</td>
      <td>7836</td><td>6624</td>
      <td>10991</td><td>9392</td>
    </tr>
    <tr>
      <td>Total Probe Latency</td>
      <td>918.00s</td><td>710.28s</td>
      <td>814.85s</td><td>776.91s</td>
      <td>767.61s</td><td>792.74s</td>
      <td>723.47s</td><td>703.08s</td>
    </tr>
    <tr>
      <td>Avg Probe Latency</td>
      <td>21.35s</td><td>16.52s</td>
      <td>18.95s</td><td>18.07s</td>
      <td>17.85s</td><td>18.44s</td>
      <td>16.82s</td><td>16.35s</td>
    </tr>
  </tbody>
</table>

## Per-Topic ROUGE-1 (F1)

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ai_chat_tools</td>
      <td>0.2021</td><td>0.4254</td>
      <td>0.2410</td><td>0.2101</td>
      <td>0.1660</td><td>0.2949</td>
      <td>0.1821</td><td>0.2635</td>
    </tr>
    <tr>
      <td>ai_consciousness</td>
      <td>0.2580</td><td>0.4540</td>
      <td>0.1501</td><td>0.2671</td>
      <td>0.1476</td><td>0.2366</td>
      <td>0.1662</td><td>0.3648</td>
    </tr>
    <tr>
      <td>ai_consciousness_friendship</td>
      <td>0.3911</td><td>0.4905</td>
      <td>0.2495</td><td>0.4639</td>
      <td>0.2624</td><td>0.4216</td>
      <td>0.3581</td><td>0.5567</td>
    </tr>
    <tr>
      <td>ai_meta</td>
      <td>0.2663</td><td>0.2581</td>
      <td>0.2994</td><td>0.3636</td>
      <td>0.1513</td><td>0.2757</td>
      <td>0.1769</td><td>0.3214</td>
    </tr>
    <tr>
      <td>bhutan_travel</td>
      <td>0.2285</td><td>0.4050</td>
      <td>0.1547</td><td>0.4433</td>
      <td>0.3182</td><td>0.0975</td>
      <td>0.3304</td><td>0.5440</td>
    </tr>
    <tr>
      <td>chess</td>
      <td>0.3337</td><td>0.3140</td>
      <td>0.1864</td><td>0.5036</td>
      <td>0.2256</td><td>0.3418</td>
      <td>0.2354</td><td>0.4324</td>
    </tr>
    <tr>
      <td>child_nutrition</td>
      <td>0.1623</td><td>0.3047</td>
      <td>0.2113</td><td>0.2341</td>
      <td>0.1610</td><td>0.2655</td>
      <td>0.1934</td><td>0.1596</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving</td>
      <td>0.3874</td><td>0.8199</td>
      <td>0.4431</td><td>0.5997</td>
      <td>0.2359</td><td>0.6293</td>
      <td>0.0841</td><td>0.6293</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_argument</td>
      <td>0.4291</td><td>0.5270</td>
      <td>0.3927</td><td>0.4427</td>
      <td>0.2213</td><td>0.6188</td>
      <td>0.2921</td><td>0.6237</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_corrections</td>
      <td>0.3542</td><td>0.5931</td>
      <td>0.3301</td><td>0.6345</td>
      <td>0.0661</td><td>0.6736</td>
      <td>0.1684</td><td>0.6911</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_math_errors</td>
      <td>0.3121</td><td>0.8059</td>
      <td>0.4259</td><td>0.6610</td>
      <td>0.0911</td><td>0.6458</td>
      <td>0.2279</td><td>0.6458</td>
    </tr>
    <tr>
      <td>covid_safety</td>
      <td>0.3567</td><td>0.3862</td>
      <td>0.2496</td><td>0.3871</td>
      <td>0.2354</td><td>0.0880</td>
      <td>0.1893</td><td>0.0698</td>
    </tr>
    <tr>
      <td>covid_safety_hiv_aids</td>
      <td>0.1604</td><td>0.3547</td>
      <td>0.2304</td><td>0.1854</td>
      <td>0.1710</td><td>0.3229</td>
      <td>0.0599</td><td>0.1566</td>
    </tr>
    <tr>
      <td>dsp_wavelets</td>
      <td>0.1245</td><td>0.1577</td>
      <td>0.1007</td><td>0.1582</td>
      <td>0.1588</td><td>0.1950</td>
      <td>0.0609</td><td>0.0963</td>
    </tr>
    <tr>
      <td>electroculture</td>
      <td>0.0892</td><td>0.2333</td>
      <td>0.1120</td><td>0.2422</td>
      <td>0.0149</td><td>0.3496</td>
      <td>0.0591</td><td>0.3274</td>
    </tr>
    <tr>
      <td>emoji_game</td>
      <td>0.1515</td><td>0.1117</td>
      <td>0.1811</td><td>0.2156</td>
      <td>0.2063</td><td>0.3143</td>
      <td>0.0419</td><td>0.3000</td>
    </tr>
    <tr>
      <td>game_degree_guess</td>
      <td>0.1891</td><td>0.4330</td>
      <td>0.2290</td><td>0.5918</td>
      <td>0.2200</td><td>0.6593</td>
      <td>0.1073</td><td>0.4763</td>
    </tr>
    <tr>
      <td>game_twenty_questions</td>
      <td>0.1354</td><td>0.1918</td>
      <td>0.2139</td><td>0.2957</td>
      <td>0.1749</td><td>0.4551</td>
      <td>0.0499</td><td>0.3575</td>
    </tr>
    <tr>
      <td>geography_belgium</td>
      <td>0.3109</td><td>0.6798</td>
      <td>0.3982</td><td>0.5222</td>
      <td>0.4461</td><td>0.4358</td>
      <td>0.1328</td><td>0.6110</td>
    </tr>
    <tr>
      <td>humanity_future_150y</td>
      <td>0.3412</td><td>0.4418</td>
      <td>0.2256</td><td>0.4732</td>
      <td>0.1368</td><td>0.4710</td>
      <td>0.0458</td><td>0.4304</td>
    </tr>
    <tr>
      <td>indian_astrology</td>
      <td>0.1591</td><td>0.3579</td>
      <td>0.1761</td><td>0.2527</td>
      <td>0.0289</td><td>0.2203</td>
      <td>0.0424</td><td>0.0185</td>
    </tr>
    <tr>
      <td>indian_history</td>
      <td>0.1420</td><td>0.6154</td>
      <td>0.1211</td><td>0.5679</td>
      <td>0.1869</td><td>0.6870</td>
      <td>0.1618</td><td>0.5185</td>
    </tr>
    <tr>
      <td>indian_legal</td>
      <td>0.2342</td><td>0.6822</td>
      <td>0.2560</td><td>0.4519</td>
      <td>0.2108</td><td>0.3882</td>
      <td>0.2389</td><td>0.3860</td>
    </tr>
    <tr>
      <td>indian_legal_family</td>
      <td>0.1410</td><td>0.3434</td>
      <td>0.2133</td><td>0.4432</td>
      <td>0.2343</td><td>0.6025</td>
      <td>0.1953</td><td>0.0270</td>
    </tr>
    <tr>
      <td>jokes</td>
      <td>0.3048</td><td>0.6551</td>
      <td>0.1566</td><td>0.6627</td>
      <td>0.1901</td><td>0.5973</td>
      <td>0.2804</td><td>0.6638</td>
    </tr>
    <tr>
      <td>karnataka_elections</td>
      <td>0.2515</td><td>0.3884</td>
      <td>0.3563</td><td>0.7264</td>
      <td>0.0278</td><td>0.3956</td>
      <td>0.2916</td><td>0.2995</td>
    </tr>
    <tr>
      <td>linux_audio</td>
      <td>0.3791</td><td>0.4970</td>
      <td>0.3067</td><td>0.5253</td>
      <td>0.2950</td><td>0.4704</td>
      <td>0.3300</td><td>0.0591</td>
    </tr>
    <tr>
      <td>literature_camus</td>
      <td>0.2144</td><td>0.3049</td>
      <td>0.1960</td><td>0.2961</td>
      <td>0.1765</td><td>0.3049</td>
      <td>0.2126</td><td>0.0270</td>
    </tr>
    <tr>
      <td>llm_knowledge</td>
      <td>0.3093</td><td>0.2710</td>
      <td>0.2396</td><td>0.3205</td>
      <td>0.1585</td><td>0.2670</td>
      <td>0.0194</td><td>0.2085</td>
    </tr>
    <tr>
      <td>logic_puzzle</td>
      <td>0.2775</td><td>0.7113</td>
      <td>0.0833</td><td>0.6097</td>
      <td>0.2430</td><td>0.4903</td>
      <td>0.1870</td><td>0.6263</td>
    </tr>
    <tr>
      <td>lsat_medical_conference</td>
      <td>0.1429</td><td>0.7286</td>
      <td>0.1687</td><td>0.4985</td>
      <td>0.0938</td><td>0.6478</td>
      <td>0.1206</td><td>0.6977</td>
    </tr>
    <tr>
      <td>lsat_product_codes</td>
      <td>0.1284</td><td>0.2628</td>
      <td>0.1806</td><td>0.2555</td>
      <td>0.0268</td><td>0.1056</td>
      <td>0.0762</td><td>0.2708</td>
    </tr>
    <tr>
      <td>medical_dsd</td>
      <td>0.2218</td><td>0.6041</td>
      <td>0.1549</td><td>0.3869</td>
      <td>0.2271</td><td>0.3125</td>
      <td>0.1974</td><td>0.3406</td>
    </tr>
    <tr>
      <td>personas_roleplay</td>
      <td>0.2727</td><td>0.4322</td>
      <td>0.2299</td><td>0.4697</td>
      <td>0.2337</td><td>0.7983</td>
      <td>0.0653</td><td>0.4448</td>
    </tr>
    <tr>
      <td>physics_cosmology</td>
      <td>0.3249</td><td>0.6305</td>
      <td>0.3117</td><td>0.4609</td>
      <td>0.2785</td><td>0.0990</td>
      <td>0.2125</td><td>0.4503</td>
    </tr>
    <tr>
      <td>physics_violin_nanoscale</td>
      <td>0.3377</td><td>0.1142</td>
      <td>0.3416</td><td>0.3005</td>
      <td>0.2473</td><td>0.4119</td>
      <td>0.1557</td><td>0.2977</td>
    </tr>
    <tr>
      <td>scifi_films</td>
      <td>0.2909</td><td>0.2210</td>
      <td>0.2248</td><td>0.2548</td>
      <td>0.0148</td><td>0.1974</td>
      <td>0.0601</td><td>0.2759</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000</td>
      <td>0.1155</td><td>0.3492</td>
      <td>0.2967</td><td>0.3358</td>
      <td>0.2331</td><td>0.4793</td>
      <td>0.0791</td><td>0.4857</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000_games</td>
      <td>0.1543</td><td>0.3055</td>
      <td>0.2009</td><td>0.2618</td>
      <td>0.1588</td><td>0.3373</td>
      <td>0.0462</td><td>0.2645</td>
    </tr>
    <tr>
      <td>scifi_films_liu_cixin</td>
      <td>0.2654</td><td>0.2099</td>
      <td>0.2943</td><td>0.3290</td>
      <td>0.3026</td><td>0.4444</td>
      <td>0.0996</td><td>0.3695</td>
    </tr>
    <tr>
      <td>therapy</td>
      <td>0.2608</td><td>0.3848</td>
      <td>0.2003</td><td>0.4561</td>
      <td>0.3206</td><td>0.5734</td>
      <td>0.1086</td><td>0.0428</td>
    </tr>
    <tr>
      <td>therapy_manipulation</td>
      <td>0.2090</td><td>0.3110</td>
      <td>0.1898</td><td>0.4475</td>
      <td>0.0466</td><td>0.4167</td>
      <td>0.0984</td><td>0.0867</td>
    </tr>
    <tr>
      <td>wildfires_alberta</td>
      <td>0.2067</td><td>0.4619</td>
      <td>0.2640</td><td>0.3957</td>
      <td>0.0396</td><td>0.4011</td>
      <td>0.2525</td><td>0.3232</td>
    </tr>
  </tbody>
</table>

## Per-Topic ROUGE-L (F1)

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ai_chat_tools</td>
      <td>0.1276</td><td>0.2810</td>
      <td>0.1480</td><td>0.0922</td>
      <td>0.0779</td><td>0.1909</td>
      <td>0.0802</td><td>0.1579</td>
    </tr>
    <tr>
      <td>ai_consciousness</td>
      <td>0.1159</td><td>0.1982</td>
      <td>0.0746</td><td>0.1786</td>
      <td>0.0779</td><td>0.1840</td>
      <td>0.0803</td><td>0.3455</td>
    </tr>
    <tr>
      <td>ai_consciousness_friendship</td>
      <td>0.1508</td><td>0.2503</td>
      <td>0.1083</td><td>0.3138</td>
      <td>0.1239</td><td>0.3253</td>
      <td>0.1266</td><td>0.3264</td>
    </tr>
    <tr>
      <td>ai_meta</td>
      <td>0.1241</td><td>0.1263</td>
      <td>0.1465</td><td>0.2466</td>
      <td>0.0798</td><td>0.1892</td>
      <td>0.0750</td><td>0.1923</td>
    </tr>
    <tr>
      <td>bhutan_travel</td>
      <td>0.1183</td><td>0.3870</td>
      <td>0.0889</td><td>0.3488</td>
      <td>0.3094</td><td>0.0796</td>
      <td>0.1550</td><td>0.4456</td>
    </tr>
    <tr>
      <td>chess</td>
      <td>0.1423</td><td>0.1433</td>
      <td>0.0993</td><td>0.4331</td>
      <td>0.0986</td><td>0.2852</td>
      <td>0.1111</td><td>0.3430</td>
    </tr>
    <tr>
      <td>child_nutrition</td>
      <td>0.0724</td><td>0.1439</td>
      <td>0.0999</td><td>0.1448</td>
      <td>0.0744</td><td>0.2157</td>
      <td>0.0889</td><td>0.1138</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving</td>
      <td>0.1635</td><td>0.7291</td>
      <td>0.3096</td><td>0.4749</td>
      <td>0.1303</td><td>0.4829</td>
      <td>0.0664</td><td>0.4829</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_argument</td>
      <td>0.2162</td><td>0.3556</td>
      <td>0.2024</td><td>0.2710</td>
      <td>0.1270</td><td>0.4094</td>
      <td>0.1445</td><td>0.3041</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_corrections</td>
      <td>0.1644</td><td>0.3690</td>
      <td>0.2300</td><td>0.4655</td>
      <td>0.0555</td><td>0.3473</td>
      <td>0.1006</td><td>0.3740</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_math_errors</td>
      <td>0.1545</td><td>0.6430</td>
      <td>0.2630</td><td>0.5428</td>
      <td>0.0771</td><td>0.5432</td>
      <td>0.1348</td><td>0.5432</td>
    </tr>
    <tr>
      <td>covid_safety</td>
      <td>0.1783</td><td>0.1501</td>
      <td>0.1110</td><td>0.2979</td>
      <td>0.1050</td><td>0.0773</td>
      <td>0.0930</td><td>0.0640</td>
    </tr>
    <tr>
      <td>covid_safety_hiv_aids</td>
      <td>0.0702</td><td>0.2993</td>
      <td>0.1130</td><td>0.1440</td>
      <td>0.0895</td><td>0.3091</td>
      <td>0.0434</td><td>0.1398</td>
    </tr>
    <tr>
      <td>dsp_wavelets</td>
      <td>0.0728</td><td>0.0791</td>
      <td>0.0597</td><td>0.0910</td>
      <td>0.0812</td><td>0.1269</td>
      <td>0.0359</td><td>0.0713</td>
    </tr>
    <tr>
      <td>electroculture</td>
      <td>0.0635</td><td>0.2119</td>
      <td>0.0744</td><td>0.2382</td>
      <td>0.0100</td><td>0.3391</td>
      <td>0.0456</td><td>0.3265</td>
    </tr>
    <tr>
      <td>emoji_game</td>
      <td>0.1038</td><td>0.0806</td>
      <td>0.1274</td><td>0.1540</td>
      <td>0.1375</td><td>0.2738</td>
      <td>0.0389</td><td>0.1529</td>
    </tr>
    <tr>
      <td>game_degree_guess</td>
      <td>0.1006</td><td>0.2108</td>
      <td>0.1279</td><td>0.4014</td>
      <td>0.1087</td><td>0.5149</td>
      <td>0.0683</td><td>0.3312</td>
    </tr>
    <tr>
      <td>game_twenty_questions</td>
      <td>0.0771</td><td>0.1120</td>
      <td>0.1262</td><td>0.1632</td>
      <td>0.0885</td><td>0.3913</td>
      <td>0.0369</td><td>0.3238</td>
    </tr>
    <tr>
      <td>geography_belgium</td>
      <td>0.1329</td><td>0.5853</td>
      <td>0.1663</td><td>0.4182</td>
      <td>0.2032</td><td>0.4071</td>
      <td>0.0945</td><td>0.3808</td>
    </tr>
    <tr>
      <td>humanity_future_150y</td>
      <td>0.2547</td><td>0.3886</td>
      <td>0.1213</td><td>0.4630</td>
      <td>0.0815</td><td>0.4684</td>
      <td>0.0316</td><td>0.4094</td>
    </tr>
    <tr>
      <td>indian_astrology</td>
      <td>0.0829</td><td>0.2640</td>
      <td>0.0999</td><td>0.2097</td>
      <td>0.0246</td><td>0.1735</td>
      <td>0.0306</td><td>0.0139</td>
    </tr>
    <tr>
      <td>indian_history</td>
      <td>0.0966</td><td>0.4497</td>
      <td>0.0895</td><td>0.3580</td>
      <td>0.1121</td><td>0.4609</td>
      <td>0.1225</td><td>0.4233</td>
    </tr>
    <tr>
      <td>indian_legal</td>
      <td>0.1155</td><td>0.6173</td>
      <td>0.1351</td><td>0.4182</td>
      <td>0.1197</td><td>0.3173</td>
      <td>0.1194</td><td>0.2202</td>
    </tr>
    <tr>
      <td>indian_legal_family</td>
      <td>0.0832</td><td>0.2144</td>
      <td>0.1343</td><td>0.3735</td>
      <td>0.1179</td><td>0.5665</td>
      <td>0.1316</td><td>0.0180</td>
    </tr>
    <tr>
      <td>jokes</td>
      <td>0.1628</td><td>0.5226</td>
      <td>0.1325</td><td>0.6209</td>
      <td>0.1281</td><td>0.4887</td>
      <td>0.1771</td><td>0.5319</td>
    </tr>
    <tr>
      <td>karnataka_elections</td>
      <td>0.1304</td><td>0.2810</td>
      <td>0.1987</td><td>0.6430</td>
      <td>0.0199</td><td>0.2706</td>
      <td>0.1434</td><td>0.2047</td>
    </tr>
    <tr>
      <td>linux_audio</td>
      <td>0.1954</td><td>0.3550</td>
      <td>0.1488</td><td>0.2373</td>
      <td>0.1605</td><td>0.2391</td>
      <td>0.1449</td><td>0.0432</td>
    </tr>
    <tr>
      <td>literature_camus</td>
      <td>0.1067</td><td>0.2587</td>
      <td>0.0993</td><td>0.2663</td>
      <td>0.0858</td><td>0.2018</td>
      <td>0.0937</td><td>0.0240</td>
    </tr>
    <tr>
      <td>llm_knowledge</td>
      <td>0.1494</td><td>0.1492</td>
      <td>0.1125</td><td>0.1700</td>
      <td>0.0784</td><td>0.2137</td>
      <td>0.0141</td><td>0.1513</td>
    </tr>
    <tr>
      <td>logic_puzzle</td>
      <td>0.1659</td><td>0.5798</td>
      <td>0.0702</td><td>0.5306</td>
      <td>0.1371</td><td>0.3666</td>
      <td>0.1220</td><td>0.4811</td>
    </tr>
    <tr>
      <td>lsat_medical_conference</td>
      <td>0.0772</td><td>0.5771</td>
      <td>0.1139</td><td>0.4758</td>
      <td>0.0704</td><td>0.6337</td>
      <td>0.0778</td><td>0.6487</td>
    </tr>
    <tr>
      <td>lsat_product_codes</td>
      <td>0.0840</td><td>0.2416</td>
      <td>0.1213</td><td>0.2247</td>
      <td>0.0255</td><td>0.1035</td>
      <td>0.0557</td><td>0.2610</td>
    </tr>
    <tr>
      <td>medical_dsd</td>
      <td>0.0988</td><td>0.3196</td>
      <td>0.0896</td><td>0.2373</td>
      <td>0.0939</td><td>0.2199</td>
      <td>0.1138</td><td>0.1339</td>
    </tr>
    <tr>
      <td>personas_roleplay</td>
      <td>0.1096</td><td>0.1648</td>
      <td>0.1236</td><td>0.3371</td>
      <td>0.1116</td><td>0.7344</td>
      <td>0.0435</td><td>0.2517</td>
    </tr>
    <tr>
      <td>physics_cosmology</td>
      <td>0.1861</td><td>0.4972</td>
      <td>0.2315</td><td>0.2868</td>
      <td>0.2089</td><td>0.0921</td>
      <td>0.1324</td><td>0.3874</td>
    </tr>
    <tr>
      <td>physics_violin_nanoscale</td>
      <td>0.1876</td><td>0.0913</td>
      <td>0.2067</td><td>0.1897</td>
      <td>0.1649</td><td>0.2348</td>
      <td>0.1107</td><td>0.2558</td>
    </tr>
    <tr>
      <td>scifi_films</td>
      <td>0.1211</td><td>0.1099</td>
      <td>0.1172</td><td>0.1471</td>
      <td>0.0121</td><td>0.1268</td>
      <td>0.0384</td><td>0.2287</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000</td>
      <td>0.0878</td><td>0.1637</td>
      <td>0.1540</td><td>0.1810</td>
      <td>0.1084</td><td>0.4247</td>
      <td>0.0494</td><td>0.2491</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000_games</td>
      <td>0.0874</td><td>0.1468</td>
      <td>0.1112</td><td>0.1527</td>
      <td>0.0907</td><td>0.2099</td>
      <td>0.0361</td><td>0.1391</td>
    </tr>
    <tr>
      <td>scifi_films_liu_cixin</td>
      <td>0.1503</td><td>0.1125</td>
      <td>0.1625</td><td>0.2857</td>
      <td>0.1655</td><td>0.3670</td>
      <td>0.0630</td><td>0.2516</td>
    </tr>
    <tr>
      <td>therapy</td>
      <td>0.1365</td><td>0.3266</td>
      <td>0.1202</td><td>0.3894</td>
      <td>0.1283</td><td>0.4230</td>
      <td>0.0658</td><td>0.0293</td>
    </tr>
    <tr>
      <td>therapy_manipulation</td>
      <td>0.1061</td><td>0.2736</td>
      <td>0.1005</td><td>0.3151</td>
      <td>0.0361</td><td>0.3913</td>
      <td>0.0679</td><td>0.0559</td>
    </tr>
    <tr>
      <td>wildfires_alberta</td>
      <td>0.1348</td><td>0.4571</td>
      <td>0.1305</td><td>0.3828</td>
      <td>0.0321</td><td>0.3140</td>
      <td>0.0957</td><td>0.2352</td>
    </tr>
  </tbody>
</table>

## Per-Topic BLEU-2

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ai_chat_tools</td>
      <td>0.0168</td><td>0.0916</td>
      <td>0.0131</td><td>0.0100</td>
      <td>0.0034</td><td>0.0071</td>
      <td>0.0087</td><td>0.0126</td>
    </tr>
    <tr>
      <td>ai_consciousness</td>
      <td>0.0119</td><td>0.1148</td>
      <td>0.0001</td><td>0.0053</td>
      <td>0.0010</td><td>0.0023</td>
      <td>0.0016</td><td>0.0352</td>
    </tr>
    <tr>
      <td>ai_consciousness_friendship</td>
      <td>0.0633</td><td>0.1564</td>
      <td>0.0126</td><td>0.1082</td>
      <td>0.0331</td><td>0.0756</td>
      <td>0.0600</td><td>0.1982</td>
    </tr>
    <tr>
      <td>ai_meta</td>
      <td>0.0260</td><td>0.0137</td>
      <td>0.0201</td><td>0.0341</td>
      <td>0.0020</td><td>0.0072</td>
      <td>0.0031</td><td>0.0148</td>
    </tr>
    <tr>
      <td>bhutan_travel</td>
      <td>0.0156</td><td>0.0300</td>
      <td>0.0030</td><td>0.0650</td>
      <td>0.0164</td><td>0.0000</td>
      <td>0.0804</td><td>0.1759</td>
    </tr>
    <tr>
      <td>chess</td>
      <td>0.0647</td><td>0.0375</td>
      <td>0.0044</td><td>0.2899</td>
      <td>0.0125</td><td>0.0463</td>
      <td>0.0255</td><td>0.1829</td>
    </tr>
    <tr>
      <td>child_nutrition</td>
      <td>0.0038</td><td>0.0940</td>
      <td>0.0112</td><td>0.0058</td>
      <td>0.0015</td><td>0.0057</td>
      <td>0.0082</td><td>0.0000</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving</td>
      <td>0.1040</td><td>0.6555</td>
      <td>0.1880</td><td>0.3241</td>
      <td>0.0241</td><td>0.3456</td>
      <td>0.0000</td><td>0.3456</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_argument</td>
      <td>0.1375</td><td>0.2428</td>
      <td>0.1045</td><td>0.1009</td>
      <td>0.0232</td><td>0.3317</td>
      <td>0.0649</td><td>0.3063</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_corrections</td>
      <td>0.0756</td><td>0.2668</td>
      <td>0.0508</td><td>0.3583</td>
      <td>0.0000</td><td>0.4033</td>
      <td>0.0030</td><td>0.4252</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_math_errors</td>
      <td>0.0444</td><td>0.6123</td>
      <td>0.1414</td><td>0.4137</td>
      <td>0.0000</td><td>0.3792</td>
      <td>0.0074</td><td>0.3792</td>
    </tr>
    <tr>
      <td>covid_safety</td>
      <td>0.0946</td><td>0.0588</td>
      <td>0.0088</td><td>0.0487</td>
      <td>0.0100</td><td>0.0000</td>
      <td>0.0006</td><td>0.0000</td>
    </tr>
    <tr>
      <td>covid_safety_hiv_aids</td>
      <td>0.0076</td><td>0.0533</td>
      <td>0.0166</td><td>0.0015</td>
      <td>0.0027</td><td>0.0246</td>
      <td>0.0000</td><td>0.0000</td>
    </tr>
    <tr>
      <td>dsp_wavelets</td>
      <td>0.0000</td><td>0.0000</td>
      <td>0.0000</td><td>0.0000</td>
      <td>0.0001</td><td>0.0003</td>
      <td>0.0000</td><td>0.0000</td>
    </tr>
    <tr>
      <td>electroculture</td>
      <td>0.0002</td><td>0.0019</td>
      <td>0.0001</td><td>0.0024</td>
      <td>0.0000</td><td>0.0268</td>
      <td>0.0000</td><td>0.0187</td>
    </tr>
    <tr>
      <td>emoji_game</td>
      <td>0.0023</td><td>0.0001</td>
      <td>0.0057</td><td>0.0155</td>
      <td>0.0140</td><td>0.0386</td>
      <td>0.0000</td><td>0.0394</td>
    </tr>
    <tr>
      <td>game_degree_guess</td>
      <td>0.0048</td><td>0.1302</td>
      <td>0.0337</td><td>0.3565</td>
      <td>0.0510</td><td>0.3866</td>
      <td>0.0001</td><td>0.1302</td>
    </tr>
    <tr>
      <td>game_twenty_questions</td>
      <td>0.0003</td><td>0.0025</td>
      <td>0.0060</td><td>0.0107</td>
      <td>0.0006</td><td>0.1385</td>
      <td>0.0000</td><td>0.0558</td>
    </tr>
    <tr>
      <td>geography_belgium</td>
      <td>0.0573</td><td>0.3591</td>
      <td>0.0846</td><td>0.1555</td>
      <td>0.1489</td><td>0.1770</td>
      <td>0.0000</td><td>0.3593</td>
    </tr>
    <tr>
      <td>humanity_future_150y</td>
      <td>0.0324</td><td>0.0825</td>
      <td>0.0117</td><td>0.1073</td>
      <td>0.0001</td><td>0.1089</td>
      <td>0.0000</td><td>0.0846</td>
    </tr>
    <tr>
      <td>indian_astrology</td>
      <td>0.0016</td><td>0.1511</td>
      <td>0.0021</td><td>0.0043</td>
      <td>0.0000</td><td>0.0011</td>
      <td>0.0000</td><td>0.0000</td>
    </tr>
    <tr>
      <td>indian_history</td>
      <td>0.0320</td><td>0.3668</td>
      <td>0.0041</td><td>0.3288</td>
      <td>0.0358</td><td>0.4292</td>
      <td>0.0238</td><td>0.3107</td>
    </tr>
    <tr>
      <td>indian_legal</td>
      <td>0.0279</td><td>0.4208</td>
      <td>0.0366</td><td>0.0891</td>
      <td>0.0341</td><td>0.0443</td>
      <td>0.0337</td><td>0.0452</td>
    </tr>
    <tr>
      <td>indian_legal_family</td>
      <td>0.0017</td><td>0.0289</td>
      <td>0.0178</td><td>0.0827</td>
      <td>0.0231</td><td>0.2784</td>
      <td>0.0592</td><td>0.0000</td>
    </tr>
    <tr>
      <td>jokes</td>
      <td>0.0869</td><td>0.4192</td>
      <td>0.0154</td><td>0.4894</td>
      <td>0.0371</td><td>0.3817</td>
      <td>0.1276</td><td>0.5105</td>
    </tr>
    <tr>
      <td>karnataka_elections</td>
      <td>0.0356</td><td>0.1337</td>
      <td>0.0713</td><td>0.5329</td>
      <td>0.0000</td><td>0.0543</td>
      <td>0.0659</td><td>0.0100</td>
    </tr>
    <tr>
      <td>linux_audio</td>
      <td>0.0843</td><td>0.1389</td>
      <td>0.0395</td><td>0.2167</td>
      <td>0.0599</td><td>0.1208</td>
      <td>0.0518</td><td>0.0000</td>
    </tr>
    <tr>
      <td>literature_camus</td>
      <td>0.0068</td><td>0.0100</td>
      <td>0.0026</td><td>0.0088</td>
      <td>0.0033</td><td>0.0155</td>
      <td>0.0069</td><td>0.0000</td>
    </tr>
    <tr>
      <td>llm_knowledge</td>
      <td>0.0532</td><td>0.0126</td>
      <td>0.0095</td><td>0.0167</td>
      <td>0.0011</td><td>0.0045</td>
      <td>0.0000</td><td>0.0008</td>
    </tr>
    <tr>
      <td>logic_puzzle</td>
      <td>0.0304</td><td>0.4504</td>
      <td>0.0145</td><td>0.2920</td>
      <td>0.0229</td><td>0.1455</td>
      <td>0.0353</td><td>0.3373</td>
    </tr>
    <tr>
      <td>lsat_medical_conference</td>
      <td>0.0211</td><td>0.4980</td>
      <td>0.0504</td><td>0.1472</td>
      <td>0.0068</td><td>0.3204</td>
      <td>0.0111</td><td>0.3805</td>
    </tr>
    <tr>
      <td>lsat_product_codes</td>
      <td>0.0019</td><td>0.0061</td>
      <td>0.0164</td><td>0.0035</td>
      <td>0.0000</td><td>0.0000</td>
      <td>0.0000</td><td>0.0060</td>
    </tr>
    <tr>
      <td>medical_dsd</td>
      <td>0.0055</td><td>0.2674</td>
      <td>0.0032</td><td>0.0567</td>
      <td>0.0043</td><td>0.0153</td>
      <td>0.0046</td><td>0.0222</td>
    </tr>
    <tr>
      <td>personas_roleplay</td>
      <td>0.0444</td><td>0.1509</td>
      <td>0.0421</td><td>0.1342</td>
      <td>0.0360</td><td>0.6437</td>
      <td>0.0000</td><td>0.1763</td>
    </tr>
    <tr>
      <td>physics_cosmology</td>
      <td>0.1455</td><td>0.3288</td>
      <td>0.0892</td><td>0.1347</td>
      <td>0.0774</td><td>0.0000</td>
      <td>0.0257</td><td>0.0943</td>
    </tr>
    <tr>
      <td>physics_violin_nanoscale</td>
      <td>0.0881</td><td>0.0007</td>
      <td>0.1040</td><td>0.0966</td>
      <td>0.0830</td><td>0.1179</td>
      <td>0.0016</td><td>0.0180</td>
    </tr>
    <tr>
      <td>scifi_films</td>
      <td>0.0328</td><td>0.0065</td>
      <td>0.0102</td><td>0.0030</td>
      <td>0.0000</td><td>0.0003</td>
      <td>0.0000</td><td>0.0058</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000</td>
      <td>0.0120</td><td>0.0741</td>
      <td>0.0420</td><td>0.0844</td>
      <td>0.0210</td><td>0.1106</td>
      <td>0.0000</td><td>0.1530</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000_games</td>
      <td>0.0110</td><td>0.0420</td>
      <td>0.0109</td><td>0.0337</td>
      <td>0.0062</td><td>0.0116</td>
      <td>0.0000</td><td>0.0074</td>
    </tr>
    <tr>
      <td>scifi_films_liu_cixin</td>
      <td>0.0249</td><td>0.0205</td>
      <td>0.0420</td><td>0.0241</td>
      <td>0.0368</td><td>0.1520</td>
      <td>0.0000</td><td>0.0496</td>
    </tr>
    <tr>
      <td>therapy</td>
      <td>0.0232</td><td>0.1376</td>
      <td>0.0168</td><td>0.0857</td>
      <td>0.0470</td><td>0.2326</td>
      <td>0.0000</td><td>0.0000</td>
    </tr>
    <tr>
      <td>therapy_manipulation</td>
      <td>0.0086</td><td>0.0146</td>
      <td>0.0078</td><td>0.0849</td>
      <td>0.0000</td><td>0.0529</td>
      <td>0.0000</td><td>0.0000</td>
    </tr>
    <tr>
      <td>wildfires_alberta</td>
      <td>0.0249</td><td>0.1150</td>
      <td>0.0287</td><td>0.0488</td>
      <td>0.0000</td><td>0.0594</td>
      <td>0.0273</td><td>0.0186</td>
    </tr>
  </tbody>
</table>


---

## Source Table: `backend/dataset/7b/merge/TABLE_3_SYSTEM_PERFORMANCE_MERGED.md`

# TABLE 3: MERGED SYSTEM PERFORMANCE METRICS (7B)

Merged from buffer-specific `TABLE_3_SYSTEM_PERFORMANCE.md` / `raw_metrics.json` files.

## Normal Conversation Performance

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Normal Conversation Turns</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
    </tr>
    <tr>
      <td>Avg Input Tokens</td>
      <td>2270</td><td>2205</td>
      <td>3384</td><td>3556</td>
      <td>5386</td><td>5685</td>
      <td>8107</td><td>8487</td>
    </tr>
    <tr>
      <td>Avg Output Tokens</td>
      <td>205</td><td>164</td>
      <td>214</td><td>235</td>
      <td>235</td><td>241</td>
      <td>220</td><td>230</td>
    </tr>
    <tr>
      <td>Avg Total Tokens</td>
      <td>2476</td><td>2369</td>
      <td>3598</td><td>3791</td>
      <td>5622</td><td>5927</td>
      <td>8327</td><td>8717</td>
    </tr>
    <tr>
      <td>Total Input Tokens</td>
      <td>701539</td><td>681497</td>
      <td>1045593</td><td>1098821</td>
      <td>1664366</td><td>1756760</td>
      <td>2505151</td><td>2622497</td>
    </tr>
    <tr>
      <td>Total Output Tokens</td>
      <td>63478</td><td>50650</td>
      <td>66087</td><td>72552</td>
      <td>72716</td><td>74536</td>
      <td>67935</td><td>70984</td>
    </tr>
    <tr>
      <td>Total Tokens</td>
      <td>765017</td><td>732147</td>
      <td>1111680</td><td>1171373</td>
      <td>1737082</td><td>1831296</td>
      <td>2573086</td><td>2693481</td>
    </tr>
    <tr>
      <td>Tokens Per Correct Answer</td>
      <td>11591</td><td>4067</td>
      <td>9038</td><td>8191</td>
      <td>35451</td><td>15389</td>
      <td>102923</td><td>25899</td>
    </tr>
    <tr>
      <td>Avg Latency</td>
      <td>12.19s</td><td>10.14s</td>
      <td>10.62s</td><td>10.55s</td>
      <td>11.70s</td><td>11.22s</td>
      <td>11.75s</td><td>11.71s</td>
    </tr>
    <tr>
      <td>Total Latency</td>
      <td>3765.47s</td><td>3133.41s</td>
      <td>3280.66s</td><td>3258.46s</td>
      <td>3615.37s</td><td>3468.37s</td>
      <td>3629.73s</td><td>3618.90s</td>
    </tr>
    <tr>
      <td>Cost per Query</td>
      <td>$0.000130</td><td>$0.000123</td>
      <td>$0.000186</td><td>$0.000197</td>
      <td>$0.000288</td><td>$0.000304</td>
      <td>$0.000423</td><td>$0.000443</td>
    </tr>
    <tr>
      <td>Cost per 1M Queries</td>
      <td>$130</td><td>$123</td>
      <td>$186</td><td>$197</td>
      <td>$288</td><td>$304</td>
      <td>$423</td><td>$443</td>
    </tr>
  </tbody>
</table>

## Including Recall/Summarization Probes

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Summarization Probe Calls</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
    </tr>
    <tr>
      <td>Summarization Probe Tokens</td>
      <td>158043</td><td>121521</td>
      <td>252519</td><td>188722</td>
      <td>336942</td><td>284817</td>
      <td>472634</td><td>403852</td>
    </tr>
    <tr>
      <td>Avg Tokens per Summarization Probe</td>
      <td>3675</td><td>2826</td>
      <td>5873</td><td>4389</td>
      <td>7836</td><td>6624</td>
      <td>10991</td><td>9392</td>
    </tr>
    <tr>
      <td>Combined Evaluated Calls</td>
      <td>352</td><td>352</td>
      <td>352</td><td>352</td>
      <td>352</td><td>352</td>
      <td>352</td><td>352</td>
    </tr>
    <tr>
      <td>Combined Total Tokens</td>
      <td>923060</td><td>853668</td>
      <td>1364199</td><td>1360095</td>
      <td>2074024</td><td>2116113</td>
      <td>3045720</td><td>3097333</td>
    </tr>
    <tr>
      <td>Combined Avg Tokens per Call</td>
      <td>2622</td><td>2425</td>
      <td>3876</td><td>3864</td>
      <td>5892</td><td>6012</td>
      <td>8653</td><td>8799</td>
    </tr>
  </tbody>
</table>


---

## Source Table: `backend/dataset/7b/merge/TABLE_4_RAG_DECISIONS_MERGED.md`

# TABLE 4: MERGED RAG DECISION BREAKDOWN (7B)

Merged from buffer-specific `TABLE_4_RAG_DECISIONS.md` / `raw_metrics.json` files.

## Normal Conversation Turns

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Total Turns</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
    </tr>
    <tr>
      <td>RAG-Eligible Turns</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>306</td><td>309</td>
      <td>302</td><td>309</td>
    </tr>
    <tr>
      <td>RAG Triggered</td>
      <td>47</td><td>48</td>
      <td>42</td><td>49</td>
      <td>27</td><td>12</td>
      <td>6</td><td>9</td>
    </tr>
    <tr>
      <td>Buffer Sufficient</td>
      <td>262</td><td>261</td>
      <td>267</td><td>260</td>
      <td>279</td><td>297</td>
      <td>296</td><td>300</td>
    </tr>
    <tr>
      <td>Retrieval Rate</td>
      <td>15.2%</td><td>15.5%</td>
      <td>13.6%</td><td>15.9%</td>
      <td>8.8%</td><td>3.9%</td>
      <td>2.0%</td><td>2.9%</td>
    </tr>
    <tr>
      <td>Buffer Rate</td>
      <td>84.8%</td><td>84.5%</td>
      <td>86.4%</td><td>84.1%</td>
      <td>91.2%</td><td>96.1%</td>
      <td>98.0%</td><td>97.1%</td>
    </tr>
    <tr>
      <td>Errors</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>3</td><td>0</td>
      <td>7</td><td>0</td>
    </tr>
    <tr>
      <td>RAG Disabled</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
    </tr>
    <tr>
      <td>No Vector Index</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
    </tr>
  </tbody>
</table>

## Recall/Summarization Probe RAG Decisions

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Probe Turns</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
    </tr>
    <tr>
      <td>RAG-Eligible Probe Turns</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
    </tr>
    <tr>
      <td>Probe RAG Triggered</td>
      <td>1</td><td>17</td>
      <td>2</td><td>9</td>
      <td>2</td><td>4</td>
      <td>0</td><td>1</td>
    </tr>
    <tr>
      <td>Probe Buffer Sufficient</td>
      <td>42</td><td>26</td>
      <td>41</td><td>34</td>
      <td>41</td><td>39</td>
      <td>43</td><td>42</td>
    </tr>
    <tr>
      <td>Probe Retrieval Rate</td>
      <td>2.3%</td><td>39.5%</td>
      <td>4.7%</td><td>20.9%</td>
      <td>4.7%</td><td>9.3%</td>
      <td>0.0%</td><td>2.3%</td>
    </tr>
    <tr>
      <td>Probe Buffer Rate</td>
      <td>97.7%</td><td>60.5%</td>
      <td>95.3%</td><td>79.1%</td>
      <td>95.3%</td><td>90.7%</td>
      <td>100.0%</td><td>97.7%</td>
    </tr>
    <tr>
      <td>Probe Errors</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
    </tr>
    <tr>
      <td>Probe RAG Disabled</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
    </tr>
  </tbody>
</table>


---

## Source Table: `backend/dataset/14b/merge/TABLE_1_CONTEXT_ISOLATION_MERGED.md`

# TABLE 1: MERGED CONTEXT ISOLATION METRICS (14B)

Merged from buffer-specific `TABLE_1_CONTEXT_ISOLATION.md` / `raw_metrics.json` files.

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Precision</td>
      <td>64.5%</td><td>77.8%</td>
      <td>81.2%</td><td>93.2%</td>
      <td>85.0%</td><td>89.2%</td>
      <td>81.6%</td><td>85.3%</td>
    </tr>
    <tr>
      <td>Recall</td>
      <td>52.6%</td><td>74.4%</td>
      <td>59.7%</td><td>80.2%</td>
      <td>60.1%</td><td>81.8%</td>
      <td>55.8%</td><td>69.5%</td>
    </tr>
    <tr>
      <td>F1</td>
      <td>51.2%</td><td>73.9%</td>
      <td>64.3%</td><td>83.4%</td>
      <td>62.5%</td><td>83.1%</td>
      <td>59.8%</td><td>73.1%</td>
    </tr>
    <tr>
      <td>Accuracy</td>
      <td>52.8%</td><td>74.4%</td>
      <td>59.9%</td><td>80.3%</td>
      <td>60.2%</td><td>81.9%</td>
      <td>56.0%</td><td>69.6%</td>
    </tr>
    <tr>
      <td>Pollution Rate</td>
      <td>47.2%</td><td>25.6%</td>
      <td>40.1%</td><td>19.7%</td>
      <td>39.8%</td><td>18.1%</td>
      <td>44.0%</td><td>30.4%</td>
    </tr>
    <tr>
      <td>Macro Precision</td>
      <td>52.0%</td><td>67.5%</td>
      <td>75.7%</td><td>88.1%</td>
      <td>77.6%</td><td>85.4%</td>
      <td>73.4%</td><td>79.5%</td>
    </tr>
    <tr>
      <td>Macro Recall</td>
      <td>52.7%</td><td>68.5%</td>
      <td>67.3%</td><td>78.7%</td>
      <td>65.4%</td><td>79.5%</td>
      <td>61.8%</td><td>65.3%</td>
    </tr>
    <tr>
      <td>Macro F1</td>
      <td>48.3%</td><td>65.8%</td>
      <td>67.1%</td><td>80.1%</td>
      <td>65.1%</td><td>79.7%</td>
      <td>61.4%</td><td>67.9%</td>
    </tr>
  </tbody>
</table>


---

## Source Table: `backend/dataset/14b/merge/TABLE_2_RECALL_SCORES_MERGED.md`

# TABLE 2: MERGED TOPIC RECALL SCORES (14B)

Merged from buffer-specific `TABLE_2_RECALL_SCORES.md` / `raw_metrics.json` files.

## Aggregate Scores and Probe Cost

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Avg ROUGE-1 (F1)</td>
      <td>0.3428</td><td>0.3896</td>
      <td>0.3378</td><td>0.4201</td>
      <td>0.2476</td><td>0.4187</td>
      <td>0.1745</td><td>0.3725</td>
    </tr>
    <tr>
      <td>Avg ROUGE-L (F1)</td>
      <td>0.2179</td><td>0.2634</td>
      <td>0.1982</td><td>0.3211</td>
      <td>0.1320</td><td>0.3143</td>
      <td>0.0997</td><td>0.2648</td>
    </tr>
    <tr>
      <td>Avg BLEU-2</td>
      <td>0.0967</td><td>0.1099</td>
      <td>0.0870</td><td>0.1338</td>
      <td>0.0516</td><td>0.1237</td>
      <td>0.0182</td><td>0.1315</td>
    </tr>
    <tr>
      <td>Topics Probed</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
    </tr>
    <tr>
      <td>Total Probe Tokens</td>
      <td>136045</td><td>104023</td>
      <td>274209</td><td>156136</td>
      <td>322902</td><td>269171</td>
      <td>359355</td><td>304196</td>
    </tr>
    <tr>
      <td>Avg Tokens per Probe</td>
      <td>3164</td><td>2419</td>
      <td>6377</td><td>3631</td>
      <td>7509</td><td>6260</td>
      <td>8357</td><td>7074</td>
    </tr>
    <tr>
      <td>Total Probe Latency</td>
      <td>1155.49s</td><td>989.76s</td>
      <td>1441.58s</td><td>997.15s</td>
      <td>1284.58s</td><td>1196.07s</td>
      <td>943.70s</td><td>957.29s</td>
    </tr>
    <tr>
      <td>Avg Probe Latency</td>
      <td>26.87s</td><td>23.02s</td>
      <td>33.53s</td><td>23.19s</td>
      <td>29.87s</td><td>27.82s</td>
      <td>21.95s</td><td>22.26s</td>
    </tr>
  </tbody>
</table>

## Per-Topic ROUGE-1 (F1)

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ai_chat_tools</td>
      <td>0.2148</td><td>0.3284</td>
      <td>0.2399</td><td>0.3234</td>
      <td>0.2600</td><td>0.3084</td>
      <td>0.2542</td><td>0.4631</td>
    </tr>
    <tr>
      <td>ai_consciousness</td>
      <td>0.3278</td><td>0.3130</td>
      <td>0.2393</td><td>0.3708</td>
      <td>0.3301</td><td>0.3407</td>
      <td>0.2873</td><td>0.4522</td>
    </tr>
    <tr>
      <td>ai_consciousness_friendship</td>
      <td>0.4958</td><td>0.4367</td>
      <td>0.3854</td><td>0.4820</td>
      <td>0.4914</td><td>0.3919</td>
      <td>0.4393</td><td>0.6308</td>
    </tr>
    <tr>
      <td>ai_meta</td>
      <td>0.3203</td><td>0.2989</td>
      <td>0.2553</td><td>0.2653</td>
      <td>0.2773</td><td>0.2542</td>
      <td>0.3800</td><td>0.2896</td>
    </tr>
    <tr>
      <td>bhutan_travel</td>
      <td>0.2604</td><td>0.5093</td>
      <td>0.3620</td><td>0.3455</td>
      <td>0.2670</td><td>0.3578</td>
      <td>0.0536</td><td>0.3580</td>
    </tr>
    <tr>
      <td>chess</td>
      <td>0.3145</td><td>0.3860</td>
      <td>0.2136</td><td>0.3079</td>
      <td>0.3286</td><td>0.3164</td>
      <td>0.1699</td><td>0.0541</td>
    </tr>
    <tr>
      <td>child_nutrition</td>
      <td>0.0597</td><td>0.2338</td>
      <td>0.0645</td><td>0.2653</td>
      <td>0.1847</td><td>0.1591</td>
      <td>0.0636</td><td>0.2512</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving</td>
      <td>0.3681</td><td>0.2827</td>
      <td>0.4463</td><td>0.8304</td>
      <td>0.4433</td><td>0.5869</td>
      <td>0.1142</td><td>0.5869</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_argument</td>
      <td>0.5306</td><td>0.4528</td>
      <td>0.5782</td><td>0.4190</td>
      <td>0.5882</td><td>0.3776</td>
      <td>0.2657</td><td>0.4026</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_corrections</td>
      <td>0.4375</td><td>0.4103</td>
      <td>0.5455</td><td>0.5422</td>
      <td>0.5263</td><td>0.5215</td>
      <td>0.1986</td><td>0.5100</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_math_errors</td>
      <td>0.3690</td><td>0.4563</td>
      <td>0.5022</td><td>0.4317</td>
      <td>0.0601</td><td>0.5876</td>
      <td>0.2765</td><td>0.5876</td>
    </tr>
    <tr>
      <td>covid_safety</td>
      <td>0.3472</td><td>0.3182</td>
      <td>0.3711</td><td>0.4786</td>
      <td>0.3068</td><td>0.3505</td>
      <td>0.2076</td><td>0.0042</td>
    </tr>
    <tr>
      <td>covid_safety_hiv_aids</td>
      <td>0.2908</td><td>0.2367</td>
      <td>0.2669</td><td>0.3147</td>
      <td>0.1855</td><td>0.2898</td>
      <td>0.2060</td><td>0.2313</td>
    </tr>
    <tr>
      <td>dsp_wavelets</td>
      <td>0.1456</td><td>0.1837</td>
      <td>0.1425</td><td>0.1574</td>
      <td>0.1225</td><td>0.1488</td>
      <td>0.0733</td><td>0.1285</td>
    </tr>
    <tr>
      <td>electroculture</td>
      <td>0.2797</td><td>0.1461</td>
      <td>0.3299</td><td>0.2496</td>
      <td>0.1563</td><td>0.3105</td>
      <td>0.1112</td><td>0.5948</td>
    </tr>
    <tr>
      <td>emoji_game</td>
      <td>0.2098</td><td>0.1628</td>
      <td>0.2237</td><td>0.2578</td>
      <td>0.1969</td><td>0.1227</td>
      <td>0.1229</td><td>0.2469</td>
    </tr>
    <tr>
      <td>game_degree_guess</td>
      <td>0.1818</td><td>0.3028</td>
      <td>0.2967</td><td>0.7091</td>
      <td>0.3461</td><td>0.7200</td>
      <td>0.1608</td><td>0.2519</td>
    </tr>
    <tr>
      <td>game_twenty_questions</td>
      <td>0.1682</td><td>0.0996</td>
      <td>0.2496</td><td>0.1376</td>
      <td>0.1858</td><td>0.1557</td>
      <td>0.0856</td><td>0.2444</td>
    </tr>
    <tr>
      <td>geography_belgium</td>
      <td>0.6840</td><td>0.6197</td>
      <td>0.6166</td><td>0.1516</td>
      <td>0.3885</td><td>0.6626</td>
      <td>0.2201</td><td>0.2827</td>
    </tr>
    <tr>
      <td>humanity_future_150y</td>
      <td>0.6165</td><td>0.4975</td>
      <td>0.4989</td><td>0.4812</td>
      <td>0.0258</td><td>0.4957</td>
      <td>0.0386</td><td>0.4494</td>
    </tr>
    <tr>
      <td>indian_astrology</td>
      <td>0.2555</td><td>0.3868</td>
      <td>0.3511</td><td>0.2678</td>
      <td>0.1743</td><td>0.3361</td>
      <td>0.1135</td><td>0.6588</td>
    </tr>
    <tr>
      <td>indian_history</td>
      <td>0.3762</td><td>0.5625</td>
      <td>0.1754</td><td>0.6824</td>
      <td>0.1889</td><td>0.7087</td>
      <td>0.1823</td><td>0.7525</td>
    </tr>
    <tr>
      <td>indian_legal</td>
      <td>0.3273</td><td>0.4579</td>
      <td>0.3074</td><td>0.4966</td>
      <td>0.2822</td><td>0.5000</td>
      <td>0.2462</td><td>0.3847</td>
    </tr>
    <tr>
      <td>indian_legal_family</td>
      <td>0.4045</td><td>0.4332</td>
      <td>0.2607</td><td>0.4029</td>
      <td>0.0270</td><td>0.5334</td>
      <td>0.1333</td><td>0.0503</td>
    </tr>
    <tr>
      <td>jokes</td>
      <td>0.0833</td><td>0.5138</td>
      <td>0.1844</td><td>0.5936</td>
      <td>0.1852</td><td>0.7105</td>
      <td>0.2451</td><td>0.7034</td>
    </tr>
    <tr>
      <td>karnataka_elections</td>
      <td>0.4453</td><td>0.3189</td>
      <td>0.4810</td><td>0.4940</td>
      <td>0.1914</td><td>0.4581</td>
      <td>0.1667</td><td>0.6508</td>
    </tr>
    <tr>
      <td>linux_audio</td>
      <td>0.7019</td><td>0.5343</td>
      <td>0.7342</td><td>0.6992</td>
      <td>0.4084</td><td>0.5210</td>
      <td>0.4132</td><td>0.5544</td>
    </tr>
    <tr>
      <td>literature_camus</td>
      <td>0.2219</td><td>0.3341</td>
      <td>0.2500</td><td>0.4397</td>
      <td>0.2137</td><td>0.3065</td>
      <td>0.0444</td><td>0.0279</td>
    </tr>
    <tr>
      <td>llm_knowledge</td>
      <td>0.3154</td><td>0.2412</td>
      <td>0.3287</td><td>0.3081</td>
      <td>0.3302</td><td>0.3605</td>
      <td>0.0665</td><td>0.3344</td>
    </tr>
    <tr>
      <td>logic_puzzle</td>
      <td>0.2078</td><td>0.5396</td>
      <td>0.3003</td><td>0.3687</td>
      <td>0.2439</td><td>0.4073</td>
      <td>0.1748</td><td>0.6639</td>
    </tr>
    <tr>
      <td>lsat_medical_conference</td>
      <td>0.3557</td><td>0.5696</td>
      <td>0.4831</td><td>0.6859</td>
      <td>0.0942</td><td>0.6933</td>
      <td>0.0993</td><td>0.4019</td>
    </tr>
    <tr>
      <td>lsat_product_codes</td>
      <td>0.1998</td><td>0.2197</td>
      <td>0.1917</td><td>0.2729</td>
      <td>0.0222</td><td>0.2556</td>
      <td>0.1023</td><td>0.0164</td>
    </tr>
    <tr>
      <td>medical_dsd</td>
      <td>0.3864</td><td>0.3557</td>
      <td>0.3853</td><td>0.4140</td>
      <td>0.0182</td><td>0.4112</td>
      <td>0.2974</td><td>0.0194</td>
    </tr>
    <tr>
      <td>personas_roleplay</td>
      <td>0.3044</td><td>0.3812</td>
      <td>0.3127</td><td>0.3097</td>
      <td>0.2711</td><td>0.4118</td>
      <td>0.2355</td><td>0.4390</td>
    </tr>
    <tr>
      <td>physics_cosmology</td>
      <td>0.5671</td><td>0.4351</td>
      <td>0.3138</td><td>0.4839</td>
      <td>0.0361</td><td>0.5460</td>
      <td>0.0532</td><td>0.4037</td>
    </tr>
    <tr>
      <td>physics_violin_nanoscale</td>
      <td>0.7542</td><td>0.8120</td>
      <td>0.3249</td><td>0.3952</td>
      <td>0.5492</td><td>0.3971</td>
      <td>0.3101</td><td>0.4575</td>
    </tr>
    <tr>
      <td>scifi_films</td>
      <td>0.2425</td><td>0.3483</td>
      <td>0.2421</td><td>0.3645</td>
      <td>0.2878</td><td>0.3446</td>
      <td>0.1211</td><td>0.0518</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000</td>
      <td>0.3087</td><td>0.3922</td>
      <td>0.3003</td><td>0.4535</td>
      <td>0.2899</td><td>0.4344</td>
      <td>0.0444</td><td>0.4400</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000_games</td>
      <td>0.2065</td><td>0.2346</td>
      <td>0.2326</td><td>0.2776</td>
      <td>0.1924</td><td>0.2086</td>
      <td>0.0856</td><td>0.2585</td>
    </tr>
    <tr>
      <td>scifi_films_liu_cixin</td>
      <td>0.4177</td><td>0.4797</td>
      <td>0.3933</td><td>0.5158</td>
      <td>0.3931</td><td>0.5862</td>
      <td>0.0440</td><td>0.1220</td>
    </tr>
    <tr>
      <td>therapy</td>
      <td>0.3477</td><td>0.6481</td>
      <td>0.3125</td><td>0.6585</td>
      <td>0.2588</td><td>0.5422</td>
      <td>0.1864</td><td>0.7239</td>
    </tr>
    <tr>
      <td>therapy_manipulation</td>
      <td>0.3819</td><td>0.3748</td>
      <td>0.4803</td><td>0.4704</td>
      <td>0.0119</td><td>0.4891</td>
      <td>0.0340</td><td>0.5561</td>
    </tr>
    <tr>
      <td>wildfires_alberta</td>
      <td>0.3077</td><td>0.5054</td>
      <td>0.3505</td><td>0.4897</td>
      <td>0.3036</td><td>0.3812</td>
      <td>0.3733</td><td>0.3257</td>
    </tr>
  </tbody>
</table>

## Per-Topic ROUGE-L (F1)

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ai_chat_tools</td>
      <td>0.1074</td><td>0.1834</td>
      <td>0.1087</td><td>0.2196</td>
      <td>0.1196</td><td>0.1834</td>
      <td>0.1134</td><td>0.2548</td>
    </tr>
    <tr>
      <td>ai_consciousness</td>
      <td>0.3026</td><td>0.1396</td>
      <td>0.1288</td><td>0.2334</td>
      <td>0.2706</td><td>0.2488</td>
      <td>0.1205</td><td>0.4032</td>
    </tr>
    <tr>
      <td>ai_consciousness_friendship</td>
      <td>0.2266</td><td>0.1606</td>
      <td>0.1622</td><td>0.3122</td>
      <td>0.2275</td><td>0.1939</td>
      <td>0.2401</td><td>0.3135</td>
    </tr>
    <tr>
      <td>ai_meta</td>
      <td>0.1797</td><td>0.1663</td>
      <td>0.1259</td><td>0.1628</td>
      <td>0.1203</td><td>0.1292</td>
      <td>0.1458</td><td>0.1805</td>
    </tr>
    <tr>
      <td>bhutan_travel</td>
      <td>0.1571</td><td>0.3628</td>
      <td>0.3182</td><td>0.2964</td>
      <td>0.1263</td><td>0.2836</td>
      <td>0.0383</td><td>0.3128</td>
    </tr>
    <tr>
      <td>chess</td>
      <td>0.1331</td><td>0.2616</td>
      <td>0.1048</td><td>0.1851</td>
      <td>0.1301</td><td>0.2210</td>
      <td>0.0949</td><td>0.0461</td>
    </tr>
    <tr>
      <td>child_nutrition</td>
      <td>0.0392</td><td>0.0956</td>
      <td>0.0409</td><td>0.2027</td>
      <td>0.0793</td><td>0.1155</td>
      <td>0.0430</td><td>0.2077</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving</td>
      <td>0.1813</td><td>0.1653</td>
      <td>0.1980</td><td>0.7435</td>
      <td>0.1873</td><td>0.4820</td>
      <td>0.0803</td><td>0.4820</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_argument</td>
      <td>0.2857</td><td>0.3270</td>
      <td>0.3050</td><td>0.2413</td>
      <td>0.3205</td><td>0.2587</td>
      <td>0.1538</td><td>0.2468</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_corrections</td>
      <td>0.2500</td><td>0.2500</td>
      <td>0.3192</td><td>0.3675</td>
      <td>0.3158</td><td>0.3954</td>
      <td>0.1206</td><td>0.3152</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_math_errors</td>
      <td>0.2222</td><td>0.2586</td>
      <td>0.2496</td><td>0.2620</td>
      <td>0.0420</td><td>0.4068</td>
      <td>0.1415</td><td>0.4068</td>
    </tr>
    <tr>
      <td>covid_safety</td>
      <td>0.1856</td><td>0.1316</td>
      <td>0.2742</td><td>0.3512</td>
      <td>0.1546</td><td>0.2762</td>
      <td>0.0908</td><td>0.0042</td>
    </tr>
    <tr>
      <td>covid_safety_hiv_aids</td>
      <td>0.2370</td><td>0.1243</td>
      <td>0.1054</td><td>0.2201</td>
      <td>0.0940</td><td>0.1870</td>
      <td>0.1166</td><td>0.1349</td>
    </tr>
    <tr>
      <td>dsp_wavelets</td>
      <td>0.1249</td><td>0.1030</td>
      <td>0.0757</td><td>0.1204</td>
      <td>0.0625</td><td>0.1038</td>
      <td>0.0520</td><td>0.0940</td>
    </tr>
    <tr>
      <td>electroculture</td>
      <td>0.2510</td><td>0.0897</td>
      <td>0.2919</td><td>0.2017</td>
      <td>0.0901</td><td>0.2993</td>
      <td>0.0748</td><td>0.5302</td>
    </tr>
    <tr>
      <td>emoji_game</td>
      <td>0.1422</td><td>0.1074</td>
      <td>0.1311</td><td>0.1828</td>
      <td>0.1205</td><td>0.1078</td>
      <td>0.1102</td><td>0.2147</td>
    </tr>
    <tr>
      <td>game_degree_guess</td>
      <td>0.0973</td><td>0.1655</td>
      <td>0.1332</td><td>0.5280</td>
      <td>0.1336</td><td>0.5557</td>
      <td>0.0863</td><td>0.1679</td>
    </tr>
    <tr>
      <td>game_twenty_questions</td>
      <td>0.1027</td><td>0.0681</td>
      <td>0.1342</td><td>0.0894</td>
      <td>0.1048</td><td>0.1123</td>
      <td>0.0589</td><td>0.1881</td>
    </tr>
    <tr>
      <td>geography_belgium</td>
      <td>0.6061</td><td>0.4361</td>
      <td>0.2951</td><td>0.0831</td>
      <td>0.2500</td><td>0.4736</td>
      <td>0.1292</td><td>0.1538</td>
    </tr>
    <tr>
      <td>humanity_future_150y</td>
      <td>0.5938</td><td>0.4608</td>
      <td>0.4883</td><td>0.4742</td>
      <td>0.0159</td><td>0.4769</td>
      <td>0.0305</td><td>0.4226</td>
    </tr>
    <tr>
      <td>indian_astrology</td>
      <td>0.1294</td><td>0.2221</td>
      <td>0.1778</td><td>0.2448</td>
      <td>0.0890</td><td>0.2954</td>
      <td>0.0922</td><td>0.4461</td>
    </tr>
    <tr>
      <td>indian_history</td>
      <td>0.2475</td><td>0.4625</td>
      <td>0.1345</td><td>0.5405</td>
      <td>0.1556</td><td>0.5827</td>
      <td>0.1042</td><td>0.4746</td>
    </tr>
    <tr>
      <td>indian_legal</td>
      <td>0.1955</td><td>0.3175</td>
      <td>0.1292</td><td>0.4139</td>
      <td>0.1349</td><td>0.4018</td>
      <td>0.1343</td><td>0.2621</td>
    </tr>
    <tr>
      <td>indian_legal_family</td>
      <td>0.3669</td><td>0.3946</td>
      <td>0.1326</td><td>0.3534</td>
      <td>0.0187</td><td>0.3727</td>
      <td>0.1079</td><td>0.0294</td>
    </tr>
    <tr>
      <td>jokes</td>
      <td>0.0606</td><td>0.4266</td>
      <td>0.1206</td><td>0.5342</td>
      <td>0.1222</td><td>0.6694</td>
      <td>0.1383</td><td>0.6667</td>
    </tr>
    <tr>
      <td>karnataka_elections</td>
      <td>0.3047</td><td>0.2054</td>
      <td>0.2262</td><td>0.3333</td>
      <td>0.1222</td><td>0.3877</td>
      <td>0.1190</td><td>0.4190</td>
    </tr>
    <tr>
      <td>linux_audio</td>
      <td>0.6374</td><td>0.4979</td>
      <td>0.7167</td><td>0.6527</td>
      <td>0.2073</td><td>0.2093</td>
      <td>0.2369</td><td>0.2280</td>
    </tr>
    <tr>
      <td>literature_camus</td>
      <td>0.0989</td><td>0.2334</td>
      <td>0.1101</td><td>0.3838</td>
      <td>0.1031</td><td>0.2319</td>
      <td>0.0317</td><td>0.0259</td>
    </tr>
    <tr>
      <td>llm_knowledge</td>
      <td>0.1228</td><td>0.1216</td>
      <td>0.1389</td><td>0.2165</td>
      <td>0.1338</td><td>0.3065</td>
      <td>0.0463</td><td>0.2121</td>
    </tr>
    <tr>
      <td>logic_puzzle</td>
      <td>0.1299</td><td>0.4075</td>
      <td>0.1769</td><td>0.2723</td>
      <td>0.1341</td><td>0.2826</td>
      <td>0.1100</td><td>0.4844</td>
    </tr>
    <tr>
      <td>lsat_medical_conference</td>
      <td>0.1816</td><td>0.5198</td>
      <td>0.2928</td><td>0.6005</td>
      <td>0.0659</td><td>0.6392</td>
      <td>0.0722</td><td>0.3690</td>
    </tr>
    <tr>
      <td>lsat_product_codes</td>
      <td>0.1199</td><td>0.1907</td>
      <td>0.1362</td><td>0.2356</td>
      <td>0.0169</td><td>0.2035</td>
      <td>0.0671</td><td>0.0104</td>
    </tr>
    <tr>
      <td>medical_dsd</td>
      <td>0.1813</td><td>0.1541</td>
      <td>0.2873</td><td>0.3283</td>
      <td>0.0114</td><td>0.3270</td>
      <td>0.1250</td><td>0.0194</td>
    </tr>
    <tr>
      <td>personas_roleplay</td>
      <td>0.1629</td><td>0.2525</td>
      <td>0.1406</td><td>0.2312</td>
      <td>0.1133</td><td>0.2762</td>
      <td>0.1038</td><td>0.3039</td>
    </tr>
    <tr>
      <td>physics_cosmology</td>
      <td>0.2960</td><td>0.3839</td>
      <td>0.1854</td><td>0.3320</td>
      <td>0.0206</td><td>0.3658</td>
      <td>0.0380</td><td>0.3421</td>
    </tr>
    <tr>
      <td>physics_violin_nanoscale</td>
      <td>0.5767</td><td>0.6466</td>
      <td>0.1987</td><td>0.1949</td>
      <td>0.4249</td><td>0.2249</td>
      <td>0.2119</td><td>0.2484</td>
    </tr>
    <tr>
      <td>scifi_films</td>
      <td>0.1104</td><td>0.1826</td>
      <td>0.1135</td><td>0.2689</td>
      <td>0.1200</td><td>0.2779</td>
      <td>0.0781</td><td>0.0345</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000</td>
      <td>0.1417</td><td>0.1905</td>
      <td>0.1360</td><td>0.3012</td>
      <td>0.1318</td><td>0.2339</td>
      <td>0.0333</td><td>0.2050</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000_games</td>
      <td>0.1196</td><td>0.1404</td>
      <td>0.1121</td><td>0.1506</td>
      <td>0.0929</td><td>0.1396</td>
      <td>0.0638</td><td>0.1355</td>
    </tr>
    <tr>
      <td>scifi_films_liu_cixin</td>
      <td>0.1994</td><td>0.3140</td>
      <td>0.2050</td><td>0.4087</td>
      <td>0.2184</td><td>0.5081</td>
      <td>0.0440</td><td>0.0871</td>
    </tr>
    <tr>
      <td>therapy</td>
      <td>0.1508</td><td>0.4341</td>
      <td>0.1364</td><td>0.5528</td>
      <td>0.1280</td><td>0.3222</td>
      <td>0.1017</td><td>0.5654</td>
    </tr>
    <tr>
      <td>therapy_manipulation</td>
      <td>0.2596</td><td>0.1635</td>
      <td>0.3704</td><td>0.3949</td>
      <td>0.0119</td><td>0.4457</td>
      <td>0.0212</td><td>0.4634</td>
    </tr>
    <tr>
      <td>wildfires_alberta</td>
      <td>0.1506</td><td>0.4087</td>
      <td>0.1525</td><td>0.3827</td>
      <td>0.1328</td><td>0.3013</td>
      <td>0.1659</td><td>0.2733</td>
    </tr>
  </tbody>
</table>

## Per-Topic BLEU-2

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ai_chat_tools</td>
      <td>0.0055</td><td>0.0352</td>
      <td>0.0102</td><td>0.0287</td>
      <td>0.0146</td><td>0.0153</td>
      <td>0.0184</td><td>0.0926</td>
    </tr>
    <tr>
      <td>ai_consciousness</td>
      <td>0.0256</td><td>0.0166</td>
      <td>0.0045</td><td>0.0333</td>
      <td>0.0241</td><td>0.0244</td>
      <td>0.0131</td><td>0.0875</td>
    </tr>
    <tr>
      <td>ai_consciousness_friendship</td>
      <td>0.1301</td><td>0.0978</td>
      <td>0.0638</td><td>0.1361</td>
      <td>0.1404</td><td>0.0494</td>
      <td>0.0917</td><td>0.3078</td>
    </tr>
    <tr>
      <td>ai_meta</td>
      <td>0.0372</td><td>0.0150</td>
      <td>0.0134</td><td>0.0057</td>
      <td>0.0187</td><td>0.0049</td>
      <td>0.0685</td><td>0.0125</td>
    </tr>
    <tr>
      <td>bhutan_travel</td>
      <td>0.0076</td><td>0.1192</td>
      <td>0.0283</td><td>0.0194</td>
      <td>0.0132</td><td>0.0234</td>
      <td>0.0000</td><td>0.0237</td>
    </tr>
    <tr>
      <td>chess</td>
      <td>0.0280</td><td>0.0101</td>
      <td>0.0004</td><td>0.0133</td>
      <td>0.0528</td><td>0.0148</td>
      <td>0.0008</td><td>0.0000</td>
    </tr>
    <tr>
      <td>child_nutrition</td>
      <td>0.0000</td><td>0.0088</td>
      <td>0.0000</td><td>0.0092</td>
      <td>0.0037</td><td>0.0000</td>
      <td>0.0000</td><td>0.0055</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving</td>
      <td>0.1018</td><td>0.0147</td>
      <td>0.1781</td><td>0.6779</td>
      <td>0.1476</td><td>0.2447</td>
      <td>0.0001</td><td>0.2447</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_argument</td>
      <td>0.2416</td><td>0.1021</td>
      <td>0.2869</td><td>0.1026</td>
      <td>0.3142</td><td>0.0434</td>
      <td>0.0037</td><td>0.0972</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_corrections</td>
      <td>0.1573</td><td>0.1257</td>
      <td>0.2562</td><td>0.2130</td>
      <td>0.2683</td><td>0.1991</td>
      <td>0.0035</td><td>0.1989</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_math_errors</td>
      <td>0.0893</td><td>0.1331</td>
      <td>0.2590</td><td>0.1573</td>
      <td>0.0000</td><td>0.2211</td>
      <td>0.0161</td><td>0.2211</td>
    </tr>
    <tr>
      <td>covid_safety</td>
      <td>0.0422</td><td>0.0241</td>
      <td>0.0353</td><td>0.1091</td>
      <td>0.0178</td><td>0.0283</td>
      <td>0.0018</td><td>0.0000</td>
    </tr>
    <tr>
      <td>covid_safety_hiv_aids</td>
      <td>0.0247</td><td>0.0199</td>
      <td>0.0379</td><td>0.0197</td>
      <td>0.0032</td><td>0.0222</td>
      <td>0.0007</td><td>0.0150</td>
    </tr>
    <tr>
      <td>dsp_wavelets</td>
      <td>0.0000</td><td>0.0003</td>
      <td>0.0000</td><td>0.0000</td>
      <td>0.0000</td><td>0.0000</td>
      <td>0.0000</td><td>0.0000</td>
    </tr>
    <tr>
      <td>electroculture</td>
      <td>0.0065</td><td>0.0001</td>
      <td>0.0182</td><td>0.0029</td>
      <td>0.0002</td><td>0.0138</td>
      <td>0.0000</td><td>0.2963</td>
    </tr>
    <tr>
      <td>emoji_game</td>
      <td>0.0153</td><td>0.0024</td>
      <td>0.0136</td><td>0.0112</td>
      <td>0.0175</td><td>0.0025</td>
      <td>0.0016</td><td>0.0413</td>
    </tr>
    <tr>
      <td>game_degree_guess</td>
      <td>0.0025</td><td>0.0403</td>
      <td>0.0688</td><td>0.5187</td>
      <td>0.0729</td><td>0.4783</td>
      <td>0.0013</td><td>0.0096</td>
    </tr>
    <tr>
      <td>game_twenty_questions</td>
      <td>0.0008</td><td>0.0000</td>
      <td>0.0201</td><td>0.0000</td>
      <td>0.0021</td><td>0.0003</td>
      <td>0.0000</td><td>0.0042</td>
    </tr>
    <tr>
      <td>geography_belgium</td>
      <td>0.4252</td><td>0.3883</td>
      <td>0.3481</td><td>0.0005</td>
      <td>0.2031</td><td>0.3440</td>
      <td>0.0046</td><td>0.1007</td>
    </tr>
    <tr>
      <td>humanity_future_150y</td>
      <td>0.2943</td><td>0.1373</td>
      <td>0.1447</td><td>0.1311</td>
      <td>0.0000</td><td>0.1458</td>
      <td>0.0000</td><td>0.0976</td>
    </tr>
    <tr>
      <td>indian_astrology</td>
      <td>0.0052</td><td>0.0488</td>
      <td>0.0325</td><td>0.0047</td>
      <td>0.0017</td><td>0.0230</td>
      <td>0.0031</td><td>0.3342</td>
    </tr>
    <tr>
      <td>indian_history</td>
      <td>0.1571</td><td>0.3048</td>
      <td>0.0199</td><td>0.5262</td>
      <td>0.0123</td><td>0.4971</td>
      <td>0.0173</td><td>0.6198</td>
    </tr>
    <tr>
      <td>indian_legal</td>
      <td>0.0681</td><td>0.0985</td>
      <td>0.0552</td><td>0.1386</td>
      <td>0.0453</td><td>0.1413</td>
      <td>0.0506</td><td>0.0437</td>
    </tr>
    <tr>
      <td>indian_legal_family</td>
      <td>0.0578</td><td>0.0886</td>
      <td>0.0298</td><td>0.0545</td>
      <td>0.0000</td><td>0.1683</td>
      <td>0.0069</td><td>0.0000</td>
    </tr>
    <tr>
      <td>jokes</td>
      <td>0.0005</td><td>0.3785</td>
      <td>0.0050</td><td>0.3503</td>
      <td>0.0308</td><td>0.5097</td>
      <td>0.0361</td><td>0.5080</td>
    </tr>
    <tr>
      <td>karnataka_elections</td>
      <td>0.1348</td><td>0.0372</td>
      <td>0.2206</td><td>0.1681</td>
      <td>0.0076</td><td>0.1458</td>
      <td>0.0061</td><td>0.3900</td>
    </tr>
    <tr>
      <td>linux_audio</td>
      <td>0.4441</td><td>0.1668</td>
      <td>0.4696</td><td>0.4476</td>
      <td>0.1207</td><td>0.1922</td>
      <td>0.1654</td><td>0.2537</td>
    </tr>
    <tr>
      <td>literature_camus</td>
      <td>0.0075</td><td>0.0205</td>
      <td>0.0130</td><td>0.0879</td>
      <td>0.0103</td><td>0.0127</td>
      <td>0.0000</td><td>0.0000</td>
    </tr>
    <tr>
      <td>llm_knowledge</td>
      <td>0.0237</td><td>0.0043</td>
      <td>0.0460</td><td>0.0132</td>
      <td>0.0388</td><td>0.0337</td>
      <td>0.0000</td><td>0.0341</td>
    </tr>
    <tr>
      <td>logic_puzzle</td>
      <td>0.0163</td><td>0.2133</td>
      <td>0.0471</td><td>0.0371</td>
      <td>0.0596</td><td>0.0719</td>
      <td>0.0040</td><td>0.3404</td>
    </tr>
    <tr>
      <td>lsat_medical_conference</td>
      <td>0.0730</td><td>0.2202</td>
      <td>0.1947</td><td>0.4022</td>
      <td>0.0001</td><td>0.3661</td>
      <td>0.0009</td><td>0.0542</td>
    </tr>
    <tr>
      <td>lsat_product_codes</td>
      <td>0.0029</td><td>0.0010</td>
      <td>0.0013</td><td>0.0066</td>
      <td>0.0000</td><td>0.0056</td>
      <td>0.0001</td><td>0.0000</td>
    </tr>
    <tr>
      <td>medical_dsd</td>
      <td>0.0696</td><td>0.1232</td>
      <td>0.0469</td><td>0.0643</td>
      <td>0.0000</td><td>0.0648</td>
      <td>0.0757</td><td>0.0000</td>
    </tr>
    <tr>
      <td>personas_roleplay</td>
      <td>0.0581</td><td>0.0466</td>
      <td>0.0471</td><td>0.0209</td>
      <td>0.0274</td><td>0.0929</td>
      <td>0.0160</td><td>0.1076</td>
    </tr>
    <tr>
      <td>physics_cosmology</td>
      <td>0.3036</td><td>0.1249</td>
      <td>0.1219</td><td>0.1819</td>
      <td>0.0000</td><td>0.2040</td>
      <td>0.0000</td><td>0.0571</td>
    </tr>
    <tr>
      <td>physics_violin_nanoscale</td>
      <td>0.6226</td><td>0.6431</td>
      <td>0.0999</td><td>0.1477</td>
      <td>0.2751</td><td>0.1499</td>
      <td>0.0914</td><td>0.1320</td>
    </tr>
    <tr>
      <td>scifi_films</td>
      <td>0.0142</td><td>0.0308</td>
      <td>0.0177</td><td>0.0374</td>
      <td>0.0183</td><td>0.0215</td>
      <td>0.0001</td><td>0.0000</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000</td>
      <td>0.1116</td><td>0.1118</td>
      <td>0.0844</td><td>0.1199</td>
      <td>0.0593</td><td>0.1071</td>
      <td>0.0000</td><td>0.1765</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000_games</td>
      <td>0.0155</td><td>0.0026</td>
      <td>0.0238</td><td>0.0123</td>
      <td>0.0067</td><td>0.0004</td>
      <td>0.0000</td><td>0.0058</td>
    </tr>
    <tr>
      <td>scifi_films_liu_cixin</td>
      <td>0.1551</td><td>0.2025</td>
      <td>0.1438</td><td>0.2035</td>
      <td>0.1278</td><td>0.2541</td>
      <td>0.0000</td><td>0.0000</td>
    </tr>
    <tr>
      <td>therapy</td>
      <td>0.0728</td><td>0.3720</td>
      <td>0.0605</td><td>0.3061</td>
      <td>0.0207</td><td>0.2017</td>
      <td>0.0052</td><td>0.5191</td>
    </tr>
    <tr>
      <td>therapy_manipulation</td>
      <td>0.0472</td><td>0.0375</td>
      <td>0.1180</td><td>0.0954</td>
      <td>0.0000</td><td>0.1376</td>
      <td>0.0000</td><td>0.2028</td>
    </tr>
    <tr>
      <td>wildfires_alberta</td>
      <td>0.0591</td><td>0.1593</td>
      <td>0.0564</td><td>0.1378</td>
      <td>0.0427</td><td>0.0407</td>
      <td>0.0783</td><td>0.0182</td>
    </tr>
  </tbody>
</table>


---

## Source Table: `backend/dataset/14b/merge/TABLE_3_SYSTEM_PERFORMANCE_MERGED.md`

# TABLE 3: MERGED SYSTEM PERFORMANCE METRICS (14B)

Merged from buffer-specific `TABLE_3_SYSTEM_PERFORMANCE.md` / `raw_metrics.json` files.

## Normal Conversation Performance

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Normal Conversation Turns</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
    </tr>
    <tr>
      <td>Avg Input Tokens</td>
      <td>1818</td><td>1919</td>
      <td>3152</td><td>3092</td>
      <td>4659</td><td>5396</td>
      <td>5685</td><td>5981</td>
    </tr>
    <tr>
      <td>Avg Output Tokens</td>
      <td>133</td><td>145</td>
      <td>170</td><td>182</td>
      <td>177</td><td>215</td>
      <td>148</td><td>160</td>
    </tr>
    <tr>
      <td>Avg Total Tokens</td>
      <td>1952</td><td>2064</td>
      <td>3321</td><td>3274</td>
      <td>4837</td><td>5611</td>
      <td>5833</td><td>6141</td>
    </tr>
    <tr>
      <td>Total Input Tokens</td>
      <td>561795</td><td>592924</td>
      <td>973916</td><td>955556</td>
      <td>1439776</td><td>1667280</td>
      <td>1756657</td><td>1848024</td>
    </tr>
    <tr>
      <td>Total Output Tokens</td>
      <td>41238</td><td>44890</td>
      <td>52376</td><td>56130</td>
      <td>54831</td><td>66582</td>
      <td>45676</td><td>49555</td>
    </tr>
    <tr>
      <td>Total Tokens</td>
      <td>603033</td><td>637814</td>
      <td>1026292</td><td>1011686</td>
      <td>1494607</td><td>1733862</td>
      <td>1802333</td><td>1897579</td>
    </tr>
    <tr>
      <td>Tokens Per Correct Answer</td>
      <td>3700</td><td>2773</td>
      <td>5548</td><td>4079</td>
      <td>8036</td><td>6853</td>
      <td>10418</td><td>8826</td>
    </tr>
    <tr>
      <td>Avg Latency</td>
      <td>16.71s</td><td>16.16s</td>
      <td>15.00s</td><td>13.58s</td>
      <td>16.06s</td><td>17.69s</td>
      <td>14.58s</td><td>14.64s</td>
    </tr>
    <tr>
      <td>Total Latency</td>
      <td>5161.96s</td><td>4993.71s</td>
      <td>4635.76s</td><td>4195.00s</td>
      <td>4962.52s</td><td>5466.95s</td>
      <td>4504.21s</td><td>4524.19s</td>
    </tr>
    <tr>
      <td>Cost per Query</td>
      <td>$0.000102</td><td>$0.000108</td>
      <td>$0.000171</td><td>$0.000169</td>
      <td>$0.000247</td><td>$0.000287</td>
      <td>$0.000296</td><td>$0.000312</td>
    </tr>
    <tr>
      <td>Cost per 1M Queries</td>
      <td>$102</td><td>$108</td>
      <td>$171</td><td>$169</td>
      <td>$247</td><td>$287</td>
      <td>$296</td><td>$312</td>
    </tr>
  </tbody>
</table>

## Including Recall/Summarization Probes

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Summarization Probe Calls</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
    </tr>
    <tr>
      <td>Summarization Probe Tokens</td>
      <td>136045</td><td>104023</td>
      <td>274209</td><td>156136</td>
      <td>322902</td><td>269171</td>
      <td>359355</td><td>304196</td>
    </tr>
    <tr>
      <td>Avg Tokens per Summarization Probe</td>
      <td>3164</td><td>2419</td>
      <td>6377</td><td>3631</td>
      <td>7509</td><td>6260</td>
      <td>8357</td><td>7074</td>
    </tr>
    <tr>
      <td>Combined Evaluated Calls</td>
      <td>352</td><td>352</td>
      <td>352</td><td>352</td>
      <td>352</td><td>352</td>
      <td>352</td><td>352</td>
    </tr>
    <tr>
      <td>Combined Total Tokens</td>
      <td>739078</td><td>741837</td>
      <td>1300501</td><td>1167822</td>
      <td>1817509</td><td>2003033</td>
      <td>2161688</td><td>2201775</td>
    </tr>
    <tr>
      <td>Combined Avg Tokens per Call</td>
      <td>2100</td><td>2107</td>
      <td>3695</td><td>3318</td>
      <td>5163</td><td>5690</td>
      <td>6141</td><td>6255</td>
    </tr>
  </tbody>
</table>


---

## Source Table: `backend/dataset/14b/merge/TABLE_4_RAG_DECISIONS_MERGED.md`

# TABLE 4: MERGED RAG DECISION BREAKDOWN (14B)

Merged from buffer-specific `TABLE_4_RAG_DECISIONS.md` / `raw_metrics.json` files.

## Normal Conversation Turns

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Total Turns</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
    </tr>
    <tr>
      <td>RAG-Eligible Turns</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>306</td><td>309</td>
      <td>284</td><td>291</td>
    </tr>
    <tr>
      <td>RAG Triggered</td>
      <td>36</td><td>29</td>
      <td>26</td><td>29</td>
      <td>27</td><td>30</td>
      <td>22</td><td>21</td>
    </tr>
    <tr>
      <td>Buffer Sufficient</td>
      <td>273</td><td>280</td>
      <td>283</td><td>280</td>
      <td>279</td><td>279</td>
      <td>262</td><td>270</td>
    </tr>
    <tr>
      <td>Retrieval Rate</td>
      <td>11.7%</td><td>9.4%</td>
      <td>8.4%</td><td>9.4%</td>
      <td>8.8%</td><td>9.7%</td>
      <td>7.7%</td><td>7.2%</td>
    </tr>
    <tr>
      <td>Buffer Rate</td>
      <td>88.3%</td><td>90.6%</td>
      <td>91.6%</td><td>90.6%</td>
      <td>91.2%</td><td>90.3%</td>
      <td>92.3%</td><td>92.8%</td>
    </tr>
    <tr>
      <td>Errors</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>3</td><td>0</td>
      <td>25</td><td>18</td>
    </tr>
    <tr>
      <td>RAG Disabled</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
    </tr>
    <tr>
      <td>No Vector Index</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
    </tr>
  </tbody>
</table>

## Recall/Summarization Probe RAG Decisions

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Probe Turns</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
    </tr>
    <tr>
      <td>RAG-Eligible Probe Turns</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>41</td>
    </tr>
    <tr>
      <td>Probe RAG Triggered</td>
      <td>25</td><td>10</td>
      <td>19</td><td>1</td>
      <td>16</td><td>2</td>
      <td>7</td><td>0</td>
    </tr>
    <tr>
      <td>Probe Buffer Sufficient</td>
      <td>18</td><td>33</td>
      <td>24</td><td>42</td>
      <td>27</td><td>41</td>
      <td>36</td><td>41</td>
    </tr>
    <tr>
      <td>Probe Retrieval Rate</td>
      <td>58.1%</td><td>23.3%</td>
      <td>44.2%</td><td>2.3%</td>
      <td>37.2%</td><td>4.7%</td>
      <td>16.3%</td><td>0.0%</td>
    </tr>
    <tr>
      <td>Probe Buffer Rate</td>
      <td>41.9%</td><td>76.7%</td>
      <td>55.8%</td><td>97.7%</td>
      <td>62.8%</td><td>95.3%</td>
      <td>83.7%</td><td>100.0%</td>
    </tr>
    <tr>
      <td>Probe Errors</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>2</td>
    </tr>
    <tr>
      <td>Probe RAG Disabled</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
    </tr>
  </tbody>
</table>


---

## Source Table: `backend/dataset/32b/merge/TABLE_1_CONTEXT_ISOLATION_MERGED.md`

# TABLE 1: MERGED CONTEXT ISOLATION METRICS (32B)

Merged from buffer-specific `TABLE_1_CONTEXT_ISOLATION.md` / `raw_metrics.json` files.

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Precision</td>
      <td>88.0%</td><td>88.5%</td>
      <td>87.3%</td><td>94.4%</td>
      <td>89.9%</td><td>93.4%</td>
      <td>84.9%</td><td>90.0%</td>
    </tr>
    <tr>
      <td>Recall</td>
      <td>64.6%</td><td>83.1%</td>
      <td>69.2%</td><td>80.2%</td>
      <td>67.2%</td><td>83.4%</td>
      <td>63.6%</td><td>74.4%</td>
    </tr>
    <tr>
      <td>F1</td>
      <td>68.6%</td><td>83.2%</td>
      <td>71.1%</td><td>83.7%</td>
      <td>69.6%</td><td>85.2%</td>
      <td>65.7%</td><td>78.2%</td>
    </tr>
    <tr>
      <td>Accuracy</td>
      <td>64.7%</td><td>83.2%</td>
      <td>69.3%</td><td>80.3%</td>
      <td>67.3%</td><td>83.5%</td>
      <td>63.8%</td><td>74.4%</td>
    </tr>
    <tr>
      <td>Pollution Rate</td>
      <td>35.3%</td><td>16.8%</td>
      <td>30.7%</td><td>19.7%</td>
      <td>32.7%</td><td>16.5%</td>
      <td>36.2%</td><td>25.6%</td>
    </tr>
    <tr>
      <td>Macro Precision</td>
      <td>83.6%</td><td>85.1%</td>
      <td>81.4%</td><td>91.8%</td>
      <td>86.7%</td><td>93.0%</td>
      <td>78.3%</td><td>88.2%</td>
    </tr>
    <tr>
      <td>Macro Recall</td>
      <td>73.9%</td><td>81.9%</td>
      <td>75.2%</td><td>79.8%</td>
      <td>75.8%</td><td>86.8%</td>
      <td>71.6%</td><td>74.0%</td>
    </tr>
    <tr>
      <td>Macro F1</td>
      <td>74.4%</td><td>80.8%</td>
      <td>73.9%</td><td>81.9%</td>
      <td>74.5%</td><td>87.1%</td>
      <td>68.4%</td><td>76.7%</td>
    </tr>
  </tbody>
</table>


---

## Source Table: `backend/dataset/32b/merge/TABLE_2_RECALL_SCORES_MERGED.md`

# TABLE 2: MERGED TOPIC RECALL SCORES (32B)

Merged from buffer-specific `TABLE_2_RECALL_SCORES.md` / `raw_metrics.json` files.

## Aggregate Scores and Probe Cost

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Avg ROUGE-1 (F1)</td>
      <td>0.2687</td><td>0.4328</td>
      <td>0.3674</td><td>0.4206</td>
      <td>0.3338</td><td>0.4283</td>
      <td>0.1503</td><td>0.3918</td>
    </tr>
    <tr>
      <td>Avg ROUGE-L (F1)</td>
      <td>0.1767</td><td>0.2830</td>
      <td>0.2274</td><td>0.2982</td>
      <td>0.2009</td><td>0.3016</td>
      <td>0.0878</td><td>0.2624</td>
    </tr>
    <tr>
      <td>Avg BLEU-2</td>
      <td>0.0502</td><td>0.1452</td>
      <td>0.1023</td><td>0.1253</td>
      <td>0.0731</td><td>0.1247</td>
      <td>0.0234</td><td>0.1206</td>
    </tr>
    <tr>
      <td>Topics Probed</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
    </tr>
    <tr>
      <td>Total Probe Tokens</td>
      <td>119832</td><td>131487</td>
      <td>249908</td><td>175875</td>
      <td>373285</td><td>264906</td>
      <td>324171</td><td>310617</td>
    </tr>
    <tr>
      <td>Avg Tokens per Probe</td>
      <td>2787</td><td>3058</td>
      <td>5812</td><td>4090</td>
      <td>8681</td><td>6161</td>
      <td>7539</td><td>7224</td>
    </tr>
    <tr>
      <td>Total Probe Latency</td>
      <td>1959.92s</td><td>2495.09s</td>
      <td>2965.46s</td><td>2722.82s</td>
      <td>3002.40s</td><td>2796.51s</td>
      <td>1888.54s</td><td>2288.25s</td>
    </tr>
    <tr>
      <td>Avg Probe Latency</td>
      <td>45.58s</td><td>58.03s</td>
      <td>68.96s</td><td>63.32s</td>
      <td>69.82s</td><td>65.04s</td>
      <td>43.92s</td><td>53.22s</td>
    </tr>
  </tbody>
</table>

## Per-Topic ROUGE-1 (F1)

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ai_chat_tools</td>
      <td>0.3593</td><td>0.2817</td>
      <td>0.3653</td><td>0.4000</td>
      <td>0.2252</td><td>0.3455</td>
      <td>0.1798</td><td>0.3985</td>
    </tr>
    <tr>
      <td>ai_consciousness</td>
      <td>0.2589</td><td>0.2945</td>
      <td>0.2690</td><td>0.3389</td>
      <td>0.2391</td><td>0.2936</td>
      <td>0.3008</td><td>0.3789</td>
    </tr>
    <tr>
      <td>ai_consciousness_friendship</td>
      <td>0.3647</td><td>0.4213</td>
      <td>0.4780</td><td>0.3983</td>
      <td>0.3721</td><td>0.4308</td>
      <td>0.4514</td><td>0.5257</td>
    </tr>
    <tr>
      <td>ai_meta</td>
      <td>0.3122</td><td>0.2893</td>
      <td>0.2543</td><td>0.3714</td>
      <td>0.3302</td><td>0.3252</td>
      <td>0.2917</td><td>0.3237</td>
    </tr>
    <tr>
      <td>bhutan_travel</td>
      <td>0.0681</td><td>0.4394</td>
      <td>0.3073</td><td>0.3465</td>
      <td>0.2359</td><td>0.3370</td>
      <td>0.2375</td><td>0.3178</td>
    </tr>
    <tr>
      <td>chess</td>
      <td>0.1337</td><td>0.2837</td>
      <td>0.2213</td><td>0.3636</td>
      <td>0.3053</td><td>0.3150</td>
      <td>0.2119</td><td>0.3994</td>
    </tr>
    <tr>
      <td>child_nutrition</td>
      <td>0.0638</td><td>0.4402</td>
      <td>0.2080</td><td>0.3421</td>
      <td>0.2978</td><td>0.2587</td>
      <td>0.0932</td><td>0.1436</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving</td>
      <td>0.2179</td><td>0.2867</td>
      <td>0.4158</td><td>0.4301</td>
      <td>0.3452</td><td>0.5273</td>
      <td>0.2761</td><td>0.4919</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_argument</td>
      <td>0.4920</td><td>0.5110</td>
      <td>0.5490</td><td>0.5207</td>
      <td>0.5615</td><td>0.5908</td>
      <td>0.0746</td><td>0.5483</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_corrections</td>
      <td>0.3374</td><td>0.4641</td>
      <td>0.4379</td><td>0.5014</td>
      <td>0.4885</td><td>0.5215</td>
      <td>0.4712</td><td>0.6383</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_math_errors</td>
      <td>0.2980</td><td>0.3601</td>
      <td>0.4378</td><td>0.4779</td>
      <td>0.3725</td><td>0.6658</td>
      <td>0.0625</td><td>0.6711</td>
    </tr>
    <tr>
      <td>covid_safety</td>
      <td>0.0666</td><td>0.3727</td>
      <td>0.2711</td><td>0.3954</td>
      <td>0.4353</td><td>0.3837</td>
      <td>0.0105</td><td>0.0278</td>
    </tr>
    <tr>
      <td>covid_safety_hiv_aids</td>
      <td>0.2625</td><td>0.2839</td>
      <td>0.3945</td><td>0.2798</td>
      <td>0.2540</td><td>0.3451</td>
      <td>0.0425</td><td>0.1702</td>
    </tr>
    <tr>
      <td>dsp_wavelets</td>
      <td>0.0219</td><td>0.1659</td>
      <td>0.1858</td><td>0.1408</td>
      <td>0.0889</td><td>0.1393</td>
      <td>0.1619</td><td>0.1412</td>
    </tr>
    <tr>
      <td>electroculture</td>
      <td>0.3497</td><td>0.3807</td>
      <td>0.3422</td><td>0.3136</td>
      <td>0.2393</td><td>0.2780</td>
      <td>0.0274</td><td>0.4615</td>
    </tr>
    <tr>
      <td>emoji_game</td>
      <td>0.0530</td><td>0.2049</td>
      <td>0.0714</td><td>0.1611</td>
      <td>0.2295</td><td>0.2025</td>
      <td>0.1935</td><td>0.3711</td>
    </tr>
    <tr>
      <td>game_degree_guess</td>
      <td>0.2363</td><td>0.5035</td>
      <td>0.4760</td><td>0.5303</td>
      <td>0.2430</td><td>0.5520</td>
      <td>0.2832</td><td>0.4530</td>
    </tr>
    <tr>
      <td>game_twenty_questions</td>
      <td>0.0622</td><td>0.3232</td>
      <td>0.2625</td><td>0.2580</td>
      <td>0.1781</td><td>0.2983</td>
      <td>0.0848</td><td>0.2668</td>
    </tr>
    <tr>
      <td>geography_belgium</td>
      <td>0.2431</td><td>0.7078</td>
      <td>0.7831</td><td>0.7617</td>
      <td>0.7337</td><td>0.6773</td>
      <td>0.0315</td><td>0.4696</td>
    </tr>
    <tr>
      <td>humanity_future_150y</td>
      <td>0.0726</td><td>0.4762</td>
      <td>0.4314</td><td>0.5175</td>
      <td>0.4013</td><td>0.5255</td>
      <td>0.1046</td><td>0.5148</td>
    </tr>
    <tr>
      <td>indian_astrology</td>
      <td>0.2117</td><td>0.3719</td>
      <td>0.2398</td><td>0.4101</td>
      <td>0.3303</td><td>0.2766</td>
      <td>0.0158</td><td>0.3860</td>
    </tr>
    <tr>
      <td>indian_history</td>
      <td>0.4359</td><td>0.5957</td>
      <td>0.4598</td><td>0.6909</td>
      <td>0.4674</td><td>0.7200</td>
      <td>0.0348</td><td>0.6828</td>
    </tr>
    <tr>
      <td>indian_legal</td>
      <td>0.2776</td><td>0.5057</td>
      <td>0.3402</td><td>0.5200</td>
      <td>0.2718</td><td>0.4604</td>
      <td>0.3042</td><td>0.4163</td>
    </tr>
    <tr>
      <td>indian_legal_family</td>
      <td>0.3731</td><td>0.4562</td>
      <td>0.3778</td><td>0.3916</td>
      <td>0.4031</td><td>0.3633</td>
      <td>0.0952</td><td>0.0862</td>
    </tr>
    <tr>
      <td>jokes</td>
      <td>0.1695</td><td>0.5631</td>
      <td>0.3401</td><td>0.5741</td>
      <td>0.2282</td><td>0.6022</td>
      <td>0.2323</td><td>0.6625</td>
    </tr>
    <tr>
      <td>karnataka_elections</td>
      <td>0.5378</td><td>0.4565</td>
      <td>0.6090</td><td>0.5541</td>
      <td>0.6195</td><td>0.5926</td>
      <td>0.0519</td><td>0.5620</td>
    </tr>
    <tr>
      <td>linux_audio</td>
      <td>0.3931</td><td>0.6580</td>
      <td>0.2950</td><td>0.7880</td>
      <td>0.4305</td><td>0.6247</td>
      <td>0.4551</td><td>0.5430</td>
    </tr>
    <tr>
      <td>literature_camus</td>
      <td>0.4306</td><td>0.4123</td>
      <td>0.2305</td><td>0.3801</td>
      <td>0.2489</td><td>0.3654</td>
      <td>0.2259</td><td>0.1739</td>
    </tr>
    <tr>
      <td>llm_knowledge</td>
      <td>0.3466</td><td>0.2486</td>
      <td>0.3029</td><td>0.2781</td>
      <td>0.3465</td><td>0.3035</td>
      <td>0.0167</td><td>0.2689</td>
    </tr>
    <tr>
      <td>logic_puzzle</td>
      <td>0.1705</td><td>0.6264</td>
      <td>0.3270</td><td>0.4738</td>
      <td>0.3732</td><td>0.5411</td>
      <td>0.2595</td><td>0.5215</td>
    </tr>
    <tr>
      <td>lsat_medical_conference</td>
      <td>0.3634</td><td>0.5178</td>
      <td>0.4884</td><td>0.5458</td>
      <td>0.5304</td><td>0.5755</td>
      <td>0.0389</td><td>0.5687</td>
    </tr>
    <tr>
      <td>lsat_product_codes</td>
      <td>0.1460</td><td>0.1701</td>
      <td>0.3030</td><td>0.2417</td>
      <td>0.1482</td><td>0.2594</td>
      <td>0.0091</td><td>0.0149</td>
    </tr>
    <tr>
      <td>medical_dsd</td>
      <td>0.5132</td><td>0.6422</td>
      <td>0.3523</td><td>0.4580</td>
      <td>0.3178</td><td>0.4941</td>
      <td>0.1636</td><td>0.4150</td>
    </tr>
    <tr>
      <td>personas_roleplay</td>
      <td>0.1545</td><td>0.3648</td>
      <td>0.3643</td><td>0.3044</td>
      <td>0.2461</td><td>0.3614</td>
      <td>0.0453</td><td>0.3707</td>
    </tr>
    <tr>
      <td>physics_cosmology</td>
      <td>0.1074</td><td>0.7212</td>
      <td>0.6006</td><td>0.5472</td>
      <td>0.3183</td><td>0.5584</td>
      <td>0.3599</td><td>0.2720</td>
    </tr>
    <tr>
      <td>physics_violin_nanoscale</td>
      <td>0.1750</td><td>0.6464</td>
      <td>0.6553</td><td>0.2805</td>
      <td>0.3333</td><td>0.4191</td>
      <td>0.0645</td><td>0.3710</td>
    </tr>
    <tr>
      <td>scifi_films</td>
      <td>0.1024</td><td>0.3740</td>
      <td>0.3040</td><td>0.3259</td>
      <td>0.2366</td><td>0.2978</td>
      <td>0.0216</td><td>0.3197</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000</td>
      <td>0.2781</td><td>0.4240</td>
      <td>0.3800</td><td>0.3768</td>
      <td>0.3339</td><td>0.4161</td>
      <td>0.2787</td><td>0.5191</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000_games</td>
      <td>0.2012</td><td>0.2663</td>
      <td>0.2249</td><td>0.2076</td>
      <td>0.2246</td><td>0.3794</td>
      <td>0.0868</td><td>0.3407</td>
    </tr>
    <tr>
      <td>scifi_films_liu_cixin</td>
      <td>0.4142</td><td>0.5891</td>
      <td>0.4684</td><td>0.6078</td>
      <td>0.3903</td><td>0.5851</td>
      <td>0.0361</td><td>0.5776</td>
    </tr>
    <tr>
      <td>therapy</td>
      <td>0.4405</td><td>0.4694</td>
      <td>0.2214</td><td>0.5247</td>
      <td>0.1860</td><td>0.4114</td>
      <td>0.0187</td><td>0.1756</td>
    </tr>
    <tr>
      <td>therapy_manipulation</td>
      <td>0.3303</td><td>0.5221</td>
      <td>0.2782</td><td>0.3647</td>
      <td>0.2313</td><td>0.3978</td>
      <td>0.0424</td><td>0.5239</td>
    </tr>
    <tr>
      <td>wildfires_alberta</td>
      <td>0.7071</td><td>0.5173</td>
      <td>0.4730</td><td>0.3929</td>
      <td>0.5624</td><td>0.3991</td>
      <td>0.0171</td><td>0.3627</td>
    </tr>
  </tbody>
</table>

## Per-Topic ROUGE-L (F1)

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ai_chat_tools</td>
      <td>0.1629</td><td>0.1596</td>
      <td>0.2037</td><td>0.2397</td>
      <td>0.1026</td><td>0.2435</td>
      <td>0.0986</td><td>0.2798</td>
    </tr>
    <tr>
      <td>ai_consciousness</td>
      <td>0.1431</td><td>0.1848</td>
      <td>0.1368</td><td>0.1885</td>
      <td>0.1195</td><td>0.1808</td>
      <td>0.2061</td><td>0.2197</td>
    </tr>
    <tr>
      <td>ai_consciousness_friendship</td>
      <td>0.1563</td><td>0.2272</td>
      <td>0.2537</td><td>0.2318</td>
      <td>0.1697</td><td>0.2893</td>
      <td>0.2069</td><td>0.3204</td>
    </tr>
    <tr>
      <td>ai_meta</td>
      <td>0.1306</td><td>0.1736</td>
      <td>0.1518</td><td>0.2337</td>
      <td>0.1336</td><td>0.2127</td>
      <td>0.1329</td><td>0.1871</td>
    </tr>
    <tr>
      <td>bhutan_travel</td>
      <td>0.0481</td><td>0.3653</td>
      <td>0.2703</td><td>0.3242</td>
      <td>0.1454</td><td>0.2806</td>
      <td>0.1625</td><td>0.2877</td>
    </tr>
    <tr>
      <td>chess</td>
      <td>0.0840</td><td>0.1576</td>
      <td>0.1277</td><td>0.1935</td>
      <td>0.1371</td><td>0.1752</td>
      <td>0.0984</td><td>0.1895</td>
    </tr>
    <tr>
      <td>child_nutrition</td>
      <td>0.0435</td><td>0.2912</td>
      <td>0.1350</td><td>0.2606</td>
      <td>0.2286</td><td>0.2040</td>
      <td>0.0529</td><td>0.0764</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving</td>
      <td>0.1401</td><td>0.1470</td>
      <td>0.2013</td><td>0.2826</td>
      <td>0.1548</td><td>0.3682</td>
      <td>0.1448</td><td>0.3573</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_argument</td>
      <td>0.2812</td><td>0.2912</td>
      <td>0.2876</td><td>0.2781</td>
      <td>0.3102</td><td>0.3415</td>
      <td>0.0672</td><td>0.3133</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_corrections</td>
      <td>0.1963</td><td>0.2762</td>
      <td>0.2438</td><td>0.3215</td>
      <td>0.3155</td><td>0.3110</td>
      <td>0.2670</td><td>0.4113</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_math_errors</td>
      <td>0.1806</td><td>0.1918</td>
      <td>0.2242</td><td>0.2726</td>
      <td>0.2118</td><td>0.4465</td>
      <td>0.0573</td><td>0.4430</td>
    </tr>
    <tr>
      <td>covid_safety</td>
      <td>0.0378</td><td>0.1660</td>
      <td>0.1295</td><td>0.2747</td>
      <td>0.2902</td><td>0.2531</td>
      <td>0.0105</td><td>0.0232</td>
    </tr>
    <tr>
      <td>covid_safety_hiv_aids</td>
      <td>0.2179</td><td>0.1986</td>
      <td>0.3423</td><td>0.1840</td>
      <td>0.2021</td><td>0.2619</td>
      <td>0.0243</td><td>0.0947</td>
    </tr>
    <tr>
      <td>dsp_wavelets</td>
      <td>0.0170</td><td>0.1068</td>
      <td>0.1577</td><td>0.1021</td>
      <td>0.0650</td><td>0.0898</td>
      <td>0.0813</td><td>0.1045</td>
    </tr>
    <tr>
      <td>electroculture</td>
      <td>0.3174</td><td>0.3150</td>
      <td>0.3105</td><td>0.2616</td>
      <td>0.1439</td><td>0.2691</td>
      <td>0.0229</td><td>0.2418</td>
    </tr>
    <tr>
      <td>emoji_game</td>
      <td>0.0419</td><td>0.1449</td>
      <td>0.0602</td><td>0.1316</td>
      <td>0.1538</td><td>0.1805</td>
      <td>0.1505</td><td>0.3286</td>
    </tr>
    <tr>
      <td>game_degree_guess</td>
      <td>0.1519</td><td>0.2517</td>
      <td>0.2579</td><td>0.3509</td>
      <td>0.1229</td><td>0.2724</td>
      <td>0.1358</td><td>0.3328</td>
    </tr>
    <tr>
      <td>game_twenty_questions</td>
      <td>0.0470</td><td>0.2216</td>
      <td>0.1702</td><td>0.2095</td>
      <td>0.1205</td><td>0.2496</td>
      <td>0.0633</td><td>0.1783</td>
    </tr>
    <tr>
      <td>geography_belgium</td>
      <td>0.1389</td><td>0.5994</td>
      <td>0.7367</td><td>0.7224</td>
      <td>0.6586</td><td>0.5550</td>
      <td>0.0210</td><td>0.3000</td>
    </tr>
    <tr>
      <td>humanity_future_150y</td>
      <td>0.0495</td><td>0.3692</td>
      <td>0.3327</td><td>0.5030</td>
      <td>0.1692</td><td>0.4986</td>
      <td>0.0624</td><td>0.4598</td>
    </tr>
    <tr>
      <td>indian_astrology</td>
      <td>0.1696</td><td>0.2049</td>
      <td>0.1358</td><td>0.2275</td>
      <td>0.1619</td><td>0.2618</td>
      <td>0.0095</td><td>0.3465</td>
    </tr>
    <tr>
      <td>indian_history</td>
      <td>0.3333</td><td>0.4574</td>
      <td>0.3218</td><td>0.5164</td>
      <td>0.3370</td><td>0.5000</td>
      <td>0.0348</td><td>0.3724</td>
    </tr>
    <tr>
      <td>indian_legal</td>
      <td>0.2310</td><td>0.4211</td>
      <td>0.2019</td><td>0.4145</td>
      <td>0.1332</td><td>0.3915</td>
      <td>0.1458</td><td>0.2881</td>
    </tr>
    <tr>
      <td>indian_legal_family</td>
      <td>0.2533</td><td>0.4253</td>
      <td>0.3082</td><td>0.2819</td>
      <td>0.3260</td><td>0.2110</td>
      <td>0.0714</td><td>0.0682</td>
    </tr>
    <tr>
      <td>jokes</td>
      <td>0.1186</td><td>0.4725</td>
      <td>0.1814</td><td>0.5237</td>
      <td>0.1456</td><td>0.4696</td>
      <td>0.1333</td><td>0.4984</td>
    </tr>
    <tr>
      <td>karnataka_elections</td>
      <td>0.3761</td><td>0.3130</td>
      <td>0.3851</td><td>0.4326</td>
      <td>0.4040</td><td>0.3951</td>
      <td>0.0461</td><td>0.4147</td>
    </tr>
    <tr>
      <td>linux_audio</td>
      <td>0.1792</td><td>0.5152</td>
      <td>0.1475</td><td>0.5671</td>
      <td>0.2007</td><td>0.3317</td>
      <td>0.1993</td><td>0.2921</td>
    </tr>
    <tr>
      <td>literature_camus</td>
      <td>0.3375</td><td>0.1921</td>
      <td>0.1099</td><td>0.2255</td>
      <td>0.1121</td><td>0.2248</td>
      <td>0.1146</td><td>0.1234</td>
    </tr>
    <tr>
      <td>llm_knowledge</td>
      <td>0.2470</td><td>0.2336</td>
      <td>0.1464</td><td>0.2258</td>
      <td>0.2333</td><td>0.2312</td>
      <td>0.0167</td><td>0.1974</td>
    </tr>
    <tr>
      <td>logic_puzzle</td>
      <td>0.1172</td><td>0.4451</td>
      <td>0.1761</td><td>0.2939</td>
      <td>0.1964</td><td>0.3539</td>
      <td>0.1628</td><td>0.2893</td>
    </tr>
    <tr>
      <td>lsat_medical_conference</td>
      <td>0.2782</td><td>0.4139</td>
      <td>0.3159</td><td>0.4230</td>
      <td>0.3749</td><td>0.4929</td>
      <td>0.0278</td><td>0.5375</td>
    </tr>
    <tr>
      <td>lsat_product_codes</td>
      <td>0.0902</td><td>0.1438</td>
      <td>0.2100</td><td>0.1869</td>
      <td>0.1159</td><td>0.2340</td>
      <td>0.0079</td><td>0.0081</td>
    </tr>
    <tr>
      <td>medical_dsd</td>
      <td>0.3383</td><td>0.3028</td>
      <td>0.1869</td><td>0.2563</td>
      <td>0.1944</td><td>0.3222</td>
      <td>0.1273</td><td>0.2916</td>
    </tr>
    <tr>
      <td>personas_roleplay</td>
      <td>0.0935</td><td>0.2240</td>
      <td>0.1783</td><td>0.1948</td>
      <td>0.1157</td><td>0.2290</td>
      <td>0.0302</td><td>0.2356</td>
    </tr>
    <tr>
      <td>physics_cosmology</td>
      <td>0.0785</td><td>0.3806</td>
      <td>0.3571</td><td>0.4306</td>
      <td>0.2200</td><td>0.3206</td>
      <td>0.2271</td><td>0.2184</td>
    </tr>
    <tr>
      <td>physics_violin_nanoscale</td>
      <td>0.1125</td><td>0.3802</td>
      <td>0.3925</td><td>0.1789</td>
      <td>0.2143</td><td>0.2058</td>
      <td>0.0323</td><td>0.2039</td>
    </tr>
    <tr>
      <td>scifi_films</td>
      <td>0.0599</td><td>0.2044</td>
      <td>0.1761</td><td>0.1673</td>
      <td>0.1205</td><td>0.2285</td>
      <td>0.0108</td><td>0.2211</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000</td>
      <td>0.1716</td><td>0.2026</td>
      <td>0.1700</td><td>0.1988</td>
      <td>0.1948</td><td>0.2484</td>
      <td>0.1434</td><td>0.2977</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000_games</td>
      <td>0.1096</td><td>0.1341</td>
      <td>0.1065</td><td>0.1213</td>
      <td>0.1184</td><td>0.2638</td>
      <td>0.0615</td><td>0.2044</td>
    </tr>
    <tr>
      <td>scifi_films_liu_cixin</td>
      <td>0.2973</td><td>0.3492</td>
      <td>0.2928</td><td>0.5120</td>
      <td>0.1963</td><td>0.4946</td>
      <td>0.0301</td><td>0.3448</td>
    </tr>
    <tr>
      <td>therapy</td>
      <td>0.3688</td><td>0.2985</td>
      <td>0.1195</td><td>0.3692</td>
      <td>0.1023</td><td>0.2547</td>
      <td>0.0187</td><td>0.1311</td>
    </tr>
    <tr>
      <td>therapy_manipulation</td>
      <td>0.1920</td><td>0.3417</td>
      <td>0.1429</td><td>0.2199</td>
      <td>0.1215</td><td>0.3115</td>
      <td>0.0424</td><td>0.2374</td>
    </tr>
    <tr>
      <td>wildfires_alberta</td>
      <td>0.4591</td><td>0.2747</td>
      <td>0.2809</td><td>0.2881</td>
      <td>0.3455</td><td>0.3097</td>
      <td>0.0146</td><td>0.3116</td>
    </tr>
  </tbody>
</table>

## Per-Topic BLEU-2

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ai_chat_tools</td>
      <td>0.0435</td><td>0.0100</td>
      <td>0.0397</td><td>0.0510</td>
      <td>0.0072</td><td>0.0158</td>
      <td>0.0010</td><td>0.0507</td>
    </tr>
    <tr>
      <td>ai_consciousness</td>
      <td>0.0076</td><td>0.0153</td>
      <td>0.0128</td><td>0.0232</td>
      <td>0.0048</td><td>0.0109</td>
      <td>0.0140</td><td>0.0447</td>
    </tr>
    <tr>
      <td>ai_consciousness_friendship</td>
      <td>0.0723</td><td>0.0778</td>
      <td>0.1927</td><td>0.0575</td>
      <td>0.0414</td><td>0.0744</td>
      <td>0.1491</td><td>0.1902</td>
    </tr>
    <tr>
      <td>ai_meta</td>
      <td>0.0359</td><td>0.0140</td>
      <td>0.0067</td><td>0.0461</td>
      <td>0.0367</td><td>0.0202</td>
      <td>0.0171</td><td>0.0212</td>
    </tr>
    <tr>
      <td>bhutan_travel</td>
      <td>0.0000</td><td>0.0490</td>
      <td>0.0091</td><td>0.0160</td>
      <td>0.0051</td><td>0.0268</td>
      <td>0.0194</td><td>0.0137</td>
    </tr>
    <tr>
      <td>chess</td>
      <td>0.0003</td><td>0.0124</td>
      <td>0.0080</td><td>0.0537</td>
      <td>0.0524</td><td>0.0120</td>
      <td>0.0072</td><td>0.0664</td>
    </tr>
    <tr>
      <td>child_nutrition</td>
      <td>0.0000</td><td>0.1020</td>
      <td>0.0014</td><td>0.0235</td>
      <td>0.0095</td><td>0.0029</td>
      <td>0.0000</td><td>0.0001</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving</td>
      <td>0.0086</td><td>0.0246</td>
      <td>0.1124</td><td>0.1197</td>
      <td>0.0427</td><td>0.2121</td>
      <td>0.0225</td><td>0.1917</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_argument</td>
      <td>0.1584</td><td>0.1943</td>
      <td>0.2612</td><td>0.1855</td>
      <td>0.2123</td><td>0.2724</td>
      <td>0.0000</td><td>0.2352</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_corrections</td>
      <td>0.0532</td><td>0.1553</td>
      <td>0.1810</td><td>0.2390</td>
      <td>0.1654</td><td>0.2065</td>
      <td>0.2178</td><td>0.3684</td>
    </tr>
    <tr>
      <td>cookies_recipe_halving_math_errors</td>
      <td>0.0368</td><td>0.0641</td>
      <td>0.1382</td><td>0.1478</td>
      <td>0.0492</td><td>0.3809</td>
      <td>0.0000</td><td>0.3860</td>
    </tr>
    <tr>
      <td>covid_safety</td>
      <td>0.0000</td><td>0.0334</td>
      <td>0.0061</td><td>0.0462</td>
      <td>0.0853</td><td>0.0390</td>
      <td>0.0000</td><td>0.0000</td>
    </tr>
    <tr>
      <td>covid_safety_hiv_aids</td>
      <td>0.0045</td><td>0.0292</td>
      <td>0.0562</td><td>0.0253</td>
      <td>0.0081</td><td>0.0390</td>
      <td>0.0000</td><td>0.0039</td>
    </tr>
    <tr>
      <td>dsp_wavelets</td>
      <td>0.0000</td><td>0.0001</td>
      <td>0.0001</td><td>0.0000</td>
      <td>0.0000</td><td>0.0000</td>
      <td>0.0002</td><td>0.0000</td>
    </tr>
    <tr>
      <td>electroculture</td>
      <td>0.0230</td><td>0.0398</td>
      <td>0.0221</td><td>0.0135</td>
      <td>0.0013</td><td>0.0065</td>
      <td>0.0000</td><td>0.0969</td>
    </tr>
    <tr>
      <td>emoji_game</td>
      <td>0.0000</td><td>0.0047</td>
      <td>0.0001</td><td>0.0004</td>
      <td>0.0109</td><td>0.0008</td>
      <td>0.0210</td><td>0.0531</td>
    </tr>
    <tr>
      <td>game_degree_guess</td>
      <td>0.0021</td><td>0.2231</td>
      <td>0.2233</td><td>0.2389</td>
      <td>0.0162</td><td>0.2464</td>
      <td>0.0235</td><td>0.1251</td>
    </tr>
    <tr>
      <td>game_twenty_questions</td>
      <td>0.0000</td><td>0.0378</td>
      <td>0.0190</td><td>0.0117</td>
      <td>0.0037</td><td>0.0253</td>
      <td>0.0000</td><td>0.0155</td>
    </tr>
    <tr>
      <td>geography_belgium</td>
      <td>0.0092</td><td>0.5862</td>
      <td>0.6837</td><td>0.5830</td>
      <td>0.5051</td><td>0.3415</td>
      <td>0.0000</td><td>0.2922</td>
    </tr>
    <tr>
      <td>humanity_future_150y</td>
      <td>0.0000</td><td>0.1126</td>
      <td>0.0686</td><td>0.1525</td>
      <td>0.0525</td><td>0.1549</td>
      <td>0.0000</td><td>0.1271</td>
    </tr>
    <tr>
      <td>indian_astrology</td>
      <td>0.0014</td><td>0.0445</td>
      <td>0.0024</td><td>0.0537</td>
      <td>0.0339</td><td>0.0073</td>
      <td>0.0000</td><td>0.0615</td>
    </tr>
    <tr>
      <td>indian_history</td>
      <td>0.2017</td><td>0.3420</td>
      <td>0.2062</td><td>0.4688</td>
      <td>0.2199</td><td>0.4842</td>
      <td>0.0000</td><td>0.4438</td>
    </tr>
    <tr>
      <td>indian_legal</td>
      <td>0.0164</td><td>0.1489</td>
      <td>0.0720</td><td>0.1419</td>
      <td>0.0268</td><td>0.0997</td>
      <td>0.0632</td><td>0.0603</td>
    </tr>
    <tr>
      <td>indian_legal_family</td>
      <td>0.0383</td><td>0.1027</td>
      <td>0.0411</td><td>0.0444</td>
      <td>0.0560</td><td>0.0367</td>
      <td>0.0010</td><td>0.0000</td>
    </tr>
    <tr>
      <td>jokes</td>
      <td>0.0036</td><td>0.3549</td>
      <td>0.1232</td><td>0.4182</td>
      <td>0.0608</td><td>0.3134</td>
      <td>0.0369</td><td>0.3528</td>
    </tr>
    <tr>
      <td>karnataka_elections</td>
      <td>0.2233</td><td>0.1528</td>
      <td>0.3479</td><td>0.2507</td>
      <td>0.3306</td><td>0.2920</td>
      <td>0.0000</td><td>0.2861</td>
    </tr>
    <tr>
      <td>linux_audio</td>
      <td>0.0654</td><td>0.4264</td>
      <td>0.0308</td><td>0.5697</td>
      <td>0.1055</td><td>0.2957</td>
      <td>0.1563</td><td>0.2753</td>
    </tr>
    <tr>
      <td>literature_camus</td>
      <td>0.0827</td><td>0.0621</td>
      <td>0.0056</td><td>0.0497</td>
      <td>0.0112</td><td>0.0404</td>
      <td>0.0110</td><td>0.0002</td>
    </tr>
    <tr>
      <td>llm_knowledge</td>
      <td>0.0315</td><td>0.0035</td>
      <td>0.0227</td><td>0.0069</td>
      <td>0.0312</td><td>0.0103</td>
      <td>0.0000</td><td>0.0052</td>
    </tr>
    <tr>
      <td>logic_puzzle</td>
      <td>0.0113</td><td>0.2971</td>
      <td>0.0820</td><td>0.1127</td>
      <td>0.1006</td><td>0.2282</td>
      <td>0.0554</td><td>0.1900</td>
    </tr>
    <tr>
      <td>lsat_medical_conference</td>
      <td>0.0791</td><td>0.1617</td>
      <td>0.2212</td><td>0.1903</td>
      <td>0.1897</td><td>0.2320</td>
      <td>0.0000</td><td>0.2213</td>
    </tr>
    <tr>
      <td>lsat_product_codes</td>
      <td>0.0008</td><td>0.0003</td>
      <td>0.0158</td><td>0.0026</td>
      <td>0.0000</td><td>0.0061</td>
      <td>0.0000</td><td>0.0000</td>
    </tr>
    <tr>
      <td>medical_dsd</td>
      <td>0.1895</td><td>0.3432</td>
      <td>0.0281</td><td>0.0931</td>
      <td>0.0141</td><td>0.1551</td>
      <td>0.0066</td><td>0.0716</td>
    </tr>
    <tr>
      <td>personas_roleplay</td>
      <td>0.0017</td><td>0.0723</td>
      <td>0.0940</td><td>0.0297</td>
      <td>0.0117</td><td>0.0661</td>
      <td>0.0000</td><td>0.0639</td>
    </tr>
    <tr>
      <td>physics_cosmology</td>
      <td>0.0016</td><td>0.5549</td>
      <td>0.3539</td><td>0.2033</td>
      <td>0.0968</td><td>0.2486</td>
      <td>0.1576</td><td>0.0117</td>
    </tr>
    <tr>
      <td>physics_violin_nanoscale</td>
      <td>0.0024</td><td>0.4295</td>
      <td>0.3353</td><td>0.0398</td>
      <td>0.1217</td><td>0.1732</td>
      <td>0.0000</td><td>0.1243</td>
    </tr>
    <tr>
      <td>scifi_films</td>
      <td>0.0000</td><td>0.0470</td>
      <td>0.0258</td><td>0.0211</td>
      <td>0.0129</td><td>0.0110</td>
      <td>0.0000</td><td>0.0162</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000</td>
      <td>0.0298</td><td>0.1229</td>
      <td>0.0670</td><td>0.1095</td>
      <td>0.0852</td><td>0.1141</td>
      <td>0.0251</td><td>0.2024</td>
    </tr>
    <tr>
      <td>scifi_films_hal9000_games</td>
      <td>0.0025</td><td>0.0124</td>
      <td>0.0042</td><td>0.0027</td>
      <td>0.0070</td><td>0.0341</td>
      <td>0.0000</td><td>0.0264</td>
    </tr>
    <tr>
      <td>scifi_films_liu_cixin</td>
      <td>0.0652</td><td>0.3296</td>
      <td>0.1404</td><td>0.2925</td>
      <td>0.0797</td><td>0.2703</td>
      <td>0.0000</td><td>0.3287</td>
    </tr>
    <tr>
      <td>therapy</td>
      <td>0.1285</td><td>0.1151</td>
      <td>0.0090</td><td>0.1663</td>
      <td>0.0078</td><td>0.0683</td>
      <td>0.0000</td><td>0.0004</td>
    </tr>
    <tr>
      <td>therapy_manipulation</td>
      <td>0.0197</td><td>0.1637</td>
      <td>0.0062</td><td>0.0406</td>
      <td>0.0076</td><td>0.0456</td>
      <td>0.0000</td><td>0.1329</td>
    </tr>
    <tr>
      <td>wildfires_alberta</td>
      <td>0.5053</td><td>0.1687</td>
      <td>0.1193</td><td>0.0444</td>
      <td>0.2224</td><td>0.0433</td>
      <td>0.0000</td><td>0.0291</td>
    </tr>
  </tbody>
</table>


---

## Source Table: `backend/dataset/32b/merge/TABLE_3_SYSTEM_PERFORMANCE_MERGED.md`

# TABLE 3: MERGED SYSTEM PERFORMANCE METRICS (32B)

Merged from buffer-specific `TABLE_3_SYSTEM_PERFORMANCE.md` / `raw_metrics.json` files.

## Normal Conversation Performance

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Normal Conversation Turns</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
    </tr>
    <tr>
      <td>Avg Input Tokens</td>
      <td>2038</td><td>2119</td>
      <td>3165</td><td>3156</td>
      <td>5043</td><td>5292</td>
      <td>6252</td><td>6405</td>
    </tr>
    <tr>
      <td>Avg Output Tokens</td>
      <td>139</td><td>158</td>
      <td>173</td><td>176</td>
      <td>191</td><td>219</td>
      <td>162</td><td>170</td>
    </tr>
    <tr>
      <td>Avg Total Tokens</td>
      <td>2177</td><td>2277</td>
      <td>3338</td><td>3331</td>
      <td>5234</td><td>5511</td>
      <td>6413</td><td>6575</td>
    </tr>
    <tr>
      <td>Total Input Tokens</td>
      <td>629813</td><td>654649</td>
      <td>977889</td><td>975125</td>
      <td>1558268</td><td>1635311</td>
      <td>1931805</td><td>1979202</td>
    </tr>
    <tr>
      <td>Total Output Tokens</td>
      <td>42810</td><td>48954</td>
      <td>53478</td><td>54260</td>
      <td>59026</td><td>67566</td>
      <td>49943</td><td>52427</td>
    </tr>
    <tr>
      <td>Total Tokens</td>
      <td>672623</td><td>703603</td>
      <td>1031367</td><td>1029385</td>
      <td>1617294</td><td>1702877</td>
      <td>1981748</td><td>2031629</td>
    </tr>
    <tr>
      <td>Tokens Per Correct Answer</td>
      <td>3363</td><td>2738</td>
      <td>4819</td><td>4151</td>
      <td>7775</td><td>6600</td>
      <td>10060</td><td>8833</td>
    </tr>
    <tr>
      <td>Avg Latency</td>
      <td>36.91s</td><td>35.86s</td>
      <td>37.52s</td><td>33.71s</td>
      <td>38.99s</td><td>39.29s</td>
      <td>34.77s</td><td>33.56s</td>
    </tr>
    <tr>
      <td>Total Latency</td>
      <td>11404.56s</td><td>11081.32s</td>
      <td>11594.14s</td><td>10417.47s</td>
      <td>12046.50s</td><td>12139.55s</td>
      <td>10745.07s</td><td>10370.19s</td>
    </tr>
    <tr>
      <td>Cost per Query</td>
      <td>$0.000113</td><td>$0.000119</td>
      <td>$0.000172</td><td>$0.000172</td>
      <td>$0.000267</td><td>$0.000282</td>
      <td>$0.000326</td><td>$0.000334</td>
    </tr>
    <tr>
      <td>Cost per 1M Queries</td>
      <td>$113</td><td>$119</td>
      <td>$172</td><td>$172</td>
      <td>$267</td><td>$282</td>
      <td>$326</td><td>$334</td>
    </tr>
  </tbody>
</table>

## Including Recall/Summarization Probes

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Summarization Probe Calls</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
    </tr>
    <tr>
      <td>Summarization Probe Tokens</td>
      <td>119832</td><td>131487</td>
      <td>249908</td><td>175875</td>
      <td>373285</td><td>264906</td>
      <td>324171</td><td>310617</td>
    </tr>
    <tr>
      <td>Avg Tokens per Summarization Probe</td>
      <td>2787</td><td>3058</td>
      <td>5812</td><td>4090</td>
      <td>8681</td><td>6161</td>
      <td>7539</td><td>7224</td>
    </tr>
    <tr>
      <td>Combined Evaluated Calls</td>
      <td>352</td><td>352</td>
      <td>352</td><td>352</td>
      <td>352</td><td>352</td>
      <td>352</td><td>352</td>
    </tr>
    <tr>
      <td>Combined Total Tokens</td>
      <td>792455</td><td>835090</td>
      <td>1281275</td><td>1205260</td>
      <td>1990579</td><td>1967783</td>
      <td>2305919</td><td>2342246</td>
    </tr>
    <tr>
      <td>Combined Avg Tokens per Call</td>
      <td>2251</td><td>2372</td>
      <td>3640</td><td>3424</td>
      <td>5655</td><td>5590</td>
      <td>6551</td><td>6654</td>
    </tr>
  </tbody>
</table>


---

## Source Table: `backend/dataset/32b/merge/TABLE_4_RAG_DECISIONS_MERGED.md`

# TABLE 4: MERGED RAG DECISION BREAKDOWN (32B)

Merged from buffer-specific `TABLE_4_RAG_DECISIONS.md` / `raw_metrics.json` files.

## Normal Conversation Turns

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Total Turns</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
    </tr>
    <tr>
      <td>RAG-Eligible Turns</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>300</td><td>306</td>
    </tr>
    <tr>
      <td>RAG Triggered</td>
      <td>61</td><td>80</td>
      <td>84</td><td>66</td>
      <td>71</td><td>67</td>
      <td>64</td><td>48</td>
    </tr>
    <tr>
      <td>Buffer Sufficient</td>
      <td>248</td><td>229</td>
      <td>225</td><td>243</td>
      <td>238</td><td>242</td>
      <td>236</td><td>258</td>
    </tr>
    <tr>
      <td>Retrieval Rate</td>
      <td>19.7%</td><td>25.9%</td>
      <td>27.2%</td><td>21.4%</td>
      <td>23.0%</td><td>21.7%</td>
      <td>21.3%</td><td>15.7%</td>
    </tr>
    <tr>
      <td>Buffer Rate</td>
      <td>80.3%</td><td>74.1%</td>
      <td>72.8%</td><td>78.6%</td>
      <td>77.0%</td><td>78.3%</td>
      <td>78.7%</td><td>84.3%</td>
    </tr>
    <tr>
      <td>Errors</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>9</td><td>3</td>
    </tr>
    <tr>
      <td>RAG Disabled</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
    </tr>
    <tr>
      <td>No Vector Index</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
    </tr>
  </tbody>
</table>

## Recall/Summarization Probe RAG Decisions

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Probe Turns</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
    </tr>
    <tr>
      <td>RAG-Eligible Probe Turns</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>42</td>
    </tr>
    <tr>
      <td>Probe RAG Triggered</td>
      <td>23</td><td>38</td>
      <td>40</td><td>23</td>
      <td>26</td><td>8</td>
      <td>31</td><td>1</td>
    </tr>
    <tr>
      <td>Probe Buffer Sufficient</td>
      <td>20</td><td>5</td>
      <td>3</td><td>20</td>
      <td>17</td><td>35</td>
      <td>12</td><td>41</td>
    </tr>
    <tr>
      <td>Probe Retrieval Rate</td>
      <td>53.5%</td><td>88.4%</td>
      <td>93.0%</td><td>53.5%</td>
      <td>60.5%</td><td>18.6%</td>
      <td>72.1%</td><td>2.4%</td>
    </tr>
    <tr>
      <td>Probe Buffer Rate</td>
      <td>46.5%</td><td>11.6%</td>
      <td>7.0%</td><td>46.5%</td>
      <td>39.5%</td><td>81.4%</td>
      <td>27.9%</td><td>97.6%</td>
    </tr>
    <tr>
      <td>Probe Errors</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>1</td>
    </tr>
    <tr>
      <td>Probe RAG Disabled</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
    </tr>
  </tbody>
</table>
