# responses-api-apim

Simple terminal script to call an Azure OpenAI **v1** chat completion endpoint that is
fronted by Azure API Management (APIM) and backed by a Microsoft Foundry instance.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Optionally copy `.env.example` to `.env` and adjust values:

```powershell
Copy-Item .env.example .env
```

| Variable        | Default                                                        | Purpose                                   |
| --------------- | ------------------------------------------------------------- | ----------------------------------------- |
| `APIM_BASE_URL` | `https://apim-zurlo.azure-api.net/aoaiv1/openai/v1`           | APIM v1 route (no `/chat/completions`).   |
| `MODEL`         | `gpt-4o`                                                       | Model / deployment name.                  |
| `API_KEY`       | `unused`                                                      | Placeholder; APIM auth is disabled.       |
| `APIM_SUBSCRIPTION_KEY` | _(empty)_                                             | Optional. Set if the gateway still requires a subscription key. |

## Usage

Single-shot:

```powershell
python chat.py "Say hello in one sentence."
```

Interactive REPL:

```powershell
python chat.py
```

Type `exit` or `quit` to leave the interactive session.

## Notes

- This uses the standard `openai` Python SDK with a custom `base_url` pointing at the APIM
  v1 (`/openai/v1`) route. The deployment name is sent in the request body as `model`,
  which is what the APIM v1 route expects.
- Auth is disabled on the APIM gateway (no subscription key, no JWT), so `API_KEY` is only
  a placeholder required by the SDK.
