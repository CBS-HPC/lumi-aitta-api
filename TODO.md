# Remaining work

## Publication cleanup (2026-10-20)

The operator chose to sanitize operational identifiers across the three inference
repositories. This client's current documentation contains no operator project
names, job/resource IDs or deployment URLs requiring replacement; official AITTA
origins are retained. AGENTS.md records the policy for future documentation.
Keep visibility private until the coordinated history/release gate described in
CBS Model Agent's docs/publication.md has been resolved.

## Licensing (2026-10-20)

The operator selected MIT for code and CC BY 4.0 for documentation. LICENSE.md
defines the split, including configuration/code examples and notebook cells;
LICENSES/ carries the full texts. Package metadata declares the combined SPDX
expression and includes both texts in new builds. Existing tags/release assets
and provider dependency pins are unchanged. Repository visibility and historical
copy cleanup are tracked above. Isolated wheel and
source builds were verified to include the scope notice, both full license texts
and the SPDX metadata.

- [x] Generic authenticated discovery, capabilities, service/worker status and preload.
- [x] Sanitized errors, fixed-origin credential handling, no redirects/retries.
- [ ] Authenticated live validation using an explicitly selected model and token.
- [x] First GitHub release v0.1.0; CBS Model Agent consumes the pinned client.
- [ ] Additional control endpoints only when a consumer needs them.
