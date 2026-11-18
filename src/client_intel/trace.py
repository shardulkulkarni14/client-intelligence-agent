"""A per-run record of what each step did and how long it took.

The evidence file already says what the tools found. The trace adds the order,
the time and the model cost of every step, so a reader can see where a run spent
its seconds and money without re-running it.
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from client_intel.llm import Writer, call_cost_usd

SECONDS_DECIMALS = 3
# Finer than the timings: one cheap call costs well under a tenth of a cent.
COST_DECIMALS = 6


class Trace:
    def __init__(self) -> None:
        self._start = time.perf_counter()
        self.steps: list[dict[str, Any]] = []

    def add(self, name: str, kind: str, seconds: float, detail: dict[str, Any]) -> None:
        self.steps.append({"name": name, "kind": kind,
                           "seconds": round(seconds, SECONDS_DECIMALS), "detail": detail})

    @contextmanager
    def step(self, name: str, kind: str) -> Iterator[dict[str, Any]]:
        """Time a block; the block fills in the yielded detail dict.

        A block that raises leaves no step: the run has no evidence file then.
        """
        detail: dict[str, Any] = {}
        started = time.perf_counter()
        yield detail
        self.add(name, kind, time.perf_counter() - started, detail)

    def to_dict(self, model: str | None) -> dict[str, Any]:
        costs = [s["detail"].get("cost_usd") for s in self.steps if s["kind"] == "model"]
        return {
            "model": model,
            "total_seconds": round(time.perf_counter() - self._start, SECONDS_DECIMALS),
            # Calls with an unknown price are left out of the sum; their step says null.
            "total_cost_usd": round(sum((c for c in costs if c is not None), 0.0),
                                    COST_DECIMALS),
            "steps": self.steps,
        }


def writer_model(writer: Writer | None) -> str | None:
    return getattr(writer, "model", None) or None


def model_detail(writer: Writer, calls_before: int) -> dict[str, Any]:
    """Tokens and cost of the call just made, read from the writer's own log.

    `calls_before` is the length of `writer.calls` before the call, so a writer
    reused across runs is attributed correctly. A plain function (a test fake
    without `.calls`) gives nulls rather than invented numbers.
    """
    calls = getattr(writer, "calls", [])
    call: dict[str, Any] = calls[calls_before] if len(calls) > calls_before else {}
    tokens_in, tokens_out = call.get("input_tokens"), call.get("output_tokens")
    cost = None
    if tokens_in is not None and tokens_out is not None:
        cost = call_cost_usd(writer_model(writer) or call.get("model"), tokens_in, tokens_out)
    return {
        "input_tokens": tokens_in,
        "output_tokens": tokens_out,
        "cost_usd": None if cost is None else round(cost, COST_DECIMALS),
        "stop_reason": call.get("stop_reason"),
    }


def calls_made(writer: Writer) -> int:
    return len(getattr(writer, "calls", []))
