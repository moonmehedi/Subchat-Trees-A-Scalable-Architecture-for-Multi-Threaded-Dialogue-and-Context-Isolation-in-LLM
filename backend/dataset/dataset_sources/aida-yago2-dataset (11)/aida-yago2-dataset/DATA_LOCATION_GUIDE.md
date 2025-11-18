# AIDA-YAGO2 Dataset Location Guide

## Exact Folder Location
```
/media/sda3/projects/simple build/Subchat-Trees-A-Scalable-Architecture-for-Multi-Threaded-Dialogue-and-Context-Isolation-in-LLM/backend/dataset/dataset_sources/aida-yago2-dataset (11)/aida-yago2-dataset/
```

## Files in This Folder

### 1. **MAIN DATA FILE** ⭐ (This is what you need!)
**File:** `AIDA-YAGO2-annotations.tsv`
- **Size:** 2.3 MB
- **Lines:** 37,715 lines
- **Documents:** 1,393 news articles
- **Format:** Tab-separated values (TSV)

**What's inside:**
- Each document starts with: `-DOCSTART- (ID Title)`
- Each line after that represents a word/entity with columns separated by TAB (`^I` in the output above)

**Example from Line 1-10:**
```
Line 1:  -DOCSTART- (1 EU)                          ← Start of document 1 about "EU"
Line 2:  0    --NME--                                ← Position 0, no entity match
Line 3:  2    Germany    http://...    11867    /m/0345h    ← Position 2: "Germany" entity
Line 4:  6    United_Kingdom    http://...           ← Position 6: "United Kingdom" entity
Line 5:  9    --NME--                                ← Position 9, no entity
Line 6:  11   Brussels    http://...                 ← Position 11: "Brussels" entity
```

**Column Format (Tab-separated):**
```
Column 1: Character position in document
Column 2: Entity name (or --NME-- if no entity)
Column 3: Wikipedia URL
Column 4: Wikipedia ID
Column 5: Freebase ID
```

---

### 2. **JAR File** (Java classes, NOT data)
**File:** `aida-yago2-dataset.jar`
- **Size:** 18 KB
- **Purpose:** Java utility to process the TSV file (you don't need this for Python)
- **Contents:** Compiled Java classes (`.class` files)

---

### 3. **Documentation Files**
**File:** `README.txt`
- **Size:** 3.9 KB
- **Contains:** Explanation of dataset format and how to use it

**File:** `README_CoNLL_2003.TXT`
- **Size:** 7.1 KB
- **Contains:** Info about the original CoNLL 2003 dataset

**File:** `Robust Disambiguation of Named Entities in Text.pdf`
- **Size:** 292 KB
- **Contains:** Research paper explaining the dataset and disambiguation methods

---

## How to Read the Data

### Option 1: View with Python script (already created)
```bash
cd /media/sda3/projects/simple\ build/Subchat-Trees-A-Scalable-Architecture-for-Multi-Threaded-Dialogue-and-Context-Isolation-in-LLM/backend/dataset

python3 view_aida.py --limit 5
```

### Option 2: View directly in terminal
```bash
cd "/media/sda3/projects/simple build/Subchat-Trees-A-Scalable-Architecture-for-Multi-Threaded-Dialogue-and-Context-Isolation-in-LLM/backend/dataset/dataset_sources/aida-yago2-dataset (11)/aida-yago2-dataset"

# View first document
head -60 AIDA-YAGO2-annotations.tsv

# Count documents
grep -c "^-DOCSTART-" AIDA-YAGO2-annotations.tsv

# Find specific document (e.g., about China)
grep -A 200 "DOCSTART.*China" AIDA-YAGO2-annotations.tsv | head -100
```

### Option 3: Open in text editor
The TSV file is plain text, so you can open it with any editor:
- VS Code
- nano
- vim
- gedit

---

## Dataset Statistics

| Metric | Value |
|--------|-------|
| Total Documents | 1,393 |
| Total Lines | 37,715 |
| File Size | 2.3 MB |
| Document IDs | 1 to 1393 |
| Data Splits | TRAIN (1-946), TESTA (947-1162), TESTB (1163-1393) |

---

## Example Documents in the File

### Document 1: "EU" (European Union politics)
- **Line:** 1
- **Command:** `sed -n '1,60p' AIDA-YAGO2-annotations.tsv`
- **Entities:** Germany, United_Kingdom, Brussels, European_Commission, France, Spain

### Document 2: "Rare" (Jimi Hendrix auction)
- **Line:** ~62
- **Command:** `sed -n '62,80p' AIDA-YAGO2-annotations.tsv`
- **Entities:** Jimi_Hendrix, London, United_States, England, Nottingham, Australia

### Document 3: "China" (China-Taiwan relations)
- **Line:** ~82
- **Command:** `sed -n '82,150p' AIDA-YAGO2-annotations.tsv`
- **Entities:** People's_Republic_of_China, Republic_of_China (Taiwan), Beijing, Taipei, Ukraine

---

## What You Should Do Next

1. **View the data** using the Python script:
   ```bash
   python3 /media/sda3/projects/simple\ build/Subchat-Trees-A-Scalable-Architecture-for-Multi-Threaded-Dialogue-and-Context-Isolation-in-LLM/backend/dataset/view_aida.py --limit 3
   ```

2. **Find documents with ambiguity** (like the China-Taiwan one):
   ```bash
   cd "/media/sda3/projects/simple build/Subchat-Trees-A-Scalable-Architecture-for-Multi-Threaded-Dialogue-and-Context-Isolation-in-LLM/backend/dataset/dataset_sources/aida-yago2-dataset (11)/aida-yago2-dataset"
   grep "DOCSTART" AIDA-YAGO2-annotations.tsv | head -20
   ```

3. **Convert to your test format** - I can help you create a script that:
   - Extracts specific documents
   - Converts them to your `03_long_context_mercury_rust_java.json` format
   - Generates test scenarios for your Subchat system

---

## Key Takeaway

**The actual data is in ONE file:**
```
AIDA-YAGO2-annotations.tsv
```

Everything else is documentation or utilities. This TSV file contains 1,393 news articles with entity annotations that you can use to test your Subchat-Trees system.
