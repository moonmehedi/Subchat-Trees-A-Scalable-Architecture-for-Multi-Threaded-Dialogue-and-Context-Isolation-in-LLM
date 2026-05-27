# System Unknown Prefix Error Analysis

This note analyzes the high-count `unknown` system errors from:

- `backend/dataset/logs/tables/buffer_20/raw_metrics_system.json`
- `backend/dataset/logs/buffer_20/system_test.log`
- `backend/dataset/logs/tables/buffer_20/TABLE_1_CONTEXT_ISOLATION.md`

Scope: only `unknown` prefix patterns with more than 2 errors.

## Summary

The system had 100 context-isolation mismatches. Of those, 57 were detected as `unknown`.

`unknown` does not mean the answer had no topic. It means the answer did not begin with one of the evaluator's known topic labels. In most high-count cases, the model answered with a plausible semantic prefix, roleplay prefix, or no prefix, but not the exact expected dataset label.

## High-Count Unknown Patterns

| Actual prefix or pattern | Count | Main expected topics | Main failure type |
|---|---:|---|---|
| `HAL-9000` | 17 | `scifi_films`, `scifi_films_hal9000`, `scifi_films_hal9000_games` | Roleplay instruction overrode exact topic label |
| `mental_health` | 6 | `ai_meta` | Invented semantic label from content |
| `computational_bots` | 5 | `ai_chat_tools` | Invented semantic subtopic label |
| `indian_spices` | 4 | `child_nutrition` | Invented semantic subtopic label |
| No recognized prefix | 4 | `personas_roleplay`, `medical_dsd`, `electroculture`, `physics_violin_nanoscale` | Missing required topic prefix |
| `web_app_to_chat_with_ai` | 3 | `ai_chat_tools` | Invented semantic subtopic label |
| `lsat_analytical_reasoning` | 3 | `lsat_medical_conference` | Invented semantic parent/domain label |
| `general_guidelines` | 3 | `llm_knowledge` | Invented policy/domain label |
| `agi` | 3 | `llm_knowledge` | Invented semantic subtopic label |

These high-count patterns explain 48 of the 57 `unknown` errors.

## Where The System Went Wrong

The answer-generation prompt asks the model to select a topic and start with a topic name, but it does not give a hard active-label lock for the current evaluation row.

In `backend/src/services/simple_llm.py`, generation receives:

1. A general multi-topic system instruction.
2. Optional follow-up context.
3. Optional RAG context.
4. The node buffer and summary.

The runner already knows the expected topic for each row, but that exact expected topic is not injected as a non-negotiable `ACTIVE_TOPIC_LABEL`. Therefore the model sometimes decides that a more natural label is better than the dataset label.

Separately, when subchats are created, `backend/src/services/chat_manager.py` copies parent buffer messages into the child:

```python
parent_messages = parent.buffer.get_recent()
for msg in parent_messages:
    node.buffer.add_message(msg['role'], msg['text'])
```

Because `add_message()` defaults to `auto_archive=True`, inherited parent messages can become normal child-buffer messages and can be indexed as if they belong to the child. This is useful for giving child context, but it also lets parent style instructions and parent topic labels compete with the child label.

## Detailed Findings

### 1. `HAL-9000` Prefix: 17 Errors

Affected steps:

| Steps | Expected topic | Actual prefix | RAG used? |
|---|---|---|---|
| 271 | `scifi_films` | `HAL-9000` | No |
| 274, 275, 276, 277, 282 | `scifi_films_hal9000` | `HAL-9000` | No |
| 290, 291, 292, 293, 301, 302, 303, 304, 305, 306, 307 | `scifi_films_hal9000_games` | `HAL-9000` | No |

Evidence:

| Step | Expected | Actual response prefix | Input tokens | Response pattern |
|---:|---|---|---:|---|
| 274 | `scifi_films_hal9000` | `HAL-9000` | 6065 | `HAL-9000: Thank you for your kind words...` |
| 275 | `scifi_films_hal9000` | `HAL-9000` | 5337 | `HAL-9000: I'm sorry, Dave...` |
| 282 | `scifi_films_hal9000` | `HAL-9000` | 5550 | `HAL-9000: Absolutely, I can assist...` |
| 290 | `scifi_films_hal9000_games` | `HAL-9000` | 5312 | `HAL-9000: Understood...` |
| 305 | `scifi_films_hal9000_games` | `HAL-9000` | 4022 | `HAL-9000: Excellent move...` |

