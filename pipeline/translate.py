"""
pipeline/translate.py
=====================
Translates all English prompts into the 6 target languages defined in config.py.

Backends:
  - googletrans (default, free, ~100 req/hour, no key required)
  - Google Cloud Translation API (set GOOGLE_CLOUD_API_KEY in .env for reliability)

The pipeline is resumable: rows that already have a translation are skipped,
so it is safe to interrupt and re-run at any time.

Usage (standalone):
    python -m pipeline.translate

Usage (from run_pipeline.py):
    from pipeline.translate import run_translation_pipeline
    run_translation_pipeline()
"""

import os
import time
import requests
import pandas as pd
from tqdm import tqdm

from config import (
    LANGUAGES,
    LANG_COLUMNS,
    PROMPTS_CSV,
    TRANSLATED_CSV,
    DATA_DIR,
    USE_CLOUD_TRANSLATE,
    GOOGLE_CLOUD_API_KEY,
    TRANSLATE_DELAY,
    TRANSLATE_CHECKPOINT,
)


# ── Translation backends ──────────────────────────────────────────────────────

def _translate_googletrans(text: str, lang_code: str) -> str:
    """Free translation via googletrans (no API key required)."""
    try:
        from googletrans import Translator
        # googletrans uses zh-CN not zh-cn
        mapped = {"zh-cn": "zh-CN"}.get(lang_code, lang_code)
        result = Translator().translate(text, dest=mapped)
        return result.text
    except Exception as exc:
        print(f"  [googletrans] {lang_code}: {exc}")
        return ""


def _translate_cloud_api(text: str, lang_code: str) -> str:
    """Paid translation via Google Cloud Translation API (higher reliability)."""
    try:
        url = "https://translation.googleapis.com/language/translate/v2"
        resp = requests.post(
            url,
            params={
                "q": text,
                "target": lang_code,
                "source": "en",
                "key": GOOGLE_CLOUD_API_KEY,
                "format": "text",
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["data"]["translations"][0]["translatedText"]
    except Exception as exc:
        print(f"  [cloud api] {lang_code}: {exc}")
        return ""


def translate(text: str, lang_code: str) -> str:
    """Route translation to the configured backend."""
    if USE_CLOUD_TRANSLATE:
        return _translate_cloud_api(text, lang_code)
    return _translate_googletrans(text, lang_code)


# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_translation_pipeline(
    input_path: str = PROMPTS_CSV,
    output_path: str = TRANSLATED_CSV,
    delay: float = TRANSLATE_DELAY,
) -> pd.DataFrame:
    """
    Translate all prompts in input_path into the 6 target languages.
    Saves a checkpoint every TRANSLATE_CHECKPOINT rows.
    Returns the completed DataFrame.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    backend = "Google Cloud Translation API" if USE_CLOUD_TRANSLATE else "googletrans (free)"
    print(f"\n{'='*60}")
    print("  TRANSLATION PIPELINE")
    print(f"  Backend : {backend}")
    print(f"  Input   : {input_path}")
    print(f"  Output  : {output_path}")
    print(f"{'='*60}\n")

    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} prompts.\n")

    # Initialise language columns if not present
    for col in LANG_COLUMNS.values():
        if col not in df.columns:
            df[col] = ""

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Translating"):
        for lang_code, col in LANG_COLUMNS.items():
            # Skip rows already translated (allows safe resume)
            if pd.notna(df.at[idx, col]) and str(df.at[idx, col]).strip():
                continue

            df.at[idx, col] = translate(row["prompt_en"], lang_code)
            time.sleep(delay)

        if (idx + 1) % TRANSLATE_CHECKPOINT == 0:
            df.to_csv(output_path, index=False)
            print(f"  [checkpoint] row {idx + 1} saved.")

    df.to_csv(output_path, index=False)

    print(f"\n{'='*60}")
    print("  TRANSLATION COMPLETE")
    print(f"  Rows : {len(df)}")
    for lang_code, lang_name in LANGUAGES.items():
        col = LANG_COLUMNS[lang_code]
        filled = df[col].notna() & (df[col].astype(str).str.strip() != "")
        status = "OK" if filled.sum() == len(df) else f"PARTIAL ({filled.sum()}/{len(df)})"
        print(f"  {lang_name:<12} {status}")
    print(f"  Saved : {output_path}\n")

    return df


if __name__ == "__main__":
    run_translation_pipeline()
