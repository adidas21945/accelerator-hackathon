---
name: storm-prep
description: >-
  Builds a household emergency-readiness brief from National Weather Service
  alerts and forecasts — or a calm all-clear brief when nothing is active.
  Use whenever asked about storm prep or readiness, weather alerts or
  warnings, hurricanes, nor'easters, floods, heat waves, go-bags or emergency
  kits, or whether a place, family, or neighbor is okay/safe in the coming
  days or this weekend.
license: MIT
---

# Storm-Readiness Brief

Turn raw NWS alerts and a point forecast into a brief a real household can
act on in ten minutes: what is happening, what to do first, what to pack.
You write for regular people — elderly neighbors, families, community
groups — so plain words, real numbers, and a calm voice. See
references/nws-api-notes.md for how the NWS API behaves.

## Defaults (do not present options)

- Horizon: the next 48 hours, never more.
- Household: 2 adults, no car, unless the task says otherwise.
- If the place names no state, assume Massachusetts ("MA", Boston at
  lat 42.36, lon -71.06) and say you assumed it.
- One brief per request — never offer alternative versions or menus.

## Workflow

1. Call get_alerts with the two-letter state code. Always, first.
2. Call get_forecast with the place's latitude and longitude.
3. Pick the mode from the alerts result: any alerts → a hazard brief tuned
   to the most severe event; zero alerts → the all-clear brief.
4. Write the brief using EXACTLY the output template below.

## Gotchas

- The alerts feed carries every hazard type — flood, heat, air quality, not
  just storms. Brief whatever is actually active; never assume "storm".
- All-clear is a first-class result. Zero alerts means a calm brief with the
  preparedness that always applies — NEVER invent urgency to seem useful.
- Stay inside the forecast periods you were given. No "next week", no season
  outlooks, no guessing beyond the data.
- Severity words belong to NWS. Never write "catastrophic" and never order
  people to evacuate — evacuation calls come from local officials only.
- The tools handle two NWS API traps for you: requests without a User-Agent
  header get rejected (403), and forecasts need the points→gridpoint
  two-step. Never fetch weather.gov URLs by hand; use the tools.

## Output template

Produce EXACTLY these sections, in this order:

## Situation
The active alerts in plain words — for each: event, NWS severity, the areas
in it, and when it expires. If there are none, open with the line "No active
NWS alerts for <area> right now." and one sentence on what that does and
does not mean.

## Next 48 hours
2-3 lines summarizing the forecast WITH the numbers: temperatures, wind
speeds, precipitation chances.

## Do now
3-7 prioritized actions as a numbered list, most urgent first. Each item is
one imperative sentence sized to the actual hazard (or to quiet-day
readiness in all-clear mode).

## Go-bag check
Up to 8 "- " checklist bullets tuned to the hazard type. Always include
drinking water (1 gallon per person per day, 3 days) and a 7-day supply of
medications.

## Sources & caveats
Name the National Weather Service (api.weather.gov) as the source, give the
alert expiry or forecast timestamps you saw, and close with: forecasts
change — recheck before deciding.
