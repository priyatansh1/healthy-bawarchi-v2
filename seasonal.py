"""
Seasonal awareness for Healthy Bawarchi.

Provides:
  • What's-in-season-now data for Pakistan + the three other cuisines
  • Imported / high-food-miles items and local alternatives
  • Helpers that produce sidebar text (English + Urdu) and AI-prompt context

Data sources:
  - Pakistan Rabi/Kharif crop calendars (Agribusiness Pakistan, AARI Punjab)
  - Qurban Agro Farms seasonal fruit guide
  - Italy / China / Mexico typical produce seasonality (general references)

Note: In Pakistan, transport is a smaller share of total food emissions
(~10% globally per WEF) than what is eaten. So the imported flag here is
informational, not alarmist — it points users toward delicious local
alternatives rather than scolding them.
"""

from datetime import datetime


# ─────────────────────────────────────────────────────────────────
# Pakistan — month-by-month produce (1 = Jan, 12 = Dec)
# Each item: (English, Urdu, "peak" | "available")
# ─────────────────────────────────────────────────────────────────
PAKISTAN_BY_MONTH = {
    1: [
        ("cauliflower", "گوبھی", "peak"),
        ("spinach", "پالک", "peak"),
        ("mustard greens", "سرسوں کا ساگ", "peak"),
        ("carrots", "گاجر", "peak"),
        ("turnips", "شلجم", "peak"),
        ("peas", "مٹر", "peak"),
        ("oranges", "مالٹا", "peak"),
        ("kinnow", "کنو", "peak"),
        ("guava", "امرود", "peak"),
        ("radish", "مولی", "available"),
        ("garlic", "لہسن", "available"),
        ("ginger", "ادرک", "available"),
    ],
    2: [
        ("cauliflower", "گوبھی", "peak"),
        ("spinach", "پالک", "peak"),
        ("mustard greens", "سرسوں کا ساگ", "peak"),
        ("peas", "مٹر", "peak"),
        ("carrots", "گاجر", "peak"),
        ("strawberries", "اسٹرابیری", "peak"),
        ("kinnow", "کنو", "available"),
        ("guava", "امرود", "available"),
        ("coriander", "دھنیا", "peak"),
        ("fenugreek (methi)", "میتھی", "peak"),
    ],
    3: [
        ("strawberries", "اسٹرابیری", "peak"),
        ("loquat", "لوکاٹ", "peak"),
        ("spinach", "پالک", "available"),
        ("peas", "مٹر", "available"),
        ("coriander", "دھنیا", "peak"),
        ("mint", "پودینہ", "peak"),
        ("fresh garlic", "تازہ لہسن", "peak"),
        ("spring onion", "ہرا پیاز", "peak"),
    ],
    4: [
        ("loquat", "لوکاٹ", "peak"),
        ("apricots", "خوبانی", "peak"),
        ("watermelon", "تربوز", "available"),
        ("cucumber", "کھیرا", "available"),
        ("mint", "پودینہ", "peak"),
        ("zucchini", "تورئی", "available"),
    ],
    5: [
        ("mango", "آم", "peak"),
        ("watermelon", "تربوز", "peak"),
        ("muskmelon", "خربوزہ", "peak"),
        ("mulberry", "شہتوت", "peak"),
        ("apricots", "خوبانی", "peak"),
        ("falsa", "فالسہ", "peak"),
        ("okra (bhindi)", "بھنڈی", "available"),
        ("bottle gourd", "لوکی", "available"),
        ("cucumber", "کھیرا", "peak"),
        ("mint", "پودینہ", "peak"),
    ],
    6: [
        ("mango", "آم", "peak"),
        ("watermelon", "تربوز", "peak"),
        ("muskmelon", "خربوزہ", "peak"),
        ("falsa", "فالسہ", "peak"),
        ("jamun", "جامن", "peak"),
        ("lychee", "لیچی", "peak"),
        ("okra", "بھنڈی", "peak"),
        ("bottle gourd", "لوکی", "peak"),
        ("ridge gourd (tori)", "توری", "peak"),
        ("bitter gourd (karela)", "کریلا", "peak"),
        ("cucumber", "کھیرا", "peak"),
    ],
    7: [
        ("mango", "آم", "peak"),
        ("jamun", "جامن", "peak"),
        ("peaches", "آڑو", "peak"),
        ("plums", "آلوبخارا", "peak"),
        ("okra", "بھنڈی", "peak"),
        ("bottle gourd", "لوکی", "peak"),
        ("ridge gourd", "توری", "peak"),
        ("bitter gourd", "کریلا", "peak"),
        ("eggplant", "بینگن", "peak"),
        ("tinda gourd", "ٹینڈا", "peak"),
        ("tomato", "ٹماٹر", "available"),
    ],
    8: [
        ("mango", "آم", "available"),
        ("peaches", "آڑو", "peak"),
        ("plums", "آلوبخارا", "peak"),
        ("pears", "ناشپاتی", "peak"),
        ("okra", "بھنڈی", "peak"),
        ("eggplant", "بینگن", "peak"),
        ("bitter gourd", "کریلا", "peak"),
        ("tinda gourd", "ٹینڈا", "peak"),
        ("pumpkin", "کدو", "available"),
    ],
    9: [
        ("apples", "سیب", "peak"),
        ("pears", "ناشپاتی", "peak"),
        ("guava", "امرود", "available"),
        ("pomegranate", "انار", "peak"),
        ("eggplant", "بینگن", "available"),
        ("pumpkin", "کدو", "peak"),
        ("spinach", "پالک", "available"),
        ("sweet potato", "شکرقندی", "available"),
    ],
    10: [
        ("apples", "سیب", "peak"),
        ("pomegranate", "انار", "peak"),
        ("persimmon", "جاپانی پھل", "peak"),
        ("guava", "امرود", "peak"),
        ("cauliflower", "گوبھی", "available"),
        ("spinach", "پالک", "available"),
        ("sweet potato", "شکرقندی", "peak"),
        ("pumpkin", "کدو", "peak"),
    ],
    11: [
        ("oranges", "مالٹا", "peak"),
        ("kinnow", "کنو", "peak"),
        ("guava", "امرود", "peak"),
        ("pomegranate", "انار", "peak"),
        ("persimmon", "جاپانی پھل", "peak"),
        ("cauliflower", "گوبھی", "peak"),
        ("spinach", "پالک", "peak"),
        ("mustard greens", "سرسوں کا ساگ", "peak"),
        ("carrots", "گاجر", "peak"),
        ("peas", "مٹر", "peak"),
    ],
    12: [
        ("oranges", "مالٹا", "peak"),
        ("kinnow", "کنو", "peak"),
        ("guava", "امرود", "peak"),
        ("cauliflower", "گوبھی", "peak"),
        ("spinach", "پالک", "peak"),
        ("mustard greens", "سرسوں کا ساگ", "peak"),
        ("carrots", "گاجر", "peak"),
        ("turnips", "شلجم", "peak"),
        ("peas", "مٹر", "peak"),
        ("radish", "مولی", "peak"),
    ],
}


