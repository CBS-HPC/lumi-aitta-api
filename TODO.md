# Remaining work

## Licensing (2026-10-20)

The operator selected MIT for code and CC BY 4.0 for documentation. LICENSE.md
defines the split, including configuration/code examples and notebook cells;
LICENSES/ carries the full texts. Package metadata declares the combined SPDX
expression and includes both texts in new builds. Existing tags/release assets
and provider dependency pins are unchanged. Repository visibility and publication
of historical operational details remain separate decisions. Isolated wheel and
source builds were verified to include the scope notice, both full license texts
and the SPDX metadata.

- [x] Generic authenticated discovery, capabilities, service/worker status and preload.
- [x] Sanitized errors, fixed-origin credential handling, no redirects/retries.
- [ ] Authenticated live validation using an explicitly selected model and token.
- [x] First GitHub release v0.1.0; CBS Model Agent consumes the pinned client.
- [ ] Additional control endpoints only when a consumer needs them.
