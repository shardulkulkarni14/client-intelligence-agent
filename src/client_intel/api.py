"""HTTP access to the briefing agent, for the web UI on the same machine.

What this is: a local, single-user API over the same pipeline as the command. It
returns the same JSON objects as `client-intel --json`, `--list` and `--portfolio`
(the payload builders live in `cli.py` and are shared) and leaves the same run
files.

What this is NOT: a service. There is no authentication, no queue and no rate
limiting. It binds to 127.0.0.1 only; every briefing with `use_model: true` is a
paid model call that any local caller can start. Do not expose it on a network.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any, Literal

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from client_intel import db
from client_intel.cli import DEFAULT_OUT, error_payload, listing, run_payload, write_run_files
from client_intel.llm import DEFAULT_MODEL, AnthropicWriter, ModelError, Writer, load_env
from client_intel.pipeline import RequestError, load_triggers, run
from client_intel.portfolio import rank_portfolio

HOST = "127.0.0.1"
DEFAULT_PORT = 8000
PORT_ENV = "CLIENT_INTEL_API_PORT"
# Where run files go; the default is the command's folder, so both leave one record.
OUT_ENV = "CLIENT_INTEL_API_OUT"
DB_ENV = "CLIENT_INTEL_DB"

CLIENT_MAX_CHARS = 80
CONTEXT_MAX_CHARS = 500

WriterFactory = Callable[[], Writer]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Load the data pack and the triggers once; requests only read them."""
    # Same .env reading as the command, so /api/health tells the truth about the key.
    load_env()
    app.state.dataset = await asyncio.to_thread(db.load, os.getenv(DB_ENV) or db.DEFAULT_DB)
    app.state.plans = load_triggers()
    app.state.out_dir = Path(os.getenv(OUT_ENV) or DEFAULT_OUT)
    yield


app = FastAPI(title="client-intel", version="0.1.0", lifespan=lifespan)
# No CORS middleware on purpose: the UI calls this API from its server, not from
# the browser, so no cross-origin request ever reaches it. Allowing origins would
# only let any web page the user has open start paid model runs on localhost.


class BriefingRequest(BaseModel):
    # Surrounding whitespace is stripped before the length limits apply, so a
    # client of only spaces is rejected as empty.
    model_config = ConfigDict(str_strip_whitespace=True)

    client: str = Field(min_length=1, max_length=CLIENT_MAX_CHARS)
    trigger: str = Field(min_length=1)
    context: str = Field(default="", max_length=CONTEXT_MAX_CHARS)
    use_model: bool = True
    # "structured": the model selects facts and comments, code writes every sentence
    # with a figure. Without a model the mode makes no difference.
    mode: Literal["prose", "structured"] = "prose"

    @field_validator("context")
    @classmethod
    def one_line(cls, value: str) -> str:
        # The context is printed inside the one-line briefing header; a line break
        # there would break the heading block of the Markdown.
        return " ".join(value.split())


def get_writer_factory() -> WriterFactory:
    """How a writer is made for one run. Tests override this with a fake.

    A factory rather than a writer: the real one keeps a per-run token log and
    raises ModelError when the key is missing, which must happen per request.
    """
    return AnthropicWriter


def _error(status: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content=error_payload(message))


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """A malformed body gets the same object as any other unanswerable request."""
    parts: list[str] = []
    for err in exc.errors():
        where = ".".join(str(p) for p in err.get("loc", ()) if p != "body")
        parts.append(f"{where}: {err.get('msg', 'invalid')}" if where else str(err.get("msg")))
    return _error(422, "Invalid request: " + "; ".join(parts))


@app.get("/api/health")
async def health(request: Request) -> dict[str, Any]:
    return {
        "status": "ok",
        "as_of": request.app.state.dataset.as_of.isoformat(),
        "model": os.getenv("CLIENT_INTEL_MODEL") or DEFAULT_MODEL,
        # Only whether a key is set. The value never leaves the process.
        "model_key_present": bool(os.getenv("ANTHROPIC_API_KEY")),
    }


@app.get("/api/meta")
async def meta(request: Request) -> dict[str, Any]:
    return listing(request.app.state.dataset, request.app.state.plans)


def _brief(dataset: db.Dataset, body: BriefingRequest, factory: WriterFactory,
           out_dir: Path) -> dict[str, Any]:
    """One whole run, including the file writes; called in a worker thread."""
    writer = factory() if body.use_model else None
    result = run(dataset, body.client, body.trigger, body.context, writer, mode=body.mode)
    write_run_files(result, out_dir)
    return run_payload(result)


@app.post("/api/briefings")
async def create_briefing(
    body: BriefingRequest,
    request: Request,
    factory: Annotated[WriterFactory, Depends(get_writer_factory)],
) -> JSONResponse:
    state = request.app.state
    try:
        # The pipeline is synchronous (tools, model call, files); a thread keeps
        # the event loop free for health checks while a briefing is written.
        payload = await asyncio.to_thread(_brief, state.dataset, body, factory, state.out_dir)
    except RequestError as exc:
        return _error(422, str(exc))
    except ModelError as exc:
        return _error(502, str(exc))
    # 200 also when lines are flagged: the briefing exists and says what is unverified.
    return JSONResponse(status_code=200, content=payload)


@app.get("/api/portfolio")
async def portfolio(request: Request) -> dict[str, Any]:
    return await asyncio.to_thread(rank_portfolio, request.app.state.dataset)


def serve() -> None:
    """Entry point of `client-intel-api`: one process, loopback only."""
    import uvicorn

    uvicorn.run(app, host=HOST, port=int(os.getenv(PORT_ENV) or DEFAULT_PORT))
