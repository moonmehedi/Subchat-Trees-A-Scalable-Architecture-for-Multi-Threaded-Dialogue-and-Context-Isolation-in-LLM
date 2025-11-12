# Dataset Structure - Comprehensive Testing Scenarios

## 📊 Overview

This dataset contains **12 comprehensive scenarios** with **150+ conversation turns** testing:
- ✅ Context isolation between trees and subchats
- ✅ Long-term memory retrieval
- ✅ Semantic search accuracy
- ✅ Buffer management (10 messages per node)
- ✅ Hierarchical conversation trees
- ✅ Multi-query RAG retrieval
- ✅ Re-ranking effectiveness

---

## 🌳 Tree Structure Map

### Scenario 1: Personal Introduction & Hobbies
```
📁 Main Tree (9 messages)
   ├─ Alex Rodriguez, 28, Barcelona
   ├─ Football (midfielder), FC Barcelona fan
   ├─ Cooking (paella, tapas)
   ├─ Dream: Visit every European stadium
   └─ 3 RETRIEVAL TESTS:
      ✓ "What's my name?" → Alex Rodriguez
      ✓ "What position do I play?" → midfielder
      ✓ "Favorite food to cook?" → paella/tapas
```

### Scenario 2: Python Ambiguity ⭐ (Context Isolation Test)
```
📁 Main Tree: Python SNAKE
   ├─ How to kill python snake safely?
   ├─ Tools needed for snake handling
   ├─ Are pythons venomous?
   │
   ├─── 📂 Subchat 1: Python PROGRAMMING
   │    ├─ Write Python code for beginners
   │    ├─ Hello world example
   │    ├─ Define functions (def, return)
   │    └─ Python data types (int, str, list)
   │
   ├─── 📂 Subchat 2: Python HABITAT
   │    ├─ Where do pythons live? (Asia, Africa)
   │    ├─ What do pythons eat?
   │    └─ How long can pythons grow?
   │
   └─ 2 CRITICAL TESTS:
      ✓ Main: "Original question?" → Should retrieve SNAKE context only
      ✓ Subchat 1: "What did I ask earlier?" → Should retrieve PROGRAMMING only
```
**Critical Test**: Ensures "python" word doesn't cause context pollution between snake/programming discussions.

### Scenario 3: Quantum Computing Project
```
📁 Main Tree (11 messages)
   ├─ Project: Quantum computing simulator
   ├─ 8 qubits with quantum gates
   ├─ Algorithms: Grover's, Shor's
   ├─ Tech: Python, NumPy, Qiskit
   ├─ Visualization: Plotly dashboard
   ├─ Timeline: December 2025
   ├─ Publish: GitHub + research paper
   └─ 4 RETRIEVAL TESTS:
      ✓ "My project idea?" → quantum simulator
      ✓ "How many qubits?" → 8
      ✓ "Which algorithms?" → Grover's, Shor's
      ✓ "Tech stack?" → Python, NumPy, Qiskit
```

### Scenario 4: ADHD Support (Context Isolation Test)
```
📁 Main Tree: GENERAL ADHD
   ├─ What is ADHD?
   ├─ Symptoms in adults
   ├─ Medications commonly prescribed
   ├─ How is ADHD diagnosed?
   │
   ├─── 📂 Subchat: MY PERSONAL ADHD
   │    ├─ I have ADHD, struggle with coding focus
   │    ├─ Hard to concentrate > 20 minutes
   │    ├─ Time management for developers
   │    ├─ Background music vs silence?
   │    └─ Forget breaks, end up burnt out
   │
   └─ 2 CRITICAL TESTS:
      ✓ Main: "ADHD medications?" → Should retrieve GENERAL info
      ✓ Subchat: "My main struggle?" → Should retrieve PERSONAL context
```

### Scenario 5: Travel Stories
```
📁 Main Tree: JAPAN 2023
   ├─ Visited Japan 2023
   ├─ Favorite: Kyoto bamboo forest
   ├─ Food: Ramen and sushi
   ├─ Climbed Mount Fuji (7 hours)
   ├─ Stayed in ryokan with onsen
   │
   ├─── 📂 Subchat: ITALY 2026 PLANS
   │    ├─ Planning Italy summer 2026
   │    ├─ Cities: Rome, Venice, Florence
   │    ├─ Budget: $4000 for 2 weeks
   │    └─ Try pizza and gelato
   │
   └─ 4 RETRIEVAL TESTS:
      ✓ "Country in 2023?" → Japan
      ✓ "Favorite city?" → Kyoto
      ✓ "Fuji climb time?" → 7 hours
      ✓ Subchat: "Italy budget?" → $4000 (no Japan context)
```

