---
name: civic-brief
description: >-
  Turns Boston open-data analysis into the standard five-section civic
  brief with sourced numbers, caveats, and a reproducible query. Use
  whenever answering questions about Boston city data, 311 complaints,
  data.boston.gov / Analyze Boston datasets, neighborhoods, or any
  "how many", "which neighborhood", "most common", or "trend" question
  about civic records.
license: MIT
---

# Civic Brief

Answer a resident's question about Boston open data the way a city data
analyst would: a plain-English headline number, the dataset it came from,
a handful of quantified findings, honest caveats, and the exact query
someone else could rerun. Numbers come from tools, never from memory.
Endpoint details live in `references/ckan-api-notes.md`; a worked example
brief lives in `assets/brief-template.md`.

## Defaults (do not present options)

- Date range: the last 12 complete months, described by the open_dt span
  the tool reports. Never silently mix older years in.
- Report counts, not rates — no per-capita math unless explicitly asked.
- Use the `neighborhood` field exactly as the data spells it (e.g.
  "Allston / Brighton"); never merge or rename neighborhoods.
- One dataset per brief: the best title match from search_datasets.

## Workflow

1. Call search_datasets with one or two topic keywords from the question
   ("311", "rodent", "crime"). Note the dataset title and its
   data.boston.gov URL — both go in the brief.
2. Call get_records with the resource_id of the newest CSV resource (copy
   the id exactly). If the question names a thing (rodents, trash,
   potholes), you MUST pass that one word as where="rodent" etc. —
   unfiltered counts answer a different question. Use where="" only for
   all-cases questions; if a filter matches nothing, retry once with "".
3. Take every number straight from the tool's tally lines — never recount
   rows yourself, never invent a number the tool did not return.
4. Write the brief using the exact output template below. Copy the tool's
   "Reproduce:" URL into the "Reproduce it" section.
5. Use run_sql only if a question needs an aggregation get_records did not
   already return — the SQL endpoint is flaky, so prefer get_records.

## Gotchas

- CKAN silently caps un-limited queries at 100 rows, so naive counts are
  wrong. get_records already sets limit=5000 and reports "analyzed N of M":
  if N < M, the analysis is a sample — say so in Caveats.
- "Duplicate of Existing Case" rows inflate counts. get_records excludes
  them and reports how many it dropped — repeat that number in Caveats.
- The current month is always incomplete (cases still arriving). Never
  call a dip in the newest month a trend; flag it in Caveats.
- 311 counts measure reports, not reality: neighborhoods that call 311
  more look worse in the data. Reporting bias belongs in Caveats.

## Output template

Produce EXACTLY these five sections, with these exact `##` headings, in
this order:

## Headline finding
One plain-English sentence that answers the question and contains a number.

## The data
Exactly four bullets, never fewer: the dataset title; the open_dt date
range; rows analyzed and duplicates excluded; the dataset URL — copy the
"dataset URL: https://data.boston.gov/dataset/..." line from
search_datasets. A brief with no dataset URL is unusable.

## What we found
3-5 bullets, each ONE sentence with a number from the tool's tallies
(top neighborhoods, top complaint types, totals).

## Caveats
At least 2 bullets from: duplicates excluded (give the count), incomplete
current month, sampled rows (analyzed N of M), reporting bias, geocoding
gaps.

## Reproduce it
The exact "Reproduce:" URL (or SQL statement) the tool returned, on its
own line.
