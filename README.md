# Multilingual Prompt Dataset Builder

> 100 hand-authored English prompts → 7 languages → quality-scored → Gemini reference outputs → published on Hugging Face in 6 days, at zero cost.

---

## Project Overview

Builds and publishes an open-source dataset of **700+ annotated multilingual
prompt-response pairs** across 7 languages and 5 task categories.

**Key differentiator:** All Malayalam translations are reviewed and corrected by a
native Malayalam speaker — one of the very few open datasets with human-verified
Malayalam content.

| Metric          | Value                              |
|-----------------|------------------------------------|
| Prompts         | 100 (hand-authored)                |
| Languages       | 7 (EN, ML, HI, AR, ZH, ES, FR)    |
| Dataset rows    | 700+                               |
| Task categories | 5                                  |
| Build time      | 6 days                             |
| Cost            | $0 (all free tiers)                |

---

## Project Structure

```
multilingual-prompt-dataset-builder/
├── config.py                    ← all paths, language codes, API settings
├── run_pipeline.py              ← master script — runs the full pipeline
│
├── pipeline/
│   ├── __init__.py
│   ├── translate.py             ← translates prompts into 6 languages
│   ├── generate_outputs.py      ← Gemini reference output generation
│   ├── quality_score.py         ← quality scoring + Malayalam review workflow
│   └── upload_hf.py             ← publishes to Hugging Face Hub
│
├── app/
│   ├── __init__.py
│   └── streamlit_app.py         ← dataset browser UI
│
├── data/
│   ├── prompts.csv              ← 100 source English prompts (committed)
│   ├── malayalam_review.csv     ← native-speaker review file (committed after review)
│   └── ...                     ← generated files (gitignored)
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Setup

### 1. Clone / create the project

```bash
git clone <your-repo-url>
cd multilingual-prompt-dataset-builder
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API keys

```bash
cp .env.example .env
```

Edit `.env` and add:

| Key                   | Where to get it                                         | Required? |
|-----------------------|---------------------------------------------------------|-----------|
| `GEMINI_API_KEY`      | https://makersuite.google.com/app/apikey                | Yes       |
| `HF_TOKEN`            | https://huggingface.co/settings/tokens (Write token)   | Yes       |
| `GOOGLE_CLOUD_API_KEY`| https://console.cloud.google.com — Cloud Translation API| Optional  |

---

## Running the Pipeline

### Option A — Run everything at once (recommended)

```bash
python run_pipeline.py
```

The script runs steps 1–4 automatically, then pauses for the native-speaker
Malayalam review. After completing the review, run:

```bash
python run_pipeline.py --step merge
```

### Option B — Run individual steps

```bash
python run_pipeline.py --step translate   # Step 1: translate into 6 languages
python run_pipeline.py --step outputs     # Step 2: generate Gemini outputs
python run_pipeline.py --step score       # Step 3: compute quality scores
python run_pipeline.py --step review      # Step 4: export Malayalam review CSV
# ... complete the review in data/malayalam_review.csv ...
python run_pipeline.py --step merge       # Step 5: merge review back in
```

### Step 4 — Malayalam native-speaker review

After running `--step review`, open `data/malayalam_review.csv` in Excel or
Google Sheets. For each row:

- If the auto-translation is accurate → set `ml_review_status = approved`
- If it needs correction → set `ml_review_status = corrected`, paste the
  corrected Malayalam into `prompt_ml_corrected`

This step is your biggest portfolio differentiator.

---

## Browsing the Dataset

```bash
streamlit run app/streamlit_app.py
# Opens at http://localhost:8501
```

Features:
- Filter by language, category, difficulty, and quality score
- View all 7 translations side by side
- Flag poor translations (saved to `data/flagged_translations.csv`)
- Download filtered subsets as CSV

---

## Publishing to Hugging Face

```bash
# Preview the dataset card locally first
python -m pipeline.upload_hf --preview-card

# Then publish
python -m pipeline.upload_hf --repo YOUR_USERNAME/multilingual-prompt-dataset-ml
```

Your dataset will be live at:
`https://huggingface.co/datasets/YOUR_USERNAME/multilingual-prompt-dataset-ml`

---

## Tech Stack

| Component              | Technology                            |
|------------------------|---------------------------------------|
| Translation            | googletrans (free) / Google Cloud API |
| Reference outputs      | Google Gemini 1.5 Flash               |
| Quality scoring        | Custom scoring (NumPy, pandas)        |
| Dataset publishing     | Hugging Face `datasets` library       |
| Browser UI             | Streamlit                             |
| Malayalam verification | Native speaker (human)                |

---

## CV Bullet Points

```
Multilingual Prompt Dataset — Published on Hugging Face
Python, Google Translate API, Gemini API, Hugging Face datasets | 2025

• Built and published an open-source multilingual prompt dataset containing 700+ rows
  (100 prompts × 7 languages) across 5 task categories, structured for LLM evaluation
  and fine-tuning pipelines.

• Designed a multi-dimensional quality annotation schema (clarity, specificity,
  completeness) and applied it programmatically across the full dataset.

• Conducted native-speaker verification of all Malayalam translations — one of the few
  open datasets with human-verified Malayalam prompt content.

• Wrote a comprehensive dataset card documenting schema, methodology, and intended use,
  demonstrating the ability to produce clear technical content for AI research audiences.
```

---

## Troubleshooting

**googletrans returns empty strings?**
The free library hits rate limits. Increase `TRANSLATE_DELAY` in `config.py` to `1.5`,
or add `GOOGLE_CLOUD_API_KEY` to your `.env` to use the Cloud API.

**Gemini rate limit errors?**
The free tier allows ~15 requests/minute. Increase `GEMINI_REQUEST_DELAY` in `config.py`
to `5.0`. All steps checkpoint automatically — safe to interrupt and resume.

**How do I add more prompts?**
Add rows to `data/prompts.csv` maintaining the column structure. No code changes needed.

**Can I add more languages?**
Add entries to the `LANGUAGES` dict in `config.py`. Everything else updates automatically.
