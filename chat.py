#!/usr/bin/env python3
"""Call an APIM-fronted Azure OpenAI v1 chat completion endpoint from the terminal.

Usage:
    python chat.py "Your prompt here"     # single-shot, prints reply, exits
    python chat.py                        # interactive REPL (type 'exit' to quit)

Configuration (env vars, optionally via a .env file):
    APIM_BASE_URL  Base URL of the APIM v1 route (no trailing /chat/completions).
    MODEL          Model / deployment name (default: gpt-4o).
    API_KEY        Placeholder key (APIM auth is disabled; SDK requires a value).
"""

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, APIStatusError, OpenAIError

load_dotenv()

BASE_URL = os.getenv(
    "APIM_BASE_URL", "APIM_BASE_URL"
)
MODEL = os.getenv("MODEL", "gpt-4o")
# APIM has auth disabled, but the OpenAI SDK requires a non-empty api_key.
API_KEY = os.getenv("API_KEY", "unused")
# Optional: set if your APIM gateway still enforces a subscription key.
SUBSCRIPTION_KEY = os.getenv("APIM_SUBSCRIPTION_KEY", "")

SYSTEM_PROMPT = "You are a helpful assistant."


def make_client() -> OpenAI:
    default_headers = {}
    if SUBSCRIPTION_KEY:
        default_headers["Ocp-Apim-Subscription-Key"] = SUBSCRIPTION_KEY
    return OpenAI(base_url=BASE_URL, api_key=API_KEY, default_headers=default_headers)


def ask(client: OpenAI, prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or ""


def handle_error(err: Exception) -> None:
    if isinstance(err, APIConnectionError):
        print(f"[connection error] Could not reach {BASE_URL}: {err}", file=sys.stderr)
    elif isinstance(err, APIStatusError):
        print(
            f"[http {err.status_code}] {err.response.text}",
            file=sys.stderr,
        )
    elif isinstance(err, OpenAIError):
        print(f"[api error] {err}", file=sys.stderr)
    else:
        print(f"[error] {err}", file=sys.stderr)


def single_shot(client: OpenAI, prompt: str) -> int:
    try:
        print(ask(client, prompt))
        return 0
    except Exception as err:  # noqa: BLE001 - surface any failure to the terminal
        handle_error(err)
        return 1


def interactive(client: OpenAI) -> int:
    print(f"Connected to {BASE_URL} (model: {MODEL}).")
    print("Type a message and press Enter. Type 'exit' or 'quit' to leave.\n")
    while True:
        try:
            prompt = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit"}:
            return 0
        try:
            print(f"ai>  {ask(client, prompt)}\n")
        except Exception as err:  # noqa: BLE001
            handle_error(err)


def main() -> int:
    client = make_client()
    if len(sys.argv) > 1:
        return single_shot(client, " ".join(sys.argv[1:]))
    return interactive(client)


if __name__ == "__main__":
    raise SystemExit(main())
