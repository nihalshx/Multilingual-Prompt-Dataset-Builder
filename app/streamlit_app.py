"""
app/streamlit_app.py
====================
Full control panel for the Multilingual Prompt Dataset Builder.

Tabs:
  ⚙  Settings    — enter API keys in the UI (no .env, no keys.py needed)
  🚀 Pipeline    — run each pipeline step from the UI
  🌍 Browse      — filter, view, and export the dataset
  🚩 Flagged     — review translations flagged as poor quality

Run from the project root:
    streamlit run app/streamlit_app.py
"""

import os
import sys
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    FINAL_CSV, SCORED_CSV, OUTPUTS_CSV, TRANSLATED_CSV, PROMPTS_CSV,
    FLAGGED_CSV, MALAYALAM_REVIEW_CSV, DATA_DIR,
)

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Multilingual Dataset Builder",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.badge-easy   { background:#d1fae5;color:#065f46;padding:2px 8px;border-radius:6px;font-size:11px;font-weight:600; }
.badge-medium { background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:6px;font-size:11px;font-weight:600; }
.badge-hard   { background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:6px;font-size:11px;font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────

for k, v in {"gemini_key": "", "gcloud_key": "", "hf_token": "",
              "flags": {}, "page": 0}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Constants ─────────────────────────────────────────────────────────────────

LANGUAGE_META = {
    "prompt_en":    ("🇬🇧", "English"),
    "prompt_ml":    ("🇮🇳", "Malayalam"),
    "prompt_hi":    ("🇮🇳", "Hindi"),
    "prompt_ar":    ("🇸🇦", "Arabic"),
    "prompt_zh_cn": ("🇨🇳", "Chinese"),
    "prompt_es":    ("🇪🇸", "Spanish"),
    "prompt_fr":    ("🇫🇷", "French"),
}

TASK_COLORS = {
    "summarisation":         "#3b82f6",
    "question_answering":    "#8b5cf6",
    "creative_writing":      "#ec4899",
    "instruction_following": "#f59e0b",
    "reasoning":             "#10b981",
}

def key_ok(k): return bool(k and k.strip() and "paste" not in k.lower())

@st.cache_data
def load_dataset():
    for path in [FINAL_CSV, SCORED_CSV, OUTPUTS_CSV, TRANSLATED_CSV, PROMPTS_CSV]:
        if os.path.exists(path):
            return pd.read_csv(path), path
    return pd.DataFrame(), ""

def reload_dataset():
    load_dataset.clear()

def save_flags(flags):
    os.makedirs(DATA_DIR, exist_ok=True)
    existing = {}
    if os.path.exists(FLAGGED_CSV):
        existing = {r["row_id"]: r for r in pd.read_csv(FLAGGED_CSV).to_dict("records")}
    existing.update(flags)
    pd.DataFrame(list(existing.values())).to_csv(FLAGGED_CSV, index=False)

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🌍 Dataset Builder")
    st.caption("Multilingual · 7 Languages · 200 Prompts")
    st.divider()
    g_dot = "🟢" if key_ok(st.session_state.gemini_key) else "🔴"
    h_dot = "🟢" if key_ok(st.session_state.hf_token)   else "🔴"
    st.markdown(f"Gemini {g_dot} &nbsp;&nbsp; HuggingFace {h_dot}")
    if not (key_ok(st.session_state.gemini_key) and key_ok(st.session_state.hf_token)):
        st.caption("→ Add keys in ⚙ Settings")
    st.divider()
    df_s, df_src = load_dataset()
    if not df_s.empty:
        st.metric("Dataset rows", f"{len(df_s):,}")
        st.caption(f"`{df_src}`")
        if st.button("🔄 Reload"):
            reload_dataset(); st.rerun()

# ── Tabs ──────────────────────────────────────────────────────────────────────

tab_settings, tab_pipeline, tab_browse, tab_flagged = st.tabs(
    ["⚙  Settings", "🚀 Pipeline", "🌍 Browse", "🚩 Flagged"]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Settings
# ══════════════════════════════════════════════════════════════════════════════

with tab_settings:
    st.header("⚙  API Keys")
    st.markdown(
        "Enter your keys here. They live only in your browser session — "
        "never written to disk or sent anywhere except the respective APIs."
    )
    st.divider()

    # Gemini
    st.subheader("1 · Gemini API Key")
    st.markdown("Free tier: ~15 req/min · [Get key →](https://makersuite.google.com/app/apikey)")
    g = st.text_input("Gemini key", value=st.session_state.gemini_key,
                       type="password", placeholder="AIza...", label_visibility="collapsed")
    if g != st.session_state.gemini_key:
        st.session_state.gemini_key = g
    if key_ok(g):   st.success("✅ Gemini key set")
    else:           st.error("❌ Required for Step 2 (generate outputs)")

    st.divider()

    # Google Cloud (optional)
    st.subheader("2 · Google Cloud Translation Key  *(optional)*")
    st.markdown("Leave blank to use free googletrans instead · [Get key →](https://console.cloud.google.com)")
    gc = st.text_input("Cloud key", value=st.session_state.gcloud_key,
                        type="password", placeholder="Leave blank for free googletrans",
                        label_visibility="collapsed")
    if gc != st.session_state.gcloud_key:
        st.session_state.gcloud_key = gc
    if key_ok(gc):  st.success("✅ Using Google Cloud Translation API")
    else:           st.info("ℹ️ Will use free googletrans")

    st.divider()

    # Hugging Face
    st.subheader("3 · Hugging Face Token")
    st.markdown("Create a **Write** token · [Get token →](https://huggingface.co/settings/tokens)")
    hf = st.text_input("HF token", value=st.session_state.hf_token,
                        type="password", placeholder="hf_...", label_visibility="collapsed")
    if hf != st.session_state.hf_token:
        st.session_state.hf_token = hf
    if key_ok(hf):  st.success("✅ Hugging Face token set")
    else:           st.error("❌ Required for Step 5 (publish dataset)")

    st.divider()
    st.subheader("Key Status")
    c1, c2, c3 = st.columns(3)
    c1.metric("Gemini",        "✅ Set"     if key_ok(st.session_state.gemini_key) else "❌ Missing")
    c2.metric("Google Cloud",  "✅ Set"     if key_ok(st.session_state.gcloud_key) else "— Optional")
    c3.metric("Hugging Face",  "✅ Set"     if key_ok(st.session_state.hf_token)   else "❌ Missing")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Pipeline
# ══════════════════════════════════════════════════════════════════════════════

with tab_pipeline:
    st.header("🚀 Pipeline Runner")
    st.markdown("Run each step in order. Every step is **resumable** — safe to interrupt and restart.")

    if not key_ok(st.session_state.gemini_key):
        st.warning("⚠️ Add your Gemini key in ⚙ Settings to enable Steps 2 and 5.")
    st.divider()

    # ── Step 1 ──
    with st.expander("**Step 1 — Translate into 6 languages**", expanded=True):
        st.caption("Malayalam · Hindi · Arabic · Chinese · Spanish · French")
        backend = "Google Cloud API" if key_ok(st.session_state.gcloud_key) else "googletrans (free)"
        st.info(f"Backend: **{backend}**")

        t_out = os.path.exists(TRANSLATED_CSV)
        col_a, col_b = st.columns([3, 1])
        with col_a:
            if t_out:
                st.success(f"✅ `{TRANSLATED_CSV}` exists ({len(pd.read_csv(TRANSLATED_CSV))} rows)")
        with col_b:
            run_t = st.button("Run" if not t_out else "Re-run", key="run_t",
                              disabled=not os.path.exists(PROMPTS_CSV))
        if run_t:
            os.environ["GOOGLE_CLOUD_API_KEY"] = st.session_state.gcloud_key
            from pipeline.translate import run_translation_pipeline
            with st.spinner("Translating — this may take several minutes…"):
                run_translation_pipeline()
            reload_dataset(); st.success("✅ Done."); st.rerun()

    # ── Step 2 ──
    with st.expander("**Step 2 — Generate Gemini reference outputs**", expanded=True):
        st.caption("Ideal reference response for every English prompt")
        o_out = os.path.exists(OUTPUTS_CSV)
        col_a, col_b = st.columns([3, 1])
        with col_a:
            if o_out:
                st.success(f"✅ `{OUTPUTS_CSV}` exists ({len(pd.read_csv(OUTPUTS_CSV))} rows)")
            if not os.path.exists(TRANSLATED_CSV):
                st.warning("Run Step 1 first.")
        with col_b:
            run_o = st.button("Run" if not o_out else "Re-run", key="run_o",
                              disabled=not (os.path.exists(TRANSLATED_CSV)
                                            and key_ok(st.session_state.gemini_key)))
        if run_o:
            os.environ["GEMINI_API_KEY"] = st.session_state.gemini_key
            from pipeline.generate_outputs import run_output_generation
            with st.spinner("Generating outputs — this may take several minutes…"):
                run_output_generation()
            reload_dataset(); st.success("✅ Done."); st.rerun()

    # ── Step 3 ──
    with st.expander("**Step 3 — Compute quality scores**", expanded=True):
        st.caption("Clarity · Specificity · Completeness · Composite 1–5")
        s_out = os.path.exists(SCORED_CSV)
        col_a, col_b = st.columns([3, 1])
        with col_a:
            if s_out:
                df_sc = pd.read_csv(SCORED_CSV)
                st.success(f"✅ Scored — avg quality {df_sc['quality_score'].mean():.2f} / 5.0")
            if not os.path.exists(OUTPUTS_CSV):
                st.warning("Run Step 2 first.")
        with col_b:
            run_s = st.button("Run" if not s_out else "Re-run", key="run_s",
                              disabled=not os.path.exists(OUTPUTS_CSV))
        if run_s:
            from pipeline.quality_score import score_prompts
            with st.spinner("Scoring…"):
                score_prompts()
            reload_dataset(); st.success("✅ Done."); st.rerun()

    # ── Step 4 ──
    with st.expander("**Step 4 — Malayalam native-speaker review**", expanded=True):
        st.caption("Export → review in Google Sheets → merge back")
        r_out = os.path.exists(MALAYALAM_REVIEW_CSV)
        f_out = os.path.exists(FINAL_CSV)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("Export review CSV", key="exp_ml",
                         disabled=not os.path.exists(SCORED_CSV)):
                from pipeline.quality_score import export_malayalam_review
                with st.spinner("Exporting…"):
                    export_malayalam_review()
                st.success(f"Exported → `{MALAYALAM_REVIEW_CSV}`")
        with col_b:
            if r_out:
                rdf = pd.read_csv(MALAYALAM_REVIEW_CSV)
                done = (rdf["ml_review_status"] != "pending").sum()
                st.info(f"Reviewed: {done} / {len(rdf)}")
        with col_c:
            if st.button("Merge review", key="merge_ml", disabled=not r_out):
                from pipeline.quality_score import merge_malayalam_review
                with st.spinner("Merging…"):
                    merge_malayalam_review()
                reload_dataset(); st.success(f"✅ Merged → `{FINAL_CSV}`"); st.rerun()

        if r_out:
            with st.expander("Preview review file"):
                st.dataframe(
                    pd.read_csv(MALAYALAM_REVIEW_CSV)[
                        ["prompt_en", "prompt_ml_auto", "ml_review_status"]
                    ].head(10), use_container_width=True)

    # ── Step 5 ──
    with st.expander("**Step 5 — Publish to Hugging Face**", expanded=True):
        st.caption("Uploads dataset + full dataset card (README)")

        f_out = os.path.exists(FINAL_CSV)
        hf_ok = key_ok(st.session_state.hf_token)

        if not f_out: st.warning("Complete Steps 1–4 first.")
        if not hf_ok: st.warning("Add your HF token in ⚙ Settings.")

        repo_id = st.text_input("Repository ID",
                                 placeholder="your_username/multilingual-prompt-dataset-ml",
                                 key="hf_repo")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Preview dataset card", key="prev_card"):
                from pipeline.upload_hf import preview_card
                preview_card()
                with open("data/dataset_card_preview.md") as f:
                    st.code(f.read(), language="markdown")
        with col_b:
            if st.button("🚀 Publish", key="publish",
                         disabled=not (f_out and hf_ok and repo_id.strip())):
                os.environ["HF_TOKEN"] = st.session_state.hf_token
                from pipeline.upload_hf import upload_to_huggingface
                with st.spinner("Publishing…"):
                    upload_to_huggingface(repo_id=repo_id.strip(),
                                          token=st.session_state.hf_token)
                st.success(f"🎉 Live at: huggingface.co/datasets/{repo_id.strip()}")
                st.balloons()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Browse
# ══════════════════════════════════════════════════════════════════════════════

with tab_browse:
    st.header("🌍 Browse Dataset")
    df, source = load_dataset()

    if df.empty:
        st.info("Run the pipeline first to generate a dataset.")
        st.stop()

    st.caption(f"`{source}` · {len(df):,} rows")
    available_langs = [col for col in LANGUAGE_META if col in df.columns]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        sel_cat  = st.selectbox("Category", ["All"] + sorted(df["task_category"].dropna().unique().tolist()))
    with col2:
        sel_diff = st.selectbox("Difficulty", ["All", "easy", "medium", "hard"])
    with col3:
        qmin = float(df["quality_score"].min()) if "quality_score" in df.columns else 1.0
        qmax = float(df["quality_score"].max()) if "quality_score" in df.columns else 5.0
        q_range = st.slider("Quality", 1.0, 5.0, (qmin, qmax), 0.1)
    with col4:
        show_langs = st.multiselect("Languages", available_langs,
            default=[c for c in ["prompt_en","prompt_ml","prompt_hi"] if c in available_langs],
            format_func=lambda c: f"{LANGUAGE_META[c][0]} {LANGUAGE_META[c][1]}")

    show_out = st.checkbox("Show expected output")

    fdf = df.copy()
    if sel_cat  != "All": fdf = fdf[fdf["task_category"] == sel_cat]
    if sel_diff != "All": fdf = fdf[fdf["difficulty"] == sel_diff]
    if "quality_score" in fdf.columns:
        fdf = fdf[fdf["quality_score"].between(q_range[0], q_range[1])]
    fdf = fdf.reset_index(drop=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rows", len(fdf))
    m2.metric("Languages", len(available_langs))
    if "quality_score" in fdf.columns: m3.metric("Avg quality", f"{fdf['quality_score'].mean():.2f}")
    m4.metric("Flagged", len(st.session_state.flags))

    st.download_button("⬇ Download filtered CSV", fdf.to_csv(index=False),
                       "filtered_dataset.csv", "text/csv")
    st.divider()

    page_size   = st.select_slider("Rows per page", [5, 10, 20, 50], value=10)
    total_pages = max(1, (len(fdf) - 1) // page_size + 1)
    pc, pi, pn  = st.columns([1, 4, 1])
    with pc:
        if st.button("← Prev", disabled=st.session_state.page == 0):
            st.session_state.page = max(0, st.session_state.page - 1)
    with pn:
        if st.button("Next →", disabled=st.session_state.page >= total_pages - 1):
            st.session_state.page = min(total_pages - 1, st.session_state.page + 1)
    with pi:
        st.write(f"Page **{st.session_state.page+1}** / **{total_pages}**")

    page_df = fdf.iloc[st.session_state.page * page_size : (st.session_state.page + 1) * page_size]

    for _, row in page_df.iterrows():
        row_id = row.name
        task   = row.get("task_category", "")
        diff   = row.get("difficulty", "medium")
        color  = TASK_COLORS.get(task, "#6b7280")

        with st.expander(f"**{str(row.get('prompt_en',''))[:85]}…**  [{task}]  [{diff}]"):
            cm, cs = st.columns([3, 2])
            with cm:
                st.markdown(
                    f'<span style="background:{color}22;color:{color};padding:2px 10px;'
                    f'border-radius:6px;font-size:12px;font-weight:600">{task}</span>&nbsp;'
                    f'<span class="badge-{diff}">{diff}</span>', unsafe_allow_html=True)
            with cs:
                if "quality_score" in row:
                    st.markdown(f"⭐ **{row['quality_score']:.2f}** · clarity {row.get('clarity_score','—'):.2f} · specificity {row.get('specificity_score','—'):.2f}")

            if show_langs:
                lcs = st.columns(len(show_langs))
                for lc, cn in zip(lcs, show_langs):
                    flag, name = LANGUAGE_META.get(cn, ("", cn))
                    with lc:
                        st.markdown(f"**{flag} {name}**")
                        val = str(row.get(cn, "")) if pd.notna(row.get(cn)) else "—"
                        st.text_area("", val, height=130, label_visibility="collapsed",
                                     key=f"ta_{row_id}_{cn}")

            if show_out:
                out = row.get("expected_output", "")
                if pd.notna(out) and str(out).strip():
                    st.markdown("**Expected output**"); st.info(out)

            with st.expander("🚩 Flag a translation"):
                non_en = [c for c in show_langs if c != "prompt_en"]
                if non_en:
                    fl = st.selectbox("Language", non_en, key=f"fl_{row_id}",
                                      format_func=lambda c: f"{LANGUAGE_META[c][0]} {LANGUAGE_META[c][1]}")
                    fr = st.text_input("Reason", key=f"fr_{row_id}")
                    if st.button("Submit", key=f"fb_{row_id}"):
                        st.session_state.flags[row_id] = {
                            "row_id": row_id, "prompt_en": str(row.get("prompt_en",""))[:80],
                            "flagged_lang": fl, "reason": fr}
                        st.warning("Flagged.")
                else:
                    st.info("Select a non-English language above.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Flagged
# ══════════════════════════════════════════════════════════════════════════════

with tab_flagged:
    st.header("🚩 Flagged Translations")

    saved = []
    if os.path.exists(FLAGGED_CSV):
        saved = pd.read_csv(FLAGGED_CSV).to_dict("records")

    combined = {r["row_id"]: r for r in saved}
    combined.update({r["row_id"]: r for r in st.session_state.flags.values()})
    all_flags = list(combined.values())

    if not all_flags:
        st.info("No translations flagged yet. Use the 🌍 Browse tab to flag poor translations.")
    else:
        st.metric("Total flagged", len(all_flags))
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("💾 Save to CSV"):
                save_flags(st.session_state.flags)
                st.success(f"Saved → `{FLAGGED_CSV}`")
        with col_b:
            st.download_button("⬇ Download", pd.DataFrame(all_flags).to_csv(index=False),
                               "flagged_translations.csv", "text/csv")
        st.divider()
        st.dataframe(pd.DataFrame(all_flags), use_container_width=True,
                     column_config={
                         "row_id":       st.column_config.NumberColumn("Row", width="small"),
                         "prompt_en":    st.column_config.TextColumn("English Prompt", width="large"),
                         "flagged_lang": st.column_config.TextColumn("Language", width="small"),
                         "reason":       st.column_config.TextColumn("Reason"),
                     })
