# NLP & Text Analytics Methodology

The SignalBrief analytics engine processes raw public articles into high-signal executive briefings through sequential deterministic and probabilistic stages.

## Analytical Flow

1. **Extraction & Sanitization**:
   - Trafilatura / BeautifulSoup extraction extracts article body text from raw HTML.
   - Language filtering (`langdetect`) retains only approved target languages (default: `en`).
   - Boilerplate, advertising phrases, and social sharing strings are stripped.
2. **Deduplication**:
   - Canonical URL matching.
   - SHA-256 body hashing for exact duplicates.
   - MinHash or character/token n-gram Jaccard similarity for near-duplicate syndications.
3. **Keyword & Relevance Scoring**:
   - Domain keyword matching with subtopic weighting.
   - Exclusion list negative scoring (filtering job ads and spam promotions).
   - Recency decay function penalizing older articles within the lookback window.
4. **Topic Clustering**:
   - TF-IDF or sentence transformer vectorization.
   - Agglomerative or DBSCAN clustering to identify dense themes without hardcoding cluster counts.
5. **Synthesis & Evidence Verification**:
   - Extraction of key factual claims.
   - Each claim must match an extracted sentence from source documents.
   - Formulation of the "What Changed, Why It Matters, What To Watch" triad.
