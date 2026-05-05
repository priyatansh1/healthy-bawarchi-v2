"""
Safety filter for Healthy Bawarchi.

Checks user-provided ingredient text BEFORE it is sent to the AI,
and blocks anything unsafe, unethical, or culturally inappropriate.

Two-layer protection:
  Layer 1 — ALWAYS_BLOCKED: rejected for every cuisine
            (pets, exotic species, human-derived, toxic, non-food, drugs)
  Layer 2 — PAKISTANI_BLOCKED: additionally rejected ONLY when
            Pakistani cuisine is selected (pork, alcohol).
            These remain allowed for Italian/Chinese/Mexican
            because they are traditional in those cuisines.

Edit the lists below to add or remove items.
"""

import re


# ─────────────────────────────────────────────
# Layer 1 — Always blocked, regardless of cuisine
# ─────────────────────────────────────────────
ALWAYS_BLOCKED = {
    # Pets and companion animals
    "cat", "cats", "kitten", "kittens", "dog", "dogs", "puppy", "puppies",
    "hamster", "rabbit pet", "guinea pig", "parrot", "budgie", "canary",

    # Exotic, wild, and endangered species
    "tiger", "lion", "leopard", "cheetah", "panther",
    "elephant", "rhino", "rhinoceros", "hippopotamus", "hippo",
    "pangolin", "shark", "whale", "dolphin", "porpoise",
    "monkey", "ape", "gorilla", "chimpanzee", "orangutan",
    "bear", "wolf", "fox",
    "eagle", "hawk", "falcon", "owl", "vulture",
    "cobra", "viper", "anaconda",
    "crocodile", "alligator", "turtle", "tortoise",
    "peacock", "swan", "flamingo",
    "deer", "antelope", "gazelle", "zebra",

    # Human-derived
    "human", "human meat", "human flesh", "human blood",
    "baby meat", "child meat", "infant meat", "placenta",

    # Non-food / cleaning chemicals / toxic
    "soap", "detergent", "bleach", "ammonia",
    "petrol", "gasoline", "diesel", "kerosene",
    "motor oil", "paint", "ink",
    "plastic", "rubber", "sawdust",
    "rat poison", "antifreeze",
    "feces", "urine", "excrement",

    # Recreational drugs
    "cocaine", "heroin", "meth", "methamphetamine",
    "marijuana", "weed", "cannabis", "hashish",

    # Known-toxic plants and mushrooms
    "hemlock", "deadly nightshade", "belladonna", "oleander", "foxglove",
    "death cap", "destroying angel", "fly agaric",

    # Known poisons
    "ricin", "cyanide", "arsenic",
}


# ─────────────────────────────────────────────
# Layer 2 — Blocked only when Pakistani cuisine is selected
# ─────────────────────────────────────────────
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


def check_ingredients(text: str, cuisine: str) -> dict:
    """
    Check user-provided ingredient text for blocked items.

    Args:
        text:    Raw text the user typed in the ingredients box.
        cuisine: The currently-selected cuisine (e.g. "Pakistani").

    Returns:
        A dict with three keys:
          safe     (bool): True if the input is acceptable
          category (str):  "" if safe, otherwise "general" or "pakistani"
          blocked  (list): the specific items that were flagged
    """
    if not text or not text.strip():
        return {"safe": True, "category": "", "blocked": []}

    text_lower = text.lower()

    # Layer 1: always-blocked items
    found = [item for item in ALWAYS_BLOCKED if _word_in(text_lower, item)]
    if found:
        return {"safe": False, "category": "general", "blocked": found}

    # Layer 2: Pakistani-specific items
    if cuisine == "Pakistani":
        found = [item for item in PAKISTANI_BLOCKED if _word_in(text_lower, item)]
        if found:
            return {"safe": False, "category": "pakistani", "blocked": found}

    return {"safe": True, "category": "", "blocked": []}


def _word_in(text: str, term: str) -> bool:
    """Return True if `term` appears as a whole word/phrase in `text`."""
    pattern = r"\b" + re.escape(term) + r"\b"
    return bool(re.search(pattern, text))
