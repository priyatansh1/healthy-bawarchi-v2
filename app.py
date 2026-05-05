# ============================================================
# Healthy Bawarchi — Main Streamlit App
# Bilingual (EN/UR) AI-powered recipe generator
# Redesigned: culturally rooted, contemporary, confident
# Now with regional seasonal awareness for Pakistan
# ============================================================
import streamlit as st
from PIL import Image

from recipe_engine import generate_recipe, generate_recipe_from_image, recipe_to_text
from usda_nutrition import calculate_recipe_nutrition, format_nutrition_source_note
from i18n import t, get_lang, inject_rtl_css, inject_ltr_css
from seasonal import in_season, month_name, list_regions, region_label
from safety_filter import check_ingredients, get_message as safety_message
from counters import record_visit, record_recipe, get_counts, format_count


# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Healthy Bawarchi — Smart Culinary Interface",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"
if "recipe" not in st.session_state:
    st.session_state["recipe"] = None
if "nutrition" not in st.session_state:
    st.session_state["nutrition"] = None
if "detected_ingredients" not in st.session_state:
    st.session_state["detected_ingredients"] = None
if "selected_cuisine" not in st.session_state:
    st.session_state["selected_cuisine"] = "Pakistani"
if "selected_region" not in st.session_state:
    st.session_state["selected_region"] = "Pakistan"
if "visit_recorded" not in st.session_state:
    st.session_state["visit_recorded"] = False

if not st.session_state["visit_recorded"]:
    record_visit()
    st.session_state["visit_recorded"] = True

lang = get_lang()


# ─────────────────────────────────────────────
# LANGUAGE-AWARE CSS
# ─────────────────────────────────────────────
if lang == "ur":
    inject_rtl_css()
else:
    inject_ltr_css()


# ─────────────────────────────────────────────
# DESIGN — split into 6 small markdown chunks
# (One giant block triggers a Streamlit render-as-text bug)
# ─────────────────────────────────────────────

# Chunk 1 — fonts + variables + base typography
st.markdown(
    '<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">'
    '<style>'
    ':root{'
    '--cream:#FAF6EC;--cream-deep:#F4ECD4;--cream-edge:#E8DDC2;'
    '--ink:#2A2419;--ink-soft:#6B5D44;--ink-mute:#97876B;'
    '--green-deep:#1F4D2C;--green-mid:#2F6638;'
    '--saffron:#B8771E;--saffron-soft:#F4C97B;--leaf:#C9B98A;--paper:#FFFFFF;'
    '}'
    '.stApp{background:var(--cream)!important;}'
    '.main .block-container{max-width:920px!important;padding-top:2rem!important;padding-bottom:4rem!important;}'
    'html,body,.stApp,[class*="css"]{font-family:"Inter",-apple-system,BlinkMacSystemFont,sans-serif!important;color:var(--ink);}'
    'h1,h2,h3,.display-serif{font-family:"Lora",Georgia,serif!important;font-weight:500!important;color:var(--green-deep)!important;letter-spacing:-0.3px;}'
    '#MainMenu{visibility:hidden;}footer{visibility:hidden;}header{visibility:hidden;}'
    '</style>',
    unsafe_allow_html=True,
)

# Chunk 2 — leaf motif decoration in margins (subtle, far from content)
st.markdown(
    '<style>'
    '.stApp::before{content:"";position:fixed;top:8%;left:2%;width:140px;height:140px;background-image:url("data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'><path d=\'M50 5 C 25 25, 25 65, 50 95 C 75 65, 75 25, 50 5 Z M50 12 L50 88\' fill=\'%23B8771E\' fill-opacity=\'0.06\' stroke=\'%23B8771E\' stroke-opacity=\'0.10\' stroke-width=\'1\'/></svg>");background-repeat:no-repeat;background-size:contain;pointer-events:none;z-index:0;}'
    '.stApp::after{content:"";position:fixed;bottom:10%;right:2%;width:160px;height:160px;background-image:url("data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'><g fill=\'%231F4D2C\' fill-opacity=\'0.05\' stroke=\'%231F4D2C\' stroke-opacity=\'0.09\' stroke-width=\'1\'><path d=\'M50 90 C 30 70, 30 30, 50 10 C 70 30, 70 70, 50 90 Z\'/><path d=\'M50 10 L50 90\' fill=\'none\'/></g></svg>");background-repeat:no-repeat;background-size:contain;pointer-events:none;z-index:0;transform:rotate(35deg);}'
    '@media (max-width:1100px){.stApp::before,.stApp::after{display:none;}}'
    '.main{position:relative;z-index:1;}'
    '</style>',
    unsafe_allow_html=True,
)

