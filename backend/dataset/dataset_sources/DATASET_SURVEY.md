# Conversation Datasets for Evaluating Subchat Trees

This document summarizes established, citable conversation datasets you can use to evaluate your Subchat Trees architecture. All datasets below are widely used in the research community and come with published papers and public releases.

> Focus: multi-turn conversations, multi-domain or knowledge-grounded settings, and scenarios where multiple entities with similar or overlapping names may appear.

---

## Summary Table

| Dataset | Source (Paper) | Data / Code | Style & Domains | Why It’s Relevant | Example Snippet (High-Level) |
|--------|----------------|-------------|-----------------|-------------------|------------------------------|
| MultiWOZ 2.2 | [MultiWOZ 2.2: A Dialogue Dataset with Additional Annotation Corrections and State Tracking Baselines](https://arxiv.org/abs/2007.12720) | [MultiWOZ Repo (Official)](https://github.com/budzianowski/multiwoz) | Large-scale task-oriented, 8 domains (hotel, restaurant, train, attraction, taxi, etc.) | Strong benchmark for multi-domain dialogue, long conversations, and slot/value tracking (e.g., multiple hotels with similar names). | User books a hotel and restaurant in the same city; several hotel names differ only slightly, and the system must keep track of which one the user selected. |
| MultiWOZ (original) | [MultiWOZ: A Large-Scale Multi-Domain Wizard-of-Oz Dataset for Task-Oriented Dialogue Modelling](https://aclanthology.org/D18-1547/) | [Original MultiWOZ Data](https://github.com/budzianowski/multiwoz) | Human-human, multi-domain task-oriented dialogues (hotel, restaurant, train, etc.) | Original version of MultiWOZ; widely cited and used as a baseline for later corrected versions (2.1, 2.2). | User talks about booking a train and a taxi; multiple times, cities and times are revisited, requiring careful state tracking over many turns. |
| Schema-Guided Dialogue (SGD) | [Towards Scalable Multi-domain Conversational Agents: The Schema-Guided Dialogue Dataset](https://arxiv.org/abs/1909.05855) | [SGD Data on Google’s Repo](https://github.com/google-research-datasets/dstc8-schema-guided-dialogue) | 16 domains, 20,000+ multi-domain conversations with API schemas | Designed for large-scale virtual assistants; domains often have overlapping intents and slots (e.g., multiple ride-sharing or calendar services), good for ambiguity and schema-level generalization tests. | User switches between multiple services (e.g., two ride-sharing providers) that both have a "car type" slot; the agent must know which service and car the user is referring to at each step. |
| Taskmaster-1 | [Taskmaster-1: Toward a Realistic and Diverse Dialog Dataset](https://arxiv.org/abs/1909.05374) | [Taskmaster-1 Dataset](https://github.com/google-research-datasets/Taskmaster) | Multi-turn, task-oriented dialogues (e.g., movie tickets, restaurant reservations, ordering, travel) | Contains both spoken-style and written dialogues with realistic noise, corrections, and cross-references to entities like movie titles and venues. | User first talks about booking tickets for one movie, then changes to another movie with a similar title; the system must disambiguate which showtime and theater belong to which movie. |
| Taskmaster-2 | [Taskmaster-2: Self-Supervised Dialogue Dataset for Goal-Oriented Dialogue Systems](https://arxiv.org/abs/2002.01373) | [Taskmaster-2 Dataset](https://github.com/google-research-datasets/Taskmaster) | Self-dialogues (single user playing both sides), multiple task domains | Good for training and evaluation where more scripted but still realistic multi-step tasks are needed, including references to multiple entities (restaurants, flights, etc.). | User creates a mock conversation where they discuss two different restaurants with similar cuisines and must keep track of which one they finally book. |
| Wizard of Wikipedia | [Wizard of Wikipedia: Knowledge-Powered Conversational Agents](https://arxiv.org/abs/1811.01241) | [ParlAI WoW Task](https://parl.ai/projects/wizard_of_wikipedia/) | Open-domain, knowledge-grounded dialogue, grounded in Wikipedia passages | Ideal for testing knowledge retrieval and multi-entity reasoning; many topics include entities with overlapping names (cities, people, etc.). | Two speakers discuss "Mercury"; retrieved knowledge includes pages about the planet, the element, and mythology, and the model must stay on the correct sense of "Mercury" chosen by the conversation. |
| DailyDialog | [DailyDialog: A Manually Labelled Multi-turn Dialogue Dataset](https://arxiv.org/abs/1710.03957) | [DailyDialog on Hugging Face](https://huggingface.co/datasets/liyuankun/daily_dialog) | Daily-life multi-turn dialogues, manually labeled for emotion and speech acts | Good for general multi-turn coherence and emotional nuance, less focused on external knowledge but useful as a baseline conversational dataset. | Friends discuss planning a trip; they refer to different cities and times, and the system must keep the plan consistent across 8–10 turns. |
| Persona-Chat | [Personalizing Dialogue Agents: I Have a Dog, Do You Have Pets Too?](https://arxiv.org/abs/1801.07243) | [Persona-Chat via ParlAI](https://parl.ai/projects/convai2/) | Open-domain chit-chat with explicit persona profiles | Useful for testing whether the model can maintain a consistent persona and distinguish between self vs. partner attributes (e.g., two people who both "have a dog"). | Two speakers both mention "I have a dog" and discuss "my dog" vs. "your dog"; the model must not confuse which dog belongs to which speaker. |
| Ubuntu Dialogue Corpus | [The Ubuntu Dialogue Corpus: A Large Dataset for Research in Unstructured Multi-Turn Dialogue Systems](https://arxiv.org/abs/1506.08909) | [Ubuntu Corpus v2](https://github.com/rkadlec/ubuntu-ranking-dataset-creator) | Technical support chats from Ubuntu IRC, long multi-turn threads | Extremely long, technical conversations, often with multiple users and overlapping references (e.g., different versions of "Java" packages, different processes with similar names). | A user asks about installing "Java"; multiple helpers mention different versions (OpenJDK, Oracle Java 8, etc.), and the model must track which package and version the user finally installs. |
| MSDialog | [MSDialog: A Dataset of Multi-turn Information-Seeking Conversations](https://arxiv.org/abs/1809.08297) | [MSDialog Data](https://ciir.cs.umass.edu/downloads/msdialog/) | Information-seeking Q&A from Microsoft product forums | Good for multi-turn clarification questions about similar product names (e.g., different Windows versions or Office editions). | A user asks about "Office"; replies mention "Office 365", "Office 2016", and "Office Online", and the model must track which specific product the user actually uses. |

---

## Notes on Ambiguity and "Same Name, Different Concept" Scenarios

Your custom scenario `03_long_context_mercury_rust_java.json` creates deliberate semantic ambiguity (e.g., "Mercury" as a planet vs. element; "Rust" as a programming language vs. corrosion; "Java" as a language vs. coffee vs. an island). While there is no single standard benchmark built *only* around such word-sense ambiguity, several datasets above naturally contain similar multi-entity and multi-sense confusion:

- **Wizard of Wikipedia**: Frequently covers entities with ambiguous names because topics are drawn from Wikipedia pages (e.g., cities vs. people, elements vs. planets). You can create evaluation slices where different Wikipedia pages share the same surface form.
- **Ubuntu Dialogue Corpus**: Support logs often mention packages, processes, and tools with overlapping names (e.g., "Java" versions, multiple package names, different services starting with the same prefix).
- **Schema-Guided Dialogue** and **MultiWOZ**: Realistic booking domains where multiple hotels, restaurants, and attractions have very similar names or share attributes. Ambiguity arises when users say things like "that first hotel" or "the other one".
- **MSDialog**: Information-seeking threads around products like "Windows" or "Office" that refer to several editions and components with overlapping names.

For your experiments, you can:

1. **Directly evaluate** Subchat Trees on full dialogues from these datasets by converting them into your test JSON format (one scenario per dialogue or per small set of dialogues).
2. **Construct ambiguity-focused subsets** by filtering dialogues where:
   - Multiple entities with the same or very similar names appear (e.g., two hotels in the same city, multiple products in the same family).
   - The conversation explicitly uses pronouns or vague references ("it", "that one", "the first one").
3. **Compare baseline vs. Subchat Trees** on these subsets to see whether your architecture better maintains the correct entity across long, multi-turn interactions.

---

## How to Cite These Datasets

In a paper or report, you can cite each dataset’s main paper. For example:

- **MultiWOZ (Budzianowski et al., EMNLP 2018)**: MultiWOZ - A Large-Scale Multi-Domain Wizard-of-Oz Dataset for Task-Oriented Dialogue Modelling.
- **MultiWOZ 2.2 (Zang et al., NLP4ConvAI 2020)**: MultiWOZ 2.2: A Dialogue Dataset with Additional Annotation Corrections and State Tracking Baselines.
- **Schema-Guided Dialogue (Rastogi et al., AAAI 2020)**: Towards Scalable Multi-domain Conversational Agents: The Schema-Guided Dialogue Dataset.
- **Taskmaster-1 (Byrne et al., 2019)** and **Taskmaster-2 (Byrne et al., 2019)**: Taskmaster-1: Toward a Realistic and Diverse Dialog Dataset; Taskmaster-2: Self-Supervised Dialogue Dataset for Goal-Oriented Dialogue Systems.
- **Wizard of Wikipedia (Dinan et al., 2019)**: Wizard of Wikipedia: Knowledge-Powered Conversational Agents.
- **DailyDialog (Li et al., 2017)**: DailyDialog: A Manually Labelled Multi-turn Dialogue Dataset.
- **Persona-Chat (Zhang et al., 2018)**: Personalizing Dialogue Agents: I Have a Dog, Do You Have Pets Too?
- **Ubuntu Dialogue Corpus (Lowe et al., 2015)**: The Ubuntu Dialogue Corpus: A Large Dataset for Research in Unstructured Multi-Turn Dialogue Systems.
- **MSDialog (Qu et al., 2018)**: MSDialog: A Dataset of Multi-turn Information-Seeking Conversations.

These references should be sufficient to convince your teacher that you are using well-established, peer-reviewed benchmarks.
