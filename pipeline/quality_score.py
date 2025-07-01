"""
pipeline/quality_score.py
=========================
Step 1 — Auto-scores every prompt on three dimensions:
    clarity      : sentence-length consistency (lower variance = clearer)
    specificity  : density of concrete nouns, numbers, and instruction verbs
    completeness : word count relative to task-type norms

Step 2 — Exports data/malayalam_review.csv for native-speaker review.
    Open the file in Excel or Google Sheets and for each row:
        - Set ml_review_status  = 'approved'  (if the auto-translation is accurate)
        - Set ml_review_status  = 'corrected' (if you've fixed it)
        - Paste the corrected Malayalam in prompt_ml_corrected

Step 3 — Merges the reviewed Malayalam back into the dataset.

Usage:
    python -m pipeline.quality_score                  # run all three steps
    python -m pipeline.quality_score --score          # step 1 only
    python -m pipeline.quality_score --review         # step 2 only
    python -m pipeline.quality_score --merge          # step 3 only
"""

import re
import os
import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm

from config import (
    OUTPUTS_CSV,
    SCORED_CSV,
    MALAYALAM_REVIEW_CSV,
    FINAL_CSV,
    DATA_DIR,
    QUALITY_WEIGHTS,
    TASK_WORD_NORMS,
)


# ── Scoring helpers ───────────────────────────────────────────────────────────

_SPECIFICITY_RE = re.compile(
    r"\b(\d+[\.,]?\d*"
    r"|[A-Z][a-z]+(?:\s[A-Z][a-z]+)*"
    r"|exactly|specific|precisely|at least|at most|between"
    r"|list|name|describe|calculate|convert|translate"
    r"|write a \w+ function|SQL|regex|CSS|JSON|Markdown)\b"
)


def _clarity(text: str) -> float:
    """Sentence-length variance → 1–5 (5 = most clear)."""
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    if len(sentences) < 2:
        return 5.0
    variance = np.var([len(s.split()) for s in sentences])
    return round(float(np.clip(5.0 - variance / 10, 1.0, 5.0)), 2)


def _specificity(text: str) -> float:
    """Concrete-noun / instruction-verb density → 1–5."""
    words = text.split()
    if not words:
        return 1.0
    density = len(_SPECIFICITY_RE.findall(text)) / len(words)
    return round(float(np.clip(1.0 + density / 0.05, 1.0, 5.0)), 2)


def _completeness(text: str, task: str) -> float:
    """Word count vs task-type norms → 1–5."""
    norms = TASK_WORD_NORMS.get(task, {"min": 10, "ideal": 50, "max": 200})
    wc = len(text.split())

    if wc < norms["min"]:
        score = 1.0 + (wc / norms["min"]) * 2
    elif wc <= norms["ideal"]:
        score = 3.0 + ((wc - norms["min"]) / (norms["ideal"] - norms["min"])) * 2
    elif wc <= norms["max"]:
        score = 5.0 - ((wc - norms["ideal"]) / (norms["max"] - norms["ideal"])) * 1.5
    else:
        score = 2.0

    return round(float(np.clip(score, 1.0, 5.0)), 2)


def _composite(clarity: float, specificity: float, completeness: float) -> float:
    """Weighted composite quality score (1–5)."""
    w = QUALITY_WEIGHTS
    return round(
        w["clarity"] * clarity
        + w["specificity"] * specificity
        + w["completeness"] * completeness,
        2,
    )


# ── Step 1: Score ─────────────────────────────────────────────────────────────

def score_prompts(
    input_path: str = OUTPUTS_CSV,
    output_path: str = SCORED_CSV,
) -> pd.DataFrame:
    """Compute quality scores for every prompt and save to output_path."""
    os.makedirs(DATA_DIR, exist_ok=True)

    print(f"\n{'='*60}")
    print("  STEP 1 — QUALITY SCORING")
    print(f"  Input  : {input_path}")
    print(f"  Output : {output_path}")
    print(f"{'='*60}\n")

    df = pd.read_csv(input_path)
    records = []

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Scoring"):
        c  = _clarity(row["prompt_en"])
        s  = _specificity(row["prompt_en"])
        co = _completeness(row["prompt_en"], row["task_category"])
        records.append({"clarity_score": c, "specificity_score": s,
                        "completeness_score": co, "quality_score": _composite(c, s, co)})

    scores = pd.DataFrame(records)
    df = pd.concat([df, scores], axis=1)
    df.to_csv(output_path, index=False)

    print(f"\n  Score averages:")
    print(f"    Clarity     : {df['clarity_score'].mean():.2f}")
    print(f"    Specificity : {df['specificity_score'].mean():.2f}")
    print(f"    Completeness: {df['completeness_score'].mean():.2f}")
    print(f"    Quality     : {df['quality_score'].mean():.2f}  "
          f"(min {df['quality_score'].min():.2f} / max {df['quality_score'].max():.2f})")
    print(f"  Saved: {output_path}\n")

    return df