# Chunk 3 — hero, brand, stats
st.markdown(
    '<style>'
    '.hb-hero{background:var(--cream-deep);border:1px solid var(--cream-edge);border-radius:24px;padding:2.25rem 2rem 2rem 2rem;}'
    '.hb-brand{display:flex;align-items:center;gap:12px;margin-bottom:1.5rem;}'
    '.hb-brand-mark{width:44px;height:44px;border-radius:50%;background:var(--green-deep);display:flex;align-items:center;justify-content:center;color:var(--saffron-soft);font-family:"Lora",serif;font-weight:500;font-size:17px;}'
    '.hb-brand-text-en{font-family:"Lora",serif;font-size:17px;font-weight:500;color:var(--green-deep);line-height:1;}'
    '.hb-brand-text-ur{font-size:12px;color:var(--ink-soft);margin-top:2px;letter-spacing:0.3px;}'
    '.hb-hero-title{font-family:"Lora",serif;font-size:clamp(28px,4.5vw,42px);font-weight:500;color:var(--green-deep);line-height:1.15;text-align:center;margin:1.5rem 0 0.5rem 0;letter-spacing:-0.5px;}'
    '.hb-hero-title em{font-style:italic;color:var(--saffron);}'
    '.hb-hero-sub{text-align:center;color:var(--ink-soft);font-size:15px;line-height:1.6;max-width:540px;margin:0 auto;}'
    '.hb-stats{display:flex;gap:12px;justify-content:center;margin-top:1.75rem;flex-wrap:wrap;}'
    '.hb-stat{background:var(--paper);border:1px solid var(--cream-edge);border-radius:14px;padding:14px 22px;min-width:130px;text-align:center;}'
    '.hb-stat-number{font-family:"Lora",serif;font-size:26px;font-weight:500;color:var(--green-deep);line-height:1;}'
    '.hb-stat-number.accent{color:var(--saffron);}'
    '.hb-stat-label{font-size:11px;color:var(--ink-soft);letter-spacing:0.6px;text-transform:uppercase;margin-top:4px;}'
    '.hb-langpill{display:flex;background:var(--paper);border:1px solid var(--cream-edge);border-radius:999px;padding:3px;gap:0;width:fit-content;margin-left:auto;}'
    '.hb-langpill button{background:transparent;border:none;border-radius:999px;padding:6px 16px;font-size:13px;font-weight:500;cursor:pointer;color:var(--ink-soft);font-family:"Inter",sans-serif;}'
    '.hb-langpill button.active{background:var(--green-deep);color:var(--paper);}'
    '</style>',
    unsafe_allow_html=True,
)

