"""
pipeline/generate_outputs.py
============================
Calls the Gemini API to generate ideal reference outputs for each English prompt.
These outputs serve as gold-standard baselines for downstream LLM evaluation.

Requires:
    GEMINI_API_KEY in .env  (free at https://makersuite.google.com/app/apikey)

Usage (standalone):
    python -m pipeline.generate_outputs

Usage (from run_pipeline.py):
    from pipeline.generate_outputs import run_output_generation
    run_output_generation()
"""

import os
import time
import pandas as pd
from tqdm import tqdm

from config import (
    TRANSLATED_CSV,
    OUTPUTS_CSV,
    DATA_DIR,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_REQUEST_DELAY,
    GEMINI_RETRIES,
)


# ── System prompt ─────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are an expert AI assistant producing ideal, high-quality reference
responses for a multilingual research dataset. Your outputs will be used as gold-standard
baselines to evaluate other language models.

Guidelines:
- Be accurate, clear, and well-structured.
- Match response length and format to the task type:
    summarisation       → faithful, concise
    question_answering  → precise and direct
    creative_writing    → genuinely creative and expressive
    instruction_following → complete the task exactly as specified
    reasoning           → show working step by step before the final answer
- Avoid filler, excessive caveats, or repetition.
- Output the response only — no preamble like "Here is my response:"."""

_TASK_HINTS = {
    "summarisation":         "Produce a clear, faithful summary.",
    "question_answering":    "Give a precise, accurate answer.",
    "creative_writing":      "Write with genuine creativity and craft.",
    "instruction_following": "Follow the instruction exactly and completely.",
    "reasoning":             "Show your reasoning step by step before giving the final answer.",
}


# ── Gemini client ─────────────────────────────────────────────────────────────

def _get_model():
    """Initialise and return the configured Gemini GenerativeModel."""
    import google.generativeai as genai

    if not GEMINI_API_KEY:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set.\n"
            "Get a free key at https://makersuite.google.com/app/apikey "
            "and add it to your .env file."
        )

    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=_SYSTEM_PROMPT,
    )


def _generate(model, prompt: str, task_category: str) -> str:
    """Generate a single reference output with exponential back-off retries."""
    hint = _TASK_HINTS.get(task_category, "")
    full_prompt = f"{hint}\n\n{prompt}" if hint else prompt

    for attempt in range(GEMINI_RETRIES):
        try:
            return model.generate_content(full_prompt).text.strip()
        except Exception as exc:
            wait = 2 ** attempt
            if attempt < GEMINI_RETRIES - 1:
                print(f"\n  [gemini] attempt {attempt + 1} failed: {exc} — retry in {wait}s")
                time.sleep(wait)
            else:
                print(f"\n  [gemini] all retries exhausted: {exc}")
                return ""


# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_output_generation(
    input_path: str = TRANSLATED_CSV,
    output_path: str = OUTPUTS_CSV,
    delay: float = GEMINI_REQUEST_DELAY,
) -> pd.DataFrame:
    """
    For each English prompt in input_path, call Gemini to generate an ideal
    reference output. Saves checkpoints every 20 rows. Returns the DataFrame.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    print(f"\n{'='*60}")
    print("  REFERENCE OUTPUT GENERATION  (Gemini)")
    print(f"  Model  : {GEMINI_MODEL}")
    print(f"  Input  : {input_path}")
    print(f"  Output : {output_path}")
    print(f"{'='*60}\n")

    df = pd.read_csv(input_path)

    if "expected_output" not in df.columns:
        df["expected_output"] = ""

    model = _get_model()
    print("Gemini model ready.\n")

    generated = 0
    skipped = 0

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Generating"):
        existing = str(row.get("expected_output", "")).strip()
        if existing and pd.notna(row.get("expected_output")):
            skipped += 1
            continue

        df.at[idx, "expected_output"] = _generate(model, row["prompt_en"], row["task_category"])
        generated += 1
        time.sleep(delay)

        if generated % 20 == 0:
            df.to_csv(output_path, index=False)
            print(f"  [checkpoint] {generated} outputs generated (row {idx + 1}).")

    df.to_csv(output_path, index=False)

    print(f"\n{'='*60}")
    print("  GENERATION COMPLETE")
    print(f"  Generated : {generated}")
    print(f"  Skipped   : {skipped}  (already existed)")
    print(f"  Total     : {len(df)}")
    print(f"  Saved     : {output_path}\n")

    return df


if __name__ == "__main__":
    run_output_generation()