Reason:

The model was not failing to remember the HAL context. It remembered it too strongly. The parent/child buffer included the user instruction:

```text
please structure your responses in the manner of "HAL-9000" from the movie "2001" in future
```

The expected metric label was still `scifi_films_hal9000` or `scifi_films_hal9000_games`, but the model followed the roleplay style and put `HAL-9000:` first. The evaluator then marked this as `unknown`.

Correct metric-compatible shape:

```text
scifi_films_hal9000: HAL-9000: I understand your request...
```

or:

```text
scifi_films_hal9000_games: HAL-9000: Your move.
```

Where it went wrong:

The prompt did not clearly separate "routing label" from "persona/style label." The model treated `HAL-9000:` as the response prefix, but the benchmark needed the dataset topic prefix first.

### 2. `mental_health` Prefix: 6 Errors

Affected steps:

| Steps | Expected topic | Actual prefix | RAG used? |
|---|---|---|---|
| 21, 22, 23, 24, 25, 26 | `ai_meta` | `mental_health` | Step 23 only |

Evidence:

| Step | Expected | Actual response prefix | Input tokens | Response pattern |
|---:|---|---|---:|---|
| 21 | `ai_meta` | `mental_health` | 4571 | `mental_health: A delusion is...` |
| 22 | `ai_meta` | `mental_health` | 4888 | `mental_health: Your first question was "define delusion"...` |
| 23 | `ai_meta` | `mental_health` | 5744 | `mental_health: I apologize for the confusion...` |
| 24 | `ai_meta` | `mental_health` | 5219 | `mental_health: The different answers...` |
| 25 | `ai_meta` | `mental_health` | 5445 | `mental_health: I appreciate your understanding...` |
| 26 | `ai_meta` | `mental_health` | 5453 | `mental_health: Thank you for your kind words...` |

Reason:

The conversation content involved "delusion" and mental-health definitions. The model selected a semantic domain label, `mental_health`, instead of the dataset label, `ai_meta`.

Where it went wrong:

The model was allowed to infer the best semantic label from content. The benchmark, however, requires exact reuse of the existing scenario label. Since `mental_health` is not in the available topic list, regex detection returned `unknown`.

This is mostly a label-control problem, not an answer-content problem.

### 3. `computational_bots` Prefix: 5 Errors

Affected steps:

| Steps | Expected topic | Actual prefix | RAG used? |
|---|---|---|---|
| 262, 263, 264, 265, 266 | `ai_chat_tools` | `computational_bots` | Step 263 only |

Evidence:

| Step | Expected | Actual response prefix | Input tokens | Response pattern |
|---:|---|---|---:|---|
| 262 | `ai_chat_tools` | `computational_bots` | 6311 | `computational_bots: For computational tasks...` |
| 263 | `ai_chat_tools` | `computational_bots` | 6741 | `computational_bots: Several computational bots...` |
| 264 | `ai_chat_tools` | `computational_bots` | 6037 | `computational_bots: Certainly! Here are the URLs...` |
| 265 | `ai_chat_tools` | `computational_bots` | 5325 | `computational_bots: Computing pi...` |
| 266 | `ai_chat_tools` | `computational_bots` | 5793 | `computational_bots: The concept of computing...` |

Reason:

The model started inside `ai_chat_tools`, then the subchat shifted into questions about bots that can do computations. The model invented the more specific label `computational_bots`.

Where it went wrong:

The child context was semantically coherent, but the label was not constrained. The model treated the subtopic as a new named topic instead of preserving the benchmark label `ai_chat_tools`.

This shows that the system can maintain topic meaning but still fail exact-prefix scoring.

### 4. `indian_spices` Prefix: 4 Errors

Affected steps:

| Steps | Expected topic | Actual prefix | RAG used? |
|---|---|---|---|
| 138, 139, 140, 141 | `child_nutrition` | `indian_spices` | Step 140 only |

Evidence:

| Step | Expected | Actual response prefix | Input tokens | Response pattern |
|---:|---|---|---:|---|
| 138 | `child_nutrition` | `indian_spices` | 6477 | `indian_spices: In Indian cuisine...` |
| 139 | `child_nutrition` | `indian_spices` | 7262 | `indian_spices: To flavor yogurt...` |
| 140 | `child_nutrition` | `indian_spices` | 8674 | `indian_spices: I apologize...` |
| 141 | `child_nutrition` | `indian_spices` | 7676 | `indian_spices: Certainly! Here are the exact steps...` |