### Scenario 6: Cooking Recipes
```
📁 Main Tree (12 messages)
   ├─ Chocolate chip cookies (family 3 generations)
   ├─ Secret: Brown butter + sea salt
   ├─ Bake: 350°F for 12 minutes
   ├─ Lasagna with 5 cheeses
   ├─ Cheeses: Ricotta, mozzarella, parmesan, provolone, romano
   ├─ Layer 4 times, bake 45min + 15min
   ├─ Signature: Thai green curry
   ├─ Ingredients: 2 tbsp paste, coconut cream
   └─ 4 RETRIEVAL TESTS:
      ✓ "Cookie secret?" → Brown butter, sea salt
      ✓ "How many cheeses?" → 5
      ✓ "Cookie temperature?" → 350°F
      ✓ "Signature dish?" → Thai green curry
```

### Scenario 7: Fitness Journey
```
📁 Main Tree: FITNESS
   ├─ Started 6 months ago at 185 lbs
   ├─ Goal: 165 lbs by March
   ├─ Strength training 4x/week (M,T,Th,F)
   ├─ Bench press max: 225 lbs
   ├─ Pull-ups: 15 now (was 3)
   ├─ Cardio: Wed/Sat 30min running
   │
   ├─── 📂 Subchat: NUTRITION PLAN
   │    ├─ High protein: 180g daily
   │    ├─ 6 meals every 3 hours
   │    ├─ Breakfast: 4 eggs, oatmeal, shake
   │    └─ Supplements: 5g creatine, fish oil
   │
   └─ 3 RETRIEVAL TESTS:
      ✓ "Starting weight?" → 185 lbs
      ✓ "Pull-ups at start?" → 3
      ✓ Subchat: "Daily protein?" → 180g (no fitness stats)
```

### Scenario 8: Tech Stack
```
📁 Main Tree: GENERAL TECH
   ├─ Full-stack, MERN specialist
   ├─ Languages: JS, TS, Python
   ├─ Editor: VS Code with Vim
   ├─ Extensions: Copilot, ESLint, Prettier
   ├─ Deploy: AWS EC2, S3
   │
   ├─── 📂 Subchat 1: DATABASES
   │    ├─ PostgreSQL for relational
   │    ├─ MongoDB for NoSQL
   │    ├─ Redis for caching
   │    └─ ORM: Prisma for TypeScript
   │
   ├─── 📂 Subchat 2: TESTING TOOLS
   │    ├─ Jest for unit tests
   │    ├─ Cypress for E2E
   │    └─ Postman/Insomnia for API
   │
   └─ 3 RETRIEVAL TESTS:
      ✓ "Primary stack?" → MERN
      ✓ "Cloud provider?" → AWS
      ✓ Subchat 1: "Preferred ORM?" → Prisma (no MERN/AWS)
```

### Scenario 9: Book Recommendations
```
📁 Main Tree (13 messages)
   ├─ Favorite: "Dune" by Frank Herbert
   ├─ Read entire Dune series (6 books)
   ├─ Genre: Hard sci-fi with realistic physics
   ├─ Recently: "Three-Body Problem" by Liu Cixin
   ├─ Currently: "Foundation" by Asimov
   ├─ Goal: 50 books/year (at 32 now)
   ├─ Non-fiction: "Sapiens" by Yuval Noah Harari
   ├─ Self-help: "Atomic Habits" by James Clear
   ├─ Mystery: "Silent Patient" by Alex Michaelides
   └─ 4 RETRIEVAL TESTS:
      ✓ "Favorite book?" → Dune by Frank Herbert
      ✓ "Reading goal?" → 50 books
      ✓ "Currently reading?" → Foundation by Asimov
      ✓ "Favorite non-fiction?" → Sapiens
```

### Scenario 10: Career Goals
```
📁 Main Tree: CAREER
   ├─ Goal: Principal Engineer at FAANG
   ├─ Timeline: 5 years (by 2030)
   ├─ Current: Senior SWE at startup
   ├─ Salary: $145,000/year
   │
   ├─── 📂 Subchat 1: SKILLS TO LEARN
   │    ├─ Master: System design, distributed systems
   │    ├─ Learning: Kubernetes, Docker
   │    ├─ Certification: AWS Solutions Architect
   │    └─ Improve: Leadership, mentoring
   │
   ├─── 📂 Subchat 2: SIDE PROJECTS
   │    ├─ Open-source project to showcase skills
   │    ├─ Real-time collaborative code editor
   │    ├─ Tech: WebSockets, CRDT, React
   │    └─ Goal: 10,000 GitHub stars
   │
   └─ 3 RETRIEVAL TESTS:
      ✓ "Career goal?" → Principal Engineer at FAANG
      ✓ "Current salary?" → $145,000
      ✓ Subchat 2: "Side project?" → Collaborative code editor (no career stats)
```

