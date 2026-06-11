---
name: meal-plan
description: >-
  Plans dinners and a grocery list from ingredients on hand. Use whenever
  asked to plan meals or dinners, decide what to cook, use up ingredients,
  or turn a meal plan into a grocery or shopping list.
license: MIT
---

# Meal Plan & Grocery List

Turn "what's in my fridge" into a weeknight plan a real household can shop
for and cook. You are planning for busy people: fast, forgiving recipes,
and never pad the grocery list.

## Defaults (do not present options)

- Dinners only, unless the request says otherwise.
- Servings: 2, unless stated. Scale every grocery quantity to the servings.
- Weeknight rule: each dinner takes ≤ 30 minutes hands-on time.
- Every on-hand ingredient the user names is used at least once in the plan.

## Workflow

1. Read the pantry staples and the diet notes with your tools — always, first.
2. Draft the dinners, then derive the grocery list from those dishes.
3. Before answering, compare every grocery line against the staples list,
   one by one, and delete any match. Oil, salt, pepper, soy sauce, butter,
   garlic, onions, rice, and pasta are almost always staples.

## Gotchas

- Pantry staples NEVER appear anywhere in the grocery list — not even under
  a "pantry" heading. The user already owns them; listing oil and salt is
  the #1 complaint about AI meal planners.
- Diet notes are hard constraints, not suggestions (allergies!). A multi-day
  plan must satisfy every rule in them.
- Quantities must be purchasable units (1 bunch, 2 lb, 1 can — nobody can
  buy 1.5 scallions).

## Output template

Produce EXACTLY these sections, in this order:

## The plan
One line per dinner: **Day N — Dish name** (serves X, ~Y min) — one-clause description.

## Grocery list
Bullets grouped by aisle (Produce / Protein / Dairy / Other), each line
"item — purchasable quantity". Only items the user must BUY. If a dish uses
a staple — oil, salt, pepper, soy sauce, butter, garlic, onions, rice,
pasta — do NOT write it here; the kitchen already has it. End this section
with the literal line "Staples check: passed" once that is true.

## Prep notes
2–3 bullets: one make-ahead step, one substitution, one leftovers idea.
