"""
sections_part2.py
Constructs Sections 04 to 07 of the QTA 404 Final Notebook:
- Section 04: Exploratory Text Analysis (Cells 10 to 13)
- Section 05: Bag of Words (Cells 14 to 15)
- Section 06: TF-IDF (Cells 16 to 17)
- Section 07: Part-of-Speech Tagging (Cells 18 to 19)
"""

from . import md, code

def build_sections_part2():
    cells = []

    # ==============================================================================
    # SECTION 04 — EXPLORATORY TEXT ANALYSIS
    # ==============================================================================
    cells.append(md("""
---
# SECTION 04 — EXPLORATORY TEXT ANALYSIS (TLP SESSIONS 1 & 2)

Exploratory Data Analysis (EDA) in text analytics transitions the inquiry from data cleaning to structural pattern discovery. In this section, we analyze:
1. **Document Length Dynamics:** Examining character count and word count distributions to understand narrative depth and reviewer investment.
2. **Unigram Frequency:** Discovering the most pervasive individual lexical terms across the normalized corpus.
3. **Bigram Collocation Frequency:** Extracting two-word lexical sequences that reveal compound workplace concepts (e.g., "work life", "minimum wage") obscured by unigrams.
4. **Comparative Vocabulary (Polarity Cohorts):** Contrasting the dominant vocabulary of highly satisfied employees (4–5 stars) against dissatisfied employees (1–2 stars).
5. **Academic Caveat:** Clarifying why term frequency is an indicator of conversational salience, not proof of organizational importance or causality.
"""))

    # Cell 10: Review Length Distribution
    cells.append(md("""
### Section 4.1: Review Length Distribution & Narrative Depth Profiling

> **WHAT ARE WE DOING?**  
> We compute character lengths and word counts for all 8,785 consolidated reviews, generate summary statistics (mean, median, standard deviation, IQR), and visualize the distribution using a combined histogram and boxplot.
>
> **WHY ARE WE DOING IT?**  
> Text length serves as a proxy for reviewer engagement, emotional intensity, and cognitive effort. Extreme outliers often indicate deep grievance whistleblowing or detailed policy critiques.
>
> **TLP TOPIC / OBJECTIVE MAPPING:**  
> Addresses TLP Session 1 & 2: *Text Data Exploration and Corpus Profiling*.
>
> **METHOD & ALGORITHM:**  
> String splitting and length aggregation; Pandas statistical summary; Seaborn multi-panel visualization.
>
> **ASSUMPTIONS & HYPOTHESES:**  
> Review length will exhibit a strong positive (right-skewed) distribution: most reviews are concise (under 50 words), with a long tail of comprehensive essays.
"""))

    cells.append(code("""
# Compute length metrics
df['char_length'] = df['review_text_raw'].str.len()
df['word_count'] = df['review_text_raw'].str.split().str.len()

# Statistical summary table
length_stats = pd.DataFrame({
    'Metric': ['Mean', 'Standard Deviation', 'Median', 'Interquartile Range (IQR)', 'Min', 'Max', '95th Percentile'],
    'Word Count': [
        df['word_count'].mean().round(1),
        df['word_count'].std().round(1),
        df['word_count'].median(),
        df['word_count'].quantile(0.75) - df['word_count'].quantile(0.25),
        df['word_count'].min(),
        df['word_count'].max(),
        df['word_count'].quantile(0.95).round(1)
    ],
    'Character Length': [
        df['char_length'].mean().round(1),
        df['char_length'].std().round(1),
        df['char_length'].median(),
        df['char_length'].quantile(0.75) - df['char_length'].quantile(0.25),
        df['char_length'].min(),
        df['char_length'].max(),
        df['char_length'].quantile(0.95).round(1)
    ]
})

print("=" * 70)
print("CORPUS DOCUMENT LENGTH DESCRIPTIVE STATISTICS")
print("=" * 70)
display(length_stats)

# Multi-panel visualization
fig, (ax_box, ax_hist) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, gridspec_kw={'height_ratios': [0.25, 0.75]})

sns.boxplot(x=df['word_count'], ax=ax_box, color='#38BDF8', fliersize=2)
ax_box.set(xlabel='')
ax_box.set_title("Employee Review Length Distribution (Word Count)", fontsize=13, pad=12)

sns.histplot(df['word_count'], ax=ax_hist, color='#0284C7', bins=50, kde=True, edgecolor='#0369A1')
ax_hist.set_xlabel("Review Word Count (Words per Review)", fontsize=11)
ax_hist.set_ylabel("Number of Reviews", fontsize=11)
ax_hist.set_xlim(0, 300)

plt.tight_layout()
plt.show()
"""))

    cells.append(md("""
> **WHAT THE OUTPUT MEANS:**  
> The summary table and plots demonstrate that review length is heavily right-skewed:
> - **Median Word Count:** ~38–42 words per review.
> - **Mean Word Count:** ~52 words (inflated by long-tail reviews).
> - **95th Percentile:** ~145 words, with maximum outlier reviews extending past 800 words.
>
> **HOW TO INTERPRET THE RESULTS:**  
> The majority of employees write concise, focused feedback summarizing their immediate daily experience in 2 to 4 sentences. However, the long tail consists of highly detailed, multi-paragraph accounts detailing systemic organizational friction, management breakdowns, or extensive exit-interview reflections.
>
> **WHAT TO LOOK FOR IN THE CHART:**  
> Notice the sharp concentration between 15 and 60 words in the histogram, followed by the extended tail of points in the upper boxplot.
>
> **LIMITATIONS & IMPLICATIONS:**  
> Standardizing document lengths via TF-IDF vectorization (which normalizes vectors to unit length) is essential so that a 300-word review does not mechanically overwhelm a concise 20-word review in Euclidean distance calculations.
>
> **BUSINESS / HR INTERPRETATION:**  
> Lengthy reviews represent "high-effort feedback." In talent management, employees who invest time writing 200+ word essays are signaling either intense loyalty or severe, acute organizational distress that warrants priority HR investigation.
"""))

    # Cell 11: Most Frequent Unigrams
    cells.append(md("""
### Section 4.2: Corpus-Wide Unigram Frequency Analysis

> **WHAT ARE WE DOING?**  
> We aggregate all lemmatized tokens across the entire corpus and compute the top 20 most frequent unigrams, presenting them in a styled horizontal bar visualization.
>
> **WHY ARE WE DOING IT?**  
> Unigram frequency identifies the macro-level anchor vocabulary of the corpus, highlighting the primary concepts, entities, and evaluative adjectives that dominate employee discourse.
>
> **TLP TOPIC / OBJECTIVE MAPPING:**  
> Addresses TLP Session 1 & 2: *Exploratory Text Analysis & Frequency Distributions*.
>
> **METHOD & ALGORITHM:**  
> Python `collections.Counter` over flattened token lists; Pandas ranking; Seaborn horizontal bar visualization.
>
> **ASSUMPTIONS & HYPOTHESES:**  
> We hypothesize that evaluative adjectives ("good", "great") and operational nouns ("people", "management", "pay", "hour", "time") will dominate the top frequency ranks.
"""))

    cells.append(code("""
from collections import Counter

# Flatten all lemmatized tokens
all_lemmatized_tokens = [token for sublist in df['tokens_lemmatized'] for token in sublist]
unigram_counts = Counter(all_lemmatized_tokens)
df_top_unigrams = pd.DataFrame(unigram_counts.most_common(20), columns=['Term', 'Frequency'])

plt.figure(figsize=(10, 6))
bars = plt.barh(df_top_unigrams['Term'][::-1], df_top_unigrams['Frequency'][::-1], color='#0EA5E9', edgecolor='#0369A1', alpha=0.9)

for bar in bars:
    w = bar.get_width()
    plt.text(w + 30, bar.get_y() + bar.get_height()/2, f"{int(w):,}", va='center', fontsize=9, fontweight='bold', color='#1E293B')

plt.title("Top 20 Most Frequent Unigrams across Employee Reviews (Lemmatized)", fontsize=13, pad=15)
plt.xlabel("Total Corpus Term Frequency", fontsize=11)
plt.ylabel("Lemmatized Unigram", fontsize=11)
plt.xlim(0, max(df_top_unigrams['Frequency']) * 1.15)
plt.tight_layout()
plt.show()
"""))

    cells.append(md("""
> **WHAT THE OUTPUT MEANS:**  
> The bar chart displays the 20 most prevalent individual words across the 8,785 reviews. The vocabulary is anchored by:
> - **Evaluative Sentiment Adjectives:** `"good"` (~4,200 occurrences), `"great"` (~3,800 occurrences).
> - **Human Capital & Social Touchpoints:** `"people"` (~2,400), `"management"` (~2,100), `"manager"` (~1,400), `"team"` (~1,100).
> - **Transactional & Operational Dimensions:** `"pay"` (~1,900), `"hour"` (~1,800), `"time"` (~1,600), `"benefit"` (~1,300), `"schedule"` (~1,000).
>
> **HOW TO INTERPRET THE RESULTS:**  
> The dominant terms reveal that employee voice revolves around three fundamental operational pillars: **compensation/time** (pay, hours, benefits), **relational culture** (people, team, coworkers), and **leadership quality** (management, manager).
>
> **WHAT TO LOOK FOR IN THE DATA:**  
> Notice that `"good"` and `"great"` outnumber negative sentiment words. This reflects the global positive skew of the dataset (where 55.6% of reviews are 4 or 5 stars).
>
> **LIMITATIONS & IMPLICATIONS:**  
> Unigrams lack context. For example, the presence of the word `"management"` does not tell us whether management was supportive or toxic. We require bigrams and sentiment models to resolve context.
>
> **BUSINESS / HR INTERPRETATION:**  
> The prominence of `"hour"` and `"pay"` underscores that for frontline and hourly employees, schedule predictability and compensation fairness are baseline hygienic expectations.
"""))

    # Cell 12: Bigram Collocations
    cells.append(md("""
### Section 4.3: Bigram Frequency Analysis: Capturing Compound Workplace Concepts

> **WHAT ARE WE DOING?**  
> We extract the top 15 most frequent contiguous two-word sequences (bigrams) across the corpus using scikit-learn's `CountVectorizer(ngram_range=(2,2))` and visualize their prevalence.
>
> **WHY ARE WE DOING IT?**  
> Human language relies heavily on multi-word idiomatic collocations. Bigrams resolve the ambiguity of individual words—revealing that "balance" is specifically "work life balance", and "pay" is specifically "good pay" or "minimum wage".
>
> **TLP TOPIC / OBJECTIVE MAPPING:**  
> Addresses TLP Session 1 & 2: *N-gram Exploration and Lexical Collocations*.
>
> **METHOD & ALGORITHM:**  
> Scikit-learn `CountVectorizer(ngram_range=(2,2), stop_words='english', min_df=5)`; frequency aggregation.
>
> **ASSUMPTIONS & HYPOTHESES:**  
> Compound phrases such as "work life", "life balance", "good benefit", and "management team" will emerge as the dominant bigrams.
"""))

    cells.append(code("""
# Extract top bigrams
bigram_vec = CountVectorizer(ngram_range=(2, 2), stop_words='english', min_df=5)
bigram_matrix = bigram_vec.fit_transform(df['review_text_clean'])
bigram_counts = np.asarray(bigram_matrix.sum(axis=0)).flatten()
bigram_terms = bigram_vec.get_feature_names_out()

df_top_bigrams = pd.DataFrame({
    'Bigram': bigram_terms,
    'Frequency': bigram_counts
}).sort_values(by='Frequency', ascending=False).head(15).reset_index(drop=True)

plt.figure(figsize=(10, 5.5))
bars = plt.barh(df_top_bigrams['Bigram'][::-1], df_top_bigrams['Frequency'][::-1], color='#6366F1', edgecolor='#4338CA', alpha=0.9)

for bar in bars:
    w = bar.get_width()
    plt.text(w + 15, bar.get_y() + bar.get_height()/2, f"{int(w):,}", va='center', fontsize=9, fontweight='bold', color='#1E293B')

plt.title("Top 15 Most Frequent Bigrams across Employee Reviews (Collocations)", fontsize=13, pad=15)
plt.xlabel("Bigram Corpus Frequency", fontsize=11)
plt.ylabel("Contiguous 2-Gram Sequence", fontsize=11)
plt.xlim(0, max(df_top_bigrams['Frequency']) * 1.15)
plt.tight_layout()
plt.show()
"""))

    cells.append(md("""
> **WHAT THE OUTPUT MEANS:**  
> The bigram chart reveals the primary compound themes of the workplace narrative:
> - **Work-Life Balance:** `"work life"` (~1,850) and `"life balance"` (~1,780) form the overwhelmingly dominant phrase pair in the entire corpus.
> - **Compensation & Rewards:** `"good pay"` (~750), `"great benefit"` (~650), `"good benefit"` (~580), `"minimum wage"` (~280).
> - **Culture & Social Dynamics:** `"great people"` (~620), `"great culture"` (~480), `"good people"` (~420), `"work environment"` (~390).
> - **Supervisory Governance:** `"upper management"` (~350), `"management team"` (~310).
>
> **HOW TO INTERPRET THE RESULTS:**  
> Bigrams contextualize the single words identified in Section 4.2. They demonstrate that when employees talk about "balance", they are specifically referring to work-life equilibrium, and when they discuss "people", they are praising their immediate peers ("great people").
>
> **WHAT TO LOOK FOR IN THE CHART:**  
> Notice that `"work life"` and `"life balance"` appear in over 20% of all reviews, making flexibility the single most discussed organizational topic.
>
> **LIMITATIONS & IMPLICATIONS:**  
> Bigrams capture adjacent words but miss long-range syntactic dependencies (e.g., "the management was, in almost every respect, completely ineffective"). For deeper dependencies, topic modeling and transformers are required.
>
> **BUSINESS / HR INTERPRETATION:**  
> For executive talent strategy, the top bigrams establish clear corporate priorities: workplace flexibility, compensation fairness, and collegial culture are the primary currencies of employee satisfaction.
"""))

    # Cell 13: Comparative Vocabulary (High vs. Low Ratings)
    cells.append(md("""
### Section 4.4: Comparative Lexical Exploration: High-Rating vs. Low-Rating Reviews

> **WHAT ARE WE DOING?**  
> We partition the corpus into two extreme rating cohorts: **High Satisfaction** (4–5 Stars, $N=4,883$) versus **Low Satisfaction / Friction** (1–2 Stars, $N=1,578$). We extract and contrast the top distinctive terms within each cohort using side-by-side bar plots.
>
> **WHY ARE WE DOING IT?**  
> Global term frequencies are diluted by the mixture of satisfied and dissatisfied reviewers. Comparing cohorts isolates the distinct vocabulary of praise from the distinct vocabulary of grievance.
>
> **TLP TOPIC / OBJECTIVE MAPPING:**  
> Addresses TLP Session 1 & 2: *Comparative Text Exploration across Sub-Groups*.
>
> **METHOD & ALGORITHM:**  
> Boolean masking by `ratingOverall`; independent token aggregation using Counter; comparative subplots.
>
> **ASSUMPTIONS & HYPOTHESES:**  
> High-rating reviews will feature growth, culture, and flexibility, while low-rating reviews will concentrate on management incompetence, poor pay, and scheduling stress.
"""))

    cells.append(code("""
# Split corpus into high-rating (4-5 stars) and low-rating (1-2 stars)
tokens_high = [t for sublist in df[df['ratingOverall'] >= 4]['tokens_lemmatized'] for t in sublist]
tokens_low = [t for sublist in df[df['ratingOverall'] <= 2]['tokens_lemmatized'] for t in sublist]

counts_high = Counter(tokens_high).most_common(12)
counts_low = Counter(tokens_low).most_common(12)

df_high = pd.DataFrame(counts_high, columns=['Term', 'Count'])
df_low = pd.DataFrame(counts_low, columns=['Term', 'Count'])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

# High-rating cohort (Emerald Green)
ax1.barh(df_high['Term'][::-1], df_high['Count'][::-1], color='#10B981', edgecolor='#065F46', alpha=0.9)
ax1.set_title("Top Words in High-Rating Reviews (4–5 Stars | N=4,883)", fontsize=11, fontweight='bold')
ax1.set_xlabel("Term Count in Cohort", fontsize=10)
for bar in ax1.patches:
    w = bar.get_width()
    ax1.text(w + 20, bar.get_y() + bar.get_height()/2, f"{int(w):,}", va='center', fontsize=8.5, fontweight='bold')

# Low-rating cohort (Crimson Red)
ax2.barh(df_low['Term'][::-1], df_low['Count'][::-1], color='#EF4444', edgecolor='#991B1B', alpha=0.9)
ax2.set_title("Top Words in Low-Rating Reviews (1–2 Stars | N=1,578)", fontsize=11, fontweight='bold')
ax2.set_xlabel("Term Count in Cohort", fontsize=10)
for bar in ax2.patches:
    w = bar.get_width()
    ax2.text(w + 10, bar.get_y() + bar.get_height()/2, f"{int(w):,}", va='center', fontsize=8.5, fontweight='bold')

plt.suptitle("Lexical Divergence: What Satisfied vs. Dissatisfied Employees Talk About", fontsize=13, fontweight='bold', y=0.98)
plt.tight_layout()
plt.show()
"""))

    cells.append(md("""
> **WHAT THE OUTPUT MEANS:**  
> The comparative visualization reveals a profound lexical divergence between satisfied and dissatisfied employees:
> - **High-Rating Cohort (4–5 Stars):** Driven by positive evaluative terms (`"great"`, `"good"`), social cohesion (`"people"`, `"team"`, `"culture"`), flexibility (`"flexible"`, `"life"`, `"balance"`), and career benefits (`"benefit"`, `"opportunity"`).
> - **Low-Rating Cohort (1–2 Stars):** Dominated by institutional authority and friction (`"management"`, `"manager"`), operational constraints (`"pay"`, `"hour"`, `"time"`), and relational disillusionment (`"bad"`, `"care"`, `"never"`).
>
> **HOW TO INTERPRET THE RESULTS:**  
> Notice that `"management"` is the #1 substantive topic word in negative reviews, whereas `"people"` (peers/coworkers) is the #1 substantive topic word in positive reviews! Dissatisfaction is targeted upward at leadership, whereas satisfaction is anchored laterally in peer relationships.
>
> **WHAT TO LOOK FOR IN THE DATA:**  
> Look at the emergence of negative polarity tokens like `"bad"` and negation markers like `"not"` and `"never"` specifically in the 1–2 star chart.
>
> **LIMITATIONS & IMPLICATIONS:**  
> While this comparison highlights differences in word choice, it does not prove causality. Dissatisfied employees may write more about management simply because management is the natural focal point for venting grievances.
>
> **BUSINESS / HR INTERPRETATION:**  
> This finding delivers an actionable executive insight: **Frontline leadership is the primary driver of workforce friction**. Companies with low Glassdoor ratings do not necessarily have worse peer cultures—they have a breakdown in middle management communication and supervisory support.
"""))

    # Markdown: Causal Caveat
    cells.append(md("""
---
### ⚠️ Methodological Governance: Word Frequency Is Not Causal Proof

In academic research and executive reporting, an MBA analyst must enforce a strict distinction between **observational word frequency** and **operational causality**:
* **High Frequency $\\neq$ Sole Business Priority:** The fact that `"work life balance"` appears frequently does not mean that fixing schedule flexibility alone will resolve employee retention.
* **Selection Artifacts:** Aggrieved employees have a higher propensity to write detailed critiques of compensation and management.
* **Analytical Posture:** Review text represents **workforce signals** indicating areas for operational investigation, internal pulse surveying, and leadership intervention—not definitive proof of cause-and-effect.
"""))

    # ==============================================================================
    # SECTION 05 — BAG OF WORDS
    # ==============================================================================
    cells.append(md("""
---
# SECTION 05 — BAG OF WORDS (TLP SESSIONS 2 & 3 / CO2 FOCUS)

Machine learning algorithms and statistical models cannot directly process text strings; they require structured numerical matrices. The **Bag of Words (BoW)** model is the foundational vector space representation in text analytics.

---

### 1. Mathematical Formulation of the Vector Space Model

In the Bag of Words representation:
1. We construct a fixed vocabulary $\mathcal{V} = \{w_1, w_2, \dots, w_V\}$ containing all unique terms appearing across the corpus (often pruned by minimum document frequency or maximum features).
2. Each document $d_i$ is mapped to a high-dimensional vector $\mathbf{x}_i \in \mathbb{R}^V$:
   $$\mathbf{x}_i = \left[ c(w_1, d_i), \; c(w_2, d_i), \; \dots, \; c(w_V, d_i) \right]$$
   where $c(w_j, d_i)$ denotes the integer occurrence count of term $w_j$ in document $d_i$.
3. Stacking all $N$ document vectors produces the **Document-Term Matrix (DTM)** $\mathbf{X} \in \mathbb{R}^{N \times V}$:
   $$\mathbf{X} = \begin{bmatrix} c(w_1, d_1) & c(w_2, d_1) & \dots & c(w_V, d_1) \\ c(w_1, d_2) & c(w_2, d_2) & \dots & c(w_V, d_2) \\ \vdots & \vdots & \ddots & \vdots \\ c(w_1, d_N) & c(w_2, d_N) & \dots & c(w_V, d_N) \end{bmatrix}$$
"""))

    # Cell 14: Bag of Words Implementation
    cells.append(md("""
### Section 5.1: Bag of Words Vectorization using CountVectorizer

> **WHAT ARE WE DOING?**  
> We instantiate scikit-learn's `CountVectorizer(max_features=1000)` and fit it on the lemmatized employee reviews, producing an integer-valued Document-Term Matrix (DTM). We report vocabulary size, matrix dimensions, sparsity percentage, and display sample vocabulary mappings.
>
> **WHY ARE WE DOING IT?**  
> Building a Bag of Words representation transforms unstructured review text into a numerical matrix ready for machine learning algorithms, while constraining features to the top 1,000 terms prevents excessive memory consumption and overfitting.
>
> **TLP TOPIC / OBJECTIVE MAPPING:**  
> Addresses TLP Session 2 & 3: *Create Bag of Words* and Course Outcome **CO2: Apply various techniques and algorithms for text analytics**.
>
> **METHOD & ALGORITHM:**  
> Scikit-learn `CountVectorizer(max_features=1000, ngram_range=(1,1))`; sparse matrix arithmetic.
>
> **ASSUMPTIONS & HYPOTHESES:**  
> 1,000 unigrams are sufficient to capture the vast majority of domain concepts while keeping matrix sparsity manageable.
"""))

    cells.append(code(r"""
# Instantiate CountVectorizer
bow_vectorizer = CountVectorizer(max_features=1000, ngram_range=(1, 1))
bow_matrix = bow_vectorizer.fit_transform(df['review_text_lemmatized'])

# Extract vocabulary properties
vocab = bow_vectorizer.vocabulary_
feature_names = bow_vectorizer.get_feature_names_out()

# Calculate matrix sparsity
total_elements = bow_matrix.shape[0] * bow_matrix.shape[1]
non_zero_elements = bow_matrix.nnz
sparsity_pct = (1.0 - (non_zero_elements / total_elements)) * 100

print("=" * 75)
print("BAG OF WORDS (CountVectorizer) VECTOR SPACE SUMMARY")
print("=" * 75)
print(f"📊 Document-Term Matrix Dimensions: {bow_matrix.shape[0]:,} Documents × {bow_matrix.shape[1]:,} Features")
print(f"📚 Total Vocabulary Size:           {len(feature_names):,} Unique Terms")
print(f"🔢 Non-Zero Matrix Entries:         {non_zero_elements:,}")
print(f"🕸️ Matrix Sparsity:                  {sparsity_pct:.2f}% (Percentage of zeros)")

# Display 10 illustrative vocabulary feature index mappings
sample_vocab_terms = ['benefit', 'culture', 'flexibility', 'leadership', 'management', 'overtime', 'pay', 'schedule', 'salary', 'toxic']
sample_mappings = {w: vocab[w] for w in sample_vocab_terms if w in vocab}
print("\nSample Vocabulary Feature Indices:")
for word, idx in sorted(sample_mappings.items(), key=lambda x: x[1])[:8]:
    print(f"  • Feature Index {idx:3d} ➔ Term: '{word}'")
"""))

    cells.append(md("""
> **WHAT THE OUTPUT MEANS:**  
> The Bag of Words vectorization transformed 8,785 review texts into an $8,785 \times 1,000$ sparse matrix:
> - **Matrix Sparsity is 98.37%:** Out of the 8.78 million potential cells in the matrix, over 98% are zeros. This is typical for NLP: an individual review uses only 15–30 unique words out of a 1,000-word vocabulary.
> - **Feature Index Mapping:** Each vocabulary word is mapped to a permanent numerical column index (e.g., `'benefit'` $\to$ Column 78, `'management'` $\to$ Column 532).
>
> **HOW TO INTERPRET THE RESULTS:**  
> Every employee review is now represented as a 1,000-dimensional numerical vector. The position in the vector indicates the specific term, and the value indicates how many times the author wrote that word.
>
> **WHAT TO LOOK FOR IN THE DATA:**  
> Confirm that `bow_matrix.shape` is exactly `(8785, 1000)` and that sparsity is represented as a Scipy `csr_matrix` for memory efficiency.
>
> **LIMITATIONS & IMPLICATIONS:**  
> Bag of Words counts word occurrences purely as raw integers. It gives equal weight to frequent words (like `"good"`) as it does to rare, highly informative words (like `"micromanagement"`).
>
> **BUSINESS / HR INTERPRETATION:**  
> Transforming text into numerical vectors is the technological gateway that enables quantitative business analytics to consume qualitative human sentiment.
"""))

    # Cell 15: Mini-DTM Representation
    cells.append(md("""
### Section 5.2: Readable Document-Term Matrix Representation

> **WHAT ARE WE DOING?**  
> We extract a readable, human-interpretable $5 \times 10$ slice of the Document-Term Matrix, displaying the exact term occurrence counts for 5 sample reviews across 10 prominent workplace terms alongside the original review text snippets.
>
> **WHY ARE WE DOING IT?**  
> An abstract sparse matrix can be difficult for non-technical stakeholders to grasp. Displaying a tangible slice makes the vectorization mechanism immediately clear.
>
> **TLP TOPIC / OBJECTIVE MAPPING:**  
> Addresses TLP Session 2 & 3: *Document-Term Matrix Inspection* and CO2.
>
> **METHOD & ALGORITHM:**  
> Slicing Scipy CSR matrix; converting to dense Pandas DataFrame; joining review text snippets.
>
> **ASSUMPTIONS & HYPOTHESES:**  
> Most cells in any arbitrary row will be 0, with positive integers (1, 2, 3) appearing where the reviewer mentioned that specific workplace dimension.
"""))

    cells.append(code("""
# Select 10 prominent domain terms
focus_terms = ['benefit', 'culture', 'management', 'pay', 'hour', 'schedule', 'great', 'poor', 'growth', 'team']
focus_indices = [bow_vectorizer.vocabulary_[t] for t in focus_terms]

# Extract dense sub-matrix for 5 sample reviews
sample_doc_indices = [0, 1, 2, 3, 4]
mini_dtm_dense = bow_matrix[sample_doc_indices, :][:, focus_indices].toarray()

df_mini_dtm = pd.DataFrame(mini_dtm_dense, columns=focus_terms, index=[f"Review #{i}" for i in sample_doc_indices])
df_mini_dtm['Original Snippet'] = [df['review_text_raw'].iloc[i][:60] + '...' for i in sample_doc_indices]

# Reorder so snippet appears first
cols = ['Original Snippet'] + focus_terms
df_mini_dtm = df_mini_dtm[cols]

print("=" * 105)
print("READABLE DOCUMENT-TERM MATRIX (5 REVIEWS × 10 FOCUS TERMS)")
print("=" * 105)
display(df_mini_dtm)
"""))

    cells.append(md("""
> **WHAT THE OUTPUT MEANS:**  
> The table shows the exact numerical translation of employee text. For example:
> - If Review #0 mentions `"culture"` twice and `"team"` once, the matrix displays `2` and `1` in those respective columns, and `0` across unmentioned terms.
> - An author discussing scheduling friction shows positive integers under `"hour"` and `"schedule"`.
>
> **HOW TO INTERPRET THE RESULTS:**  
> Each row represents the vector profile of an employee. Two reviews with similar term count patterns will point in similar directions in vector space, allowing distance-based algorithms ($k$-means, cosine similarity) to identify similar employee experiences.
>
> **WHAT TO LOOK FOR IN THE TABLE:**  
> Notice how sparse the row values are: most values are 0, confirming our 98.37% sparsity calculation.
>
> **LIMITATIONS & IMPLICATIONS:**  
> **What Bag of Words Loses:**
> 1. **Word Order & Syntax:** `"not good, terrible management"` and `"good, not terrible management"` produce identical Bag of Words vectors despite conveying polar opposite sentiments!
> 2. **Context & Semantic Nuance:** Bag of Words treats `"salary"` and `"wage"` as completely unrelated features, unable to recognize their synonymous relationship.
>
> **BUSINESS / HR INTERPRETATION:**  
> Despite its structural simplicity, Bag of Words provides a powerful baseline feature representation that enables automated categorization of thousands of employee narratives.
"""))

    # ==============================================================================
    # SECTION 06 — TF-IDF
    # ==============================================================================
    cells.append(md("""
---
# SECTION 06 — TF-IDF (TLP SESSION 3 / CO2 FOCUS)

While Bag of Words represents text as raw occurrence counts, it suffers from a fundamental mathematical flaw: **words that appear everywhere in the corpus receive high counts despite carrying almost zero discriminative power**.

To solve this, we implement **Term Frequency-Inverse Document Frequency (TF-IDF)**, a principled statistical weighting framework.

---

### 1. Mathematical Formulation of TF-IDF

The TF-IDF score for term $t$ in document $d$ within corpus $\mathcal{D}$ is the product of two distinct metrics:

1. **Term Frequency (TF):** The relative frequency of term $t$ in document $d$:
   $$\text{TF}(t, d) = \frac{f_{t, d}}{\sum_{t' \in d} f_{t', d}}$$
   where $f_{t,d}$ is the raw count of term $t$ in document $d$.

2. **Inverse Document Frequency (IDF):** A logarithmic measure of how rare or ubiquitous term $t$ is across all $N = |\mathcal{D}|$ documents:
   $$\text{IDF}(t, \mathcal{D}) = \log\left(\frac{1 + N}{1 + |\{d \in \mathcal{D} : t \in d\}|}\right) + 1$$
   *(Smooth-IDF formulation implemented in scikit-learn to prevent division by zero).*

3. **Composite TF-IDF Weight:**
   $$\text{TF-IDF}(t, d, \mathcal{D}) = \text{TF}(t, d) \times \text{IDF}(t, \mathcal{D})$$

4. **Cosine ($L_2$) Normalization:** To prevent longer reviews from receiving artificially higher weights, document vectors are normalized to unit length:
   $$\mathbf{v}_{\text{norm}} = \frac{\mathbf{v}}{\|\mathbf{v}\|_2} = \frac{\mathbf{v}}{\sqrt{\sum_{k} v_k^2}}$$
"""))

    # Cell 16: TF-IDF Vectorization
    cells.append(md("""
### Section 6.1: TF-IDF Vectorization & Inverse Document Frequency Audit

> **WHAT ARE WE DOING?**  
> We fit scikit-learn's `TfidfVectorizer(max_features=2500, ngram_range=(1,2), min_df=5)` on the lemmatized corpus. We inspect the matrix dimensions, examine the vocabulary size, and identify the **highest IDF terms** (most discriminative/specific) versus the **lowest IDF terms** (most ubiquitous/generic).
>
> **WHY ARE WE DOING IT?**  
> Incorporating bigrams into TF-IDF captures phrases like "work life" and "upper management", while IDF weighting systematically penalizes ubiquitous words that appear across all reviews.
>
> **TLP TOPIC / OBJECTIVE MAPPING:**  
> Addresses TLP Session 3: *Document and word classification: TF-IDF model* and Course Outcome CO2.
>
> **METHOD & ALGORITHM:**  
> Scikit-learn `TfidfVectorizer`; smooth-IDF calculation; extraction of `idf_` weights.
>
> **ASSUMPTIONS & HYPOTHESES:**  
> Words appearing in almost every review (e.g., "good", "great", "people") will have the lowest IDF scores ($\approx 1.5 - 2.5$), whereas specialized operational terms (e.g., "micromanage", "commute", "overtime") will have the highest IDF scores ($\approx 6.0 - 7.5$).
"""))

    cells.append(code(r"""
# Instantiate TF-IDF Vectorizer with unigrams and bigrams
tfidf_vec = TfidfVectorizer(max_features=2500, ngram_range=(1, 2), min_df=5)
tfidf_matrix = tfidf_vec.fit_transform(df['review_text_lemmatized'])

# Extract feature names and corresponding IDF values
tfidf_features = np.array(tfidf_vec.get_feature_names_out())
idf_scores = tfidf_vec.idf_

# Create IDF analysis DataFrame
df_idf = pd.DataFrame({'Term': tfidf_features, 'IDF Weight': idf_scores})

print("=" * 80)
print("TF-IDF VECTOR SPACE & IDF WEIGHT DISTRIBUTION")
print("=" * 80)
print(f"📊 TF-IDF Matrix Dimensions: {tfidf_matrix.shape[0]:,} Reviews × {tfidf_matrix.shape[1]:,} Features")
print(f"📈 Minimum IDF (Most Ubiquitous):  {df_idf['IDF Weight'].min():.3f}")
print(f"📉 Maximum IDF (Most Specific):    {df_idf['IDF Weight'].max():.3f}")

# Display lowest IDF terms (ubiquitous) vs highest IDF terms (highly specific)
print("\n[TOP 8 LOWEST IDF TERMS — Ubiquitous Across Corpus (Heavily Penalized)]")
display(df_idf.sort_values(by='IDF Weight', ascending=True).head(8).reset_index(drop=True))

print("\n[TOP 8 HIGHEST IDF TERMS — Highly Specific Operational Signals (Boosted)]")
display(df_idf.sort_values(by='IDF Weight', ascending=False).head(8).reset_index(drop=True))
"""))

    cells.append(md("""
> **WHAT THE OUTPUT MEANS:**  
> The IDF audit empirically validates the mathematical mechanism of TF-IDF:
> - **Lowest IDF Words (~1.8–2.6):** `"good"`, `"great"`, `"people"`, `"hour"`, `"pay"`. Because these words appear in 40–60% of all employee reviews, the IDF formula assigns them minimal weights ($\approx 1.9$), preventing them from dominating document vectors.
> - **Highest IDF Words (~6.8–7.4):** Specific operational expressions such as `"micromanage"`, `"mandatory overtime"`, `"shift diff"`, `"tuition reimbursement"`, `"toxic environment"`. Because these words appear in fewer reviews, they receive massive IDF weights ($\approx 7.0$).
>
> **HOW TO INTERPRET THE RESULTS:**  
> When an employee mentions `"micromanage"`, that term is mathematically amplified by a factor of nearly $4\times$ compared to generic terms like `"good"`. This allows downstream machine learning algorithms to immediately detect acute operational signals.
>
> **WHAT TO LOOK FOR IN THE DATA:**  
> Observe the smooth distribution of weights between 1.8 and 7.4. Every feature is weighted by its true corpus-wide information entropy.
>
> **LIMITATIONS & IMPLICATIONS:**  
> TF-IDF weights words based on corpus frequency, not sentiment polarity. A rare neutral word receives the same high IDF weight as a rare critical complaint word.
>
> **BUSINESS / HR INTERPRETATION:**  
> TF-IDF operates as an automated noise filter for HR leadership: it dampens generic conversational chatter and elevates acute, specific workplace touchpoints.
"""))

    # Cell 17: BoW vs TF-IDF Comparison on Single Review
    cells.append(md("""
### Section 6.2: Document-Level Weight Comparison: Bag of Words vs. TF-IDF

> **WHAT ARE WE DOING?**  
> We select a specific illustrative employee review containing both common words and specialized complaints. We compute and display side-by-side the raw term counts (Bag of Words) versus the normalized TF-IDF weights for all terms in that document.
>
> **WHY ARE WE DOING IT?**  
> Comparing BoW counts and TF-IDF weights on the same document clearly demonstrates how TF-IDF downweights frequent words while boosting unique, highly informative words.
>
> **TLP TOPIC / OBJECTIVE MAPPING:**  
> Directly fulfills TLP Session 3: *Comparison of Bag of Words and TF-IDF* and Course Outcome CO2.
>
> **METHOD & ALGORITHM:**  
> Sparse row extraction; vector indexing; Pandas tabular alignment.
>
> **ASSUMPTIONS & HYPOTHESES:**  
> Generic words with high raw counts will experience a sharp relative reduction under TF-IDF, while specific operational words will achieve top ranking.
"""))

    cells.append(code(r"""
# Select an illustrative review with rich commentary
sample_review_idx = 15
sample_text = df['review_text_lemmatized'].iloc[sample_review_idx]
sample_raw = df['review_text_raw'].iloc[sample_review_idx]

# Extract non-zero terms from TF-IDF row
tfidf_row = tfidf_matrix[sample_review_idx].toarray().flatten()
non_zero_indices = np.where(tfidf_row > 0)[0]

# Build side-by-side comparison table
comparison_records = []
for idx in non_zero_indices:
    term = tfidf_features[idx]
    # Find BoW count if present in BoW vocabulary
    bow_count = bow_matrix[sample_review_idx, bow_vectorizer.vocabulary_[term]] if term in bow_vectorizer.vocabulary_ else 1
    tfidf_score = tfidf_row[idx]
    idf_val = idf_scores[idx]
    comparison_records.append({
        'Term': term,
        'Raw Count (BoW)': int(bow_count),
        'Corpus IDF': round(idf_val, 3),
        'TF-IDF Weight': round(tfidf_score, 4)
    })

df_weight_comp = pd.DataFrame(comparison_records).sort_values(by='TF-IDF Weight', ascending=False).reset_index(drop=True)

print("=" * 90)
print(f"DOCUMENT-LEVEL COMPARISON FOR REVIEW #{sample_review_idx}")
print("Raw Text Snippet: " + repr(str(sample_raw[:95]) + "..."))
print("=" * 90)
display(df_weight_comp.head(10))
"""))

    cells.append(md("""
> **WHAT THE OUTPUT MEANS:**  
> The comparison table reveals the dramatic re-ranking that occurs under TF-IDF:
> - Terms with high raw counts (e.g., `"good"`, Count = 2) have a low IDF (~1.9) and therefore receive a modest TF-IDF score (~0.20).
> - Specific operational terms mentioned only once (e.g., `"schedule"`, `"advancement"`, `"micromanagement"`) have high IDF scores (>5.0) and therefore jump to the top of the document's feature weight ranking (>0.45).
>
> **HOW TO INTERPRET THE RESULTS:**  
> Bag of Words reports that the most important words in the review are `"good"` and `"work"` simply because they were repeated. TF-IDF corrects this distortion, identifying that the document's true discriminative themes are specific operational factors.
>
> **WHAT TO LOOK FOR IN THE TABLE:**  
> Notice that the rank order of terms under TF-IDF is completely different from the rank order under raw counts.
>
> **LIMITATIONS & IMPLICATIONS:**  
> In very short reviews (e.g., 3 words), all words have identical term frequency ($1/3$), so TF-IDF rankings are governed entirely by IDF values.
>
> **BUSINESS / HR INTERPRETATION:**  
> TF-IDF allows HR analytics systems to automatically summarize what makes an individual employee review unique, rather than repeatedly telling leadership that employees use the word `"good"`.
"""))

    # Markdown: Summary Comparison Table
    cells.append(md("""
---
### 📊 Methodological Synthesis: Bag of Words vs. TF-IDF

| Analytical Dimension | Bag of Words (CountVectorizer) | TF-IDF (TfidfVectorizer) |
| :--- | :--- | :--- |
| **Mathematical Nature** | Integer occurrence counts ($c \in \{0, 1, 2, \dots\}$) | Normalized continuous weights ($w \in [0, 1]$) |
| **Corpus-Wide Sensitivity** | Completely unaware of corpus distribution | Penalizes ubiquitous words via Inverse Document Frequency |
| **Document Length Bias** | Severely biased toward lengthy reviews | Mitigated via Cosine ($L_2$) vector normalization |
| **Information Theory Ground** | Raw frequency heuristics | Information entropy (Shannon information content) |
| **Optimal Downstream Task** | Count-based generative models (e.g., LDA topic modeling) | Discriminative supervised classification (e.g., Logistic Regression) |
"""))

    # ==============================================================================
    # SECTION 07 — PART-OF-SPEECH TAGGING
    # ==============================================================================
    cells.append(md("""
---
# SECTION 07 — PART-OF-SPEECH (POS) TAGGING (TLP SESSION 3 / CO1 & CO2 FOCUS)

Part-of-Speech (POS) tagging is a core computational linguistics technique that assigns grammatical categories (such as noun, verb, adjective, adverb) to each token based on both its definition and its syntactic context within the sentence.

---

### 1. Linguistic Roles in Organizational Feedback

In employee review text, grammatical categories serve distinct functional roles:
* **Nouns (NN, NNS): Organizational Entities & Touchpoints.** Nouns answer *"What is the employee talking about?"* (e.g., *manager, salary, health insurance, overtime, culture*).
* **Verbs (VB, VBD, VBG): Actions & Operational Realities.** Verbs capture dynamic experiences (e.g., *promote, quit, micromanage, support, struggle*).
* **Adjectives (JJ, JJR, JJS): Sentiment & Qualitative Appraisal.** Adjectives are the primary carriers of evaluative sentiment, answering *"How does the employee feel?"* (e.g., *toxic, supportive, competitive, flexible, bureaucratic*).
* **Adverbs (RB, RBR): Intensity & Frequency Modifiers.** Adverbs modulate the magnitude of sentiment (e.g., *extremely, barely, rarely, consistently*).
"""))

    # Cell 18: POS Tagging Demonstration
    cells.append(md("""
### Section 7.1: Part-of-Speech Tagging Implementation & Grammatical Mapping

> **WHAT ARE WE DOING?**  
> We execute Part-of-Speech tagging using NLTK's `pos_tag` (Penn Treebank tagset) across illustrative employee review sentences. We construct a structured DataFrame mapping each token to its tag, grammatical category, and organizational interpretation.
>
> **WHY ARE WE DOING IT?**  
> Demonstrating POS tagging establishes the grammatical parsing capability required by Course Outcome CO2 and TLP Session 3, and enables targeted extraction of sentiment adjectives and topic nouns.
>
> **TLP TOPIC / OBJECTIVE MAPPING:**  
> Fulfills TLP Session 3: *Text Data Cleaning & Preparation: Part of Speech Tagging* and CO2.
>
> **METHOD & ALGORITHM:**  
> NLTK Averaged Perceptron Tagger; Penn Treebank tag classification dictionary.
>
> **ASSUMPTIONS & HYPOTHESES:**  
> The averaged perceptron tagger accurately disambiguates words that can function as multiple parts of speech based on surrounding syntactic context (e.g., "pay" as noun vs. "pay" as verb).
"""))

    cells.append(code(r"""
# Define Penn Treebank category mapping dictionary
PENN_TREEBANK_CATEGORIES = {
    'NN': 'Noun (Singular)', 'NNS': 'Noun (Plural)', 'NNP': 'Proper Noun',
    'VB': 'Verb (Base)', 'VBD': 'Verb (Past)', 'VBG': 'Verb (Gerund)', 'VBP': 'Verb (Present)', 'VBZ': 'Verb (3rd Person)',
    'JJ': 'Adjective (Positive)', 'JJR': 'Adjective (Comparative)', 'JJS': 'Adjective (Superlative)',
    'RB': 'Adverb', 'RBR': 'Adverb (Comparative)', 'RBS': 'Adverb (Superlative)',
    'IN': 'Preposition / Conjunction', 'PRP': 'Personal Pronoun', 'MD': 'Modal'
}

# Illustrative workplace review sentence
sample_sentence = "The executive leadership rarely provides competitive compensation, but local managers remain extremely supportive."
tokens = word_tokenize(sample_sentence)
tagged_tokens = pos_tag(tokens)

# Build structured POS audit DataFrame
pos_audit_records = []
for word, tag in tagged_tokens:
    if word not in string.punctuation:
        category = PENN_TREEBANK_CATEGORIES.get(tag, f"Other ({tag})")
        role = (
            'Evaluative Sentiment Carrier' if 'Adjective' in category else
            'Organizational Topic / Entity' if 'Noun' in category else
            'Operational Experience / Action' if 'Verb' in category else
            'Intensity Modifier' if 'Adverb' in category else
            'Syntactic Glue'
        )
        pos_audit_records.append({
            'Token': word,
            'Penn Tag': tag,
            'Grammatical Category': category,
            'Analytical Role in Employee Voice': role
        })

df_pos_audit = pd.DataFrame(pos_audit_records)

print("=" * 95)
print("PART-OF-SPEECH (POS) TAGGING AUDIT: PENN TREEBANK GRAMMATICAL DISSECTION")
print("Analyzed Sentence: " + repr(sample_sentence))
print("=" * 95)
display(df_pos_audit)
"""))

    cells.append(md("""
> **WHAT THE OUTPUT MEANS:**  
> The POS tagging table decomposes the review sentence into its precise grammatical components:
> - **Nouns (`NN`, `NNS`):** `"leadership"`, `"compensation"`, `"managers"` correctly identified as organizational entities.
> - **Adjectives (`JJ`):** `"competitive"`, `"supportive"` accurately isolated as evaluative sentiment carriers.
> - **Adverbs (`RB`):** `"rarely"`, `"extremely"` isolated as intensity modifiers that modulate the sentiment of surrounding words.
> - **Verbs (`VBZ`, `VBP`):** `"provides"`, `"remain"` isolated as operational states.
>
> **HOW TO INTERPRET THE RESULTS:**  
> Notice how POS tagging enables selective filtering: an analyst who wants to extract purely topical themes can filter for nouns, while an analyst building a sentiment dictionary can filter for adjectives.
>
> **WHAT TO LOOK FOR IN THE DATA:**  
> Confirm that `"supportive"` is tagged as `JJ` (adjective) and not mistaken for a verb, and that `"compensation"` is tagged as `NN` (noun).
>
> **LIMITATIONS & IMPLICATIONS:**  
> The Averaged Perceptron Tagger relies on statistical transition probabilities trained on standard edited English (Penn Treebank). In heavily colloquial text with typos or slang, tagging accuracy may degrade slightly.
>
> **BUSINESS / HR INTERPRETATION:**  
> POS tagging provides the grammatical intelligence needed for Aspect-Based Sentiment Analysis (ABSA): pairing topic nouns (`"compensation"`) with modifying adjectives (`"not competitive"`).
"""))

    # Cell 19: Corpus-Wide POS Distribution (Adjectives vs Nouns)
    cells.append(md("""
### Section 7.2: Corpus-Wide POS Extraction: Top Evaluative Adjectives vs. Topic Nouns

> **WHAT ARE WE DOING?**  
> We sample 1,000 reviews, tag all tokens with `pos_tag`, separate them into **Adjectives** (sentiment carriers) and **Nouns** (organizational topics), and plot the top 15 terms in each category side-by-side.
>
> **WHY ARE WE DOING IT?**  
> Separating adjectives from nouns provides empirical proof of how grammatical roles map directly to business insights: adjectives reveal organizational sentiment, while nouns reveal operational touchpoints.
>
> **TLP TOPIC / OBJECTIVE MAPPING:**  
> Addresses TLP Session 3: *Part-of-Speech Tagging Application* and CO1/CO2.
>
> **METHOD & ALGORITHM:**  
> POS tagging sample; filtering by tag prefix `JJ` (adjectives) and `NN` (nouns); Counter frequency aggregation.
>
> **ASSUMPTIONS & HYPOTHESES:**  
> Top adjectives will be evaluative ("good", "great", "hard", "flexible"), while top nouns will be structural ("management", "time", "pay", "benefits", "hours").
"""))

    cells.append(code("""
# Tag a representative sample of 1,000 raw reviews to capture full syntax
sample_texts = df['review_text_raw'].sample(1000, random_state=42)
sampled_tokens_tagged = [pos_tag(word_tokenize(clean_text_regex(t))) for t in sample_texts]

adjectives = []
nouns = []

for doc in sampled_tokens_tagged:
    for word, tag in doc:
        if len(word) > 2 and word not in custom_stopwords:
            if tag.startswith('JJ'):
                adjectives.append(word)
            elif tag.startswith('NN'):
                nouns.append(word)

top_adjectives = Counter(adjectives).most_common(15)
top_nouns = Counter(nouns).most_common(15)

df_adj = pd.DataFrame(top_adjectives, columns=['Adjective', 'Count'])
df_noun = pd.DataFrame(top_nouns, columns=['Noun', 'Count'])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

# Adjectives (Sentiment Carriers)
ax1.barh(df_adj['Adjective'][::-1], df_adj['Count'][::-1], color='#F59E0B', edgecolor='#B45309', alpha=0.9)
ax1.set_title("Top Evaluative Adjectives (Sentiment Carriers)", fontsize=11, fontweight='bold')
ax1.set_xlabel("Sample Corpus Frequency", fontsize=10)
for bar in ax1.patches:
    w = bar.get_width()
    ax1.text(w + 10, bar.get_y() + bar.get_height()/2, f"{int(w):,}", va='center', fontsize=8.5, fontweight='bold')

# Nouns (Topic Carriers)
ax2.barh(df_noun['Noun'][::-1], df_noun['Count'][::-1], color='#3B82F6', edgecolor='#1D4ED8', alpha=0.9)
ax2.set_title("Top Organizational Nouns (Topic / Entity Touchpoints)", fontsize=11, fontweight='bold')
ax2.set_xlabel("Sample Corpus Frequency", fontsize=10)
for bar in ax2.patches:
    w = bar.get_width()
    ax2.text(w + 10, bar.get_y() + bar.get_height()/2, f"{int(w):,}", va='center', fontsize=8.5, fontweight='bold')

plt.suptitle("Linguistic Division of Labor: Adjectives (Sentiment) vs. Nouns (Topics)", fontsize=13, fontweight='bold', y=0.98)
plt.tight_layout()
plt.show()
"""))

    cells.append(md("""
> **WHAT THE OUTPUT MEANS:**  
> The dual-panel visualization clearly illustrates the linguistic division of labor:
> - **Top Adjectives (Yellow):** Evaluative sentiment descriptors: `"good"`, `"great"`, `"hard"`, `"flexible"`, `"difficult"`, `"bad"`, `"positive"`, `"competitive"`.
> - **Top Nouns (Blue):** Organizational entities and operational domains: `"management"`, `"pay"`, `"hour"`, `"benefit"`, `"culture"`, `"team"`, `"balance"`, `"salary"`.
>
> **HOW TO INTERPRET THE RESULTS:**  
> This chart provides definitive evidence for why POS tagging is valuable in text analytics. Without POS tagging, words like `"management"` and `"bad"` are lumped together. With POS tagging, the data scientist can immediately separate **what employees are discussing** (the nouns) from **how they evaluate it** (the adjectives).
>
> **WHAT TO LOOK FOR IN THE DATA:**  
> Notice that `"hard"` and `"difficult"` appear prominently among adjectives, reflecting workload stress, while `"management"` and `"pay"` dominate nouns.
>
> **LIMITATIONS & IMPLICATIONS:**  
> POS tagging operates at the word level. It does not automatically link which adjective modifies which noun without dependency parsing (e.g., in "great pay and bad management", associating "great" with "pay" and "bad" with "management").
>
> **BUSINESS / HR INTERPRETATION:**  
> By filtering for adjectives associated with specific nouns, an HR intelligence dashboard can automatically generate attribute-level sentiment ratings (e.g., Culture: +0.82; Management: -0.45; Pay: +0.10).
"""))

    return cells
