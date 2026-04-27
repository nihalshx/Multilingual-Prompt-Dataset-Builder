# 🌍 Multilingual Prompt Dataset Builder

A production-ready pipeline for building, scoring, and publishing a high-quality **multilingual LLM prompt dataset** — spanning **7 languages** and **5 task categories** — with native-speaker verified Malayalam translations and a Streamlit control panel.

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Datasets-orange.svg)](https://huggingface.co/datasets)

---

## 📖 Overview

The **Multilingual Prompt Dataset Builder** automates the full lifecycle of a research-grade prompt dataset:

1. **Translate** — English prompts → 6 target languages (free or paid API)
2. **Generate outputs** — Gemini 1.5 Flash creates gold-standard reference responses
3. **Score quality** — automated clarity, specificity, and completeness scoring (1–5)
4. **Human review** — native Malayalam speaker verifies and corrects translations
5. **Publish** — push to Hugging Face Hub with a full dataset card

The Streamlit UI lets you run every step from a browser without touching the command line.

---

## ✨ Key Features

| Feature | Detail |
|---|---|
| 🌐 **7 Languages** | English, Malayalam, Hindi, Arabic, Chinese (Simplified), Spanish, French |
| 📝 **5 Task Types** | Summarisation, Q&A, Creative Writing, Instruction Following, Reasoning |
| 🤖 **AI Outputs** | Reference responses via Gemini 1.5 Flash (resumable, checkpointed) |
| 📊 **Quality Scores** | Clarity · Specificity · Completeness · Composite score (1–5) |
| 🧑‍🏫 **Human-Verified ML** | Malayalam translations reviewed by a native speaker — rare in open datasets |
| 🔁 **Resumable Pipeline** | Every step can be safely interrupted and re-run |
| 🖥️ **Streamlit UI** | Full control panel — no CLI required |
| 🚀 **HF Publishing** | One-click upload with auto-generated dataset card |

---

## 🗂️ Project Structure

```
Multilingual Prompt Dataset Builder/
│
├── app/
│   └── streamlit_app.py        # Streamlit control panel (4 tabs)
│
├── pipeline/
│   ├── __init__.py
│   ├── translate.py            # Step 1 — multilingual translation
│   ├── generate_outputs.py     # Step 2 — Gemini reference output generation
│   ├── quality_score.py        # Step 3 — automated quality scoring
│   └── upload_hf.py            # Step 5 — Hugging Face publishing
│
├── data/
│   ├── prompts.csv             # Source English prompts
│   ├── translated_prompts.csv  # After Step 1
│   ├── dataset_with_outputs.csv# After Step 2
│   ├── dataset_scored.csv      # After Step 3
│   ├── malayalam_review.csv    # Native-speaker review file (Step 4)
│   ├── dataset_final.csv       # Final merged dataset
│   └── dataset_card_preview.md # HF dataset card preview
│
├── config.py                   # Centralized config (paths, keys, settings)
├── run_pipeline.py             # Master CLI pipeline runner
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/multilingual-prompt-dataset-builder.git
cd multilingual-prompt-dataset-builder
pip install -r requirements.txt
```

### 2. Launch the Streamlit UI *(recommended)*

```bash
streamlit run app/streamlit_app.py
```

Open the **⚙ Settings** tab and enter your API keys — no `.env` file needed.

### 3. Run via CLI *(alternative)*

```bash
# Run all steps (1→4, then prompts you for --step merge)
python run_pipeline.py

# Or run individual steps
python run_pipeline.py --step translate
python run_pipeline.py --step outputs
python run_pipeline.py --step score
python run_pipeline.py --step review    # export Malayalam review CSV
python run_pipeline.py --step merge     # merge reviewed Malayalam back in
```

---

## 🔑 API Keys

| Key | Required | Used For | Get It |
|---|---|---|---|
| `GEMINI_API_KEY` | ✅ Yes | Step 2 — generate reference outputs | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| `GOOGLE_CLOUD_API_KEY` | ⬜ Optional | Step 1 — higher-quality translation (falls back to free `googletrans`) | [Google Cloud Console](https://console.cloud.google.com) |
| `HF_TOKEN` | ✅ Yes | Step 5 — publish to Hugging Face | [HF Settings → Tokens](https://huggingface.co/settings/tokens) (Write token) |

> **Security:** Keys entered in the Streamlit UI are stored only in your browser session — never written to disk.

---

## ⚙️ Pipeline Steps

### Step 1 — Translation (`pipeline/translate.py`)

Translates every English prompt into 6 languages using either:
- **`googletrans`** (free, ~100 req/hour, no key required) — default
- **Google Cloud Translation API** (higher reliability, paid) — activated when `GOOGLE_CLOUD_API_KEY` is set

The pipeline saves a checkpoint every 10 rows. Rows that already have a translation are skipped on re-run.

**Target languages:**

| Code | Language |
|---|---|
| `ml` | Malayalam 🇮🇳 |
| `hi` | Hindi 🇮🇳 |
| `ar` | Arabic 🇸🇦 |
| `zh-cn` | Chinese (Simplified) 🇨🇳 |
| `es` | Spanish 🇪🇸 |
| `fr` | French 🇫🇷 |

---

### Step 2 — Reference Output Generation (`pipeline/generate_outputs.py`)

Calls **Gemini 1.5 Flash** with task-specific system prompts to produce gold-standard reference responses for every English prompt. Features:
- Exponential back-off retry (3 attempts)
- Checkpoint saved every 20 rows
- Already-generated outputs are skipped safely on re-run

**Task-type system prompts:**

| Category | Gemini Instruction |
|---|---|
| `summarisation` | Produce a clear, faithful summary |
| `question_answering` | Give a precise, accurate answer |
| `creative_writing` | Write with genuine creativity and craft |
| `instruction_following` | Follow the instruction exactly and completely |
| `reasoning` | Show step-by-step working before the final answer |

---

### Step 3 — Quality Scoring (`pipeline/quality_score.py`)

Each English prompt is automatically scored on three dimensions:

| Dimension | Weight | Method |
|---|---|---|
| **Clarity** | 40% | Inverse of sentence-length variance |
| **Specificity** | 35% | Density of concrete nouns, numbers, and instruction verbs |
| **Completeness** | 25% | Word count vs. per-task-type norms |

Composite `quality_score` = weighted average, scaled **1–5**.

**Task-type word-count norms:**

| Task | Min | Ideal | Max |
|---|---|---|---|
| Summarisation | 30 | 80 | 250 |
| Question Answering | 20 | 60 | 200 |
| Creative Writing | 40 | 120 | 400 |
| Instruction Following | 10 | 30 | 120 |
| Reasoning | 20 | 50 | 150 |

---

### Step 4 — Malayalam Native-Speaker Review

Exports `data/malayalam_review.csv` with columns:

| Column | Description |
|---|---|
| `prompt_en` | Original English prompt |
| `prompt_ml_auto` | Machine-translated Malayalam |
| `prompt_ml_corrected` | ← Reviewer fills this if needed |
| `ml_review_status` | `pending` / `approved` / `corrected` |
| `ml_reviewer_notes` | Optional notes |

Open the file in Excel or Google Sheets, review, then run `--step merge` to fold the corrections back in.

---

### Step 5 — Publish to Hugging Face (`pipeline/upload_hf.py`)

Uploads the final dataset + a full dataset card to the Hugging Face Hub:

```bash
python -m pipeline.upload_hf --repo YOUR_USERNAME/multilingual-prompt-dataset-ml
```

Preview the dataset card locally without uploading:

```bash
python -m pipeline.upload_hf --preview-card
```

---

## 🖥️ Streamlit UI

Run `streamlit run app/streamlit_app.py` to access the 4-tab control panel:

| Tab | Description |
|---|---|
| **⚙ Settings** | Enter API keys securely (session-only, never persisted) |
| **🚀 Pipeline** | Run / re-run each pipeline step with progress feedback |
| **🌍 Browse** | Filter by category, difficulty, quality; view side-by-side translations |
| **🚩 Flagged** | Review and export translations flagged as poor quality |

The Browse tab supports:
- Filter by task category, difficulty level, and quality score range
- Side-by-side multi-language prompt view
- Show/hide Gemini reference output
- Paginated display (5 / 10 / 20 / 50 rows per page)
- Download filtered subset as CSV
- Flag individual translations with a reason

---

## 📊 Dataset Schema

The final dataset (`data/dataset_final.csv`) contains:

| Column | Type | Description |
|---|---|---|
| `prompt_en` | string | Original English prompt |
| `prompt_ml` | string | Malayalam (human-verified) |
| `prompt_hi` | string | Hindi (machine-translated) |
| `prompt_ar` | string | Arabic (machine-translated) |
| `prompt_zh_cn` | string | Chinese/Mandarin (machine-translated) |
| `prompt_es` | string | Spanish (machine-translated) |
| `prompt_fr` | string | French (machine-translated) |
| `task_category` | string | One of 5 task types |
| `difficulty` | string | `easy` / `medium` / `hard` |
| `expected_output` | string | Gemini 1.5 Flash reference response |
| `quality_score` | float | Composite score (1–5) |
| `clarity_score` | float | Sentence-length variance score (1–5) |
| `specificity_score` | float | Concrete noun/verb density score (1–5) |
| `completeness_score` | float | Word-count norm score (1–5) |
| `ml_review_status` | string | `approved` / `corrected` / `pending` |
| `ml_reviewer_notes` | string | Optional reviewer notes |

---

## 📦 Requirements

```
# Core pipeline
googletrans==4.0.0-rc1
google-generativeai>=0.5.0
google-cloud-translate>=3.0.0
pandas>=2.0.0
numpy>=1.24.0
tqdm>=4.66.0
requests>=2.31.0

# Publishing
datasets>=2.14.0
huggingface_hub>=0.20.0

# UI
streamlit>=1.30.0
```

Install with:

```bash
pip install -r requirements.txt
```

---

## 🎯 Intended Uses

- **LLM evaluation** — compare model outputs against `expected_output` baselines
- **Fine-tuning** — prompt-response pairs as supervised training data
- **Cross-lingual research** — prompt transfer across 7 language families
- **Malayalam NLP** — the human-verified Malayalam subset is immediately usable for low-resource NLP

---

## ⚠️ Limitations

- Machine translations (all languages except Malayalam) are unverified by native speakers
- Reference outputs are AI-generated (Gemini 1.5 Flash) and may reflect model biases
- Creative prompts may embed cultural assumptions of the English-speaking world

---

## 📄 License

This project is released under the **CC BY 4.0** license.  
You are free to share and adapt the material for any purpose, provided appropriate credit is given.

---

## 🙏 Acknowledgements

- [Google Gemini](https://deepmind.google/technologies/gemini/) for reference output generation
- [Google Cloud Translation](https://cloud.google.com/translate) for multilingual translation
- [Hugging Face](https://huggingface.co/) for dataset hosting and the `datasets` library
- [Streamlit](https://streamlit.io/) for the interactive UI framework
