# Civic brief — worked example (shape, not numbers)

## Headline finding
Roxbury logged the most rodent 311 complaints in Boston over the last 12
months, with 7 reports.

## The data
311 Service Requests on Analyze Boston, rows with open_dt from 2025-06-14
to 2026-06-02, 34 matching rows analyzed (31 after removing duplicates).
Dataset: https://data.boston.gov/dataset/311-service-requests

## What we found
- Roxbury led with 7 rodent complaints, followed by Back Bay with 5.
- Dorchester and Beacon Hill each logged 3 complaints.
- 13 neighborhoods reported at least one rodent case in the period.

## Caveats
- 3 "Duplicate of Existing Case" rows were excluded from all counts.
- The current month is incomplete; recent totals will still rise.
- Counts reflect 311 reports, not rodent populations — neighborhoods that
  call 311 more often look worse in this data.

## Reproduce it
https://data.boston.gov/api/3/action/datastore_search?resource_id=dff4d804-5031-443a-8409-8344efd0e5c8&q=rodent&limit=5000