# ─────────────────────────────────────────────────────────────────
# Other cuisines — abbreviated month-by-month (Northern hemisphere)
# ─────────────────────────────────────────────────────────────────
ITALIAN_BY_MONTH = {
    1:  ["radicchio", "fennel", "cabbage", "leeks", "oranges", "blood oranges"],
    2:  ["radicchio", "fennel", "artichokes", "blood oranges", "kale"],
    3:  ["artichokes", "asparagus", "spring onions", "fava beans", "lemons"],
    4:  ["asparagus", "fava beans", "artichokes", "peas", "spring onions"],
    5:  ["asparagus", "peas", "strawberries", "cherries", "fennel", "fava beans"],
    6:  ["zucchini", "tomatoes", "basil", "cherries", "apricots", "peaches"],
    7:  ["tomatoes", "zucchini", "eggplant", "basil", "peaches", "figs"],
    8:  ["tomatoes", "eggplant", "peppers", "basil", "figs", "grapes", "melon"],
    9:  ["grapes", "figs", "porcini mushrooms", "pumpkin", "tomatoes", "peppers"],
    10: ["mushrooms", "pumpkin", "chestnuts", "persimmons", "pomegranate", "broccoli"],
    11: ["mushrooms", "pumpkin", "chestnuts", "cabbage", "fennel", "oranges"],
    12: ["radicchio", "fennel", "cabbage", "oranges", "pomegranate", "leeks"],
}

