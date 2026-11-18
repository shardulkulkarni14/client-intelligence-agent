"""The one place that talks to a language model.

The rest of the code only knows `Writer`: a function from (system, user) to text.
Tests and the offline mode pass a fake, so nothing else imports the SDK.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

Writer = Callable[[str, str], str]

DEFAULT_MODEL = "claude-haiku-5-5"
# The briefing is about a page; this leaves room for the model's own reasoning.
MAX_TOKENS = 8000
TIMEOUT_SECONDS = 120.0


class ModelError(RuntimeError):
    """The model could not produce a briefing; the message says why and what to do."""


def load_env(path: Path | None = None) -> None:
    """Read KEY=VALUE lines from .env into the environment, without overriding it.

    Kept tiny on purpose instead of adding a dependency for one file.
    """
    env_path = path or Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


@dataclass
class AnthropicWriter:
    """Calls Claude once per request and records token usage for the evidence file."""

    model: str = ""
    calls: list[dict[str, int | str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        load_env()
        self.model = self.model or os.getenv("CLIENT_INTEL_MODEL", DEFAULT_MODEL)
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ModelError(
                "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add a key, "
                "or run with --no-llm for the offline briefing."
            )

    def __call__(self, system: str, user: str) -> str:
        import anthropic

        client = anthropic.Anthropic(timeout=TIMEOUT_SECONDS, max_retries=2)
        try:
            # No sampling parameters: current models reject non-default values, and
            # determinism here comes from the verifier, not from temperature.
            response = client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
        except anthropic.AuthenticationError as exc:
            raise ModelError("The Anthropic API key was rejected.") from exc
        except anthropic.NotFoundError as exc:
            raise ModelError(f"Model '{self.model}' was not found.") from exc
        except anthropic.RateLimitError as exc:
            raise ModelError("Rate limited by the Anthropic API after retries.") from exc
        except anthropic.APIStatusError as exc:
            raise ModelError(f"Anthropic API error {exc.status_code}: {exc.message}") from exc
        except anthropic.APIConnectionError as exc:
            raise ModelError("Could not reach the Anthropic API (network or timeout).") from exc

        self.calls.append(
            {
                "model": response.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "stop_reason": response.stop_reason or "",
            }
        )
        if response.stop_reason == "refusal":
            raise ModelError("The model declined to write this briefing.")
        if response.stop_reason == "max_tokens":
            raise ModelError("The briefing was cut off at the token limit.")
        text = "".join(block.text for block in response.content if block.type == "text").strip()
        if not text:
            raise ModelError("The model returned no text.")
        return text
