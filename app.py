# ============================================================
# Healthy Bawarchi — Main Streamlit App
# Bilingual (EN/UR) AI-powered recipe generator
# ============================================================
import streamlit as st
from PIL import Image

from recipe_engine import generate_recipe, generate_recipe_from_image, recipe_to_text
from usda_nutrition import calculate_recipe_nutrition, format_nutrition_source_note
from i18n import t, get_lang, inject_rtl_css, inject_ltr_css
from seasonal import in_season, month_name
from safety_filter import check_ingredients, get_message as safety_message
from counters import record_visit, record_recipe, get_counts, format_count


# ─────────────────────────────────────────────
# PAGE CONFIG — must be first Streamlit call
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Healthy Bawarchi — Smart Recipe Generator",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ─────────────────────────────────────────────
# SESSION STATE INITIALISATION
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
if "visit_recorded" not in st.session_state:
    st.session_state["visit_recorded"] = False

# Record a visit once per session (avoids inflating count on every reload)
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
# GLOBAL CSS — Green theme, Healthy Bawarchi brand
# ─────────────────────────────────────────────
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #F1F8E9 0%, #E8F5E9 100%);
}
.hero-banner {
    background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #388E3C 100%);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(27, 94, 32, 0.3);
}
.hero-banner h1 {
    color: white;
    font-size: 2.8rem;
    font-weight: 700;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    letter-spacing: 1px;
}
.hero-banner p {
    color: rgba(255,255,255,0.92);
    font-size: 1.05rem;
    margin: 0.5rem 0 0 0;
    font-weight: 300;
}
.hero-tagline {
    color: #CCFF90;
    font-size: 0.95rem;
    font-style: italic;
    margin-top: 0.3rem;
}
.section-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    border-left: 4px solid #2E7D32;
}
.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1B5E20;
    margin-bottom: 0.8rem;
}
.stButton > button {
    background: linear-gradient(135deg, #1B5E20, #2E7D32) !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.75rem 2.5rem !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    width: 100% !important;
    cursor: pointer !important;
    box-shadow: 0 4px 15px rgba(27, 94, 32, 0.4) !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.5px !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(27, 94, 32, 0.5) !important;
}
.recipe-output {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    border-top: 5px solid #2E7D32;
    margin-top: 1.5rem;
}
.cuisine-pill {
    display: inline-block;
    background: #E8F5E9;
    color: #2E7D32;
    border: 1px solid #2E7D32;
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.85rem;
    font-weight: 600;
    margin-right: 0.4rem;
    margin-bottom: 0.8rem;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #E8F5E9;
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 8px 20px;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: #2E7D32 !important;
    color: white !important;
}
.detected-box {
    background: #E8F5E9;
    border: 1px solid #4CAF50;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    font-size: 0.9rem;
    color: #1B5E20;
    margin: 0.5rem 0 1rem 0;
}
.nutrition-card {
    background: #F9FBE7;
    border-radius: 12px;
    padding: 1rem;
    border: 1px solid #C5E1A5;
}
.usda-badge {
    font-size: 0.75rem;
    color: #388E3C;
    font-weight: 600;
    margin-top: 0.5rem;
}
div[data-testid="column"]:last-child .stButton > button {
    background: #E8F5E9 !important;
    color: #1B5E20 !important;
    border: 1px solid #2E7D32 !important;
    border-radius: 20px !important;
    padding: 0.3rem 0.8rem !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    width: auto !important;
    min-width: 90px !important;
    white-space: nowrap !important;
    box-shadow: none !important;
}
.footer {
    text-align: center;
    color: #777;
    font-size: 0.8rem;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid #ddd;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LANGUAGE TOGGLE — top right
# ─────────────────────────────────────────────
col_title, col_toggle = st.columns([6, 1])
with col_toggle:
    if st.button(t("lang_toggle"), key="lang_btn"):
        st.session_state["lang"] = "ur" if lang == "en" else "en"
        st.session_state["recipe"] = None
        st.session_state["nutrition"] = None
        st.rerun()


# ─────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="hero-banner">
    <h1>🥗 {t("title")}</h1>
    <p>{t("subtitle")}</p>
    <div class="hero-tagline">{t("tagline")}</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ACTIVITY COUNTER — visits & recipes generated
# ─────────────────────────────────────────────
_counts = get_counts()
_visits = format_count(_counts.get("visits"))
_recipes = format_count(_counts.get("recipes"))

if get_lang() == "ur":
    _visit_label = "گھریلو باورچیوں نے دورہ کیا"
    _recipe_label = "صحت بخش کھانے تیار کیے گئے"
else:
    _visit_label = "home cooks visited"
    _recipe_label = "healthy meals planned"

st.markdown(
    f"""
<div style="
    display:flex; gap:1rem; flex-wrap:wrap; justify-content:center;
    margin: -0.5rem 0 1.5rem 0;
">
  <div style="
      flex:1 1 220px; min-width:200px; max-width:340px;
      background: white; border-radius: 14px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06);
      padding: 1rem 1.2rem; text-align:center;
      border-bottom: 3px solid #2E7D32;
  ">
    <div style="font-size:1.6rem; font-weight:700; color:#1B5E20; line-height:1.1;">
      🌍 {_visits}
    </div>
    <div style="font-size:0.82rem; color:#555; margin-top:0.25rem;">
      {_visit_label}
    </div>
  </div>
  <div style="
      flex:1 1 220px; min-width:200px; max-width:340px;
      background: white; border-radius: 14px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06);
      padding: 1rem 1.2rem; text-align:center;
      border-bottom: 3px solid #2E7D32;
  ">
    <div style="font-size:1.6rem; font-weight:700; color:#1B5E20; line-height:1.1;">
      🌱 {_recipes}
    </div>
    <div style="font-size:0.82rem; color:#555; margin-top:0.25rem;">
      {_recipe_label}
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# SIDEBAR — Settings / About / Disclaimer
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
    f'<div class="section-card"><div class="section-title">🌍 {t("choose_cuisine")}</div>',
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
# IN SEASON NOW — main-page card (mobile-friendly)
# ─────────────────────────────────────────────
_lang = get_lang()
if _lang == "ur":
    _ss_header = "🌱 ابھی موسم میں"
    _ss_subhead = f"{month_name(lang='ur')} میں {cuisine} کھانوں کے لیے تازہ"
    _ss_tip = "موسمی پیداوار کھانا زیادہ تازہ، سستا اور ماحول کے لیے بہتر ہے۔"
else:
    _ss_header = "🌱 In Season Now"
    _ss_subhead = f"Fresh in {month_name(lang='en')} for {cuisine} cuisine"
    _ss_tip = "Cooking with seasonal produce is fresher, cheaper, and uses less energy to grow and ship."

st.markdown(
    f'<div class="section-card"><div class="section-title">{_ss_header}</div>',
    unsafe_allow_html=True,
)
st.caption(_ss_subhead)

_season_items = in_season(cuisine, max_items=8)
if _season_items:
    # Build horizontally-scrolling pill chips so the strip works on mobile
    _chips_html = []
    for _it in _season_items:
        _star = "⭐ " if _it["peak"] else ""
        if _lang == "ur" and _it.get("ur"):
            _label = f"{_star}{_it['ur']}"
        else:
            _label = f"{_star}{_it['en']}"
            if _it.get("ur"):
                _label += f" · {_it['ur']}"
        _bg = "#E8F5E9" if _it["peak"] else "#F1F8E9"
        _border = "#2E7D32" if _it["peak"] else "#A5D6A7"
        _chips_html.append(
            f'<span style="display:inline-block; background:{_bg}; '
            f'color:#1B5E20; border:1px solid {_border}; '
            f'border-radius:20px; padding:0.35rem 0.85rem; margin:0.2rem 0.3rem 0.2rem 0; '
            f'font-size:0.92rem; font-weight:600; white-space:nowrap;">{_label}</span>'
        )

    st.markdown(
        f'<div style="overflow-x:auto; padding:0.4rem 0; -webkit-overflow-scrolling:touch;">'
        f'<div style="display:flex; flex-wrap:wrap;">{"".join(_chips_html)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div style="margin-top:0.6rem; padding:0.5rem 0.8rem; '
        f'background:#E8F5E9; border-left:3px solid #2E7D32; '
        f'border-radius:6px; font-size:0.85rem; color:#1B5E20; '
        f'font-style:italic;">💡 {_ss_tip}</div>',
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAX INGREDIENTS SLIDER
# ─────────────────────────────────────────────
st.markdown(
    f'<div class="section-card"><div class="section-title">🔢 {t("max_ingredients_label")}</div>',
    unsafe_allow_html=True,
)

max_ingredients = st.slider(
    "Max ingredients",
    min_value=3,
    max_value=10,
    value=5,
    help="Fewer ingredients = more budget-friendly and less food waste",
    label_visibility="collapsed",
)
st.caption(t("max_ingredients_caption", n=max_ingredients))

st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# INGREDIENT INPUT
# ─────────────────────────────────────────────
st.markdown(
    f'<div class="section-card"><div class="section-title">🥦 {t("what_ingredients")}</div>',
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs([t("tab_type"), t("tab_photo")])

ingredients_text = ""
uploaded_image_bytes = None

with tab1:
    ingredients_text = st.text_area(
        "Ingredients",
        placeholder=t("type_placeholder"),
        height=120,
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
        st.image(image, caption="", use_container_width=True)
        uploaded_image_bytes = uploaded_file.getvalue()
    st.caption(t("photo_caption"))

st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# GENERATE BUTTON
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
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

    # ── Safety check — runs ONLY on typed text ──────────────────
    # (Image-based detection goes through GPT-4o vision which has
    # its own safety; we filter the typed pathway here.)
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

            # Record this successful recipe generation in the global counter
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
# RECIPE OUTPUT RENDERING
# ─────────────────────────────────────────────
recipe = st.session_state.get("recipe")
nutrition = st.session_state.get("nutrition")
detected = st.session_state.get("detected_ingredients")

if recipe:
    lang = get_lang()

    if detected:
        st.markdown(
            f'<div class="detected-box">{t("photo_detected")}<br>{detected}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="recipe-output">', unsafe_allow_html=True)

    name = recipe.get("recipe_name_ur" if lang == "ur" else "recipe_name", "")
    desc = recipe.get("description_ur" if lang == "ur" else "description", "")
    st.markdown(f"## 🥗 {name}")
    st.markdown(f"*{desc}*")

    prep = recipe.get("prep_time_min", "?")
    cook = recipe.get("cook_time_min", "?")
    servings = recipe.get("servings", "?")
    st.markdown(
        f'<span class="cuisine-pill">{cuisine_display}</span>'
        f'<span class="cuisine-pill">⏱ {prep} {t("min_label")} {t("prep_label")}</span>'
        f'<span class="cuisine-pill">🍳 {cook} {t("min_label")} {t("cook_label")}</span>'
        f'<span class="cuisine-pill">🍽 {servings} {t("servings_label")}</span>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    col_ing, col_nut = st.columns([1.1, 0.9])

    with col_ing:
        st.markdown(f"### 🛒 {t('ingredients_header')}")
        ingredients_list = recipe.get("ingredients", [])
        total_pkr = 0
        for ing in ingredients_list:
            item = ing.get("item_ur" if lang == "ur" else "item", "")
            qty = ing.get("quantity", "")
            pkr = ing.get("price_pkr", 0)
            total_pkr += pkr if isinstance(pkr, (int, float)) else 0
            st.markdown(f"• **{item}** — {qty} *(~PKR {pkr})*")
        st.markdown(f"**{t('total_label')}: ~PKR {total_pkr}**")

    with col_nut:
        st.markdown(f"### 📊 {t('nutrition_header')}")
        if nutrition:
            cal = nutrition.get("calories", 0)
            prot = nutrition.get("protein", 0)
            carbs = nutrition.get("carbs", 0)
            fat = nutrition.get("fat", 0)
            fiber = nutrition.get("fiber", 0)
            src_note = format_nutrition_source_note(nutrition)

            st.markdown('<div class="nutrition-card">', unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            m1.metric(t("calories_label"), f"{cal} kcal")
            m2.metric(t("protein_label"), f"{prot}g")
            m3, m4 = st.columns(2)
            m3.metric(t("carbs_label"), f"{carbs}g")
            m4.metric(t("fat_label"), f"{fat}g")
            st.metric(t("fiber_label"), f"{fiber}g")
            st.markdown(
                f'<div class="usda-badge">{src_note}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### 👨‍🍳 {t('instructions_header')}")
    steps = recipe.get("instructions_ur" if lang == "ur" else "instructions", [])
    for i, step in enumerate(steps, 1):
        st.markdown(f"**{i}.** {step}")

    st.markdown("---")
    health = recipe.get("health_tips_ur" if lang == "ur" else "health_tips", "")
    st.success(f"💚 **{t('health_header')}**\n\n{health}")

    sustain = recipe.get("sustainability_tip_ur" if lang == "ur" else "sustainability_tip", "")
    st.info(f"♻️ **{t('sustainability_header')}**\n\n{sustain}")

    serving = recipe.get("serving_suggestions_ur" if lang == "ur" else "serving_suggestions", "")
    st.markdown(f"🍽 **{t('serving_header')}:** {serving}")

    closing = recipe.get("closing_remark", "")
    st.markdown(
        f'<div style="margin-top:1rem; padding:0.8rem 1rem; background:#E8F5E9; '
        f'border-radius:10px; font-style:italic; color:#1B5E20;">'
        f'💬 <strong>{t("closing_header")}:</strong> {closing}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    download_text = recipe_to_text(recipe, lang=lang)
    st.download_button(
        label=t("download_btn"),
        data=download_text,
        file_name=t("download_filename"),
        mime="text/plain",
        use_container_width=True,
    )

    st.caption(t("sidebar_disclaimer"))


# ─────────────────────────────────────────────
# SHARE THIS APP — QR code & link
# ─────────────────────────────────────────────
APP_URL = "https://healthy-bawarchi-v2-d6jvkxzb4ghgae8ae3iiyb.streamlit.app/"

if get_lang() == "ur":
    share_header = "ہیلتھی باورچی شیئر کریں"
    share_tagline = "اپنے فون سے کیو آر کوڈ اسکین کریں، یا نیچے دیا گیا لنک کاپی کریں۔"
    share_link_label = "ایپ کا لنک"
else:
    share_header = "Share Healthy Bawarchi"
    share_tagline = "Scan the QR code with your phone, or copy the link below to share."
    share_link_label = "App link"

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    f'<div class="section-card"><div class="section-title">📱 {share_header}</div>',
    unsafe_allow_html=True,
)

share_col1, share_col2 = st.columns([1, 1.4], gap="medium")

with share_col1:
    try:
        st.image("healthy_bawarchi_qr_only.png", use_container_width=True)
    except Exception:
        st.caption("QR code image not found.")

with share_col2:
    st.markdown(
        f'<p style="color:#1B5E20; font-size:0.95rem; margin-bottom:0.8rem;">'
        f'{share_tagline}</p>',
        unsafe_allow_html=True,
    )
    st.text_input(
        share_link_label,
        value=APP_URL,
        label_visibility="collapsed",
    )
    st.markdown(
        f'<a href="{APP_URL}" target="_blank" '
        f'style="display:inline-block; background:#2E7D32; color:white; '
        f'padding:0.5rem 1.2rem; border-radius:50px; text-decoration:none; '
        f'font-weight:600; font-size:0.9rem; margin-top:0.5rem;">'
        f'🔗 Open in new tab</a>',
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown(
    f'<div class="footer">{t("footer")}</div>',
    unsafe_allow_html=True,
)