# ── Step 2: Export Malayalam review file ──────────────────────────────────────

def export_malayalam_review(
    input_path: str = SCORED_CSV,
    review_path: str = MALAYALAM_REVIEW_CSV,
) -> pd.DataFrame:
    """Export a review CSV for native-speaker Malayalam verification."""
    os.makedirs(DATA_DIR, exist_ok=True)

    print(f"\n{'='*60}")
    print("  STEP 2 — MALAYALAM REVIEW EXPORT")
    print(f"  Input  : {input_path}")
    print(f"  Output : {review_path}")
    print(f"{'='*60}\n")

    df = pd.read_csv(input_path)

    review_df = pd.DataFrame({
        "row_id":               df.index,
        "prompt_en":            df["prompt_en"],
        "task_category":        df["task_category"],
        "difficulty":           df["difficulty"],
        "prompt_ml_auto":       df.get("prompt_ml", ""),
        "prompt_ml_corrected":  "",        # ← native speaker fills this
        "ml_review_status":     "pending", # pending | approved | corrected
        "ml_reviewer_notes":    "",
    })

    review_df.to_csv(review_path, index=False)

    print(f"  Exported {len(review_df)} rows to {review_path}")
    print()
    print("  Instructions:")
    print("  1. Open data/malayalam_review.csv in Excel or Google Sheets")
    print("  2. For each row, read 'prompt_ml_auto' (machine translation)")
    print("  3. If accurate → set ml_review_status = 'approved'")
    print("  4. If needs fixing → set ml_review_status = 'corrected'")
    print("               → write corrected Malayalam in prompt_ml_corrected")
    print("  5. Save and run: python -m pipeline.quality_score --merge\n")

    return review_df


# ── Step 3: Merge reviewed Malayalam ─────────────────────────────────────────

def merge_malayalam_review(
    dataset_path: str = SCORED_CSV,
    review_path: str = MALAYALAM_REVIEW_CSV,
    output_path: str = FINAL_CSV,
) -> pd.DataFrame:
    """Merge the native-reviewed Malayalam translations back into the dataset."""
    os.makedirs(DATA_DIR, exist_ok=True)

    print(f"\n{'='*60}")
    print("  STEP 3 — MERGE MALAYALAM REVIEW")
    print(f"  Dataset : {dataset_path}")
    print(f"  Review  : {review_path}")
    print(f"  Output  : {output_path}")
    print(f"{'='*60}\n")

    df     = pd.read_csv(dataset_path)
    review = pd.read_csv(review_path)

    def _pick(row):
        if (row["ml_review_status"] == "corrected"
                and pd.notna(row["prompt_ml_corrected"])
                and str(row["prompt_ml_corrected"]).strip()):
            return str(row["prompt_ml_corrected"]).strip()
        return row.get("prompt_ml_auto", "")

    review["prompt_ml_final"] = review.apply(_pick, axis=1)

    df["prompt_ml"]          = review["prompt_ml_final"].values
    df["ml_review_status"]   = review["ml_review_status"].values
    df["ml_reviewer_notes"]  = review.get("ml_reviewer_notes", "").values

    df.to_csv(output_path, index=False)

    approved  = (review["ml_review_status"] == "approved").sum()
    corrected = (review["ml_review_status"] == "corrected").sum()
    pending   = (review["ml_review_status"] == "pending").sum()

    print(f"  Merged successfully → {output_path}")
    print(f"  Review status:")
    print(f"    Approved  : {approved}")
    print(f"    Corrected : {corrected}")
    print(f"    Pending   : {pending}  (kept auto-translation)\n")

    return df


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quality Scoring + Malayalam Review")
    parser.add_argument("--score",  action="store_true")
    parser.add_argument("--review", action="store_true")
    parser.add_argument("--merge",  action="store_true")
    args = parser.parse_args()

    run_all = not (args.score or args.review or args.merge)

    if args.score  or run_all: score_prompts()
    if args.review or run_all: export_malayalam_review()
    if args.merge  or run_all: merge_malayalam_review()

    if run_all:
        print("All steps complete. Final dataset: data/dataset_final.csv\n")
