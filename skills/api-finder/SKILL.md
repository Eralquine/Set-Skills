---
name: api-finder
description: Find a free/public API for a given need (weather, animals, finance, geocoding, jobs, movies, etc.) before reaching for a paid provider or scraping. Use this whenever the user needs external data or a third-party integration and hasn't already named a specific provider — e.g. "necesito datos del clima", "¿hay alguna API gratis de películas?", "cómo consigo cotizaciones de criptomonedas sin pagar". Curated from https://github.com/public-apis/public-apis.
---

# API Finder

Curated list of ~1400 free/public APIs across 51 categories, sourced from the
`public-apis/public-apis` GitHub repo. Use it to shortlist real, working APIs
instead of guessing provider names or inventing endpoints.

## Categories

Animals, Anime, Anti-Malware, Art & Design, Authentication & Authorization,
Blockchain, Books, Business, Calendar, Cloud Storage & File Sharing,
Continuous Integration, Cryptocurrency, Currency Exchange, Data Validation,
Development, Dictionaries, Documents & Productivity, Email, Entertainment,
Environment, Events, Finance, Food & Drink, Games & Comics, Geocoding,
Government, Health, Jobs, Machine Learning, Music, News, Open Data,
Open Source Projects, Patent, Personality, Phone, Photography, Programming,
Science & Math, Security, Shopping, Social, Sports & Fitness, Test Data,
Text Analysis, Tracking, Transportation, URL Shorteners, Vehicle, Video,
Weather.

## Workflow

1. Map the user's need to one or more categories above.
2. **Don't read the whole reference file** (it's ~2000 lines) — grep it:
   - By category: search for the `### <Category>` heading and read the table
     that follows it (ends at the next `### ` heading or `**[⬆`).
   - By keyword: grep the API name or description column directly.
3. Each row is `| [Name](url) | Description | Auth | HTTPS | CORS |`.
   - `Auth` tells you what's required: `No` (nothing), `apiKey`, `OAuth`,
     `X-Mashape-Key`, `User-Agent`, etc.
   - Prefer `Auth: No` or simple `apiKey` options when the user wants
     something quick to try.
4. Present 2-4 real candidates with their auth requirement and a one-line
   reason to pick each, rather than a single pick — the user decides.
5. Link directly to the API's own docs (the URL in the table) for exact
   request/response shapes; this list only tells you the API exists and its
   basic constraints, not its full spec.

## Caveats

- This is a community-curated snapshot — some entries may have moved, gone
  paid, or shut down since. If a request fails, say so and suggest the next
  candidate instead of assuming the list is wrong.
- Prefer official, well-known providers when the user's use case is
  production-facing (uptime/rate-limit guarantees matter); the lesser-known
  entries are fine for prototypes, side projects, and one-off scripts.

Full data: `references/apis.md`.