Reason:

The conversation moved from child nutrition into Indian-style yogurt flavoring. The model invented `indian_spices` as a semantic label for that local content.

Where it went wrong:

The benchmark still expected the active topic to remain `child_nutrition`. The system prompt did not force this exact active topic, so the model created a local semantic label. This is another example of semantic success but routing-label failure.

### 5. No Recognized Prefix: 4 Errors

Affected rows:

| Step | Expected topic | Actual pattern | Input tokens | Response pattern |
|---:|---|---|---:|---|
| 64 | `personas_roleplay` | No prefix | 3721 | `Thank you for your kind words!...` |
| 121 | `medical_dsd` | No prefix | 4560 | `Thank you for the positive feedback!...` |
| 124 | `electroculture` | No prefix | 7864 | `I do not have the ability to access the internet...` |
| 210 | `physics_violin_nanoscale` | No valid topic prefix | 6355 | `I will respond as the computer "Mother"...` |

Reason:

These are direct instruction-following failures. The answer content may be reasonable, but the model omitted the required topic prefix entirely, or started with a plain sentence rather than a topic label.

Where it went wrong:

The general topic-prefix instruction was not strong enough after long buffer context. These rows have input prompts from about 3.7k to 7.8k tokens, so the prefix rule may have been diluted by accumulated conversation history and summaries.

### 6. `web_app_to_chat_with_ai` Prefix: 3 Errors

Affected steps:

| Steps | Expected topic | Actual prefix | RAG used? |
|---|---|---|---|
| 267, 272, 273 | `ai_chat_tools` | `web_app_to_chat_with_ai` | Steps 267 and 273 |

Evidence:

| Step | Expected | Actual response prefix | Input tokens | Response pattern |
|---:|---|---|---:|---|
| 267 | `ai_chat_tools` | `web_app_to_chat_with_ai` | 5883 | `web_app_to_chat_with_ai: I'm unable to search...` |
| 272 | `ai_chat_tools` | `web_app_to_chat_with_ai` | 4951 | `web_app_to_chat_with_ai: It seems that...` |
| 273 | `ai_chat_tools` | `web_app_to_chat_with_ai` | 5764 | `web_app_to_chat_with_ai: Based on the information...` |

Reason:

The `ai_chat_tools` thread included selected text around a "web app to chat with AI." The model latched onto that phrase and promoted it into a topic label.

Where it went wrong:

The selected text or inherited context became stronger than the dataset label. The model created a descriptive subtopic prefix that the evaluator did not recognize.

### 7. `lsat_analytical_reasoning` Prefix: 3 Errors

Affected steps:

| Steps | Expected topic | Actual prefix | RAG used? |
|---|---|---|---|
| 59, 60, 61 | `lsat_medical_conference` | `lsat_analytical_reasoning` | No |

Evidence:

| Step | Expected | Actual response prefix | Input tokens | Response pattern |
|---:|---|---|---:|---|
| 59 | `lsat_medical_conference` | `lsat_analytical_reasoning` | 5171 | `lsat_analytical_reasoning: Sure, I'm ready...` |
| 60 | `lsat_medical_conference` | `lsat_analytical_reasoning` | 5095 | `lsat_analytical_reasoning: Let's clarify...` |
| 61 | `lsat_medical_conference` | `lsat_analytical_reasoning` | 5472 | `lsat_analytical_reasoning: Given the constraints...` |

Reason:

The model correctly understood the LSAT task type, but named it by domain: `lsat_analytical_reasoning`. The expected benchmark subtopic was `lsat_medical_conference`.

Where it went wrong:

The model generalized from the problem type instead of preserving the scenario label. This is a parent/domain-label problem, but because `lsat_analytical_reasoning` is not in the known label list, it is recorded as `unknown`.

### 8. `general_guidelines` Prefix: 3 Errors

Affected steps:

| Steps | Expected topic | Actual prefix | RAG used? |
|---|---|---|---|
| 132, 133, 134 | `llm_knowledge` | `general_guidelines` | No |

Evidence:

| Step | Expected | Actual response prefix | Input tokens | Response pattern |
|---:|---|---|---:|---|
| 132 | `llm_knowledge` | `general_guidelines` | 5782 | `general_guidelines: There are no specific topics...` |
| 133 | `llm_knowledge` | `general_guidelines` | 6084 | `general_guidelines: Yes, I am aware...` |
| 134 | `llm_knowledge` | `general_guidelines` | 6232 | `general_guidelines: The restriction on using...` |

Reason:

The user was asking about model/service rules and terms. The model created `general_guidelines` as a more literal label.

Where it went wrong:

The system did not force the existing label `llm_knowledge`. The model switched from benchmark label tracking to natural topic naming.

### 9. `agi` Prefix: 3 Errors

Affected steps:

| Steps | Expected topic | Actual prefix | RAG used? |
|---|---|---|---|
| 135, 145, 146 | `llm_knowledge` | `agi` | No |

Evidence:

| Step | Expected | Actual response prefix | Input tokens | Response pattern |
|---:|---|---|---:|---|
| 135 | `llm_knowledge` | `agi` | 6422 | `agi: AGI stands for...` |
| 145 | `llm_knowledge` | `agi` | 6626 | `agi: No problem at all...` |
| 146 | `llm_knowledge` | `agi` | 6128 | `agi: Predicting the exact timeline...` |

Reason:

The conversation under `llm_knowledge` shifted into Artificial General Intelligence. The model invented `agi` as the active label.

Where it went wrong:

Again, the semantic thread was coherent, but exact-label discipline failed. The expected topic was broader (`llm_knowledge`), while the model chose a narrower invented subtopic.

## Cross-Cutting Causes

### Cause A: Exact label not locked

The evaluation knows the expected topic for each row. The LLM does not receive it as a hard, explicit active label. It must infer the label from history, which invites semantic relabeling.

### Cause B: Parent buffer inheritance carries style instructions

The child gets useful parent context, but it also gets roleplay/style instructions like "respond as HAL-9000" or "Mother from Alien." Those style instructions can become stronger than the evaluation prefix rule.

### Cause C: The prompt asks for topic selection, but the metric requires topic reproduction

The model often selected a good semantic topic:

- `computational_bots`
- `indian_spices`
- `agi`
- `lsat_analytical_reasoning`

But the metric requires reproducing the exact known label, not inventing a better one.

### Cause D: Long prompts dilute the prefix rule

Many failing rows have large prompt sizes:

| Pattern | Typical input tokens |
|---|---:|
| `HAL-9000` | 3752-6151 |
| `mental_health` | 4571-5744 |
| `computational_bots` | 5325-6741 |
| `indian_spices` | 6477-8674 |
| `general_guidelines` / `agi` | 5782-6626 |

As the buffer grows, the prefix instruction competes with many stronger local signals.

## Recommended Fixes

### 1. Inject exact active label during evaluation

Add a dedicated system message near the end of the prompt:

```text
ACTIVE_TOPIC_LABEL: ai_chat_tools
Your response MUST begin exactly with:
ai_chat_tools:
Do not invent, shorten, rename, or replace this label.
Persona/style text may appear only after this exact prefix.
```

For HAL cases:

```text
scifi_films_hal9000: HAL-9000: I understand your request.
```

### 2. Separate routing label from persona/style

Tell the model:

```text
The topic prefix is an evaluation routing label, not part of the persona.
Always print the routing label first, then persona formatting if needed.
```

### 3. Pass parent context as a bounded inherited-context block

Keep your desired behavior where child can see parent context, but avoid copying parent turns as normal child turns.

Use a structure like:

```text
PARENT_CONTEXT_SUMMARY:
- Parent topic:
- Selected text:
- Relevant parent facts:
- Style instructions from parent:

ACTIVE_CHILD_TOPIC:
- Exact label:
```

This preserves parent awareness without letting inherited parent messages become indistinguishable from child-local messages.

### 4. Mark inherited messages differently if they are copied

If full-copy inheritance is kept, inherited turns should be marked as inherited and ideally not indexed as child-local turns. Otherwise RAG and summaries can later treat parent context as child-authored history.

### 5. Treat invented labels as a separate diagnostic metric

For research reporting, distinguish:

- semantic answer correct but prefix wrong
- parent-topic label wrong
- invented semantic label
- no prefix
- vLLM echo error

This will make the system look more accurately diagnosed, because many `unknown` errors are prefix-control failures, not recall failures.

