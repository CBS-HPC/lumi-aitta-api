# API boundary

Reviewed 2026-10-07 against the [official LUMI AITTA guide](https://docs.lumi-supercomputer.eu/laif/inference/aitta/).
The [frontend](https://aitta.csc.fi/) can also start offline models manually.
The [service Swagger reference](https://aitta-api.csc.fi/docs) documents API details.

| Client method | Service route | Behavior |
| --- | --- | --- |
| models | GET /model | Names from HAL item links; returned URLs are never followed |
| model | GET /model/vendor~model | Model identity and advertised capabilities |
| status | GET /status | Service availability and retry-after interval |
| workers | GET /worker/vendor~model | Reported worker states, including requested/running |
| preload | GET model details then POST /model/vendor~model/preload | Explicit loading request |

Only the exact documented preload link/method is accepted, on the fixed CSC
origin. Empty successful POST responses are accepted. Responses are bounded to
1 MB, transport timeout is 30 seconds, redirects are rejected and no operation
is automatically retried. Reports deliberately omit raw worker details, error
bodies and service messages. HTTP failures retain their status (e.g. 401, 429).

The public OpenAPI schema was also inspected without credentials on 2026-10-07:
`POST /model/{model_id}/preload` accepts no request body and returns HTTP 202
with an `application/hal+json` response. Accepted means loading was requested.

AITTA owns Slurm resource selection and workers. Consumers own model choice,
synthetic chat/embedding tests, inference timeouts and evidence. No UCloud
machine estimate or revision pin can be inferred from the AITTA model ID alone.
Models and capacities change; query the live catalog rather than treating
documentation examples as current availability.

Requesting preload or inference can allocate shared resources. A failed/timeout
request may have been accepted by the service; inspect workers before requesting
another load. The current CLI does not poll, preload many models, select a
fallback model or stop shared workers. A successful preload only reports
`preload_requested`; verify inference separately.
