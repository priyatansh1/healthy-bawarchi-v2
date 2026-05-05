"""
Seasonal awareness for Healthy Bawarchi.

Provides:
  • What's-in-season-now data for Pakistan + the three other cuisines
  • Imported / high-food-miles items and local alternatives
  • Helpers that produce sidebar text (English + Urdu) and AI-prompt context

Each Pakistani item is tagged as fruit / veg / herb / grain so the sidebar
can show a balanced mix — not just whichever items happen to come first.

Data sources:
  - Pakistan Rabi/Kharif crop calendars (Agribusiness Pakistan, AARI Punjab)
  - Qurban Agro Farms seasonal fruit guide
  - Italy / China / Mexico typical produce seasonality (general references)
"""

from datetime import datetime


# ─────────────────────────────────────────────────────────────────
# Pakistan — month-by-month produce (1 = Jan, 12 = Dec)
# Each item: (English, Urdu, "peak" | "available", category)
# Categories: "fruit", "veg", "herb", "grain"
# ─────────────────────────────────────────────────────────────────
PAKISTAN_BY_MONTH = {
    1: [
        ("cauliflower", "گوبھی", "peak", "veg"),
        ("spinach", "پالک", "peak", "veg"),
        ("mustard greens", "سرسوں کا ساگ", "peak", "veg"),
        ("carrots", "گاجر", "peak", "veg"),
        ("turnips", "شلجم", "peak", "veg"),
        ("peas", "مٹر", "peak", "veg"),
        ("oranges", "مالٹا", "peak", "fruit"),
        ("kinnow", "کنو", "peak", "fruit"),
        ("guava", "امرود", "peak", "fruit"),
        ("radish", "مولی", "available", "veg"),
        ("garlic", "لہسن", "available", "herb"),
        ("ginger", "ادرک", "available", "herb"),
    ],
    2: [
        ("cauliflower", "گوبھی", "peak", "veg"),
        ("spinach", "پالک", "peak", "veg"),
        ("mustard greens", "سرسوں کا ساگ", "peak", "veg"),
        ("peas", "مٹر", "peak", "veg"),
        ("carrots", "گاجر", "peak", "veg"),
        ("strawberries", "اسٹرابیری", "peak", "fruit"),
        ("kinnow", "کنو", "available", "fruit"),
        ("guava", "امرود", "available", "fruit"),
        ("coriander", "دھنیا", "peak", "herb"),
        ("fenugreek (methi)", "میتھی", "peak", "herb"),
    ],
    3: [
        ("strawberries", "اسٹرابیری", "peak", "fruit"),
        ("loquat", "لوکاٹ", "peak", "fruit"),
        ("spinach", "پالک", "available", "veg"),
        ("peas", "مٹر", "available", "veg"),
        ("coriander", "دھنیا", "peak", "herb"),
        ("mint", "پودینہ", "peak", "herb"),
        ("fresh garlic", "تازہ لہسن", "peak", "herb"),
        ("spring onion", "ہرا پیاز", "peak", "veg"),
    ],
    4: [
        ("loquat", "لوکاٹ", "peak", "fruit"),
        ("apricots", "خوبانی", "peak", "fruit"),
        ("watermelon", "تربوز", "available", "fruit"),
        ("cucumber", "کھیرا", "available", "veg"),
        ("mint", "پودینہ", "peak", "herb"),
        ("zucchini", "تورئی", "available", "veg"),
    ],
    5: [
        ("mango", "آم", "peak", "fruit"),
        ("watermelon", "تربوز", "peak", "fruit"),
        ("muskmelon", "خربوزہ", "peak", "fruit"),
        ("mulberry", "شہتوت", "peak", "fruit"),
        ("apricots", "خوبانی", "peak", "fruit"),
        ("falsa", "فالسہ", "peak", "fruit"),
        ("okra (bhindi)", "بھنڈی", "available", "veg"),
        ("bottle gourd", "لوکی", "available", "veg"),
        ("cucumber", "کھیرا", "peak", "veg"),
        ("mint", "پودینہ", "peak", "herb"),
    ],
    6: [
        ("mango", "آم", "peak", "fruit"),
        ("watermelon", "تربوز", "peak", "fruit"),
        ("muskmelon", "خربوزہ", "peak", "fruit"),
        ("falsa", "فالسہ", "peak", "fruit"),
        ("jamun", "جامن", "peak", "fruit"),
        ("lychee", "لیچی", "peak", "fruit"),
        ("okra", "بھنڈی", "peak", "veg"),
        ("bottle gourd", "لوکی", "peak", "veg"),
        ("ridge gourd (tori)", "توری", "peak", "veg"),
        ("bitter gourd (karela)", "کریلا", "peak", "veg"),
        ("cucumber", "کھیرا", "peak", "veg"),
    ],
    7: [
        ("mango", "آم", "peak", "fruit"),
        ("jamun", "جامن", "peak", "fruit"),
        ("peaches", "آڑو", "peak", "fruit"),
        ("plums", "آلوبخارا", "peak", "fruit"),
        ("okra", "بھنڈی", "peak", "veg"),
        ("bottle gourd", "لوکی", "peak", "veg"),
        ("ridge gourd", "توری", "peak", "veg"),
        ("bitter gourd", "کریلا", "peak", "veg"),
        ("eggplant", "بینگن", "peak", "veg"),
        ("tinda gourd", "ٹینڈا", "peak", "veg"),
        ("tomato", "ٹماٹر", "available", "veg"),
    ],
    8: [
        ("mango", "آم", "available", "fruit"),
        ("peaches", "آڑو", "peak", "fruit"),
        ("plums", "آلوبخارا", "peak", "fruit"),
        ("pears", "ناشپاتی", "peak", "fruit"),
        ("okra", "بھنڈی", "peak", "veg"),
        ("eggplant", "بینگن", "peak", "veg"),
        ("bitter gourd", "کریلا", "peak", "veg"),
        ("tinda gourd", "ٹینڈا", "peak", "veg"),
        ("pumpkin", "کدو", "available", "veg"),
    ],
    9: [
        ("apples", "سیب", "peak", "fruit"),
        ("pears", "ناشپاتی", "peak", "fruit"),
        ("guava", "امرود", "available", "fruit"),
        ("pomegranate", "انار", "peak", "fruit"),
        ("eggplant", "بینگن", "available", "veg"),
        ("pumpkin", "کدو", "peak", "veg"),
        ("spinach", "پالک", "available", "veg"),
        ("sweet potato", "شکرقندی", "available", "veg"),
    ],
    10: [
        ("apples", "سیب", "peak", "fruit"),
        ("pomegranate", "انار", "peak", "fruit"),
        ("persimmon", "جاپانی پھل", "peak", "fruit"),
        ("guava", "امرود", "peak", "fruit"),
        ("cauliflower", "گوبھی", "available", "veg"),
        ("spinach", "پالک", "available", "veg"),
        ("sweet potato", "شکرقندی", "peak", "veg"),
        ("pumpkin", "کدو", "peak", "veg"),
    ],
    11: [
        ("oranges", "مالٹا", "peak", "fruit"),
        ("kinnow", "کنو", "peak", "fruit"),
        ("guava", "امرود", "peak", "fruit"),
        ("pomegranate", "انار", "peak", "fruit"),
        ("persimmon", "جاپانی پھل", "peak", "fruit"),
        ("cauliflower", "گوبھی", "peak", "veg"),
        ("spinach", "پالک", "peak", "veg"),
        ("mustard greens", "سرسوں کا ساگ", "peak", "veg"),
        ("carrots", "گاجر", "peak", "veg"),
        ("peas", "مٹر", "peak", "veg"),
    ],
    12: [
        ("oranges", "مالٹا", "peak", "fruit"),
        ("kinnow", "کنو", "peak", "fruit"),
        ("guava", "امرود", "peak", "fruit"),
        ("cauliflower", "گوبھی", "peak", "veg"),
        ("spinach", "پالک", "peak", "veg"),
        ("mustard greens", "سرسوں کا ساگ", "peak", "veg"),
        ("carrots", "گاجر", "peak", "veg"),
        ("turnips", "شلجم", "peak", "veg"),
        ("peas", "مٹر", "peak", "veg"),
        ("radish", "مولی", "peak", "veg"),
    ],
}


