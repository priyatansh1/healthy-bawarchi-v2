"""
Safety filter for Healthy Bawarchi — allowlist-based.

Design philosophy:
  • PROTEINS are checked strictly: only items on the ALLOWED_PROTEINS
    list are accepted. Anything else (rat, mouse, snake, frog, exotic
    species, pets, etc.) is rejected automatically — even items the
    author never explicitly thought of.
  • Produce, herbs, spices, and pantry items are NOT checked.
    Users can freely type tomato, onion, mint, atta, etc.
  • Pakistani cuisine additionally rejects pork and alcohol
    (these remain allowed for Italian / Chinese / Mexican).
  • Cultural authenticity is respected: Pakistani organ meats
    (kaleji, paya, nihari, etc.) ARE allowed. The AI's nutritional
    breakdown will honestly flag cholesterol where relevant.

This is much safer than a blocklist because the surface of "things
that should be blocked" is unbounded; the surface of "things that
are commonly eaten" is small and stable.
"""

import re


# ─────────────────────────────────────────────────────────────────
# ALLOWED PROTEINS — the only proteins the app will accept.
# Anything claiming to be a protein outside this list is rejected.
# ─────────────────────────────────────────────────────────────────
ALLOWED_PROTEINS = {
    # Common red & white meats
    "chicken", "chicken breast", "chicken thigh", "chicken leg", "chicken wing",
    "chicken mince", "chicken qeema",
    "beef", "beef mince", "qeema", "beef qeema", "steak", "veal",
    "mutton", "lamb", "goat", "goat meat", "bakra",

    # Pakistani / traditional additions
    "camel", "camel meat",
    "turkey",
    "duck",
    "quail", "bater",
    "dove",

    # Pakistani organ meats — culturally traditional, allowed
    "kaleji", "liver", "chicken liver", "mutton liver",
    "gurda", "kidney", "kidneys",
    "dil", "heart",
    "maghaz", "brain",
    "paya", "trotters",
    "nihari", "nihari shank", "shank",
    "ojhri", "tripe",
    "zaban", "tongue",

    # Fish — common in Pakistan and the other cuisines
    "fish", "rohu", "hilsa", "pomfret", "mackerel", "trout", "salmon",
    "tuna", "sardine", "sardines", "surmai", "kingfish", "tilapia",
    "cod", "haddock", "anchovy", "anchovies",

    # Shellfish
    "prawn", "prawns", "shrimp", "shrimps",
    "squid", "calamari", "octopus",
    "crab", "lobster", "scallops", "mussels", "clams",

    # Eggs and dairy proteins
    "egg", "eggs", "egg white", "egg whites", "egg yolk", "boiled egg",
    "milk", "yogurt", "dahi", "yoghurt",
    "paneer", "cottage cheese", "cheese", "mozzarella", "cheddar",
    "feta", "ricotta", "parmesan", "halloumi",
    "cream", "sour cream", "butter", "ghee", "mawa", "khoya",

    # Plant proteins — lentils & legumes
    "lentils", "daal", "dal",
    "masoor", "masoor daal", "red lentils",
    "moong", "moong daal", "mung", "mung beans",
    "chana", "chana daal", "chickpeas", "garbanzo", "garbanzos",
    "kabuli chana", "kala chana",
    "urad", "urad daal", "black gram",
    "toor", "toor daal", "arhar",

    # Plant proteins — beans
    "kidney beans", "rajma", "red beans",
    "black beans", "white beans", "navy beans", "cannellini beans",
    "pinto beans", "lima beans", "fava beans", "broad beans", "lobia",
    "black eyed peas", "soybeans", "soya beans",

    # Plant proteins — soy & seitan
    "tofu", "silken tofu", "firm tofu", "tempeh", "soy chunks",
    "tvp", "textured vegetable protein", "seitan",
}


