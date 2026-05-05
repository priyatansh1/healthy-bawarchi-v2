"""
Counter module for Healthy Bawarchi.

Tracks two simple numbers across all users:
  • Total visits   — page loads (deduplicated per session)
  • Recipes made   — successful recipe generations

Uses Abacus.Counter (https://abacus.jasoncameron.dev) — a free, no-signup
counter service. Numbers persist across deploys and are shared across all
users of this app.

────────────────────────────────────────────────────────────────────
HOW TO MAINTAIN / CHANGE THIS LATER
────────────────────────────────────────────────────────────────────

To change the counter service:
    Edit `_BASE_URL` and the `_hit()` / `_get()` functions below.
    The two public functions (`record_visit`, `record_recipe`,
    `get_counts`) keep the same shape, so app.py never needs to
    change.

To change the counter names (e.g. start fresh with new totals):
    Edit `NAMESPACE` below. Old numbers stay where they were; the
    new namespace starts at zero.

To stop counting visits/recipes:
    Comment out or remove the `record_visit()` and `record_recipe()`
    calls in app.py. This module will stay healthy.

To add a NEW counter (e.g. "newsletter signups"):
    1. Add a new line under "Counter names" below.
    2. Add a small `record_<thing>()` function alongside the existing
       record_visit / record_recipe.
    3. Add the new counter's name to `get_counts()` so it's displayed.

If the service goes down:
    All functions fail silently — the app keeps working. The card on
    the front page just won't show numbers (or will show whatever the
    last successful read returned).
"""

import requests


# ─────────────────────────────────────────────────────────────────
# CONFIG — easy to change
# ─────────────────────────────────────────────────────────────────

# Service base URL. Swap this if you switch services.
_BASE_URL = "https://abacus.jasoncameron.dev"

# Namespace = unique identifier for THIS app's counters.
# Change this to start fresh with zero counts.
# Each app instance (yours vs Nadia's) needs its own namespace
# so the numbers don't mix.
NAMESPACE = "healthy-bawarchi-v2"

# Counter names within this namespace.
COUNTER_VISITS  = "visits"
COUNTER_RECIPES = "recipes"

# Network timeout (seconds). Short to keep the page snappy if the
# service is slow. Failures are silent.
_TIMEOUT = 2.0


# ─────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────

def record_visit() -> None:
    """Increment the visits counter. Call once per session."""
    _hit(COUNTER_VISITS)


def record_recipe() -> None:
    """Increment the recipes-generated counter. Call after each successful recipe."""
    _hit(COUNTER_RECIPES)


def get_counts() -> dict:
    """
    Return current counter values as a dict.
    Keys: 'visits', 'recipes'.
    On any failure, missing keys default to None — caller should handle.
    """
    return {
        "visits":  _get(COUNTER_VISITS),
        "recipes": _get(COUNTER_RECIPES),
    }


# ─────────────────────────────────────────────────────────────────
# INTERNAL — service-specific implementation
# ─────────────────────────────────────────────────────────────────

def _hit(counter_name: str):
    """
    Increment a counter by 1 and return the new value.
    Fails silently — the app must never crash because the
    counter service had a bad day.
    """
    url = f"{_BASE_URL}/hit/{NAMESPACE}/{counter_name}"
    try:
        r = requests.get(url, timeout=_TIMEOUT)
        if r.ok:
            return r.json().get("value")
    except Exception:
        pass
    return None


def _get(counter_name: str):
    """Return the current counter value without incrementing it."""
    url = f"{_BASE_URL}/get/{NAMESPACE}/{counter_name}"
    try:
        r = requests.get(url, timeout=_TIMEOUT)
        if r.ok:
            return r.json().get("value")
    except Exception:
        pass
    return None


def format_count(n) -> str:
    """
    Format a number for display: '1,247' instead of '1247'.
    Returns a placeholder dash if the count couldn't be fetched.
    """
    if n is None:
        return "—"
    try:
        return f"{int(n):,}"
    except Exception:
        return "—"