# ─────────────────────────────────────────────────────────────────
# Other cuisines — abbreviated month-by-month (Northern hemisphere)
# Format kept simple: just English names
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
    Return a balanced mix of items in season for a cuisine in a given month.

    For Pakistan: balanced across fruits, veggies, and herbs.
    For other cuisines: simple ordered list, English only.

    Returns a list of dicts with keys: en, ur, peak, category.
    """
    m = month if month else current_month()

    if cuisine == "Pakistani":
        items = PAKISTAN_BY_MONTH.get(m, [])

        # Bucket items by category, peak items first within each bucket
        buckets = {"fruit": [], "veg": [], "herb": [], "grain": []}
        for entry in items:
            en, ur, status, cat = entry
            buckets.setdefault(cat, []).append({
                "en": en, "ur": ur, "peak": (status == "peak"), "category": cat,
            })
        for cat in buckets:
            buckets[cat].sort(key=lambda x: 0 if x["peak"] else 1)

        # Aim for up to half fruits, half veggies, plus 1 herb if available
        half = max_items // 2
        herb_quota = 1 if max_items >= 4 else 0
        veg_quota = max_items - half - herb_quota

        result = []
        result.extend(buckets.get("fruit", [])[:half])
        result.extend(buckets.get("veg",   [])[:veg_quota])
        result.extend(buckets.get("herb",  [])[:herb_quota])

        # Fill any remaining slots from whichever bucket has spares
        remaining = max_items - len(result)
        if remaining > 0:
            already = {r["en"] for r in result}
            spares = []
            for cat in ("veg", "fruit", "herb", "grain"):
                for entry in buckets.get(cat, []):
                    if entry["en"] not in already:
                        spares.append(entry)
            result.extend(spares[:remaining])

        # Re-sort: peak items first overall, then category grouping for nice display
        result.sort(key=lambda x: (0 if x["peak"] else 1, ["fruit", "veg", "herb", "grain"].index(x["category"])))
        return result[:max_items]

    cal = CUISINE_CALENDARS.get(cuisine)
    if not cal:
        return []
    items = cal.get(m, [])[:max_items]
    return [
        {"en": en, "ur": None, "peak": True, "category": "mixed"}
        for en in items
    ]


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
