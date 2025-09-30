<div align="center">

# 🌍 Multilingual Prompt Dataset Builder

### *From 100 English prompts to a published, human-verified multilingual dataset — in 6 days, at zero cost.*

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Gemini](https://img.shields.io/badge/Gemini_1.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![HuggingFace](https://img.shields.io/badge/🤗_Hugging_Face-Datasets-FFD21E?style=for-the-badge)](https://huggingface.co/datasets)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey?style=for-the-badge)](https://creativecommons.org/licenses/by/4.0/)

<br/>

> **700+ annotated multilingual prompt-response pairs** · **7 languages** · **5 task categories** · **Human-verified Malayalam** · **$0 cost**

</div>

---

## 📖 What Is This?

**Multilingual Prompt Dataset Builder** is a fully automated, end-to-end Python pipeline that:

1. Takes **100 hand-crafted English prompts** across 5 NLP task categories
2. Translates them into **6 additional languages** using Google Translate
3. Generates **high-quality reference answers** with Google Gemini 1.5 Flash
4. Applies a **custom multi-dimensional quality scoring** system
5. Runs a **native-speaker Malayalam verification** step
6. Publishes the final dataset to **Hugging Face Hub** — publicly and freely available

The result is a **research-grade, open-source dataset** ready for LLM fine-tuning, evaluation, and benchmarking.

---

## ✨ Key Highlights

|  | Feature | Details |
|--|---------|---------|
| 🧑‍🤝‍🧑 | **Human-verified Malayalam** | Native speaker reviews & corrects every Malayalam translation — rare in open NLP datasets |
| 📐 | **3-Dimensional Quality Scoring** | Every prompt scored on Clarity (40%), Specificity (35%), Completeness (25%) |
| 🤖 | **Gemini Reference Outputs** | Each prompt paired with a Gemini 1.5 Flash response for supervised learning use |
| ♻️ | **Checkpointed Pipeline** | Safe to interrupt and resume at any step — no work is lost |
| 💸 | **Zero Cost** | Built entirely on free-tier APIs (Google Translate, Gemini, Hugging Face) |
| 🌐 | **7 Languages** | English, Malayalam, Hindi, Arabic, Chinese, Spanish, French |

---

## 📊 Dataset at a Glance

<div align="center">

| Metric | Value |
|:-------|:------|
| 📝 Source Prompts | **100** (hand-authored in English) |
| 🌍 Languages | **7** — EN · ML · HI · AR · ZH · ES · FR |
| 🗃️ Total Dataset Rows | **700+** |
| 🏷️ Task Categories | **5** — Summarisation · QA · Creative Writing · Instruction Following · Reasoning |
| 📏 Quality Dimensions | **3** — Clarity · Specificity · Completeness |
| ⏱️ Build Time | **6 days** |
| 💰 Total Cost | **$0** |

</div>

---

## 🗂️ Project Structure

```
multilingual-prompt-dataset-builder/
│
├── 📄 config.py                     ← Central config: paths, languages, API settings, scoring weights
├── 🚀 run_pipeline.py               ← Master script — run all steps or individual steps
│
├── 📦 pipeline/
│   ├── __init__.py
│   ├── translate.py                 ← Step 1: Translate 100 prompts into 6 languages
│   ├── generate_outputs.py          ← Step 2: Generate Gemini 1.5 Flash reference answers
│   ├── quality_score.py             ← Step 3/4/5: Score, export review, merge corrections
│   └── upload_hf.py                 ← Step 6: Publish final dataset to Hugging Face Hub
│
├── 🖥️  app/
│   ├── __init__.py
│   └── streamlit_app.py             ← Interactive dataset browser (filter, view, download)
│
├── 📂 data/
│   ├── prompts.csv                  ← 100 source English prompts [committed]
│   ├── malayalam_review.csv         ← Native-speaker review file [committed post-review]
│   ├── translated_prompts.csv       ← [generated — gitignored]
│   ├── dataset_with_outputs.csv     ← [generated — gitignored]
│   ├── dataset_scored.csv           ← [generated — gitignored]
│   └── dataset_final.csv            ← [generated — gitignored]
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Pipeline Architecture

The pipeline runs **6 sequential, resumable steps**:

```
┌─────────────────────────────────────────────────────────────┐
│                     INPUT: prompts.csv                      │
│              (100 hand-authored English prompts)            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
          ┌────────────────────────────────┐
          │  STEP 1 · translate.py         │
          │  Translates into 6 languages   │
          │  → translated_prompts.csv      │
          └────────────────┬───────────────┘
                           │
                           ▼
          ┌────────────────────────────────┐
          │  STEP 2 · generate_outputs.py  │
          │  Gemini 1.5 Flash responses    │
          │  → dataset_with_outputs.csv    │
          └────────────────┬───────────────┘
                           │
                           ▼
          ┌────────────────────────────────┐
          │  STEP 3 · quality_score.py     │
          │  Multi-dimensional scoring     │
          │  → dataset_scored.csv          │
          └────────────────┬───────────────┘
                           │
                           ▼
          ┌────────────────────────────────┐
          │  STEP 4 · quality_score.py     │
          │  Export Malayalam review CSV   │
          │  → malayalam_review.csv        │
          └────────────────┬───────────────┘
                           │
                    👤 HUMAN REVIEW
               (Native Malayalam speaker)
                           │
                           ▼
          ┌────────────────────────────────┐
          │  STEP 5 · quality_score.py     │
          │  Merge corrections back in     │
          │  → dataset_final.csv           │
          └────────────────┬───────────────┘
                           │
                           ▼
          ┌────────────────────────────────┐
          │  STEP 6 · upload_hf.py         │
          │  Publish to Hugging Face Hub   │
          │  → 🤗 Live public dataset      │
          └────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/nihalshx/Multilingual-Prompt-Dataset-Builder.git
cd Multilingual-Prompt-Dataset-Builder
```

### 2️⃣ Set Up a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Configure API Keys

API keys are entered through the **Streamlit ⚙️ Settings tab** at runtime — no `.env` file needed.

| Key | Where to Get It | Required? |
|-----|----------------|-----------|
| `GEMINI_API_KEY` | [Google AI Studio](https://makersuite.google.com/app/apikey) | ✅ Required |
| `HF_TOKEN` | [Hugging Face Tokens](https://huggingface.co/settings/tokens) *(Write access)* | ✅ Required |
| `GOOGLE_CLOUD_API_KEY` | [Google Cloud Console](https://console.cloud.google.com) → Cloud Translation API | ⚡ Optional — improves translation quality |

---

## 🏃 Running the Pipeline

### Option A — Full Pipeline (Recommended)

Run everything in one command:

```bash
python run_pipeline.py
```

The pipeline runs **Steps 1–4 automatically**, then pauses for the Malayalam human review. After completing the review file, finalize with:

```bash
python run_pipeline.py --step merge
```

### Option B — Step by Step

Run each step individually for full control:

```bash
# Step 1: Translate all prompts into 6 languages
python run_pipeline.py --step translate

# Step 2: Generate Gemini 1.5 Flash reference outputs
python run_pipeline.py --step outputs

# Step 3: Compute multi-dimensional quality scores
python run_pipeline.py --step score

# Step 4: Export Malayalam review CSV for human verification
python run_pipeline.py --step review

#  ✋ PAUSE: Open data/malayalam_review.csv and complete the review

# Step 5: Merge the reviewed corrections back into the dataset
python run_pipeline.py --step merge
```

### 👤 The Malayalam Human Review (Step 4)

This step is what makes this dataset **unique among open NLP datasets**.

After running `--step review`, open `data/malayalam_review.csv` in Excel or Google Sheets:

| Column | Action |
|--------|--------|
| `ml_review_status` | Set to `approved` if translation is correct |
| `ml_review_status` | Set to `corrected` if it needs fixing |
| `prompt_ml_corrected` | Paste the corrected Malayalam text here |

> 💡 **Why this matters:** Most multilingual datasets rely purely on automated translation. Human verification of Malayalam text is exceptionally rare — this is a key portfolio differentiator.

---

## 🖥️ Dataset Browser UI

Explore the full dataset interactively with the built-in Streamlit app:

```bash
streamlit run app/streamlit_app.py
# → Opens at http://localhost:8501
```

**What you can do:**

| Feature | Description |
|---------|-------------|
| 🔍 **Multi-axis Filtering** | Filter by language, task category, difficulty level, and quality score |
| 🌐 **Side-by-side View** | Compare all 7 language translations in a single row |
| 🚩 **Flag Bad Translations** | Mark poor outputs (auto-saved to `data/flagged_translations.csv`) |
| 📥 **Export** | Download any filtered subset as a CSV file |

---

## 📤 Publishing to Hugging Face

```bash
# Preview the auto-generated dataset card locally
python -m pipeline.upload_hf --preview-card

# Publish the full dataset to Hugging Face Hub
python -m pipeline.upload_hf --repo YOUR_USERNAME/multilingual-prompt-dataset-ml
```

🎉 Your dataset goes live at:
```
https://huggingface.co/datasets/YOUR_USERNAME/multilingual-prompt-dataset-ml
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Translation** | `googletrans 4.0` / Google Cloud Translate API | Translate 100 prompts × 6 languages |
| **LLM Outputs** | Google Gemini 1.5 Flash (`google-generativeai`) | Generate high-quality reference responses |
| **Data Processing** | `pandas`, `numpy`, `tqdm` | Pipeline data manipulation and progress tracking |
| **Quality Scoring** | Custom weighted schema | Multi-dimensional prompt quality annotation |
| **Dataset Publishing** | `datasets`, `huggingface_hub` | Publish to Hugging Face Hub with dataset card |
| **Browser UI** | Streamlit | Interactive dataset exploration and filtering |
| **Human Verification** | Native Malayalam speaker | Manual correction of Malayalam translations |

---

## 📐 Quality Scoring Schema

Every prompt is scored on a **0.0 – 1.0 scale** across three dimensions:

### Prompt Quality Weights

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| 🎯 **Clarity** | **40%** | How unambiguous, concise, and well-structured the prompt is |
| 🔬 **Specificity** | **35%** | How precisely the prompt defines the desired task output |
| ✅ **Completeness** | **25%** | Whether all necessary context and constraints are provided |

**Final Score Formula:**
```
quality_score = (clarity × 0.40) + (specificity × 0.35) + (completeness × 0.25)
```

### Output Length Norms by Task

Task-specific ideal word counts are applied when evaluating Gemini outputs:

| Task Category | Min Words | Ideal Words | Max Words |
|---------------|:---------:|:-----------:|:---------:|
| Summarisation | 30 | 80 | 250 |
| Question Answering | 20 | 60 | 200 |
| Creative Writing | 40 | 120 | 400 |
| Instruction Following | 10 | 30 | 120 |
| Reasoning | 20 | 50 | 150 |

---

## 🐛 Troubleshooting

<details>
<summary><b>❓ <code>googletrans</code> returns empty strings?</b></summary>

The free library can hit rate limits under heavy use. Try two fixes:
1. Increase `TRANSLATE_DELAY` in `config.py` from `0.5` → `1.5`
2. Add `GOOGLE_CLOUD_API_KEY` to switch to the more reliable Cloud Translation API

</details>

<details>
<summary><b>❓ Gemini returns rate limit errors?</b></summary>

The free tier allows ~15 requests/minute. Increase `GEMINI_REQUEST_DELAY` in `config.py` to `5.0`. All pipeline steps checkpoint automatically — it is safe to interrupt and re-run at any time.

</details>

<details>
<summary><b>❓ How do I add more prompts?</b></summary>

Add rows to `data/prompts.csv` maintaining the existing column schema. No code changes are required — the pipeline will process all rows automatically.

</details>

<details>
<summary><b>❓ Can I add more languages?</b></summary>

Yes. Add an entry to the `LANGUAGES` dict in `config.py`:
```python
LANGUAGES = {
    "ml": "Malayalam",
    "hi": "Hindi",
    # Add your language here, e.g.:
    "de": "German",
}
```
The translation, scoring, and Hugging Face upload steps all adapt automatically.

</details>

<details>
<summary><b>❓ The Streamlit app won't start?</b></summary>

The app requires the translated data to exist. Run at minimum Step 1 first:
```bash
python run_pipeline.py --step translate
```

</details>

---

## 📋 Portfolio / CV Section

```
────────────────────────────────────────────────────────────────────
Multilingual Prompt Dataset Builder — Published on Hugging Face
Python · Google Translate API · Gemini API · Hugging Face | Jul–Oct 2025
────────────────────────────────────────────────────────────────────

• Built and published an open-source multilingual NLP dataset with
  700+ rows (100 prompts × 7 languages) across 5 task categories,
  structured for LLM fine-tuning and evaluation benchmarks.

• Designed a 3-dimensional quality annotation schema (Clarity 40%,
  Specificity 35%, Completeness 25%) with task-specific output length
  norms, applied programmatically across the entire dataset.

• Integrated Google Translate, Gemini 1.5 Flash, and Hugging Face
  Hub into a fully automated, checkpointed pipeline — built at $0
  cost using exclusively free-tier APIs.

• Conducted native-speaker verification of all Malayalam translations,
  making this one of the very few open datasets with human-verified
  Malayalam prompt-response content.

• Developed an interactive Streamlit dataset browser supporting
  multi-axis filtering, 7-language side-by-side comparison, bad
  translation flagging, and CSV export.
────────────────────────────────────────────────────────────────────
```

---

## 📄 License

This project is released under the **[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)** license.

You are free to share and adapt this work for any purpose, provided appropriate credit is given.

---

## 🤝 Contributing

Contributions are very welcome! Areas where you can help:

- 📝 Add more diverse English source prompts
- 🌐 Add new language translations
- 🔧 Improve quality scoring algorithms
- 🐛 Report and fix translation errors
- 📖 Improve documentation

Please **open an issue** to discuss your idea or **submit a pull request** directly.

---

<div align="center">

**Built to advance open, multilingual NLP research — one prompt at a time. 🌍**

<br/>

*Made with ❤️ by [nihalshx](https://github.com/nihalshx)*

</div>
