# LUMI AITTA API client

CBS Model Agent (https://github.com/CBS-HPC/model-agent) is the cross-provider
consumer. The UCloud provider agent must not depend on this package. Keep model
selection and task-specific checks in the wrapper; API transport/control stays here.

This package owns the generic AITTA control API: project-token settings, safe
HTTP transport, live model/capability discovery, service/worker status and explicit
preload. Follow the dependency boundary used by CBS-HPC/ucloud-api. Consumers own
model choice, task-specific inference checks, notebooks and validation evidence.

Read docs/api.md and the official AITTA documentation before changing routes.
Use the fixed CSC service origin. Never forward credentials to redirects or
untrusted HAL links, print environment values or raw authenticated error bodies.
Read local .env by code only. Do not copy tokens between projects or commit them.

Preload may consume shared LUMI capacity. Discovery is read-only; preload/inference
require an explicit model-use request. Do not preload every offline model, silently
switch models, retry unknown outcomes or manage Slurm directly. Preload accepted
does not mean ready. Preserve HTTP status in sanitized errors, including 429.

There is no GPU sizing, UCloud template logic, notebook hosting or unattended
scheduler here. Unit tests use mocked transport; do not call live AITTA in tests.
No authenticated live validation has yet been performed. Do not claim otherwise.
Maintain README, docs and TODO with behavior; releases must pass tests and build.
Keep operator project names, resource IDs and deployment URLs out of tracked
documentation. Use role labels and reserved example domains where needed; retain
official AITTA service/API origins. Follow CBS Model Agent's docs/publication.md
before changing repository visibility or published history.
