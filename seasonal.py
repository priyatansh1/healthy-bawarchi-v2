"""
Seasonal awareness for Healthy Bawarchi.

NEW: Regional calendars for Pakistan
  • Punjab (default — Pakistan's plains heartland, baseline national)
  • Sindh (coastal, hottest, mangoes earlier, dates dominate summer)
  • KPK (similar to Punjab plains in lower areas; upper KPK like Swat
         shifts later by 3-4 weeks, more stone fruits)
  • Balochistan (Pakistan's "fruit basket" — apples, grapes, cherries,
         pomegranates dominate; Mekran dates in summer)
  • Gilgit-Baltistan (mountain calendar — ~6 weeks behind plains;
         apricot/cherry blossoms April; harvest June-July; apples
         Aug-Oct; harsh winter)
  • Pakistan (national average — used when "Outside Pakistan" or
         no region selected; same as Punjab calendar)

Each item is tagged: (English, Urdu, "peak"|"available", category)
Categories: "fruit", "veg", "herb", "grain"

Public API (back-compatible):
  current_month()                        — int 1..12
  month_name(month, lang)                — "May" or "مئی"
  in_season(cuisine, month, max_items, region)
                                          — region defaults to "Pakistan"
  find_imported(text)
  find_seasonal_in_text(text, cuisine, month, region)
  seasonal_prompt_context(text, cuisine, month, region)
  list_regions(lang)                     — NEW: returns list of (code, label)

Sources:
  - Pakistan Crop Calendars (NAMC, AARI Punjab, KP Crop Reporting)
  - Qurban Agro / Multan Farms / Hunza ATP (fruit calendars)
  - Dawn / Balochistan Point articles on regional fruit production
  - General climate knowledge of Pakistan's agro-ecological zones
"""

from datetime import datetime


# ─────────────────────────────────────────────────────────────────
# REGION METADATA
# ─────────────────────────────────────────────────────────────────
REGIONS = [
    ("Pakistan",     "Pakistan",         "پاکستان"),
    ("Punjab",       "Punjab",           "پنجاب"),
    ("Sindh",        "Sindh",            "سندھ"),
    ("KPK",          "KPK",              "خیبر پختونخوا"),
    ("Balochistan",  "Balochistan",      "بلوچستان"),
    ("GilgitBaltistan", "Gilgit-Baltistan",  "گلگت بلتستان"),
    ("Outside",      "Outside Pakistan", "پاکستان سے باہر"),
]


def list_regions(lang: str = "en") -> list:
    """Return list of (region_code, display_label) for the dropdown."""
    return [(code, ur if lang == "ur" else en) for code, en, ur in REGIONS]


def region_label(code: str, lang: str = "en") -> str:
    """Return display label for a region code."""
    for rcode, en, ur in REGIONS:
        if rcode == code:
            return ur if lang == "ur" else en
    return code


