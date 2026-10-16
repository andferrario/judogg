from decimal import Decimal

# From 2017: 4-minute contests, hansoku-make at the 3rd shido, no koka. Older data is ignored everywhere.
FIRST_YEAR = 2017

MIN_TAG_COVERAGE = Decimal("0.7")

# Must match the app.weight_category seed of the initial migration (a test checks it).
WEIGHT_CATEGORY_IDS: dict[str, int] = {
    "m-60": 1,
    "m-66": 2,
    "m-73": 3,
    "m-81": 4,
    "m-90": 5,
    "m-100": 6,
    "m+100": 7,
    "f-48": 8,
    "f-52": 9,
    "f-57": 10,
    "f-63": 11,
    "f-70": 12,
    "f-78": 13,
    "f+78": 14,
}
