"""
AIDA-YAGO2 Dataset Viewer
Reads and displays the AIDA-YAGO2-annotations.tsv file in a readable format

The AIDA dataset contains named entity annotations from news articles.
It's useful for testing entity disambiguation and multi-entity conversations.
"""

import sys
from pathlib import Path


def read_aida_tsv(file_path, limit=10):
    """
    Read and display AIDA-YAGO2 dataset
    
    Format:
    - Lines starting with "-DOCSTART-" indicate new documents
    - Each line contains: token, POS tag, NE tag, YAGO2 entity (if applicable)
    - Empty lines separate sentences
    """
    
    print(f"📂 Reading AIDA-YAGO2 dataset from: {file_path}\n")
    print("="*80)
    
    documents_shown = 0
    current_doc = []
    current_sentence = []
    doc_id = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # New document marker
            if line.startswith("-DOCSTART-"):
                # Print previous document if exists
                if current_doc and documents_shown < limit:
                    print_document(doc_id, current_doc)
                    documents_shown += 1
                    
                    if documents_shown >= limit:
                        print(f"\n✅ Displayed {limit} documents")
                        print(f"   (File has more documents - use --limit to see more)")
                        return
                
                # Start new document
                doc_id = line.split()[1] if len(line.split()) > 1 else f"Doc_{line_num}"
                current_doc = []
                current_sentence = []
                continue
            
            # Empty line = end of sentence
            if not line:
                if current_sentence:
                    current_doc.append(current_sentence)
                    current_sentence = []
                continue
            
            # Parse token line
            parts = line.split('\t')
            if len(parts) >= 4:
                token, pos, ne_tag, entity = parts[0], parts[1], parts[2], parts[3]
            elif len(parts) >= 3:
                token, pos, ne_tag = parts[0], parts[1], parts[2]
                entity = "--"
            else:
                continue
            
            current_sentence.append({
                'token': token,
                'pos': pos,
                'ne_tag': ne_tag,
                'entity': entity
            })
    
    # Print last document
    if current_doc and documents_shown < limit:
        print_document(doc_id, current_doc)
        documents_shown += 1
    
    print(f"\n✅ Displayed {documents_shown} documents")


def print_document(doc_id, sentences):
    """Print a document with entity highlighting"""
    print(f"\n{'='*80}")
    print(f"📄 DOCUMENT: {doc_id}")
    print(f"{'='*80}")
    print(f"Number of sentences: {len(sentences)}\n")
    
    for sent_idx, sentence in enumerate(sentences, 1):
        print(f"Sentence {sent_idx}:")
        print("-" * 80)
        
        # Print the text
        text_tokens = []
        entities_found = []
        current_entity = []
        current_entity_name = None
        
        for token_data in sentence:
            token = token_data['token']
            ne_tag = token_data['ne_tag']
            entity = token_data['entity']
            
            # Track entities
            if ne_tag.startswith('B-'):  # Beginning of entity
                if current_entity:
                    entities_found.append({
                        'text': ' '.join(current_entity),
                        'entity': current_entity_name
                    })
                current_entity = [token]
                current_entity_name = entity if entity != "--" else "Unknown"
            elif ne_tag.startswith('I-'):  # Inside entity
                current_entity.append(token)
            else:  # Outside entity
                if current_entity:
                    entities_found.append({
                        'text': ' '.join(current_entity),
                        'entity': current_entity_name
                    })
                    current_entity = []
                    current_entity_name = None
            
            text_tokens.append(token)
        
        # Handle last entity
        if current_entity:
            entities_found.append({
                'text': ' '.join(current_entity),
                'entity': current_entity_name
            })
        
        # Print sentence text
        sentence_text = ' '.join(text_tokens)
        print(f"📝 Text: {sentence_text}")
        
        # Print entities
        if entities_found:
            print(f"\n🔗 Named Entities:")
            for ent in entities_found:
                entity_id = ent['entity']
                # Make YAGO2 IDs more readable
                if entity_id and entity_id.startswith('http://'):
                    entity_id = entity_id.split('/')[-1]
                print(f"   • '{ent['text']}' → {entity_id}")
        
        print()


def main():
    """Main function with argument parsing"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="View AIDA-YAGO2 named entity dataset in readable format"
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='Number of documents to display (default: 5)'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Path to AIDA-YAGO2-annotations.tsv file (auto-detected if not specified)'
    )
    
    args = parser.parse_args()
    
    # Auto-detect file path if not provided
    if args.file:
        tsv_path = Path(args.file)
    else:
        # Look in the expected location
        script_dir = Path(__file__).parent
        tsv_path = script_dir / "dataset_sources" / "aida-yago2-dataset (11)" / "aida-yago2-dataset" / "AIDA-YAGO2-annotations.tsv"
    
    if not tsv_path.exists():
        print(f"❌ Error: File not found at {tsv_path}")
        print(f"\nPlease specify the file location with --file")
        sys.exit(1)
    
    try:
        read_aida_tsv(tsv_path, limit=args.limit)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