CHINESE_BY_MONTH = {
    1:  ["bok choy", "napa cabbage", "daikon radish", "winter melon", "mandarin orange"],
    2:  ["bok choy", "napa cabbage", "daikon", "scallions", "shiitake"],
    3:  ["bamboo shoots", "snow peas", "spring onions", "garlic chives", "spinach"],
    4:  ["bamboo shoots", "snow peas", "asparagus", "Chinese celery", "loquat"],
    5:  ["bamboo shoots", "asparagus", "lychee", "loquat", "snow peas"],
    6:  ["lychee", "longan", "bitter melon", "winter melon", "cucumber", "eggplant"],
    7:  ["bitter melon", "winter melon", "luffa", "Chinese long beans", "eggplant"],
    8:  ["winter melon", "luffa", "long beans", "eggplant", "lotus root"],
    9:  ["lotus root", "taro", "pears", "Chinese yam", "bok choy"],
    10: ["taro", "pumpkin", "Chinese yam", "persimmon", "pomelo", "pears"],
    11: ["napa cabbage", "winter melon", "pomelo", "mandarin", "daikon"],
    12: ["napa cabbage", "bok choy", "daikon", "winter melon", "mandarin"],
}

MEXICAN_BY_MONTH = {
    1:  ["oranges", "limes", "cabbage", "carrots", "jicama", "guava"],
    2:  ["limes", "oranges", "cabbage", "jicama", "papaya"],
    3:  ["nopales (cactus)", "fava beans", "spring onions", "cilantro", "limes"],
    4:  ["nopales", "tomatillos", "fava beans", "cilantro", "papaya"],
    5:  ["tomatillos", "tomatoes", "zucchini", "mango", "papaya", "avocado"],
    6:  ["tomatoes", "tomatillos", "zucchini", "corn", "mango", "avocado", "chiles"],
    7:  ["corn", "tomatoes", "tomatillos", "chiles", "squash blossoms", "mango"],
    8:  ["corn", "tomatoes", "chiles", "squash blossoms", "avocado", "watermelon"],
    9:  ["corn", "chiles", "squash", "tomatillos", "guava", "pomegranate"],
    10: ["squash", "pumpkin", "guava", "pomegranate", "limes", "tejocotes"],
    11: ["squash", "pumpkin", "guava", "limes", "oranges", "tejocotes"],
    12: ["pumpkin", "tejocotes", "limes", "oranges", "jicama", "cabbage"],
}


CUISINE_CALENDARS = {
    "Pakistani": PAKISTAN_BY_MONTH,
    "Italian":   ITALIAN_BY_MONTH,
    "Chinese":   CHINESE_BY_MONTH,
    "Mexican":   MEXICAN_BY_MONTH,
}


# ─────────────────────────────────────────────────────────────────
# Imported / high-food-miles items in the Pakistan context
# ─────────────────────────────────────────────────────────────────
IMPORTED_ALTERNATIVES = {
    "avocado":      ("often imported", "guava — creamy texture, locally grown"),
    "blueberries":  ("imported / out of season", "jamun or falsa — same antioxidant rush"),
    "raspberries":  ("imported", "mulberries (shahtoot) when in season"),
    "kale":         ("imported / niche", "saag, palak, or methi — same nutrient profile"),
    "quinoa":       ("imported grain", "millet (bajra), barley (jau), or daliya"),
    "salmon":       ("imported / air-freighted", "rohu, trout, or local hilsa"),
    "tuna":         ("imported / canned-imported", "fresh local mackerel or pomfret"),
    "chia seeds":   ("imported", "basil seeds (tukh malanga) — almost identical"),
    "goji berries": ("imported", "dried mulberry or apricot"),
    "asparagus":    ("often imported", "young bottle gourd or zucchini"),
    "broccoli":     ("imported / off-season locally", "cauliflower (gobhi)"),
    "cranberries":  ("imported", "pomegranate (anar) seeds"),
    "kiwi":         ("imported", "guava — comparable vitamin C, lower miles"),
    "almonds (US)": ("often imported", "local Hunza almonds when in season"),
    "olive oil":    ("imported", "mustard or sesame oil for desi dishes"),
    "maple syrup":  ("imported", "jaggery (gur) or honey (shahd)"),
    "edamame":      ("imported", "fresh peas (matar) or chickpeas (chana)"),
}


