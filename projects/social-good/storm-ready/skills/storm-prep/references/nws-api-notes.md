# NWS API notes (api.weather.gov)

Keyless, free, public. JSON (GeoJSON dialect). Two endpoints this skill uses:

## Endpoints

- Active alerts by state:
  `GET https://api.weather.gov/alerts/active?area=<2-letter state code>`
  → `features[].properties`: `event`, `severity` (Minor/Moderate/Severe/
  Extreme), `urgency`, `headline`, `areaDesc`, `onset`, `expires`,
  `instruction`.
- Point forecast — **the two-step**:
  1. `GET https://api.weather.gov/points/{lat},{lon}` → read
     `properties.forecast` (a gridpoint URL like
     `https://api.weather.gov/gridpoints/BOX/71,101/forecast`).
  2. `GET` that URL → `properties.periods[]`: `name`, `temperature`,
     `windSpeed`, `windDirection`, `shortForecast`,
     `probabilityOfPrecipitation.value`.

## The two gotchas

1. **User-Agent is mandatory.** Requests without a `User-Agent` header are
   rejected with 403 ("missing parameters"). Identify your app and a
   contact, e.g. `(AgentDay-Example, storm-ready starter; contact: repo
   issues)`. Verified live: no UA → 403, with UA → 200.
2. **Never guess gridpoint URLs.** Forecasts hang off NWS grid squares, not
   lat/lon — `/points/{lat},{lon}` is the only supported way to find the
   forecast URL. Coordinates are fine at ~2-4 decimals (more get redirected).

## Quirks worth knowing

- The alerts feed mixes ALL hazard types: Heat Advisory, Air Quality Alert,
  Coastal Flood Warning, Hurricane Warning — filter by reading `event`.
- Zero alerts is the normal case most days; `features` is just empty.
- `expires` is when the *message* expires; `ends` (when present) is when the
  *hazard* ends.
- Forecast `periods` are half-days ("Saturday", "Saturday Night"), so
  5 periods ≈ 60 hours; trim to the 48-hour horizon.
