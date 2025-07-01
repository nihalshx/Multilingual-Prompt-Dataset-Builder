"""
config.py — Centralized project configuration
API keys are entered through the Streamlit UI (app/streamlit_app.py ⚙ Settings tab).
The pipeline modules read keys from environment variables set at runtime by the UI.
"""

import os

# ── API Keys (set at runtime by the Streamlit UI) ─────────────────────────────

GEMINI_API_KEY       = os.getenv("GEMINI_API_KEY", "")
GOOGLE_CLOUD_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY", "")
HF_TOKEN             = os.getenv("HF_TOKEN", "")
USE_CLOUD_TRANSLATE  = bool(GOOGLE_CLOUD_API_KEY)

# ── Paths ─────────────────────────────────────────────────────────────────────

DATA_DIR              = "data"
PROMPTS_CSV           = "data/prompts.csv"
TRANSLATED_CSV        = "data/translated_prompts.csv"
OUTPUTS_CSV           = "data/dataset_with_outputs.csv"
SCORED_CSV            = "data/dataset_scored.csv"
MALAYALAM_REVIEW_CSV  = "data/malayalam_review.csv"
FINAL_CSV             = "data/dataset_final.csv"
FLAGGED_CSV           = "data/flagged_translations.csv"
DATASET_CARD_PREVIEW  = "data/dataset_card_preview.md"

# ── Languages ─────────────────────────────────────────────────────────────────

LANGUAGES = {
    "ml":    "Malayalam",
    "hi":    "Hindi",
    "ar":    "Arabic",
    "zh-cn": "Chinese",
    "es":    "Spanish",
    "fr":    "French",
}

LANG_COLUMNS = {
    code: f"prompt_{code.replace('-', '_')}"
    for code in LANGUAGES
}

# ── Gemini settings ───────────────────────────────────────────────────────────

GEMINI_MODEL         = "gemini-1.5-flash"
GEMINI_REQUEST_DELAY = 1.5
GEMINI_RETRIES       = 3

# ── Translation settings ──────────────────────────────────────────────────────

TRANSLATE_DELAY      = 0.5
TRANSLATE_CHECKPOINT = 10

# ── Quality scoring ───────────────────────────────────────────────────────────

QUALITY_WEIGHTS = {
    "clarity":      0.40,
    "specificity":  0.35,
    "completeness": 0.25,
}

TASK_WORD_NORMS = {
    "summarisation":         {"min": 30,  "ideal": 80,  "max": 250},
    "question_answering":    {"min": 20,  "ideal": 60,  "max": 200},
    "creative_writing":      {"min": 40,  "ideal": 120, "max": 400},
    "instruction_following": {"min": 10,  "ideal": 30,  "max": 120},
    "reasoning":             {"min": 20,  "ideal": 50,  "max": 150},
}

# ── Dataset card metadata ─────────────────────────────────────────────────────

DATASET_LICENSE   = "cc-by-4.0"
DATASET_LANGUAGES = ["en", "ml", "hi", "ar", "zh", "es", "fr"]
