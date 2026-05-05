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
    f'<div class="hb-hero"><div class="hb-brand"><div class="hb-brand-mark">HB</div><div><div class="hb-brand-text-en">Healthy Bawarchi</div><div class="hb-brand-text-ur">{_hero_eyebrow_ur}</div></div></div>{_hero_title_html}<div class="hb-hero-sub">{_hero_sub}</div><div class="hb-stats"><div class="hb-stat"><div class="hb-stat-number">{_visits}</div><div class="hb-stat-label">{_stat_visits}</div></div><div class="hb-stat"><div class="hb-stat-number accent">{_recipes}</div><div class="hb-stat-label">{_stat_recipes}</div></div></div></div>',
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
    f'<div class="hb-card"><div class="hb-card-head"><div class="hb-card-title">{t("choose_cuisine")}</div><div class="hb-card-step">step 1 of 3</div></div>',
    unsafe_allow_html=True,
)

cuisine_options = {
    "🇵🇰 Pakistani": "Pakistani",
    "🇨🇳 Chinese": "Chinese",
    "🇮🇹 Italian": "Italian",
    "🇲🇽 Mexican": "Mexican",
}
cuisine_display = st.radio(
    "Cuisine",
    options=list(cuisine_options.keys()),
    horizontal=True,
    label_visibility="collapsed",
)
cuisine = cuisine_options[cuisine_display]
st.session_state["selected_cuisine"] = cuisine

st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# IN SEASON NOW — region-aware dark green hero
# ─────────────────────────────────────────────
# Region dropdown only matters for Pakistani cuisine
region = st.session_state.get("selected_region", "Pakistan")

if cuisine == "Pakistani":
    if lang == "ur":
        _ss_title = "ابھی موسم میں"
        _ss_sub = f"{month_name(lang='ur')} میں {region_label(region, 'ur')} کے لیے تازہ"
        _ss_tip = "موسمی پیداوار کھانا زیادہ تازہ، سستا اور ماحول کے لیے بہتر ہے۔"
        _ss_pill = "تازہ"
        _region_lbl = "علاقہ:"
    else:
        _ss_title = f"In season this {month_name(lang='en')}"
        _ss_sub = f"For {region_label(region, 'en')}"
        _ss_tip = "Cooking with what's in season is fresher, cheaper, and uses less energy to grow and ship."
        _ss_pill = "FRESH NOW"
        _region_lbl = "Region:"
else:
    if lang == "ur":
        _ss_title = "ابھی موسم میں"
        _ss_sub = f"{month_name(lang='ur')} میں {cuisine} کھانوں کے لیے تازہ"
        _ss_tip = "موسمی پیداوار کھانا زیادہ تازہ، سستا اور ماحول کے لیے بہتر ہے۔"
        _ss_pill = "تازہ"
    else:
        _ss_title = f"In season this {month_name(lang='en')}"
        _ss_sub = f"For {cuisine} cuisine"
        _ss_tip = "Cooking with what's in season is fresher, cheaper, and uses less energy to grow and ship."
        _ss_pill = "FRESH NOW"

_season_items = in_season(cuisine, max_items=8, region=region)
_chips = []
for _it in _season_items:
    _label = _it["ur"] if (lang == "ur" and _it.get("ur")) else _it["en"]
    if _it["peak"]:
        _chips.append(f'<span class="hb-chip-peak">{_label}</span>')
    else:
        _chips.append(f'<span class="hb-chip-avail">{_label}</span>')

# Build seasonal card HTML (region selector inserted via Streamlit below)
st.markdown(
    f'<div class="hb-season"><div class="hb-season-head"><div><div class="hb-season-title">{_ss_title}</div><div class="hb-season-sub">{_ss_sub}</div></div><div class="hb-season-pill">{_ss_pill}</div></div><div class="hb-season-chips">{"".join(_chips)}</div><div class="hb-season-tip">{_ss_tip}</div></div>',
    unsafe_allow_html=True,
)

# Region dropdown — small caption + selectbox below the seasonal card
# (Visible only for Pakistani cuisine)
if cuisine == "Pakistani":
    _region_options = list_regions(lang)
    _region_codes = [code for code, _ in _region_options]
    _region_labels = [lbl for _, lbl in _region_options]
    _current_idx = _region_codes.index(region) if region in _region_codes else 0

    _rcol1, _rcol2 = st.columns([1, 3])
    with _rcol1:
        st.markdown(
            f'<div style="padding-top:0.7rem; color:var(--ink-mute); font-size:13px;">📍 {_region_lbl}</div>',
            unsafe_allow_html=True,
        )
    with _rcol2:
        new_region_label = st.selectbox(
            "Region",
            options=_region_labels,
            index=_current_idx,
            label_visibility="collapsed",
            key="region_select",
        )
        new_region_code = _region_codes[_region_labels.index(new_region_label)]
        if new_region_code != region:
            st.session_state["selected_region"] = new_region_code
            st.rerun()


