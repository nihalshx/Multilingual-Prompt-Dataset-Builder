"""
pipeline/upload_hf.py
=====================
Publishes the final dataset to Hugging Face Hub and writes a full dataset card.

Requires:
    HF_TOKEN in .env  (https://huggingface.co/settings/tokens → Write token)

Usage:
    python -m pipeline.upload_hf --repo YOUR_USERNAME/multilingual-prompt-dataset-ml
    python -m pipeline.upload_hf --preview-card   # write dataset card locally only
"""

import os
import argparse
import pandas as pd

from config import (
    FINAL_CSV,
    DATASET_CARD_PREVIEW,
    DATA_DIR,
    HF_TOKEN,
    DATASET_LICENSE,
    DATASET_LANGUAGES,
)


# ── Dataset card ──────────────────────────────────────────────────────────────

DATASET_CARD = f"""---
language:
{chr(10).join(f'- {lang}' for lang in DATASET_LANGUAGES)}
license: {DATASET_LICENSE}
task_categories:
- text-generation
- question-answering
- summarization
- text2text-generation
tags:
- multilingual
- malayalam
- prompt-dataset
- llm-evaluation
- fine-tuning
- human-verified
- quality-annotated
pretty_name: Multilingual Prompt Dataset with Human-Verified Malayalam
size_categories:
- 1K<n<10K
---

# Multilingual Prompt Dataset with Human-Verified Malayalam

## Dataset Summary

A structured, quality-labelled dataset of **700+ prompt-response pairs** across
**7 languages** and **5 task categories**, designed for LLM evaluation, fine-tuning,
and cross-lingual transfer research.

**Key differentiator:** All Malayalam translations were reviewed and corrected by a
native Malayalam speaker — one of the few open datasets with human-verified Malayalam
prompt content.

## Languages

| Code | Language  |   Speakers | Notes                                       |
|------|-----------|----------:|---------------------------------------------|
| en   | English   |      1.5B+ | Source language; all reference outputs      |
| ml   | Malayalam |        38M | **Native-speaker verified** ← unique        |
| hi   | Hindi     |       580M | Largest underserved language in AI datasets |
| ar   | Arabic    |      300M+ | Right-to-left; tests structural robustness  |
| zh   | Chinese   |      1.3B+ | Mandarin (Simplified)                       |
| es   | Spanish   |      500M+ | Well-documented; useful for benchmarking    |
| fr   | French    |      300M+ | Broad European coverage                     |

## Task Categories

| Category              | Count | Description                                     |
|-----------------------|------:|-------------------------------------------------|
| summarisation         |    20 | Condense text, write abstracts, create TL;DRs   |
| question_answering    |    20 | Factual, explanatory, and analytical questions  |
| creative_writing      |    20 | Stories, poems, dialogue, product copy          |
| instruction_following |    20 | Code tasks, formatting, structured output       |
| reasoning             |    20 | Logic puzzles, maths, step-by-step deduction    |

## Dataset Structure

### Data Fields

| Column                | Type   | Description                                              |
|-----------------------|--------|----------------------------------------------------------|
| `prompt_en`           | string | Original English prompt                                  |
| `prompt_ml`           | string | Malayalam prompt (human-verified)                        |
| `prompt_hi`           | string | Hindi prompt (machine-translated)                        |
| `prompt_ar`           | string | Arabic prompt (machine-translated)                       |
| `prompt_zh_cn`        | string | Chinese/Mandarin prompt (machine-translated)             |
| `prompt_es`           | string | Spanish prompt (machine-translated)                      |
| `prompt_fr`           | string | French prompt (machine-translated)                       |
| `task_category`       | string | Task type (five categories)                              |
| `difficulty`          | string | easy / medium / hard (manually assigned)                 |
| `expected_output`     | string | Reference response from Gemini 1.5 Flash (English)       |
| `quality_score`       | float  | Composite quality score 1–5                              |
| `clarity_score`       | float  | Sentence-length variance metric (1–5)                    |
| `specificity_score`   | float  | Concrete noun / instruction-verb density (1–5)           |
| `completeness_score`  | float  | Word count vs task-type norms (1–5)                      |
| `ml_review_status`    | string | approved / corrected / pending (Malayalam only)          |

## Dataset Creation

### Source Data

100 English prompts were authored manually with attention to clarity, specificity,
and cross-lingual transferability across agglutinative (Malayalam, Hindi), Semitic
(Arabic), tonal (Chinese), and Romance (Spanish, French) language families.

### Translation

Translations were generated using the Google Cloud Translation API. All Malayalam
translations were subsequently reviewed and where necessary corrected by the dataset
author, a native Malayalam speaker from Kerala, India.

### Expected Outputs

Reference outputs were generated using **Gemini 1.5 Flash** with task-type-specific
system prompts. These serve as quality baselines for evaluation, not as ground truth.

### Quality Annotation

Each prompt is scored on three normalised dimensions:

1. **Clarity (40%)** — inverse of sentence-length variance
2. **Specificity (35%)** — density of concrete nouns, numbers, and instruction verbs
3. **Completeness (25%)** — word count relative to per-category norms

Composite `quality_score` = weighted average, scaled 1–5.

## Intended Uses

- **LLM evaluation**: compare model outputs against `expected_output` baselines
- **Fine-tuning**: prompt-response pairs as supervised training data
- **Cross-lingual research**: prompt transfer across seven language families
- **Malayalam NLP**: the human-verified Malayalam subset is immediately usable

## Limitations

- Machine translations (all languages except Malayalam) are unverified
- Expected outputs are AI-generated and may reflect Gemini's biases
- Creative prompts may embed cultural assumptions of the English-speaking world

## Citation

```bibtex
@dataset{{multilingual_prompt_dataset_ml_2025,
  title     = {{Multilingual Prompt Dataset with Human-Verified Malayalam}},
  author    = {{[Your Name]}},
  year      = {{2025}},
  publisher = {{Hugging Face}},
  url       = {{https://huggingface.co/datasets/[your-username]/multilingual-prompt-dataset-ml}},
  license   = {{CC-BY-4.0}}
}}
```

## Dataset Card Authors

[Your Name] — Kozhikode, Kerala, India.
Native Malayalam speaker motivated by the severe underrepresentation of verified
Malayalam content in open AI training datasets.
"""