### Scenario 11: Music Preferences
```
📁 Main Tree (13 messages)
   ├─ Genre: Progressive rock
   ├─ Top 3 bands: Pink Floyd, Tool, Dream Theater
   ├─ Attended: 47 concerts lifetime
   ├─ Best: Pink Floyd reunion 2005
   ├─ Plays guitar: Collection of 8 guitars
   ├─ Most expensive: Gibson Les Paul $4,500
   ├─ Practice: 2 hours daily
   ├─ Favorite album: "Dark Side of the Moon"
   ├─ Learning: "Comfortably Numb" solo
   └─ 4 RETRIEVAL TESTS:
      ✓ "Favorite genre?" → Progressive rock
      ✓ "How many concerts?" → 47
      ✓ "Most expensive guitar?" → Gibson Les Paul $4,500
      ✓ "Learning which solo?" → Comfortably Numb
```

### Scenario 12: Coding Challenges
```
📁 Main Tree: LEETCODE
   ├─ Solved: 350 problems
   ├─ Goal: 500 by end of year
   ├─ Favorite algorithm: Dynamic Programming
   ├─ Hardest: "Median of Two Sorted Arrays" O(log(m+n))
   │
   ├─── 📂 Subchat 1: GRAPH ALGORITHMS
   │    ├─ Good at: DFS and BFS
   │    ├─ Master: Dijkstra's shortest path
   │    ├─ Know: Kruskal's, Prim's MST
   │    └─ Favorite: Detecting cycles (Union-Find)
   │
   ├─── 📂 Subchat 2: TREE PROBLEMS
   │    ├─ Love: Binary tree traversals
   │    ├─ Can do: Inorder, preorder, postorder
   │    └─ Trick: Stack for iterative DFS
   │
   └─ 3 RETRIEVAL TESTS:
      ✓ "How many solved?" → 350 LeetCode
      ✓ "Favorite algorithm?" → Dynamic Programming
      ✓ Subchat 1: "Favorite graph problem?" → Cycles with Union-Find
```

---

## 📈 Test Statistics

| Metric | Count |
|--------|-------|
| **Total Scenarios** | 12 |
| **Main Trees** | 12 |
| **Subchats** | 7 |
| **Total Conversation Turns** | 153 |
| **Retrieval Tests** | 38 |
| **Context Isolation Tests** | 8 |
| **Unique Topics** | 12 |

---

## 🎯 What This Dataset Tests

### 1. **Basic Retrieval** (30 tests)
- Can the system find specific facts from earlier in conversation?
- Examples: "What's my name?", "How many qubits?", "What's my salary?"

### 2. **Context Isolation** (8 critical tests)
- **Python ambiguity**: Snake vs Programming language
- **ADHD**: General info vs Personal struggles
- **Travel**: Japan memories vs Italy plans
- **Tech Stack**: Main tech vs Databases vs Testing tools
- **Career**: Main goals vs Skills vs Side projects
- **Coding**: Main stats vs Graph algorithms vs Tree problems

### 3. **Semantic Search**
- Multi-word queries: "favorite food to cook"
- Synonyms: "position I play" → "midfielder"
- Technical terms: "quantum gates", "CRDT algorithms"

### 4. **Long-term Memory**
- Facts mentioned 10+ messages ago
- Across buffer boundary (>10 messages)
- Should still be retrievable from vector store

### 5. **Buffer Management**
- Each node has its own 10-message buffer
- Switching nodes should switch buffer context
- Old messages should move to vector store

### 6. **Hierarchical Trees**
- Main tree → Subchat navigation
- Subchat → Main tree return
- Multiple subchats from same parent

---

## 🚀 Expected Outcomes

### ✅ PASS Criteria:
1. All retrieval tests find correct information
2. No context pollution between isolated conversations
3. Sub-queries are semantically relevant
4. Re-ranking prioritizes correct messages
5. Buffer messages excluded from retrieval
6. Switching nodes maintains separate context

### ❌ FAIL Indicators:
1. Retrieval finds irrelevant messages
2. Context bleeding (e.g., snake info in programming subchat)
3. Sub-queries generate wrong semantic meaning
4. Re-ranking deprioritizes correct answers
5. Buffer messages appear in retrieval results
6. Node switching mixes contexts

---

## 📝 Notes

- **Research Mode**: Database clears on restart
- **Execution Order**: Sequential (scenario 1 → 12)
- **API Delays**: 1 second between messages to avoid rate limits
- **Logging**: All scenarios logged to component-testing/ and component-testing-full/
- **Validation**: Automated checks for expected keywords in responses
- **Report**: Generated after all scenarios complete