# ─────────────────────────────────────────────────────────────────
# Lightweight detection: does the user's text claim a protein?
# We look for "meat" or specific protein-suggesting words like
# steak, mince, qeema, fillet, drumstick — to catch things like
# "rat meat", "snake meat" that obviously assert a protein.
# ─────────────────────────────────────────────────────────────────
PROTEIN_TRIGGERS = {
    # Generic words that signal "I'm putting a protein on the list"
    "meat", "flesh", "mince", "qeema", "fillet", "filet",
    "steak", "chop", "chops", "roast", "ribs", "ribeye",
    "drumstick", "drumsticks", "wing", "wings", "thigh", "thighs",
    "breast", "breasts", "leg", "legs", "shank", "shanks",
    "loin", "tenderloin", "sirloin",
}


# ─────────────────────────────────────────────────────────────────
# Pakistani-cuisine additional cultural blocks
# (Always rejected when Pakistani is selected)
# ─────────────────────────────────────────────────────────────────
PAKISTANI_BLOCKED = {
    # Pork and pork products
    "pork", "ham", "bacon", "prosciutto", "pancetta", "salami",
    "pepperoni", "chorizo", "lard", "pig", "piglet",
    "boar", "wild boar",

    # Alcohol
    "wine", "red wine", "white wine", "rosé",
    "beer", "lager", "ale", "stout",
    "vodka", "whisky", "whiskey", "rum", "gin", "tequila", "brandy",
    "cognac", "champagne", "prosecco",
    "sake", "soju",
    "liqueur", "cooking wine", "sherry", "marsala", "vermouth", "mirin",
}


# ─────────────────────────────────────────────────────────────────
# Friendly, non-preachy messages by category
# ─────────────────────────────────────────────────────────────────
MESSAGES_EN = {
    "unrecognized_protein": (
        "Bawarchi only suggests recipes using common everyday proteins. "
        "We didn't recognise: {items}. "
        "Try chicken, beef, mutton, fish, lentils, chickpeas, paneer, eggs, or tofu."
    ),
    "pakistani": (
        "{items} isn't traditionally used in Pakistani cuisine. "
        "Try the Italian, Chinese, or Mexican option, or remove it from your list."
    ),
}

MESSAGES_UR = {
    "unrecognized_protein": (
        "باورچی صرف عام، روزمرہ پروٹین استعمال کرتا ہے۔ "
        "ہم نے یہ نہیں پہچانا: {items}۔ "
        "چکن، گوشت، دال، مچھلی، چنا، پنیر، انڈے یا ٹوفو آزمائیں۔"
    ),
    "pakistani": (
        "{items} روایتی پاکستانی کھانوں میں استعمال نہیں ہوتا۔ "
        "اطالوی، چینی یا میکسیکن آپشن آزمائیں، یا اسے اپنی فہرست سے ہٹا دیں۔"
    ),
}


# ─────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────
def check_ingredients(text: str, cuisine: str) -> dict:
    """
    Validate user-typed ingredient text against the allowlist.

    Args:
        text:    Raw text the user typed in the ingredients box.
        cuisine: The currently-selected cuisine (e.g. "Pakistani").

    Returns:
        A dict with keys:
          safe     (bool): True if the input is acceptable
          category (str):  "" if safe, otherwise the rejection category
          blocked  (list): the specific items that were flagged
    """
    if not text or not text.strip():
        return {"safe": True, "category": "", "blocked": []}

    text_lower = text.lower()

    # ── 1. Pakistani-specific cultural check ──
    # (Always run, even before the protein check, because pork
    # is technically a "recognised protein" in the West.)
    if cuisine == "Pakistani":
        cultural = [item for item in PAKISTANI_BLOCKED if _word_in(text_lower, item)]
        if cultural:
            return {
                "safe": False,
                "category": "pakistani",
                "blocked": _dedupe(cultural),
            }

    # ── 2. Protein allowlist check ──
    # Split user text into ingredient phrases, then for each phrase
    # decide whether it claims to be a protein. If yes, it must
    # match the allowlist.
    phrases = _split_into_ingredients(text_lower)
    rejected = []

    for phrase in phrases:
        if not phrase:
            continue
        if _claims_protein(phrase) and not _matches_allowed_protein(phrase):
            rejected.append(phrase.strip())

    if rejected:
        return {
            "safe": False,
            "category": "unrecognized_protein",
            "blocked": _dedupe(rejected),
        }

    return {"safe": True, "category": "", "blocked": []}


