"""
run_pipeline.py — Master pipeline script
=========================================
Runs the full data pipeline in order. Each step is resumable
(interrupting and re-running skips already-completed work).

Usage:
    python run_pipeline.py                   # run all steps
    python run_pipeline.py --step translate  # one step only
    python run_pipeline.py --step outputs
    python run_pipeline.py --step score
    python run_pipeline.py --step review     # exports Malayalam review CSV
    python run_pipeline.py --step merge      # merges reviewed Malayalam back in

After completing all steps, browse the dataset:
    streamlit run app/streamlit_app.py

Then publish to Hugging Face:
    python -m pipeline.upload_hf --repo YOUR_USERNAME/multilingual-prompt-dataset-ml
"""

import argparse
import sys
import os


def check_env() -> None:
    """Warn about missing API keys before starting."""
    from config import GEMINI_API_KEY, HF_TOKEN

    warnings = []
    if not GEMINI_API_KEY:
        warnings.append("  GEMINI_API_KEY not set — step 'outputs' will fail")
    if not HF_TOKEN:
        warnings.append("  HF_TOKEN not set — upload step will require browser login")

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(w)
        print()


def step_translate() -> None:
    from pipeline.translate import run_translation_pipeline
    run_translation_pipeline()


def step_outputs() -> None:
    from pipeline.generate_outputs import run_output_generation
    run_output_generation()


def step_score() -> None:
    from pipeline.quality_score import score_prompts
    score_prompts()


def step_review() -> None:
    from pipeline.quality_score import export_malayalam_review
    export_malayalam_review()


def step_merge() -> None:
    from pipeline.quality_score import merge_malayalam_review
    merge_malayalam_review()


STEPS = {
    "translate": step_translate,
    "outputs":   step_outputs,
    "score":     step_score,
    "review":    step_review,
    "merge":     step_merge,
}

PIPELINE_ORDER = ["translate", "outputs", "score", "review", "merge"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Multilingual Prompt Dataset Builder — master pipeline"
    )
    parser.add_argument(
        "--step",
        choices=list(STEPS.keys()),
        default=None,
        help="Run a single step (default: run all steps in order)",
    )
    args = parser.parse_args()

    check_env()

    if args.step:
        print(f"\nRunning step: {args.step}\n")
        STEPS[args.step]()
    else:
        print("\nRunning full pipeline...\n")
        print("NOTE: After 'review', open data/malayalam_review.csv,")
        print("      complete the native-speaker review, then re-run with --step merge.\n")

        for step_name in PIPELINE_ORDER:
            if step_name == "merge":
                print("\nPipeline paused after 'review'.")
                print("Open data/malayalam_review.csv, complete the review, then run:")
                print("    python run_pipeline.py --step merge\n")
                break
            STEPS[step_name]()

        print("\nNext steps:")
        print("  1. Open data/malayalam_review.csv and complete the native-speaker review")
        print("  2. python run_pipeline.py --step merge")
        print("  3. streamlit run app/streamlit_app.py")
        print("  4. python -m pipeline.upload_hf --repo YOUR_USERNAME/multilingual-prompt-dataset-ml\n")


if __name__ == "__main__":
    main()
