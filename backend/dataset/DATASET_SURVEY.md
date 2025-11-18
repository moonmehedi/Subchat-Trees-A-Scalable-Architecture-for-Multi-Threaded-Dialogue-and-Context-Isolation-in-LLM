

## How These Datasets Create Ambiguity (for Subchat Testing)

Your project aims to solve semantic confusion where a single-threaded conversation fails. Here’s how the most relevant datasets from this list provide the exact kind of ambiguity needed to test your architecture, similar to your `01_python_confusion.json` and `03_long_context_mercury_rust_java.json` scenarios.

### 1. Wizard of Wikipedia (WoW) - Best for Word-Sense Ambiguity

This dataset is your strongest candidate for replicating the "Mercury/Rust/Java" style of confusion.

*   **How it Creates Confusion:** Conversations are grounded in Wikipedia. Many topics are **homonyms** with multiple, distinct Wikipedia pages. A linear model will easily confuse them.
    *   **Example:** A conversation about "**Chicago**" could refer to the **city**, the **band**, or the **musical**. A question like, "What was their first album?" after discussing the city's architecture would confuse a baseline model. Your Subchat system could maintain separate, isolated contexts for `Chicago (City)` and `Chicago (Band)`.
*   **How to Use:** Filter the dataset for dialogues where the initial topic corresponds to multiple Wikipedia entries. These are pre-made, naturalistic confusion scenarios.

### 2. Ubuntu Dialogue Corpus & MSDialog - Best for Technical Ambiguity

These are perfect for replicating the "Python" (snake vs. language) style of confusion in a technical domain.

*   **How it Creates Confusion:** These are real-world support logs where software names are inherently ambiguous.
    *   **Example:** A user asks for help with "**Java**". This could mean **OpenJDK 11**, **Oracle Java 8**, or even **JavaScript**. A long thread with multiple suggestions will easily confuse a linear model trying to track which version is being installed or fixed.
*   **How to Use:** Extract dialogues containing keywords for software with multiple versions or overlapping names (e.g., `java`, `python`, `docker`, `kernel`).

### 3. MultiWOZ & Schema-Guided Dialogue (SGD) - Best for Entity Ambiguity

These datasets test a more subtle but critical form of confusion: distinguishing between similar real-world entities.

*   **How it Creates Confusion:** The dialogues involve booking multiple entities (hotels, restaurants) that often have very similar names or attributes.
    *   **Example:** A user discusses two hotels, "Cambridge Hotel" and "Hotel Cambridge." After booking one and moving on to discuss a restaurant, they ask, "What's the postcode for **that hotel**?" A baseline model is at high risk of retrieving the wrong hotel's details.
*   **How to Use:** Select dialogues where users inquire about multiple entities of the same type (e.g., two hotels, three restaurants) or switch domains frequently. These are ideal for testing your system's ability to manage distinct sub-tasks.
