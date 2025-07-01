"""
pipeline — core data engineering modules

Modules:
    translate        : translates English prompts into 6 target languages
    generate_outputs : generates Gemini reference outputs for each prompt
    quality_score    : computes multi-dimensional quality scores + Malayalam review
    upload_hf        : publishes the final dataset to Hugging Face Hub
"""