# Chunk 4 — cards, seasonal, region selector
st.markdown(
    '<style>'
    '.hb-card{background:var(--paper);border:1px solid var(--cream-edge);border-radius:20px;padding:1.75rem;margin-top:1.25rem;}'
    '.hb-card-head{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:1rem;gap:1rem;flex-wrap:wrap;}'
    '.hb-card-title{font-family:"Lora",serif;font-size:19px;font-weight:500;color:var(--green-deep);margin:0;}'
    '.hb-card-step{font-size:12px;color:var(--ink-mute);}'
    '.hb-season{background:var(--green-deep);color:var(--cream-deep);border-radius:20px;padding:1.5rem 1.75rem;margin-top:1rem;}'
    '.hb-season-head{display:flex;align-items:center;justify-content:space-between;gap:1rem;margin-bottom:14px;flex-wrap:wrap;}'
    '.hb-season-title{font-family:"Lora",serif;font-size:18px;color:var(--paper);font-weight:500;margin:0;}'
    '.hb-season-sub{font-size:12px;color:var(--leaf);margin-top:2px;}'
    '.hb-season-pill{font-size:11px;color:var(--leaf);background:rgba(244,201,123,0.15);padding:4px 10px;border-radius:999px;letter-spacing:0.5px;white-space:nowrap;}'
    '.hb-season-chips{display:flex;flex-wrap:wrap;gap:8px;}'
    '.hb-chip-peak{background:rgba(244,201,123,0.20);color:var(--saffron-soft);padding:6px 14px;border-radius:999px;font-size:13px;font-weight:500;display:inline-flex;align-items:center;gap:6px;white-space:nowrap;}'
    '.hb-chip-peak::before{content:"";width:6px;height:6px;background:var(--saffron-soft);border-radius:50%;}'
    '.hb-chip-avail{background:rgba(255,255,255,0.08);color:#E5D9B5;padding:6px 14px;border-radius:999px;font-size:13px;border:1px solid rgba(255,255,255,0.12);white-space:nowrap;}'
    '.hb-season-tip{margin-top:14px;padding-top:12px;border-top:1px solid rgba(244,201,123,0.15);font-size:12px;color:var(--leaf);font-style:italic;line-height:1.5;}'
    '.hb-region-row{margin-top:14px;padding-top:12px;border-top:1px solid rgba(244,201,123,0.12);display:flex;align-items:center;gap:10px;flex-wrap:wrap;}'
    '.hb-region-label{font-size:12px;color:var(--leaf);letter-spacing:0.5px;}'
    '</style>',
    unsafe_allow_html=True,
)

# Chunk 5 — Streamlit widget overrides
st.markdown(
    '<style>'
    '.stButton>button{background:var(--green-deep)!important;color:var(--paper)!important;border:none!important;border-radius:999px!important;padding:0.85rem 2rem!important;font-family:"Inter",sans-serif!important;font-size:15px!important;font-weight:500!important;width:100%!important;cursor:pointer!important;letter-spacing:0.2px!important;box-shadow:none!important;transition:transform 0.15s ease,background 0.2s ease!important;}'
    '.stButton>button:hover{background:var(--green-mid)!important;transform:translateY(-1px)!important;}'
    '.stTextArea textarea,.stTextInput input{background:var(--cream)!important;border:1px solid var(--cream-edge)!important;border-radius:12px!important;font-family:"Inter",sans-serif!important;font-size:15px!important;color:var(--ink)!important;line-height:1.6!important;padding:14px!important;}'
    '.stTextArea textarea:focus,.stTextInput input:focus{border-color:var(--green-mid)!important;box-shadow:0 0 0 3px rgba(31,77,44,0.10)!important;}'
    '.stRadio>label{display:none;}'
    '.stRadio [role="radiogroup"]{display:flex!important;gap:10px!important;flex-wrap:wrap!important;}'
    '.stRadio [role="radiogroup"]>label{background:var(--cream)!important;border:1px solid var(--cream-edge)!important;border-radius:14px!important;padding:12px 18px!important;cursor:pointer!important;flex:1 1 140px!important;}'
    '.stRadio [role="radiogroup"]>label:hover{border-color:var(--green-mid)!important;}'
    '.stRadio [role="radiogroup"]>label:has(input:checked){background:var(--green-deep)!important;border-color:var(--green-deep)!important;}'
    '.stRadio [role="radiogroup"]>label:has(input:checked)>div{color:var(--paper)!important;}'
    '.stSlider>label{display:none;}'
    '[data-baseweb="slider"] [role="slider"]{background:var(--green-deep)!important;}'
    '.stTabs [data-baseweb="tab-list"]{gap:4px!important;background:var(--cream)!important;border-radius:12px!important;padding:4px!important;border:1px solid var(--cream-edge)!important;}'
    '.stTabs [data-baseweb="tab"]{border-radius:10px!important;padding:8px 18px!important;font-weight:500!important;font-family:"Inter",sans-serif!important;}'
    '.stTabs [aria-selected="true"]{background:var(--green-deep)!important;color:var(--paper)!important;}'
    '.stSelectbox>div>div{background:rgba(244,201,123,0.10)!important;border:1px solid rgba(244,201,123,0.25)!important;border-radius:999px!important;color:var(--saffron-soft)!important;font-size:12px!important;font-family:"Inter",sans-serif!important;min-height:30px!important;}'
    '.stSelectbox>label{display:none!important;}'
    '</style>',
    unsafe_allow_html=True,
)