# ─────────────────────────────────────────────────────────────────
# PUNJAB — baseline national calendar (Pakistan's plains heartland)
# Used as default and "Pakistan" national average.
# ─────────────────────────────────────────────────────────────────
PUNJAB_BY_MONTH = {
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
# SINDH — coastal, hotter, dates dominant in summer.
# Mangoes start earlier (April) and run longer.
# Dates from Khairpur peak July-August.
# Less of the cool-weather crops than Punjab in winter.
# ─────────────────────────────────────────────────────────────────
SINDH_BY_MONTH = {
    1: [
        ("spinach", "پالک", "peak", "veg"),
        ("cauliflower", "گوبھی", "peak", "veg"),
        ("peas", "مٹر", "peak", "veg"),
        ("carrots", "گاجر", "peak", "veg"),
        ("oranges", "مالٹا", "peak", "fruit"),
        ("guava", "امرود", "peak", "fruit"),
        ("papaya", "پپیتا", "peak", "fruit"),
        ("banana", "کیلا", "peak", "fruit"),
        ("coriander", "دھنیا", "peak", "herb"),
    ],
    2: [
        ("spinach", "پالک", "peak", "veg"),
        ("cauliflower", "گوبھی", "peak", "veg"),
        ("strawberries", "اسٹرابیری", "peak", "fruit"),
        ("guava", "امرود", "peak", "fruit"),
        ("banana", "کیلا", "peak", "fruit"),
        ("papaya", "پپیتا", "peak", "fruit"),
        ("coriander", "دھنیا", "peak", "herb"),
        ("mint", "پودینہ", "available", "herb"),
    ],
    3: [
        ("watermelon", "تربوز", "available", "fruit"),
        ("muskmelon", "خربوزہ", "available", "fruit"),
        ("strawberries", "اسٹرابیری", "peak", "fruit"),
        ("banana", "کیلا", "peak", "fruit"),
        ("cucumber", "کھیرا", "available", "veg"),
        ("mint", "پودینہ", "peak", "herb"),
        ("coriander", "دھنیا", "peak", "herb"),
    ],
    4: [
        ("mango", "آم", "peak", "fruit"),
        ("watermelon", "تربوز", "peak", "fruit"),
        ("muskmelon", "خربوزہ", "peak", "fruit"),
        ("banana", "کیلا", "peak", "fruit"),
        ("cucumber", "کھیرا", "peak", "veg"),
        ("okra", "بھنڈی", "available", "veg"),
        ("mint", "پودینہ", "peak", "herb"),
    ],
    5: [
        ("mango", "آم", "peak", "fruit"),
        ("watermelon", "تربوز", "peak", "fruit"),
        ("muskmelon", "خربوزہ", "peak", "fruit"),
        ("falsa", "فالسہ", "peak", "fruit"),
        ("banana", "کیلا", "peak", "fruit"),
        ("okra", "بھنڈی", "peak", "veg"),
        ("bottle gourd", "لوکی", "peak", "veg"),
        ("cucumber", "کھیرا", "peak", "veg"),
        ("mint", "پودینہ", "peak", "herb"),
    ],
    6: [
        ("mango", "آم", "peak", "fruit"),
        ("dates (fresh)", "تازہ کھجور", "peak", "fruit"),
        ("falsa", "فالسہ", "peak", "fruit"),
        ("watermelon", "تربوز", "peak", "fruit"),
        ("banana", "کیلا", "peak", "fruit"),
        ("okra", "بھنڈی", "peak", "veg"),
        ("bottle gourd", "لوکی", "peak", "veg"),
        ("ridge gourd", "توری", "peak", "veg"),
        ("bitter gourd", "کریلا", "peak", "veg"),
    ],
    7: [
        ("mango", "آم", "peak", "fruit"),
        ("dates", "کھجور", "peak", "fruit"),
        ("jamun", "جامن", "peak", "fruit"),
        ("banana", "کیلا", "peak", "fruit"),
        ("okra", "بھنڈی", "peak", "veg"),
        ("eggplant", "بینگن", "peak", "veg"),
        ("bitter gourd", "کریلا", "peak", "veg"),
        ("tinda gourd", "ٹینڈا", "peak", "veg"),
    ],
    8: [
        ("dates", "کھجور", "peak", "fruit"),
        ("mango", "آم", "available", "fruit"),
        ("guava", "امرود", "available", "fruit"),
        ("banana", "کیلا", "peak", "fruit"),
        ("okra", "بھنڈی", "peak", "veg"),
        ("eggplant", "بینگن", "peak", "veg"),
        ("tinda gourd", "ٹینڈا", "peak", "veg"),
    ],
    9: [
        ("guava", "امرود", "peak", "fruit"),
        ("banana", "کیلا", "peak", "fruit"),
        ("papaya", "پپیتا", "peak", "fruit"),
        ("eggplant", "بینگن", "available", "veg"),
        ("pumpkin", "کدو", "peak", "veg"),
        ("sweet potato", "شکرقندی", "available", "veg"),
    ],
    10: [
        ("guava", "امرود", "peak", "fruit"),
        ("banana", "کیلا", "peak", "fruit"),
        ("papaya", "پپیتا", "peak", "fruit"),
        ("pomegranate", "انار", "peak", "fruit"),
        ("pumpkin", "کدو", "peak", "veg"),
        ("sweet potato", "شکرقندی", "peak", "veg"),
        ("spinach", "پالک", "available", "veg"),
    ],
    11: [
        ("oranges", "مالٹا", "peak", "fruit"),
        ("guava", "امرود", "peak", "fruit"),
        ("banana", "کیلا", "peak", "fruit"),
        ("papaya", "پپیتا", "peak", "fruit"),
        ("cauliflower", "گوبھی", "peak", "veg"),
        ("spinach", "پالک", "peak", "veg"),
        ("carrots", "گاجر", "peak", "veg"),
        ("peas", "مٹر", "available", "veg"),
    ],
    12: [
        ("oranges", "مالٹا", "peak", "fruit"),
        ("guava", "امرود", "peak", "fruit"),
        ("banana", "کیلا", "peak", "fruit"),
        ("papaya", "پپیتا", "peak", "fruit"),
        ("cauliflower", "گوبھی", "peak", "veg"),
        ("spinach", "پالک", "peak", "veg"),
        ("carrots", "گاجر", "peak", "veg"),
        ("peas", "مٹر", "peak", "veg"),
        ("coriander", "دھنیا", "peak", "herb"),
    ],
}


# ─────────────────────────────────────────────────────────────────
# KPK — lower KPK (Peshawar) similar to Punjab; upper KPK (Swat,
# Dir, Hazara) is cooler — apples earlier, stone fruits prominent.
# This calendar blends the two with a slight northern bias toward
# stone fruits and apples.
# ─────────────────────────────────────────────────────────────────
KPK_BY_MONTH = {
    1: [
        ("spinach", "پالک", "peak", "veg"),
        ("mustard greens", "سرسوں کا ساگ", "peak", "veg"),
        ("cauliflower", "گوبھی", "peak", "veg"),
        ("turnips", "شلجم", "peak", "veg"),
        ("carrots", "گاجر", "peak", "veg"),
        ("oranges", "مالٹا", "peak", "fruit"),
        ("kinnow", "کنو", "peak", "fruit"),
        ("guava", "امرود", "peak", "fruit"),
        ("walnuts (dry)", "اخروٹ", "available", "fruit"),
    ],
    2: [
        ("spinach", "پالک", "peak", "veg"),
        ("mustard greens", "سرسوں کا ساگ", "peak", "veg"),
        ("cauliflower", "گوبھی", "peak", "veg"),
        ("strawberries", "اسٹرابیری", "peak", "fruit"),
        ("kinnow", "کنو", "available", "fruit"),
        ("coriander", "دھنیا", "peak", "herb"),
        ("fenugreek (methi)", "میتھی", "peak", "herb"),
    ],
    3: [
        ("strawberries", "اسٹرابیری", "peak", "fruit"),
        ("loquat", "لوکاٹ", "available", "fruit"),
        ("spinach", "پالک", "peak", "veg"),
        ("spring onion", "ہرا پیاز", "peak", "veg"),
        ("coriander", "دھنیا", "peak", "herb"),
        ("mint", "پودینہ", "peak", "herb"),
    ],
    4: [
        ("loquat", "لوکاٹ", "peak", "fruit"),
        ("apricots", "خوبانی", "available", "fruit"),
        ("strawberries", "اسٹرابیری", "available", "fruit"),
        ("cucumber", "کھیرا", "available", "veg"),
        ("mint", "پودینہ", "peak", "herb"),
        ("zucchini", "تورئی", "available", "veg"),
    ],
    5: [
        ("apricots", "خوبانی", "peak", "fruit"),
        ("mulberry", "شہتوت", "peak", "fruit"),
        ("loquat", "لوکاٹ", "peak", "fruit"),
        ("watermelon", "تربوز", "available", "fruit"),
        ("cucumber", "کھیرا", "peak", "veg"),
        ("okra", "بھنڈی", "available", "veg"),
        ("mint", "پودینہ", "peak", "herb"),
    ],
    6: [
        ("apricots", "خوبانی", "peak", "fruit"),
        ("plums", "آلوبخارا", "peak", "fruit"),
        ("peaches", "آڑو", "peak", "fruit"),
        ("cherries", "چیری", "peak", "fruit"),
        ("mango", "آم", "available", "fruit"),
        ("okra", "بھنڈی", "peak", "veg"),
        ("bottle gourd", "لوکی", "peak", "veg"),
        ("cucumber", "کھیرا", "peak", "veg"),
    ],
    7: [
        ("peaches", "آڑو", "peak", "fruit"),
        ("plums", "آلوبخارا", "peak", "fruit"),
        ("pears", "ناشپاتی", "peak", "fruit"),
        ("apricots", "خوبانی", "available", "fruit"),
        ("mango", "آم", "available", "fruit"),
        ("okra", "بھنڈی", "peak", "veg"),
        ("eggplant", "بینگن", "peak", "veg"),
        ("bitter gourd", "کریلا", "peak", "veg"),
    ],
    8: [
        ("apples", "سیب", "peak", "fruit"),
        ("pears", "ناشپاتی", "peak", "fruit"),
        ("peaches", "آڑو", "peak", "fruit"),
        ("plums", "آلوبخارا", "peak", "fruit"),
        ("eggplant", "بینگن", "peak", "veg"),
        ("bitter gourd", "کریلا", "peak", "veg"),
        ("tinda gourd", "ٹینڈا", "peak", "veg"),
        ("pumpkin", "کدو", "available", "veg"),
    ],
    9: [
        ("apples", "سیب", "peak", "fruit"),
        ("pears", "ناشپاتی", "peak", "fruit"),
        ("persimmon", "جاپانی پھل", "available", "fruit"),
        ("walnuts (fresh)", "تازہ اخروٹ", "peak", "fruit"),
        ("pumpkin", "کدو", "peak", "veg"),
        ("eggplant", "بینگن", "available", "veg"),
        ("spinach", "پالک", "available", "veg"),
    ],
    10: [
        ("apples", "سیب", "peak", "fruit"),
        ("persimmon", "جاپانی پھل", "peak", "fruit"),
        ("pomegranate", "انار", "peak", "fruit"),
        ("walnuts", "اخروٹ", "peak", "fruit"),
        ("pumpkin", "کدو", "peak", "veg"),
        ("spinach", "پالک", "available", "veg"),
        ("sweet potato", "شکرقندی", "peak", "veg"),
    ],
    11: [
        ("oranges", "مالٹا", "peak", "fruit"),
        ("kinnow", "کنو", "peak", "fruit"),
        ("persimmon", "جاپانی پھل", "peak", "fruit"),
        ("apples (stored)", "سیب", "peak", "fruit"),
        ("walnuts", "اخروٹ", "peak", "fruit"),
        ("cauliflower", "گوبھی", "peak", "veg"),
        ("spinach", "پالک", "peak", "veg"),
        ("carrots", "گاجر", "peak", "veg"),
    ],
    12: [
        ("oranges", "مالٹا", "peak", "fruit"),
        ("kinnow", "کنو", "peak", "fruit"),
        ("guava", "امرود", "peak", "fruit"),
        ("walnuts", "اخروٹ", "available", "fruit"),
        ("cauliflower", "گوبھی", "peak", "veg"),
        ("spinach", "پالک", "peak", "veg"),
        ("mustard greens", "سرسوں کا ساگ", "peak", "veg"),
        ("turnips", "شلجم", "peak", "veg"),
        ("peas", "مٹر", "peak", "veg"),
    ],
}


# ─────────────────────────────────────────────────────────────────
# BALOCHISTAN — Pakistan's "fruit basket".
# Quetta valley = high altitude (~1700m), distinct deciduous fruit zone.
# Mekran (Turbat, Panjgur) = dates dominate summer.
# Almonds & grapes are a Balochistan specialty.
# ─────────────────────────────────────────────────────────────────
BALOCHISTAN_BY_MONTH = {
    1: [
        ("oranges", "مالٹا", "peak", "fruit"),
        ("kinnow", "کنو", "peak", "fruit"),
        ("apples (stored)", "سیب", "peak", "fruit"),
        ("walnuts", "اخروٹ", "peak", "fruit"),
        ("almonds (dry)", "بادام", "peak", "fruit"),
        ("dates (dry)", "خشک کھجور", "peak", "fruit"),
        ("cauliflower", "گوبھی", "available", "veg"),
        ("spinach", "پالک", "available", "veg"),
        ("turnips", "شلجم", "available", "veg"),
    ],
    2: [
        ("apples (stored)", "سیب", "peak", "fruit"),
        ("kinnow", "کنو", "available", "fruit"),
        ("almonds (dry)", "بادام", "peak", "fruit"),
        ("walnuts", "اخروٹ", "peak", "fruit"),
        ("dates (dry)", "خشک کھجور", "peak", "fruit"),
        ("spinach", "پالک", "available", "veg"),
        ("coriander", "دھنیا", "available", "herb"),
    ],
    3: [
        ("strawberries", "اسٹرابیری", "available", "fruit"),
        ("almonds (blossom)", "بادام پھول", "peak", "fruit"),
        ("spinach", "پالک", "peak", "veg"),
        ("spring onion", "ہرا پیاز", "peak", "veg"),
        ("coriander", "دھنیا", "peak", "herb"),
        ("mint", "پودینہ", "peak", "herb"),
    ],
    4: [
        ("loquat", "لوکاٹ", "peak", "fruit"),
        ("strawberries", "اسٹرابیری", "peak", "fruit"),
        ("watermelon", "تربوز", "available", "fruit"),
        ("cucumber", "کھیرا", "available", "veg"),
        ("mint", "پودینہ", "peak", "herb"),
        ("coriander", "دھنیا", "peak", "herb"),
    ],
    5: [
        ("apricots", "خوبانی", "peak", "fruit"),
        ("mulberry", "شہتوت", "peak", "fruit"),
        ("watermelon", "تربوز", "peak", "fruit"),
        ("muskmelon", "خربوزہ", "peak", "fruit"),
        ("loquat", "لوکاٹ", "available", "fruit"),
        ("cucumber", "کھیرا", "peak", "veg"),
        ("mint", "پودینہ", "peak", "herb"),
    ],
    6: [
        ("cherries", "چیری", "peak", "fruit"),
        ("apricots", "خوبانی", "peak", "fruit"),
        ("plums", "آلوبخارا", "peak", "fruit"),
        ("peaches", "آڑو", "peak", "fruit"),
        ("mulberry", "شہتوت", "peak", "fruit"),
        ("almonds (fresh)", "تازہ بادام", "peak", "fruit"),
        ("okra", "بھنڈی", "peak", "veg"),
        ("bottle gourd", "لوکی", "peak", "veg"),
        ("cucumber", "کھیرا", "peak", "veg"),
    ],
    7: [
        ("cherries", "چیری", "peak", "fruit"),
        ("peaches", "آڑو", "peak", "fruit"),
        ("plums", "آلوبخارا", "peak", "fruit"),
        ("dates (fresh)", "تازہ کھجور", "peak", "fruit"),
        ("grapes", "انگور", "available", "fruit"),
        ("almonds (fresh)", "تازہ بادام", "peak", "fruit"),
        ("okra", "بھنڈی", "peak", "veg"),
        ("eggplant", "بینگن", "peak", "veg"),
        ("tomato", "ٹماٹر", "peak", "veg"),
    ],
    8: [
        ("apples", "سیب", "peak", "fruit"),
        ("grapes", "انگور", "peak", "fruit"),
        ("peaches", "آڑو", "peak", "fruit"),
        ("plums", "آلوبخارا", "peak", "fruit"),
        ("pears", "ناشپاتی", "peak", "fruit"),
        ("dates", "کھجور", "peak", "fruit"),
        ("eggplant", "بینگن", "peak", "veg"),
        ("tomato", "ٹماٹر", "peak", "veg"),
        ("pumpkin", "کدو", "available", "veg"),
    ],
    9: [
        ("apples", "سیب", "peak", "fruit"),
        ("grapes", "انگور", "peak", "fruit"),
        ("pomegranate", "انار", "peak", "fruit"),
        ("pears", "ناشپاتی", "peak", "fruit"),
        ("dates", "کھجور", "peak", "fruit"),
        ("walnuts (fresh)", "تازہ اخروٹ", "peak", "fruit"),
        ("pumpkin", "کدو", "peak", "veg"),
        ("eggplant", "بینگن", "available", "veg"),
    ],
    10: [
        ("apples", "سیب", "peak", "fruit"),
        ("pomegranate", "انار", "peak", "fruit"),
        ("grapes", "انگور", "peak", "fruit"),
        ("walnuts", "اخروٹ", "peak", "fruit"),
        ("almonds", "بادام", "peak", "fruit"),
        ("pumpkin", "کدو", "peak", "veg"),
        ("sweet potato", "شکرقندی", "available", "veg"),
        ("spinach", "پالک", "available", "veg"),
    ],
    11: [
        ("apples", "سیب", "peak", "fruit"),
        ("pomegranate", "انار", "peak", "fruit"),
        ("oranges", "مالٹا", "peak", "fruit"),
        ("kinnow", "کنو", "peak", "fruit"),
        ("walnuts", "اخروٹ", "peak", "fruit"),
        ("almonds", "بادام", "peak", "fruit"),
        ("cauliflower", "گوبھی", "peak", "veg"),
        ("spinach", "پالک", "peak", "veg"),
        ("carrots", "گاجر", "peak", "veg"),
    ],
    12: [
        ("apples (stored)", "سیب", "peak", "fruit"),
        ("oranges", "مالٹا", "peak", "fruit"),
        ("kinnow", "کنو", "peak", "fruit"),
        ("pomegranate", "انار", "available", "fruit"),
        ("walnuts", "اخروٹ", "peak", "fruit"),
        ("almonds", "بادام", "peak", "fruit"),
        ("dates (dry)", "خشک کھجور", "peak", "fruit"),
        ("cauliflower", "گوبھی", "peak", "veg"),
        ("spinach", "پالک", "peak", "veg"),
        ("turnips", "شلجم", "peak", "veg"),
    ],
}


# ─────────────────────────────────────────────────────────────────
# GILGIT-BALTISTAN — mountain calendar, ~6 weeks behind plains.
# Apricot/cherry blossoms April; harvest June–July.
# Apples Aug–Oct. Dry fruits dominate winter.
# Harsh winter limits fresh produce Jan–Feb.
# ─────────────────────────────────────────────────────────────────
GILGITBALTISTAN_BY_MONTH = {
    1: [
        ("apples (stored)", "سیب", "peak", "fruit"),
        ("walnuts", "اخروٹ", "peak", "fruit"),
        ("dried apricots", "خشک خوبانی", "peak", "fruit"),
        ("almonds", "بادام", "peak", "fruit"),
        ("dried mulberry", "خشک شہتوت", "peak", "fruit"),
        ("turnips", "شلجم", "available", "veg"),
        ("potato (stored)", "آلو", "peak", "veg"),
    ],
    2: [
        ("apples (stored)", "سیب", "peak", "fruit"),
        ("walnuts", "اخروٹ", "peak", "fruit"),
        ("dried apricots", "خشک خوبانی", "peak", "fruit"),
        ("almonds", "بادام", "peak", "fruit"),
        ("dried mulberry", "خشک شہتوت", "peak", "fruit"),
        ("potato (stored)", "آلو", "peak", "veg"),
    ],
    3: [
        ("dried apricots", "خشک خوبانی", "peak", "fruit"),
        ("walnuts", "اخروٹ", "peak", "fruit"),
        ("apricot blossom", "خوبانی پھول", "peak", "fruit"),
        ("cherry blossom", "چیری پھول", "peak", "fruit"),
        ("spinach", "پالک", "available", "veg"),
    ],
    4: [
        ("apricot blossom", "خوبانی پھول", "peak", "fruit"),
        ("cherry blossom", "چیری پھول", "peak", "fruit"),
        ("apple blossom", "سیب پھول", "peak", "fruit"),
        ("dried apricots", "خشک خوبانی", "peak", "fruit"),
        ("spinach", "پالک", "peak", "veg"),
        ("spring onion", "ہرا پیاز", "peak", "veg"),
        ("mint", "پودینہ", "available", "herb"),
    ],
    5: [
        ("strawberries", "اسٹرابیری", "available", "fruit"),
        ("mulberry", "شہتوت", "available", "fruit"),
        ("spring onion", "ہرا پیاز", "peak", "veg"),
        ("spinach", "پالک", "peak", "veg"),
        ("mint", "پودینہ", "peak", "herb"),
        ("coriander", "دھنیا", "peak", "herb"),
    ],
    6: [
        ("cherries", "چیری", "peak", "fruit"),
        ("apricots", "خوبانی", "peak", "fruit"),
        ("mulberry", "شہتوت", "peak", "fruit"),
        ("strawberries", "اسٹرابیری", "peak", "fruit"),
        ("cucumber", "کھیرا", "peak", "veg"),
        ("zucchini", "تورئی", "peak", "veg"),
        ("mint", "پودینہ", "peak", "herb"),
    ],
    7: [
        ("apricots", "خوبانی", "peak", "fruit"),
        ("cherries", "چیری", "peak", "fruit"),
        ("peaches", "آڑو", "available", "fruit"),
        ("mulberry", "شہتوت", "peak", "fruit"),
        ("plums", "آلوبخارا", "peak", "fruit"),
        ("cucumber", "کھیرا", "peak", "veg"),
        ("zucchini", "تورئی", "peak", "veg"),
        ("tomato", "ٹماٹر", "available", "veg"),
    ],
    8: [
        ("apples", "سیب", "peak", "fruit"),
        ("apricots", "خوبانی", "available", "fruit"),
        ("plums", "آلوبخارا", "peak", "fruit"),
        ("peaches", "آڑو", "peak", "fruit"),
        ("pears", "ناشپاتی", "peak", "fruit"),
        ("grapes (early)", "انگور", "available", "fruit"),
        ("tomato", "ٹماٹر", "peak", "veg"),
        ("zucchini", "تورئی", "peak", "veg"),
        ("potato (new)", "نیا آلو", "peak", "veg"),
    ],
    9: [
        ("apples", "سیب", "peak", "fruit"),
        ("pears", "ناشپاتی", "peak", "fruit"),
        ("grapes", "انگور", "peak", "fruit"),
        ("walnuts (fresh)", "تازہ اخروٹ", "peak", "fruit"),
        ("plums", "آلوبخارا", "available", "fruit"),
        ("potato", "آلو", "peak", "veg"),
        ("cabbage", "بند گوبھی", "peak", "veg"),
        ("tomato", "ٹماٹر", "peak", "veg"),
    ],
    10: [
        ("apples", "سیب", "peak", "fruit"),
        ("walnuts", "اخروٹ", "peak", "fruit"),
        ("dried apricots", "خشک خوبانی", "peak", "fruit"),
        ("pears", "ناشپاتی", "peak", "fruit"),
        ("potato", "آلو", "peak", "veg"),
        ("cabbage", "بند گوبھی", "peak", "veg"),
        ("turnips", "شلجم", "peak", "veg"),
        ("spinach", "پالک", "peak", "veg"),
    ],
    11: [
        ("apples (stored)", "سیب", "peak", "fruit"),
        ("walnuts", "اخروٹ", "peak", "fruit"),
        ("dried apricots", "خشک خوبانی", "peak", "fruit"),
        ("almonds", "بادام", "peak", "fruit"),
        ("dried mulberry", "خشک شہتوت", "peak", "fruit"),
        ("potato (stored)", "آلو", "peak", "veg"),
        ("cabbage", "بند گوبھی", "available", "veg"),
        ("turnips", "شلجم", "peak", "veg"),
    ],
    12: [
        ("apples (stored)", "سیب", "peak", "fruit"),
        ("walnuts", "اخروٹ", "peak", "fruit"),
        ("dried apricots", "خشک خوبانی", "peak", "fruit"),
        ("almonds", "بادام", "peak", "fruit"),
        ("dried mulberry", "خشک شہتوت", "peak", "fruit"),
        ("potato (stored)", "آلو", "peak", "veg"),
        ("turnips", "شلجم", "available", "veg"),
    ],
}


# Map region code to its calendar
REGION_CALENDARS = {
    "Pakistan":         PUNJAB_BY_MONTH,
    "Punjab":           PUNJAB_BY_MONTH,
    "Sindh":            SINDH_BY_MONTH,
    "KPK":              KPK_BY_MONTH,
    "Balochistan":      BALOCHISTAN_BY_MONTH,
    "GilgitBaltistan":  GILGITBALTISTAN_BY_MONTH,
    "Outside":          PUNJAB_BY_MONTH,  # fallback
}


# Backwards-compat alias for legacy code that imported PAKISTAN_BY_MONTH
PAKISTAN_BY_MONTH = PUNJAB_BY_MONTH


# ─────────────────────────────────────────────────────────────────
# Other cuisines (unchanged) — Italian, Chinese, Mexican
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
    "Pakistani": PUNJAB_BY_MONTH,  # default; overridden by region for Pakistani
    "Italian":   ITALIAN_BY_MONTH,
    "Chinese":   CHINESE_BY_MONTH,
    "Mexican":   MEXICAN_BY_MONTH,
}


