import re
import math
from collections import Counter, defaultdict
from typing import List, Tuple, Dict, Optional, Set, Union
import itertools

class Rouge:
    """
    Implementation of ROUGE (Recall-Oriented Understudy for Gisting Evaluation)
    Based on the original ROUGE paper by Chin-Yew Lin and ROUGE 2.0 extensions
    """
    
    def __init__(self, stopwords: Optional[Set[str]] = None, 
                 stemming: bool = False,
                 language: str = 'english'):
        """
        Initialize ROUGE evaluator
        
        Args:
            stopwords: Set of stopwords to exclude (if None, no stopwords removed)
            stemming: Whether to apply stemming to words
            language: Language for processing
        """
        self.stopwords = stopwords or set()
        self.stemming = stemming
        self.language = language
        
        # Porter stemmer (simplified version)
        if stemming:
            self.stemmer = self._porter_stemmer
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Simple tokenization - split on non-alphanumeric characters
        tokens = re.findall(r'\b\w+\b', text.lower())
        return [t for t in tokens if t not in self.stopwords]
    
    def _porter_stemmer(self, word: str) -> str:
        """Simplified Porter stemmer"""
        # This is a simplified version - in practice, use nltk or similar
        if word.endswith('sses'):
            word = word[:-2]
        elif word.endswith('ies'):
            word = word[:-2]
        elif word.endswith('ss'):
            word = word
        elif word.endswith('s'):
            word = word[:-1]
        
        # Additional stemming rules would go here
        return word
    
    def _stem(self, word: str) -> str:
        """Apply stemming if enabled"""
        if self.stemming:
            return self.stemmer(word)
        return word
    
    def _get_ngrams(self, tokens: List[str], n: int) -> Counter:
        """Generate n-grams from tokens"""
        if n < 1 or n > len(tokens):
            return Counter()
        
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i+n])
            ngrams.append(ngram)
        
        return Counter(ngrams)
    
    def _longest_common_subsequence(self, X: List[str], Y: List[str]) -> int:
        """Compute length of Longest Common Subsequence (LCS)"""
        m, n = len(X), len(Y)
        
        # Create DP table
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Fill DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if X[i-1] == Y[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    def _weighted_lcs(self, X: List[str], Y: List[str], alpha: float = 1.2) -> float:
        """
        Compute Weighted Longest Common Subsequence (WLCS)
        with weighting function f(k) = k^alpha
        """
        m, n = len(X), len(Y)
        
        # DP tables
        c = [[0.0] * (n + 1) for _ in range(m + 1)]  # WLCS score
        w = [[0] * (n + 1) for _ in range(m + 1)]  # length of consecutive matches
        
        # Weighting function
        def f(k: int) -> float:
            return k ** alpha if k > 0 else 0
        
        # Dynamic programming
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if X[i-1] == Y[j-1]:
                    k = w[i-1][j-1]
                    c[i][j] = c[i-1][j-1] + f(k + 1) - f(k)
                    w[i][j] = k + 1
                else:
                    if c[i-1][j] > c[i][j-1]:
                        c[i][j] = c[i-1][j]
                    else:
                        c[i][j] = c[i][j-1]
                    w[i][j] = 0
        
        return c[m][n]
    
    def _get_skip_bigrams(self, tokens: List[str], max_skip: Optional[int] = None) -> Counter:
        """Generate skip-bigrams from tokens"""
        n = len(tokens)
        skip_bigrams = []
        
        for i in range(n):
            for j in range(i + 1, n):
                if max_skip is None or (j - i - 1) <= max_skip:
                    skip_bigram = (tokens[i], tokens[j])
                    skip_bigrams.append(skip_bigram)
        
        return Counter(skip_bigrams)
    
    def _f_measure(self, recall: float, precision: float, beta: float = 1.0) -> float:
        """Compute F-measure given recall and precision"""
        if recall == 0 and precision == 0:
            return 0.0
        
        beta_sq = beta ** 2
        return (1 + beta_sq) * recall * precision / (recall + beta_sq * precision + 1e-10)
    
    def rouge_n(self, candidate: str, references: List[str], n: int = 1, 
                beta: float = 1.0, jackknife: bool = False) -> Dict[str, float]:
        """
        Compute ROUGE-N score
        
        Args:
            candidate: Candidate summary text
            references: List of reference summary texts
            n: N-gram order
            beta: Parameter controlling recall/precision balance
            jackknife: Whether to use jackknifing procedure
        
        Returns:
            Dictionary with recall, precision, and f1 scores
        """
        # Tokenize
        cand_tokens = [self._stem(t) for t in self._tokenize(candidate)]
        ref_tokens_list = [[self._stem(t) for t in self._tokenize(ref)] for ref in references]
        
        # Get n-grams
        cand_ngrams = self._get_ngrams(cand_tokens, n)
        
        if not jackknife or len(references) == 1:
            # Standard computation (max over references)
            best_score = {'recall': 0.0, 'precision': 0.0, 'f1': 0.0}
            
            for ref_tokens in ref_tokens_list:
                ref_ngrams = self._get_ngrams(ref_tokens, n)
                
                # Count matching n-grams
                match_count = sum((cand_ngrams & ref_ngrams).values())
                total_cand = sum(cand_ngrams.values())
                total_ref = sum(ref_ngrams.values())
                
                if total_ref == 0:
                    recall = 0.0
                else:
                    recall = match_count / total_ref
                
                if total_cand == 0:
                    precision = 0.0
                else:
                    precision = match_count / total_cand
                
                f1 = self._f_measure(recall, precision, beta)
                
                if f1 > best_score['f1']:
                    best_score = {'recall': recall, 'precision': precision, 'f1': f1}
            
            return best_score
        
        else:
            # Jackknifing procedure
            m = len(references)
            scores = []
            
            for i in range(m):
                # Leave one reference out
                ref_subset = ref_tokens_list[:i] + ref_tokens_list[i+1:]
                
                # Compute union of n-grams from remaining references
                union_ngrams = Counter()
                for ref_tokens in ref_subset:
                    union_ngrams.update(self._get_ngrams(ref_tokens, n))
                
                # Calculate scores
                match_count = sum((cand_ngrams & union_ngrams).values())
                total_cand = sum(cand_ngrams.values())
                total_ref = sum(union_ngrams.values())
                
                if total_ref == 0:
                    recall = 0.0
                else:
                    recall = match_count / total_ref
                
                if total_cand == 0:
                    precision = 0.0
                else:
                    precision = match_count / total_cand
                
                f1 = self._f_measure(recall, precision, beta)
                scores.append({'recall': recall, 'precision': precision, 'f1': f1})
            
            # Average the scores
            avg_recall = sum(s['recall'] for s in scores) / m
            avg_precision = sum(s['precision'] for s in scores) / m
            avg_f1 = sum(s['f1'] for s in scores) / m
            
            return {'recall': avg_recall, 'precision': avg_precision, 'f1': avg_f1}
    
    def rouge_l(self, candidate: str, references: List[str], 
                beta: float = 1.0, level: str = 'summary') -> Dict[str, float]:
        """
        Compute ROUGE-L score based on Longest Common Subsequence
        
        Args:
            candidate: Candidate summary text
            references: List of reference summary texts
            beta: Parameter controlling recall/precision balance
            level: 'sentence' or 'summary' level LCS
        
        Returns:
            Dictionary with recall, precision, and f1 scores
        """
        cand_tokens = [self._stem(t) for t in self._tokenize(candidate)]
        
        if level == 'sentence':
            # Sentence-level LCS (simplified - assuming single sentence)
            best_score = {'recall': 0.0, 'precision': 0.0, 'f1': 0.0}
            
            for ref in references:
                ref_tokens = [self._stem(t) for t in self._tokenize(ref)]
                
                lcs_len = self._longest_common_subsequence(cand_tokens, ref_tokens)
                
                recall = lcs_len / len(ref_tokens) if ref_tokens else 0.0
                precision = lcs_len / len(cand_tokens) if cand_tokens else 0.0
                f1 = self._f_measure(recall, precision, beta)
                
                if f1 > best_score['f1']:
                    best_score = {'recall': recall, 'precision': precision, 'f1': f1}
            
            return best_score
        
        else:  # summary level
            # For summary level, we need to handle multiple sentences
            # This is a simplified implementation
            best_score = {'recall': 0.0, 'precision': 0.0, 'f1': 0.0}
            
            for ref in references:
                ref_tokens = [self._stem(t) for t in self._tokenize(ref)]
                
                lcs_len = self._longest_common_subsequence(cand_tokens, ref_tokens)
                
                recall = lcs_len / len(ref_tokens) if ref_tokens else 0.0
                precision = lcs_len / len(cand_tokens) if cand_tokens else 0.0
                f1 = self._f_measure(recall, precision, beta)
                
                if f1 > best_score['f1']:
                    best_score = {'recall': recall, 'precision': precision, 'f1': f1}
            
            return best_score
    
    def rouge_w(self, candidate: str, references: List[str], 
                alpha: float = 1.2, beta: float = 1.0) -> Dict[str, float]:
        """
        Compute ROUGE-W score based on Weighted LCS
        
        Args:
            candidate: Candidate summary text
            references: List of reference summary texts
            alpha: Weighting parameter (for f(k) = k^alpha)
            beta: Parameter for F-measure
        
        Returns:
            Dictionary with recall, precision, and f1 scores
        """
        cand_tokens = [self._stem(t) for t in self._tokenize(candidate)]
        best_score = {'recall': 0.0, 'precision': 0.0, 'f1': 0.0}
        
        def f_inv(score: float) -> float:
            """Inverse function for f(k) = k^alpha"""
            return score ** (1/alpha) if score > 0 else 0.0
        
        for ref in references:
            ref_tokens = [self._stem(t) for t in self._tokenize(ref)]
            
            wlcs_score = self._weighted_lcs(cand_tokens, ref_tokens, alpha)
            m, n = len(ref_tokens), len(cand_tokens)
            
            recall = f_inv(wlcs_score) / m if m > 0 else 0.0
            precision = f_inv(wlcs_score) / n if n > 0 else 0.0
            f1 = self._f_measure(recall, precision, beta)
            
            if f1 > best_score['f1']:
                best_score = {'recall': recall, 'precision': precision, 'f1': f1}
        
        return best_score
    
    def rouge_s(self, candidate: str, references: List[str], 
                max_skip: Optional[int] = None, beta: float = 1.0) -> Dict[str, float]:
        """
        Compute ROUGE-S score based on skip-bigram co-occurrence
        
        Args:
            candidate: Candidate summary text
            references: List of reference summary texts
            max_skip: Maximum allowed skip distance (None for unlimited)
            beta: Parameter for F-measure
        
        Returns:
            Dictionary with recall, precision, and f1 scores
        """
        cand_tokens = [self._stem(t) for t in self._tokenize(candidate)]
        cand_skip_bigrams = self._get_skip_bigrams(cand_tokens, max_skip)
        
        best_score = {'recall': 0.0, 'precision': 0.0, 'f1': 0.0}
        
        for ref in references:
            ref_tokens = [self._stem(t) for t in self._tokenize(ref)]
            ref_skip_bigrams = self._get_skip_bigrams(ref_tokens, max_skip)
            
            # Count matching skip-bigrams
            match_count = sum((cand_skip_bigrams & ref_skip_bigrams).values())
            
            # Total possible skip-bigrams
            m, n = len(ref_tokens), len(cand_tokens)
            total_ref = m * (m - 1) // 2 if max_skip is None else sum(1 for i in range(m) for j in range(i+1, m) if j-i-1 <= max_skip)
            total_cand = n * (n - 1) // 2 if max_skip is None else sum(1 for i in range(n) for j in range(i+1, n) if j-i-1 <= max_skip)
            
            recall = match_count / total_ref if total_ref > 0 else 0.0
            precision = match_count / total_cand if total_cand > 0 else 0.0
            f1 = self._f_measure(recall, precision, beta)
            
            if f1 > best_score['f1']:
                best_score = {'recall': recall, 'precision': precision, 'f1': f1}
        
        return best_score
    
    def rouge_su(self, candidate: str, references: List[str], 
                 max_skip: Optional[int] = None, beta: float = 1.0) -> Dict[str, float]:
        """
        Compute ROUGE-SU score (skip-bigram + unigram)
        
        Args:
            candidate: Candidate summary text
            references: List of reference summary texts
            max_skip: Maximum allowed skip distance
            beta: Parameter for F-measure
        
        Returns:
            Dictionary with recall, precision, and f1 scores
        """
        # Add beginning of sentence marker
        candidate_with_bos = "<s> " + candidate
        references_with_bos = ["<s> " + ref for ref in references]
        
        # Compute ROUGE-S with the modified texts
        return self.rouge_s(candidate_with_bos, references_with_bos, max_skip, beta)
    
    def evaluate_all(self, candidate: str, references: List[str], 
                    rouge_n_params: List[int] = [1, 2, 3, 4],
                    rouge_s_params: List[Optional[int]] = [1, 4, 9, None]) -> Dict[str, Dict[str, float]]:
        """
        Compute all ROUGE metrics
        
        Args:
            candidate: Candidate summary text
            references: List of reference summary texts
            rouge_n_params: List of n values for ROUGE-N
            rouge_s_params: List of max_skip values for ROUGE-S
        
        Returns:
            Dictionary containing all ROUGE scores
        """
        results = {}
        
        # ROUGE-N variants
        for n in rouge_n_params:
            results[f'ROUGE-{n}'] = self.rouge_n(candidate, references, n=n)
        
        # ROUGE-L
        results['ROUGE-L'] = self.rouge_l(candidate, references)
        
        # ROUGE-W
        results['ROUGE-W'] = self.rouge_w(candidate, references, alpha=1.2)
        
        # ROUGE-S and ROUGE-SU variants
        for max_skip in rouge_s_params:
            if max_skip is not None:
                results[f'ROUGE-S{max_skip}'] = self.rouge_s(candidate, references, max_skip=max_skip)
                results[f'ROUGE-SU{max_skip}'] = self.rouge_su(candidate, references, max_skip=max_skip)
            else:
                results['ROUGE-S'] = self.rouge_s(candidate, references, max_skip=None)
                results['ROUGE-SU'] = self.rouge_su(candidate, references, max_skip=None)
        
        return results


class Rouge20(Rouge):
    """
    ROUGE 2.0 implementation with synonym support and topic-based evaluation
    Based on the ROUGE 2.0 paper by Kavita Ganesan
    """
    
    def __init__(self, synonym_dict: Optional[Dict[str, Set[str]]] = None,
                 pos_tagger = None, **kwargs):
        """
        Initialize ROUGE 2.0
        
        Args:
            synonym_dict: Dictionary mapping words to sets of synonyms
            pos_tagger: Part-of-speech tagger function
            **kwargs: Other parameters for base Rouge class
        """
        super().__init__(**kwargs)
        self.synonym_dict = synonym_dict or {}
        self.pos_tagger = pos_tagger
        
        # Create reverse synonym mapping
        self.reverse_synonym_dict = {}
        for word, synonyms in self.synonym_dict.items():
            for synonym in synonyms:
                if synonym not in self.reverse_synonym_dict:
                    self.reverse_synonym_dict[synonym] = set()
                self.reverse_synonym_dict[synonym].add(word)
    
    def _map_to_synonym(self, word: str) -> str:
        """Map word to its canonical synonym if available"""
        if word in self.synonym_dict:
            # Return the word itself (it's already canonical)
            return word
        elif word in self.reverse_synonym_dict:
            # Return first canonical synonym
            return next(iter(self.reverse_synonym_dict[word]))
        return word
    
    def rouge_n_synonyms(self, candidate: str, references: List[str], n: int = 1,
                        beta: float = 1.0) -> Dict[str, float]:
        """
        Compute ROUGE-N with synonym support
        
        Args:
            candidate: Candidate summary text
            references: List of reference summary texts
            n: N-gram order
            beta: Parameter for F-measure
        
        Returns:
            Dictionary with recall, precision, and f1 scores
        """
        # Tokenize and map to synonyms
        cand_tokens = [self._stem(self._map_to_synonym(t)) 
                      for t in self._tokenize(candidate)]
        ref_tokens_list = [[self._stem(self._map_to_synonym(t)) 
                          for t in self._tokenize(ref)] for ref in references]
        
        # Get n-grams
        cand_ngrams = self._get_ngrams(cand_tokens, n)
        best_score = {'recall': 0.0, 'precision': 0.0, 'f1': 0.0}
        
        for ref_tokens in ref_tokens_list:
            ref_ngrams = self._get_ngrams(ref_tokens, n)
            
            # Count matching n-grams
            match_count = sum((cand_ngrams & ref_ngrams).values())
            total_cand = sum(cand_ngrams.values())
            total_ref = sum(ref_ngrams.values())
            
            recall = match_count / total_ref if total_ref > 0 else 0.0
            precision = match_count / total_cand if total_cand > 0 else 0.0
            f1 = self._f_measure(recall, precision, beta)
            
            if f1 > best_score['f1']:
                best_score = {'recall': recall, 'precision': precision, 'f1': f1}
        
        return best_score
    
    def rouge_topic(self, candidate: str, references: List[str],
                   pos_tags: List[str] = ['NN', 'JJ'], use_unique: bool = False,
                   beta: float = 1.0) -> Dict[str, float]:
        """
        Compute ROUGE-Topic or ROUGE-TopicUniq score
        
        Args:
            candidate: Candidate summary text
            references: List of reference summary texts
            pos_tags: List of POS tags to consider as topics
            use_unique: If True, count unique topics (ROUGE-TopicUniq)
            beta: Parameter for F-measure
        
        Returns:
            Dictionary with recall, precision, and f1 scores
        """
        if not self.pos_tagger:
            raise ValueError("POS tagger is required for ROUGE-Topic")
        
        # Tokenize and get POS tags
        cand_tokens = self._tokenize(candidate)
        ref_tokens_list = [self._tokenize(ref) for ref in references]
        
        # Get topic words based on POS tags
        def get_topic_words(tokens: List[str]) -> List[str]:
            # This is a simplified version - in practice, use actual POS tagging
            # Here we assume all tokens are tagged as nouns for demonstration
            return [t for t in tokens if True]  # Simplified: all words are topics
        
        cand_topics = get_topic_words(cand_tokens)
        ref_topics_list = [get_topic_words(ref_tokens) for ref_tokens in ref_tokens_list]
        
        if use_unique:
            # ROUGE-TopicUniq: use sets of unique topics
            cand_set = set(cand_topics)
            best_score = {'recall': 0.0, 'precision': 0.0, 'f1': 0.0}
            
            for ref_topics in ref_topics_list:
                ref_set = set(ref_topics)
                intersection = cand_set & ref_set
                
                recall = len(intersection) / len(ref_set) if ref_set else 0.0
                precision = len(intersection) / len(cand_set) if cand_set else 0.0
                f1 = self._f_measure(recall, precision, beta)
                
                if f1 > best_score['f1']:
                    best_score = {'recall': recall, 'precision': precision, 'f1': f1}
            
            return best_score
        
        else:
            # ROUGE-Topic: use multisets (allow repetitions)
            cand_counter = Counter(cand_topics)
            best_score = {'recall': 0.0, 'precision': 0.0, 'f1': 0.0}
            
            for ref_topics in ref_topics_list:
                ref_counter = Counter(ref_topics)
                
                # Count matching topics (with multiplicity)
                match_count = sum((cand_counter & ref_counter).values())
                total_cand = sum(cand_counter.values())
                total_ref = sum(ref_counter.values())
                
                recall = match_count / total_ref if total_ref > 0 else 0.0
                precision = match_count / total_cand if total_cand > 0 else 0.0
                f1 = self._f_measure(recall, precision, beta)
                
                if f1 > best_score['f1']:
                    best_score = {'recall': recall, 'precision': precision, 'f1': f1}
            
            return best_score
    
    def evaluate_all_extended(self, candidate: str, references: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Compute all ROUGE 2.0 metrics
        
        Args:
            candidate: Candidate summary text
            references: List of reference summary texts
        
        Returns:
            Dictionary containing all ROUGE 2.0 scores
        """
        results = {}
        
        # Base ROUGE metrics
        base_results = super().evaluate_all(candidate, references)
        results.update(base_results)
        
        # ROUGE with synonyms
        for n in [1, 2]:
            results[f'ROUGE-{n}+Synonyms'] = self.rouge_n_synonyms(candidate, references, n=n)
        
        # ROUGE-Topic variants
        if self.pos_tagger:
            results['ROUGE-TopicNN-JJ'] = self.rouge_topic(candidate, references, pos_tags=['NN', 'JJ'])
            results['ROUGE-TopicUniqNN-JJ'] = self.rouge_topic(candidate, references, pos_tags=['NN', 'JJ'], use_unique=True)
            
            # With synonyms
            # Note: This would require combining synonym mapping with topic extraction
            # For simplicity, we compute base topic metrics here
        
        return results


# Example usage
def main():
    """Example usage of ROUGE implementation"""
    
    # Example from the ROUGE 2.0 paper
    candidate = "Lightweight phone. Bright screen. Screen is very clear."
    references = ["The phone is very lightweight. The display is also very bright and clear."]
    
    # Initialize basic ROUGE
    rouge = Rouge(stopwords={'the', 'is', 'very', 'also', 'and'}, stemming=False)
    
    # Compute various ROUGE scores
    print("Basic ROUGE Scores:")
    print("-" * 50)
    
    # ROUGE-1
    rouge1 = rouge.rouge_n(candidate, references, n=1)
    print(f"ROUGE-1: Recall={rouge1['recall']:.3f}, Precision={rouge1['precision']:.3f}, F1={rouge1['f1']:.3f}")
    
    # ROUGE-2
    rouge2 = rouge.rouge_n(candidate, references, n=2)
    print(f"ROUGE-2: Recall={rouge2['recall']:.3f}, Precision={rouge2['precision']:.3f}, F1={rouge2['f1']:.3f}")
    
    # ROUGE-L
    rouge_l = rouge.rouge_l(candidate, references)
    print(f"ROUGE-L: Recall={rouge_l['recall']:.3f}, Precision={rouge_l['precision']:.3f}, F1={rouge_l['f1']:.3f}")
    
    # ROUGE-S
    rouge_s = rouge.rouge_s(candidate, references, max_skip=4)
    print(f"ROUGE-S4: Recall={rouge_s['recall']:.3f}, Precision={rouge_s['precision']:.3f}, F1={rouge_s['f1']:.3f}")
    
    print("\n" + "=" * 50)
    print("All ROUGE Metrics:")
    print("=" * 50)
    
    # Compute all metrics
    all_scores = rouge.evaluate_all(candidate, references)
    for metric, scores in all_scores.items():
        print(f"{metric}: R={scores['recall']:.3f}, P={scores['precision']:.3f}, F1={scores['f1']:.3f}")
    
    # ROUGE 2.0 with synonyms
    print("\n" + "=" * 50)
    print("ROUGE 2.0 with Synonyms:")
    print("=" * 50)
    
    # Define synonyms (example: 'screen' and 'display' are synonyms)
    synonym_dict = {
        'screen': {'display', 'monitor'},
        'display': {'screen', 'monitor'},
        'phone': {'device', 'smartphone'},
        'lightweight': {'light', 'thin'}
    }
    
    rouge20 = Rouge20(synonym_dict=synonym_dict, 
                      stopwords={'the', 'is', 'very', 'also', 'and'})
    
    rouge1_syn = rouge20.rouge_n_synonyms(candidate, references, n=1)
    print(f"ROUGE-1+Synonyms: R={rouge1_syn['recall']:.3f}, P={rouge1_syn['precision']:.3f}, F1={rouge1_syn['f1']:.3f}")
    
    # Compare with and without synonyms
    print(f"\nComparison (ROUGE-1):")
    print(f"Without synonyms: F1={rouge1['f1']:.3f}")
    print(f"With synonyms: F1={rouge1_syn['f1']:.3f}")
    print(f"Improvement: {rouge1_syn['f1'] - rouge1['f1']:.3f}")


if __name__ == "__main__":
    main()