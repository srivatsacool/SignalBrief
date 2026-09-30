# 🏛️ Employee Voice Analytics — QTA 404 Master Capstone Dossier
## Prin. L. N. Welingkar Institute of Management Development & Research (WeSchool)
### MBA / PGDM Trimester IV — Course Code: QTA 404 (Text Analytics)

---

## 📌 Executive Overview

This repository contains the definitive, presentation-grade Jupyter Notebook **`Employee_Voice_Analytics_Final.ipynb`** developed for the MBA Text Analytics course (**QTA 404**) at Welingkar Institute of Management. 

The project analyzes **8,785 employee reviews across 90 top US employers** from the Kaggle dataset (`scrapifier/glassdoor-employee-reviews-top-us-employers`), converting raw, unstructured qualitative feedback into decision-ready workforce intelligence.

### Academic Supervision & Institutional Alignment
* **Course:** Text Analytics (QTA 404, 1.5 Credits / 15 Hours)
* **Faculty Mentor:** Dr. Sonal Daulatkar (`sonal.daulatkar@welingkar.org`)
* **Program Head:** Dr. Kavita Kalyandurgmath
* **Academic Batch:** 2025–2027 (Trimester IV)

---

## 🎯 Course Outcome (CO) Verification

The notebook provides rigorous, reproducible empirical evidence for every outcome defined in the official Teaching and Learning Plan (TLP):

| Course Outcome | Bloom's Level | Mapped Sections | Key Empirical Deliverables & Evidence |
| :--- | :---: | :---: | :--- |
| **QTA 404. CO1**<br/>*Demonstrate cleaning of unstructured data* | Level II<br/>(Understanding) | Sec 02, 03, 07 | • Complete missing value profiling & data dictionary audit across 31 attributes<br>• Regex HTML/URL sanitization and lowercasing<br>• **Negation-preserving stopword removal** (retaining *not, no, never*)<br>• Porter Stemming vs. WordNet Lemmatization comparative benchmark<br>• Penn Treebank Part-of-Speech tagging (`pos_tag`)<br>• **5-Stage Before-and-After Text Transformation Table** |
| **QTA 404. CO2**<br/>*Apply various techniques and algorithms for text analytics* | Level III<br/>(Applying) | Sec 04, 05, 06,<br>08, 09, 12 | • Document word count & character length distribution profiling<br>• Top 20 Unigram & Top 15 Bigram collocation frequency analysis<br>• Bag of Words Document-Term Matrix ($8,785 \times 1,000$, 98.37% sparsity)<br>• Mathematical TF-IDF Vectorization with Smooth-IDF & $L_2$ Normalization<br>• Supervised Text Classification (TF-IDF + Balanced Logistic Regression)<br>• Three Segmented Word Clouds (Overall, Positive, Negative)<br>• **Latent Dirichlet Allocation (LDA) Topic Modeling ($k=6$ Thematic Clusters)** |
| **QTA 404. CO3**<br/>*Analyze data for Sentiment Analysis* | Level IV<br/>(Analyzing) | Sec 08, 10,<br>11, 12 | • Supervised Classification: **84.5% Accuracy, 79.8% Negative Recall**<br>• Classification report & styled Seaborn confusion matrix heatmap<br>• Model Interpretability: Top 15 Positive vs. Top 15 Negative Feature Coefficients<br>• VADER Rule-Based Compound Intensity Scoring across 8,785 Reviews<br>• Dual-Channel Asymmetry: Pros (+0.684) vs. Cons (-0.318) Density Distributions<br>• Organizational Sentiment Benchmarking across Top US Employers<br>• **The Rating–Text Divergence: 42.8% of 1-Star Reviews Net-Positive**<br>• Representative Review Case Inspection (4 Quadrants of Workforce Voice)<br>• Executive HR Case Study & 4-Tier Analytic Protocol |

> [!NOTE]
> **Academic Note on CO4 Reference:** While the TLP assessment evaluation grid contains references to CO4 in certain evaluation schedules, the official Course Outcome Definition Table defines outcomes strictly up to **CO1, CO2, and CO3**. To maintain strict academic integrity and avoid fabricating an unauthorized institutional definition, all advanced topics (LDA Topic Modeling, GenAI synthesis) have been mapped directly to the expansion of **CO2 and CO3**.

---

## 📂 Notebook Architecture (17 Sections, 120 Cells)

`Employee_Voice_Analytics_Final.ipynb` is structured into 17 comprehensive sections. Every code cell is strictly preceded by an explanatory Markdown cell (`WHAT ARE WE DOING?`, `WHY ARE WE DOING IT?`, `TLP MAPPING`, `ALGORITHM`, `ASSUMPTIONS`) and immediately followed by an explanatory Markdown cell (`WHAT THE OUTPUT MEANS`, `HOW TO INTERPRET`, `WHAT TO LOOK FOR`, `LIMITATIONS`, `BUSINESS INTERPRETATION`).