def get_message(category: str, blocked: list, lang: str = "en") -> str:
    """Compose a friendly user-facing message for a blocked input."""
    items_str = ", ".join(blocked) if blocked else ""
    table = MESSAGES_UR if lang == "ur" else MESSAGES_EN
    template = table.get(category, table["unrecognized_protein"])
    return template.format(items=items_str)


# ─────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────
def _split_into_ingredients(text: str) -> list:
    """Split user text on commas, semicolons, newlines, ' and '."""
    parts = re.split(r"[,;\n]| and ", text)
    return [p.strip() for p in parts if p.strip()]


def _claims_protein(phrase: str) -> bool:
    """
    Return True if a phrase looks like it's specifying a protein.

    Triggers:
      - Contains a protein-trigger word (meat, mince, steak, etc.)
      - Or contains an explicitly known protein head-noun
        (rat, snake, frog, dog, etc.) even without 'meat'
    """
    # Fast path: any explicit protein trigger word?
    for trig in PROTEIN_TRIGGERS:
        if _word_in(phrase, trig):
            return True

    # Even without "meat", certain words clearly assert an animal
    # being used as food. Listing them lets us catch e.g. "rat" alone.
    SOLO_ANIMAL_NAMES = {
        # Pets
        "cat", "cats", "kitten", "kittens", "dog", "dogs", "puppy", "puppies",
        # Rodents
        "rat", "rats", "mouse", "mice", "rodent", "rodents",
        "squirrel", "chipmunk", "porcupine", "muskrat",
        # Reptiles & amphibians
        "snake", "cobra", "viper", "python",
        "frog", "frogs", "frog legs", "toad",
        "lizard", "iguana", "gecko",
        "crocodile", "alligator", "turtle", "tortoise",
        # Birds (exotic / non-typical)
        "eagle", "hawk", "falcon", "owl", "vulture",
        "peacock", "swan", "flamingo", "ostrich", "emu",
        "parrot", "budgie", "canary",
        # Wild mammals
        "tiger", "lion", "leopard", "cheetah", "panther",
        "elephant", "rhino", "rhinoceros", "hippopotamus", "hippo",
        "pangolin", "shark", "whale", "dolphin", "porpoise",
        "monkey", "ape", "gorilla", "chimpanzee", "orangutan",
        "bear", "wolf", "fox", "jackal", "hyena",
        "deer", "antelope", "gazelle", "zebra", "giraffe",
        "horse", "donkey", "mule",
        "bat", "bats",
        # Insects
        "cockroach", "cockroaches", "ant", "ants",
        "spider", "scorpion", "centipede", "millipede",
        "worm", "earthworm", "maggot", "maggots",
        "cricket", "crickets", "grasshopper", "locust",
        # Human
        "human", "baby", "infant", "child",
    }
    for name in SOLO_ANIMAL_NAMES:
        if _word_in(phrase, name):
            return True

    return False


def _matches_allowed_protein(phrase: str) -> bool:
    """Return True if the phrase contains a recognised allowed protein."""
    for allowed in ALLOWED_PROTEINS:
        if _word_in(phrase, allowed):
            return True
    return False


def _word_in(text: str, term: str) -> bool:
    """Whole-word/phrase match using regex word boundaries."""
    pattern = r"\b" + re.escape(term) + r"\b"
    return bool(re.search(pattern, text))


def _dedupe(items: list) -> list:
    """Remove duplicates and substring-of duplicates, keeping longest."""
    items = list(set(items))
    items.sort(key=len, reverse=True)
    kept = []
    for it in items:
        if not any(it != k and it in k for k in kept):
            kept.append(it)
    return kept