# ─────────────────────────────────────────────
# MAX INGREDIENTS
# ─────────────────────────────────────────────
st.markdown(
    f'<div class="hb-card"><div class="hb-card-head"><div class="hb-card-title">{t("max_ingredients_label")}</div></div>',
    unsafe_allow_html=True,
)
max_ingredients = st.slider(
    "Max ingredients", min_value=3, max_value=10, value=5,
    label_visibility="collapsed",
)
st.caption(t("max_ingredients_caption", n=max_ingredients))
st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# INGREDIENT INPUT
# ─────────────────────────────────────────────
st.markdown(
    f'<div class="hb-card"><div class="hb-card-head"><div class="hb-card-title">{t("what_ingredients")}</div><div class="hb-card-step">step 2 of 3</div></div>',
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs([t("tab_type"), t("tab_photo")])
ingredients_text = ""
uploaded_image_bytes = None

with tab1:
    ingredients_text = st.text_area(
        "Ingredients",
        placeholder=t("type_placeholder"),
        height=110,
        label_visibility="collapsed",
    )
    st.caption(t("type_caption"))

with tab2:
    uploaded_file = st.file_uploader(
        "Upload a photo of your ingredients",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        uploaded_image_bytes = uploaded_file.getvalue()
    st.caption(t("photo_caption"))

st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# GENERATE
# ─────────────────────────────────────────────
st.markdown(
    '<div style="text-align:center;margin-top:1.5rem;">'
    '<div class="hb-card-step" style="margin-bottom:0.75rem;">step 3 of 3</div>'
    '</div>',
    unsafe_allow_html=True,
)
generate_btn = st.button(t("generate_btn"), use_container_width=True)


# ─────────────────────────────────────────────
# GENERATION LOGIC
# ─────────────────────────────────────────────
if generate_btn:
    has_text = bool(ingredients_text.strip())
    has_image = uploaded_image_bytes is not None

    if not has_text and not has_image:
        st.warning(t("error_no_input"))
        st.stop()

    if has_text:
        safety = check_ingredients(ingredients_text, cuisine)
        if not safety["safe"]:
            msg = safety_message(safety["category"], safety["blocked"], lang=get_lang())
            st.error(f"🚫 {msg}")
            st.stop()

    with st.spinner(t("spinner")):
        try:
            if has_image:
                detected, recipe = generate_recipe_from_image(
                    uploaded_image_bytes, cuisine, max_ingredients
                )
                st.session_state["detected_ingredients"] = detected
            else:
                recipe = generate_recipe(ingredients_text, cuisine, max_ingredients)
                st.session_state["detected_ingredients"] = None

            usda_key = st.secrets.get("USDA_API_KEY", "")
            nutrition = calculate_recipe_nutrition(
                recipe.get("ingredients", []),
                recipe.get("servings", 2),
                usda_key,
            )

            st.session_state["recipe"] = recipe
            st.session_state["nutrition"] = nutrition
            record_recipe()

        except Exception as e:
            err = str(e)
            if "api_key" in err.lower() or "authentication" in err.lower() or "401" in err:
                st.error(t("error_api_key"))
            elif "quota" in err.lower() or "429" in err:
                st.error(t("error_quota"))
            else:
                st.error(t("error_generic", msg=err))
            st.stop()


# ─────────────────────────────────────────────
# RECIPE OUTPUT
# ─────────────────────────────────────────────
recipe = st.session_state.get("recipe")
nutrition = st.session_state.get("nutrition")
detected = st.session_state.get("detected_ingredients")

if recipe:
    if detected:
        st.markdown(
            f'<div class="hb-detected">{t("photo_detected")}<br/>{detected}</div>',
            unsafe_allow_html=True,
        )

    name = recipe.get("recipe_name_ur" if lang == "ur" else "recipe_name", "")
    desc = recipe.get("description_ur" if lang == "ur" else "description", "")
    prep = recipe.get("prep_time_min", "?")
    cook = recipe.get("cook_time_min", "?")
    servings = recipe.get("servings", "?")

    _eyebrow = "آپ کی ترکیب" if lang == "ur" else "your recipe"
    st.markdown(
        f'<div class="hb-recipe"><div class="hb-recipe-head"><div class="hb-recipe-eyebrow">{_eyebrow}</div><div class="hb-recipe-title">{name}</div><div class="hb-recipe-desc">{desc}</div><div class="hb-recipe-meta"><span class="hb-recipe-meta-item">⏱ {prep} {t("min_label")} {t("prep_label")}</span><span class="hb-recipe-meta-item">🔥 {cook} {t("min_label")} {t("cook_label")}</span><span class="hb-recipe-meta-item">🍽 {servings} {t("servings_label")}</span></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div style="padding:1.75rem;">', unsafe_allow_html=True)
    col_ing, col_nut = st.columns([1.1, 0.9])

    with col_ing:
        st.markdown(
            f'<div class="hb-recipe-section-head">{t("ingredients_header")}</div>',
            unsafe_allow_html=True,
        )
        ingredients_list = recipe.get("ingredients", [])
        total_pkr = 0
        rows = []
        for ing in ingredients_list:
            item = ing.get("item_ur" if lang == "ur" else "item", "")
            qty = ing.get("quantity", "")
            pkr = ing.get("price_pkr", 0)
            if isinstance(pkr, (int, float)):
                total_pkr += pkr
            rows.append(
                f'<div class="hb-ing-row"><span class="hb-ing-name"><b>{item}</b> · {qty}</span><span class="hb-ing-price">PKR {pkr}</span></div>'
            )
        rows.append(
            f'<div class="hb-ing-total"><span>{t("total_label")}</span><span>~PKR {total_pkr}</span></div>'
        )
        st.markdown("".join(rows), unsafe_allow_html=True)

    with col_nut:
        st.markdown(
            f'<div class="hb-recipe-section-head">{t("nutrition_header")}</div>',
            unsafe_allow_html=True,
        )
        if nutrition:
            cal = nutrition.get("calories", 0)
            prot = nutrition.get("protein", 0)
            carbs = nutrition.get("carbs", 0)
            fat = nutrition.get("fat", 0)
            fiber = nutrition.get("fiber", 0)
            src_note = format_nutrition_source_note(nutrition)
            st.markdown(
                f'<div class="hb-nut-grid"><div><div class="hb-nut-num">{cal}</div><div class="hb-nut-label">{t("calories_label")}</div></div><div><div class="hb-nut-num">{prot}g</div><div class="hb-nut-label">{t("protein_label")}</div></div><div><div class="hb-nut-num">{carbs}g</div><div class="hb-nut-label">{t("carbs_label")}</div></div><div><div class="hb-nut-num">{fat}g</div><div class="hb-nut-label">{t("fat_label")}</div></div><div style="grid-column:1 / -1;"><div class="hb-nut-num">{fiber}g</div><div class="hb-nut-label">{t("fiber_label")}</div></div></div><div class="hb-nut-source">{src_note}</div>',
                unsafe_allow_html=True,
            )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="padding:0 1.75rem 1rem 1.75rem;">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="hb-recipe-section-head">{t("instructions_header")}</div>',
        unsafe_allow_html=True,
    )
    steps = recipe.get("instructions_ur" if lang == "ur" else "instructions", [])
    step_rows = []
    for i, step in enumerate(steps, 1):
        step_rows.append(
            f'<div class="hb-step-row"><span class="hb-step-num">{i}</span><span class="hb-step-text">{step}</span></div>'
        )
    st.markdown("".join(step_rows), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    health = recipe.get("health_tips_ur" if lang == "ur" else "health_tips", "")
    sustain = recipe.get("sustainability_tip_ur" if lang == "ur" else "sustainability_tip", "")
    serving = recipe.get("serving_suggestions_ur" if lang == "ur" else "serving_suggestions", "")
    closing = recipe.get("closing_remark", "")

    if health:
        st.markdown(
            f'<div class="hb-callout green"><b>{t("health_header")}:</b> {health}</div>',
            unsafe_allow_html=True,
        )
    if sustain:
        st.markdown(
            f'<div class="hb-callout"><b>{t("sustainability_header")}:</b> {sustain}</div>',
            unsafe_allow_html=True,
        )
    if serving:
        st.markdown(
            f'<div class="hb-callout"><b>{t("serving_header")}:</b> {serving}</div>',
            unsafe_allow_html=True,
        )
    if closing:
        st.markdown(
            f'<div class="hb-callout"><i>{closing}</i></div>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="margin-top:1rem;">', unsafe_allow_html=True)
    download_text = recipe_to_text(recipe, lang=lang)
    st.download_button(
        label=t("download_btn"),
        data=download_text,
        file_name=t("download_filename"),
        mime="text/plain",
        use_container_width=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SHARE
# ─────────────────────────────────────────────
APP_URL = "https://healthy-bawarchi-v2-d6jvkxzb4ghgae8ae3iiyb.streamlit.app/"

if lang == "ur":
    _share_title = "ہیلتھی باورچی شیئر کریں"
    _share_body = "اپنے فون سے کیو آر کوڈ اسکین کریں، یا نیچے دیا گیا لنک کاپی کریں۔"
else:
    _share_title = "Share Healthy Bawarchi"
    _share_body = "Scan the QR with any phone, or copy the link to send to family."

st.markdown('<div class="hb-card">', unsafe_allow_html=True)
share_col1, share_col2 = st.columns([1, 2.2], gap="medium")
with share_col1:
    try:
        st.image("healthy_bawarchi_qr_only.png", use_container_width=True)
    except Exception:
        st.caption("—")
with share_col2:
    st.markdown(
        f'<div class="hb-share-text-title">{_share_title}</div><div class="hb-share-text-body">{_share_body}</div>',
        unsafe_allow_html=True,
    )
    st.text_input("App link", value=APP_URL, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
if lang == "ur":
    _footer = "محبت سے بنایا گیا · OpenAI کی AI · USDA کی غذائیت · پاکستان کے لیے"
else:
    _footer = "Built with care · AI by OpenAI · Nutrition by USDA · Made for Pakistan"

st.markdown(
    f'<div class="hb-footer">{_footer}</div>',
    unsafe_allow_html=True,
)
