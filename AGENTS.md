# AGENTS

## Main Repo
- `LIVE-uk-aq-webpage` is the main repo for this project and the default starting point for cross-repo work.
- Filesystem location: `/Users/mikehinford/Dropbox/Projects/CIC Website/CIC Air Quality Networks/LIVE UK AQ Networks/LIVE-uk-aq-webpage`.

## Planning Requests
When proposing plans, offer more than one option when possible, list pros/cons for each, and recommend which to pick with a brief rationale.

## Notes
- PM2.5 outlier handling: edge functions already drop any station whose latest PM2.5 reading is above 500 µg/m³. The hex map keeps a frontend safety net at the same threshold (`MAX_VALID_PM25_VALUE = 500`) to guard against regressions or stale caches. If this duplicate guard ever causes issues, it can be removed safely once backend filtering is trusted.

## Documentation Hygiene
When adding or updating agent/project notes, also update relevant files under `system_docs` if they need to stay in sync.

## R2/Cloudflare Cache Cost Policy
- For AQI history served via R2 + Cloudflare, assume cost is primarily driven by R2 operation counts (especially Class B reads) and Worker request volume, not R2 bandwidth egress.
- Prefer stable request URLs/params for normal traffic so Cloudflare cache can return warm-cache hits.
- Use cache-buster/version params only for diagnostics, forced-refresh actions, or explicit bypass-cache testing.
- When evaluating performance/cost changes, check cache-hit behavior (`CF-Cache-Status`) and distinguish cache-hit traffic from origin-fetch traffic.
