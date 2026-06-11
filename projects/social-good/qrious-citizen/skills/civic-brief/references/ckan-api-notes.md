# Analyze Boston CKAN API notes

Analyze Boston (https://data.boston.gov) runs CKAN. Everything below is
keyless GET requests against the action API.

Base: `https://data.boston.gov/api/3/action`

## Endpoints

| Action | Use | Key params |
|---|---|---|
| `package_search` | find datasets | `q` (keywords), `rows` (default 10) |
| `datastore_search` | pull rows from one resource | `resource_id`, `limit`, `q` (full-text), `filters` (JSON dict of exact matches) |
| `datastore_search_sql` | SQL over a resource | `sql` — `SELECT ... FROM "<resource_id>"` (table name is the quoted resource id). Historically flaky on CKAN instances; prefer `datastore_search`. |

Every response is `{"success": true, "result": {...}}`. For
`datastore_search`, `result.total` is the number of MATCHING rows in the
resource, while `result.records` holds only the page you asked for.

## Pagination — the classic trap

`datastore_search` defaults to `limit=100` and says nothing when it
truncates. Counting `len(records)` without an explicit generous `limit`
silently caps every answer at 100. Always set `limit` (this project uses
5000) and compare it against `result.total`.

## The 311 dataset

- Dataset page (cite this URL in briefs):
  `https://data.boston.gov/dataset/311-service-requests`
- One CSV resource per year. The 2024 resource id, used by the fixtures:
  `dff4d804-5031-443a-8409-8344efd0e5c8` (~280k rows).
- Useful fields: `open_dt`, `case_status`, `case_title`, `subject`,
  `reason`, `neighborhood`.
- `case_status` includes `Duplicate of Existing Case` — exclude before
  counting.

## URL patterns

- Dataset page: `https://data.boston.gov/dataset/<name>` where `<name>`
  comes from `package_search` results.
- Reproducible row query:
  `https://data.boston.gov/api/3/action/datastore_search?resource_id=<id>&q=<word>&limit=5000`