# ─────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────
MONTH_NAMES_EN = ["", "January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
MONTH_NAMES_UR = ["", "جنوری", "فروری", "مارچ", "اپریل", "مئی", "جون",
                  "جولائی", "اگست", "ستمبر", "اکتوبر", "نومبر", "دسمبر"]


def current_month() -> int:
    """Return current month number (1-12)."""
    return datetime.now().month


def month_name(month: int = None, lang: str = "en") -> str:
    """Return month name in English or Urdu."""
    m = month if month else current_month()
    if lang == "ur":
        return MONTH_NAMES_UR[m]
    return MONTH_NAMES_EN[m]


def in_season(cuisine: str, month: int = None, max_items: int = 8) -> list:
    """
    Return a list of items in season for a cuisine in a given month.

    For Pakistan: returns list of dicts {en, ur, peak}.
    For other cuisines: returns list of dicts {en, ur=None, peak=True}.
    """
    m = month if month else current_month()

    if cuisine == "Pakistani":
        items = PAKISTAN_BY_MONTH.get(m, [])
        # Sort peak items first
        items_sorted = sorted(items, key=lambda x: 0 if x[2] == "peak" else 1)
        return [
            {"en": en, "ur": ur, "peak": (status == "peak")}
            for (en, ur, status) in items_sorted[:max_items]
        ]

    cal = CUISINE_CALENDARS.get(cuisine)
    if not cal:
        return []
    items = cal.get(m, [])[:max_items]
    return [{"en": en, "ur": None, "peak": True} for en in items]


def find_imported(text: str) -> list:
    """
    Scan user-provided ingredient text for known imported items.
    Returns a list of dicts {item, label, alternative}.
    """
    if not text:
        return []
    t = text.lower()
    found = []
    for item, (label, alt) in IMPORTED_ALTERNATIVES.items():
        key = item.split(" (")[0].strip()
        if key in t:
            found.append({"item": key, "label": label, "alternative": alt})
    return found


def find_seasonal_in_text(text: str, cuisine: str, month: int = None) -> list:
    """
    Scan user-provided ingredient text for items currently in season
    for the given cuisine. Returns list of English names.
    """
    if not text:
        return []
    t = text.lower()
    season_items = in_season(cuisine, month, max_items=20)
    hits = []
    for s in season_items:
        en = s["en"].lower()
        key = en.split(" (")[0].strip()
        if key in t:
            hits.append(s["en"])
    return hits


def seasonal_prompt_context(text: str, cuisine: str, month: int = None) -> str:
    """
    Compose a short string injected into the AI recipe prompt, telling it
    which items are seasonal and which are imported with local alternatives.

    Returns plain text — empty string if there's nothing useful to add.
    """
    parts = []

    seasonal_hits = find_seasonal_in_text(text, cuisine, month)
    if seasonal_hits:
        parts.append(
            "SEASONAL NOTE: The following user ingredients are at peak season "
            f"this month for {cuisine} cuisine: {', '.join(seasonal_hits)}. "
            "Build the recipe around these where possible and briefly mention "
            "their seasonal freshness in the recipe's health or sustainability note."
        )

    imported_hits = find_imported(text)
    if imported_hits:
        items_str = "; ".join(
            f"{h['item']} ({h['label']}; suggest local alternative: {h['alternative']})"
            for h in imported_hits
        )
        parts.append(
            "IMPORTED ITEMS NOTE: The user mentioned items often imported into "
            "Pakistan. Use them if needed for the recipe, but in the "
            "sustainability_tip field gently suggest the local alternative for "
            f"future cooking. Items: {items_str}."
        )

    return "\n\n".join(parts)