# ─────────────────────────────────────────────────────────────────
# Imported / high-food-miles items in Pakistan context
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
    return datetime.now().month


def month_name(month: int = None, lang: str = "en") -> str:
    m = month if month else current_month()
    if lang == "ur":
        return MONTH_NAMES_UR[m]
    return MONTH_NAMES_EN[m]


def in_season(cuisine: str, month: int = None, max_items: int = 8,
              region: str = "Pakistan") -> list:
    """
    Return balanced seasonal items for a cuisine, in a specific region.

    For Pakistani cuisine, the region selects which of 5 regional calendars
    is used. For Italian/Chinese/Mexican, region is ignored.

    Returns list of dicts: {en, ur, peak, category}
    """
    m = month if month else current_month()

    if cuisine == "Pakistani":
        cal = REGION_CALENDARS.get(region, PUNJAB_BY_MONTH)
        items = cal.get(m, [])

        buckets = {"fruit": [], "veg": [], "herb": [], "grain": []}
        for entry in items:
            en, ur, status, cat = entry
            buckets.setdefault(cat, []).append({
                "en": en, "ur": ur, "peak": (status == "peak"), "category": cat,
            })
        for cat in buckets:
            buckets[cat].sort(key=lambda x: 0 if x["peak"] else 1)

        half = max_items // 2
        herb_quota = 1 if max_items >= 4 else 0
        veg_quota = max_items - half - herb_quota

        result = []
        result.extend(buckets.get("fruit", [])[:half])
        result.extend(buckets.get("veg",   [])[:veg_quota])
        result.extend(buckets.get("herb",  [])[:herb_quota])

        remaining = max_items - len(result)
        if remaining > 0:
            already = {r["en"] for r in result}
            spares = []
            for cat in ("veg", "fruit", "herb", "grain"):
                for entry in buckets.get(cat, []):
                    if entry["en"] not in already:
                        spares.append(entry)
            result.extend(spares[:remaining])

        result.sort(
            key=lambda x: (
                0 if x["peak"] else 1,
                ["fruit", "veg", "herb", "grain"].index(x["category"]),
            )
        )
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
    if not text:
        return []
    t = text.lower()
    found = []
    for item, (label, alt) in IMPORTED_ALTERNATIVES.items():
        key = item.split(" (")[0].strip()
        if key in t:
            found.append({"item": key, "label": label, "alternative": alt})
    return found


def find_seasonal_in_text(text: str, cuisine: str, month: int = None,
                          region: str = "Pakistan") -> list:
    if not text:
        return []
    t = text.lower()
    season_items = in_season(cuisine, month, max_items=20, region=region)
    hits = []
    for s in season_items:
        en = s["en"].lower()
        key = en.split(" (")[0].strip()
        if key in t:
            hits.append(s["en"])
    return hits


def seasonal_prompt_context(text: str, cuisine: str, month: int = None,
                            region: str = "Pakistan") -> str:
    parts = []
    seasonal_hits = find_seasonal_in_text(text, cuisine, month, region)
    if seasonal_hits:
        parts.append(
            "SEASONAL NOTE: The following user ingredients are at peak season "
            f"this month for {cuisine} cuisine in {region}: {', '.join(seasonal_hits)}. "
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