# Chunk 6 — recipe output editorial card + share + footer + mobile
st.markdown(
    '<style>'
    '.hb-recipe{background:var(--paper);border:1px solid var(--cream-edge);border-radius:20px;overflow:hidden;margin-top:1.25rem;}'
    '.hb-recipe-head{background:var(--green-deep);padding:1.5rem 1.75rem;color:var(--paper);}'
    '.hb-recipe-eyebrow{font-size:11px;color:var(--leaf);letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px;}'
    '.hb-recipe-title{font-family:"Lora",serif;font-size:28px;font-weight:500;line-height:1.2;color:var(--paper);margin:0;}'
    '.hb-recipe-desc{font-size:13px;color:var(--leaf);margin-top:6px;font-style:italic;}'
    '.hb-recipe-meta{display:flex;gap:16px;margin-top:14px;flex-wrap:wrap;}'
    '.hb-recipe-meta-item{font-size:13px;color:var(--saffron-soft);display:inline-flex;align-items:center;gap:6px;}'
    '.hb-recipe-section-head{font-family:"Lora",serif;font-size:16px;font-weight:500;color:var(--green-deep);margin:0 0 12px 0;display:flex;align-items:center;gap:10px;}'
    '.hb-recipe-section-head::before{content:"";display:inline-block;width:24px;height:1px;background:var(--saffron);}'
    '.hb-ing-row{display:flex;justify-content:space-between;padding:6px 0 8px 0;border-bottom:1px dashed var(--cream-edge);font-size:14px;line-height:1.5;}'
    '.hb-ing-row:last-child{border-bottom:none;}'
    '.hb-ing-name{color:var(--ink);}'
    '.hb-ing-name b{font-weight:500;}'
    '.hb-ing-price{color:var(--ink-mute);font-size:12px;white-space:nowrap;margin-left:8px;}'
    '.hb-ing-total{display:flex;justify-content:space-between;padding-top:10px;margin-top:6px;border-top:1px solid var(--cream-edge);font-weight:500;color:var(--green-deep);}'
    '.hb-nut-grid{background:var(--cream);border-radius:14px;padding:16px;display:grid;grid-template-columns:1fr 1fr;gap:14px;}'
    '.hb-nut-num{font-family:"Lora",serif;font-size:24px;font-weight:500;color:var(--green-deep);line-height:1;}'
    '.hb-nut-label{font-size:11px;color:var(--ink-mute);letter-spacing:0.5px;text-transform:uppercase;margin-top:4px;}'
    '.hb-nut-source{font-size:11px;color:var(--ink-mute);margin-top:10px;font-style:italic;}'
    '.hb-callout{background:var(--cream);border-radius:14px;padding:14px 18px;border-left:3px solid var(--saffron);margin:0 1.75rem 1rem 1.75rem;font-size:13px;color:var(--ink-soft);line-height:1.6;}'
    '.hb-callout b{color:var(--green-deep);font-weight:500;}'
    '.hb-callout.green{border-left-color:var(--green-mid);}'
    '.hb-step-row{display:flex;gap:14px;padding:10px 0;border-bottom:1px solid var(--cream-edge);font-size:14px;line-height:1.6;}'
    '.hb-step-row:last-child{border-bottom:none;}'
    '.hb-step-num{font-family:"Lora",serif;font-size:18px;font-weight:500;color:var(--saffron);min-width:22px;line-height:1.4;}'
    '.hb-step-text{color:var(--ink);}'
    '.hb-share-text-title{font-family:"Lora",serif;font-size:17px;font-weight:500;color:var(--green-deep);margin-bottom:4px;}'
    '.hb-share-text-body{font-size:13px;color:var(--ink-soft);line-height:1.6;margin-bottom:10px;}'
    '.hb-detected{background:var(--cream);border:1px solid var(--cream-edge);border-left:3px solid var(--green-mid);border-radius:12px;padding:12px 16px;font-size:13px;color:var(--ink-soft);margin-top:1rem;line-height:1.5;}'
    '.hb-footer{text-align:center;color:var(--ink-mute);font-size:12px;margin-top:3rem;padding-top:1.5rem;border-top:1px solid var(--cream-edge);font-style:italic;line-height:1.6;}'
    '@media (max-width:600px){.hb-hero{padding:1.75rem 1.25rem;}.hb-card{padding:1.25rem;}.hb-recipe-head{padding:1.25rem;}.hb-recipe-title{font-size:22px;}.hb-callout{margin-left:1.25rem;margin-right:1.25rem;}}'
    '</style>',
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# LANGUAGE TOGGLE — two-button pill, top right
# ─────────────────────────────────────────────
_lt_col1, _lt_col2, _lt_col3 = st.columns([5, 1, 1])
with _lt_col2:
    if st.button("EN", key="lang_en_btn",
                 help="English",
                 type="primary" if lang == "en" else "secondary"):
        if lang != "en":
            st.session_state["lang"] = "en"
            st.session_state["recipe"] = None
            st.session_state["nutrition"] = None
            st.rerun()
with _lt_col3:
    if st.button("اردو", key="lang_ur_btn",
                 help="Urdu",
                 type="primary" if lang == "ur" else "secondary"):
        if lang != "ur":
            st.session_state["lang"] = "ur"
            st.session_state["recipe"] = None
            st.session_state["nutrition"] = None
            st.rerun()


# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
_counts = get_counts()
_visits = format_count(_counts.get("visits"))
_recipes = format_count(_counts.get("recipes"))

if lang == "ur":
    _hero_eyebrow_ur = "صحت کا باورچی"
    _hero_title_html = (
        '<div class="hb-hero-title">'
        'اچھا پکائیں، اچھا کھائیں،<br/><em>اچھا جیئیں۔</em>'
        '</div>'
    )
    _hero_sub = (
        "ہمیں بتائیں آپ کے کچن میں کیا ہے — ہم ایک صحت بخش پاکستانی "
        "کھانا تجویز کریں گے، اصل غذائیت اور موسمی تازہ پیداوار کے ساتھ۔"
    )
    _stat_visits = "گھریلو باورچی"
    _stat_recipes = "تیار کھانے"
else:
    _hero_eyebrow_ur = "صحت کا باورچی"
    _hero_title_html = (
        '<div class="hb-hero-title">'
        'Cook well, eat well,<br/><em>live well.</em>'
        '</div>'
    )
    _hero_sub = (
        "Tell us what's in your kitchen — we'll suggest a wholesome Pakistani meal, "
        "with real nutrition and seasonal produce in mind."
    )
    _stat_visits = "home cooks"
    _stat_recipes = "meals planned"

st.markdown(
    f'<div class="hb-hero">'
    f'<div class="hb-brand">'
    f'<div class="hb-brand-mark">HB</div>'
    f'<div>'
    f'<div class="hb-brand-text-en">Healthy Bawarchi</div>'
    f'<div class="hb-brand-text-ur">{_hero_eyebrow_ur}</div>'
    f'</div></div>'
    f'{_hero_title_html}'
    f'<div class="hb-hero-sub">{_hero_sub}</div>'
    f'<div class="hb-stats">'
    f'<div class="hb-stat">'
    f'<div class="hb-stat-number">{_visits}</div>'
    f'<div class="hb-stat-label">{_stat_visits}</div>'
    f'</div>'
    f'<div class="hb-stat">'
    f'<div class="hb-stat-number accent">{_recipes}</div>'
    f'<div class="hb-stat-label">{_stat_recipes}</div>'
    f'</div>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 🌿 {t('sidebar_settings')}")
    st.markdown("---")
    st.markdown(t("sidebar_about"))
    st.markdown("---")
    st.caption(t("sidebar_disclaimer"))


# ─────────────────────────────────────────────
# CUISINE SELECTOR
# ─────────────────────────────────────────────
st.markdown(
    f'<div class="hb-card"><div class="hb-card-head">'
    f'<div class="hb-card-title">{t("choose_cuisine")}</div>'
    f'<
