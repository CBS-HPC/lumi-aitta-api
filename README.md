# LUMI AITTA API

The independent LUMI control client consumed by
[CBS Model Agent](https://github.com/CBS-HPC/model-agent).
The wrapper owns provider selection and task verification; the UCloud inference
provider has no dependency on this package. The API client remains independently usable.

A Python client and CLI for AITTA's managed inference control API, designed as a
reusable dependency for hosting agents in the same pattern as CBS-HPC/ucloud-api.
It reads available models/capabilities, service/worker status and explicitly
requests loading an offline model. It does not submit Slurm jobs itself.

```powershell
python -m pip install -e ".[dev]"
aitta models
aitta model --model "vendor/model-from-the-live-list"
aitta status
aitta workers --model "vendor/model-from-the-live-list"
aitta preload --model "vendor/model-from-the-live-list"
```

Obtain a project-bound token from [AITTA token generation](https://aitta-auth.csc.fi/myToken)
with an active LUMI project. Add `AITTA_API_KEY=<token>` to a local ignored `.env`.
Existing environment variables take precedence. Never paste the token into CLI
arguments, logs or Git. Settings repr hides the token.

```python
from lumi_aitta_api import AittaClient, Settings
from lumi_aitta_api.settings import load_env

load_env()
client = AittaClient(Settings.from_env())
catalog = client.models()
# Choose an actual model from catalog; discovery never starts workers.
# client.preload(model_id)  # only when loading this model is requested
```

The OpenAI-compatible inference URL is `https://aitta-api.csc.fi/openai/v1`.
Use the same AITTA project token with an inference client. Consumers implement
their task checks; OpenAI compatibility does not imply every endpoint is supported.

Preload requests loading; it does not prove readiness. Inference can itself start
loading an offline model. Loading depends on shared capacity and may time out.
AITTA is intended for research/development without guaranteed availability.
Token lifetime is currently documented as 90 days or shorter if the account/project
ends. There is no automatic retry, worker shutdown or renewal in this package.

See [API boundary and sources](docs/api.md) and [remaining work](TODO.md).
Local contract tests cover transport and control operations. Authenticated live
validation is pending; no model or allocation has been started by development.

```powershell
python -m pytest
python -m build
```