# ── Upload ────────────────────────────────────────────────────────────────────

def preview_card(output_path: str = DATASET_CARD_PREVIEW) -> None:
    """Write the dataset card locally for review before uploading."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(DATASET_CARD)
    print(f"Dataset card written to {output_path}")


def upload_to_huggingface(
    repo_id: str,
    input_path: str = FINAL_CSV,
    token: str = HF_TOKEN,
) -> None:
    """Upload the final dataset and dataset card to Hugging Face Hub."""
    from datasets import Dataset
    from huggingface_hub import HfApi, login

    if not repo_id:
        raise ValueError("repo_id is required. Pass --repo YOUR_USERNAME/dataset-name")

    hf_token = token or HF_TOKEN
    if hf_token:
        login(token=hf_token, add_to_git_credential=False)
    else:
        print("No HF_TOKEN found — attempting browser login...")
        login()

    print(f"\n{'='*60}")
    print("  PUBLISHING TO HUGGING FACE")
    print(f"  Repo  : {repo_id}")
    print(f"  Input : {input_path}")
    print(f"{'='*60}\n")

    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} rows.")

    dataset = Dataset.from_pandas(df, preserve_index=False)
    dataset.push_to_hub(repo_id, token=hf_token)
    print("Dataset pushed.")

    HfApi().upload_file(
        path_or_fileobj=DATASET_CARD.encode("utf-8"),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="dataset",
        token=hf_token,
        commit_message="Add comprehensive dataset card",
    )

    print(f"\n{'='*60}")
    print("  PUBLISHED SUCCESSFULLY")
    print(f"  URL: https://huggingface.co/datasets/{repo_id}")
    print(f"{'='*60}\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload dataset to Hugging Face")
    parser.add_argument("--repo",         type=str, default=None,
                        help="HF repo ID, e.g. username/multilingual-prompt-dataset-ml")
    parser.add_argument("--token",        type=str, default=None,
                        help="HF API token (or set HF_TOKEN in .env)")
    parser.add_argument("--input",        type=str, default=FINAL_CSV,
                        help="Path to the final dataset CSV")
    parser.add_argument("--preview-card", action="store_true",
                        help="Write dataset card locally without uploading")
    args = parser.parse_args()

    if args.preview_card:
        preview_card()
    else:
        upload_to_huggingface(
            repo_id=args.repo,
            input_path=args.input,
            token=args.token or HF_TOKEN,
        )