* **SECTION 00 — Title and Project Overview** (Institutional alignment, CRISP-DM flow, problem framing)
* **SECTION 01 — Text Analytics Fundamentals** (Text Analytics vs. Mining vs. NLP comparison table, HR use cases, corpus theory)
* **SECTION 02 — Dataset Acquisition and Corpus Formation** (Dynamic ingestion, 31-column data dictionary, sparsity plot, sample reviews, sampling bias discussion)
* **SECTION 03 — Text Cleaning and Preparation** (Consolidation, lowercasing, regex noise removal, negation-preserving stopwords, stemming vs. lemmatization, 5-stage audit)
* **SECTION 04 — Exploratory Text Analysis** (Word count distribution, top 20 unigrams, top 15 bigrams, comparative high vs. low rating vocabulary)
* **SECTION 05 — Bag of Words** (Vector space model, CountVectorizer DTM, sparsity calculation, sample vocabulary, readable mini-DTM DataFrame)
* **SECTION 06 — TF-IDF** (Mathematical formulation with LaTeX formulas, Smooth-IDF, highest vs. lowest IDF terms, document-level weight comparison)
* **SECTION 07 — Part-of-Speech Tagging** (Penn Treebank tagset, NLTK `pos_tag`, grammatical parsing, corpus-wide adjectives vs. nouns distributions)
* **SECTION 08 — Text Classification** (Supervised binary polarity, stratified 80/20 split, balanced Logistic Regression, confusion matrix, top feature coefficients)
* **SECTION 09 — Word Cloud** (Segmented word clouds for overall, 4-5 star positive, and 1-2 star negative reviews; academic critique of limitations)
* **SECTION 10 — Sentiment Analysis** (VADER compound scoring, pros vs. cons asymmetry, employer benchmarking, The Rating–Text Divergence matrix, 4-quadrant qualitative excerpts)
* **SECTION 11 — Case Study and Business Interpretation** (5 core business questions answered, 4-tier analytic protocol: $\text{Obs} \to \text{Interp} \to \text{Impl} \to \text{Caut}$)
* **SECTION 12 — Beyond the TLP: Advanced Text Analytics** (Unsupervised LDA topic modeling with $k=6$, topic visualization, The Workforce Signal Matrix)
* **SECTION 13 — Text Analytics in GenAI** (Conceptual GenAI extensions, privacy/PII rules, 100% local reproducible executive briefing generator)
* **SECTION 14 — End-to-End Workflow** (Unified pipeline flowchart, comprehensive TLP Session 1–8 mapping table)
* **SECTION 15 — Conclusion and Future Strategies** (Key findings, limitations, practical HR roadmaps, future research)
* **SECTION 16 — Final Course Outcome Mapping** (Comprehensive Bloom's Taxonomy CO compliance matrix)

---

## 🛠️ Dataset Placement & Execution Guide

### 1. Dataset Location
Place the Kaggle dataset CSV file at:
```
data/raw/glassdoor_employee_reviews_us.csv
```
*(The notebook contains dynamic path resolution that automatically checks `./data/raw/`, `../data/raw/`, and the local directory).*

### 2. Environment Prerequisites
The notebook runs on Python 3.10+ (tested and verified on Python 3.12). All dependencies can be installed via:
```bash
pip install pandas numpy scikit-learn nltk vaderSentiment wordcloud matplotlib seaborn joblib nbformat nbconvert ipykernel
```

Required NLTK corpora (automatically checked and downloaded if missing):
```python
import nltk
nltk.download(['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'punkt_tab', 'averaged_perceptron_tagger_eng'])
```

### 3. Running the Notebook
Open and execute `Employee_Voice_Analytics_Final.ipynb` using your preferred Jupyter environment:
* **VS Code:** Open `Employee_Voice_Analytics_Final.ipynb`, select the Python 3.12 kernel, and click **"Run All"**.
* **JupyterLab / Classic Notebook:**
  ```bash
  jupyter notebook Employee_Voice_Analytics_Final.ipynb
  ```
* **Headless CLI Execution:**
  ```bash
  jupyter nbconvert --to notebook --execute Employee_Voice_Analytics_Final.ipynb --output Employee_Voice_Analytics_Final_Executed.ipynb
  ```

---

## 🔬 Core Empirical Discoveries

1. **The Rating–Text Divergence (Divergent Voice):**
   * **42.8% of 1-star reviews contain net-positive narrative text** because employees buffer institutional complaints with sincere praise for teammates and benefits (*"Collegial Buffering"*).
   * **6.9% of 5-star reviews conceal acute negative operational warnings** (burnout, excessive hours).
   * Proves that scalar star ratings alone obscure granular workforce dynamics.
2. **Supervised Polarity Classification:**
   * TF-IDF features combined with balanced Logistic Regression achieve **84.5% test accuracy**, **79.8% recall on negative reviews**, and **86.7% recall on positive reviews**.
   * Identifies acute organizational friction terms (`"poor"`, `"worst"`, `"toxic"`, `"management"`) with negative log-odds weights.
3. **Unsupervised Latent Topic Modeling ($k=6$):**
   * LDA autonomously discovers six operational domains: Compensation & Benefits, Work-Life Balance & Flexibility, Frontline Supervision Friction, Peer Camaraderie, Career Growth & Learning, and Shift Operations Stress.
   * Cross-tabulation proves that **Frontline Supervision and Shift Stress account for over 58% of all low-rating reviews**, proving that leadership and scheduling are the primary operational friction points.
