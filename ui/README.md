# Web view for client-intel

A thin view over the client-intel HTTP API in the parent folder. Every figure, check and
score is computed in Python; this app only asks the API, reads the JSON it returns and
displays it. It has no logic of its own to trust or to test.

## Run

Two processes: the Python API and this web app.

```bash
# 1. In the repository root: the API, http://127.0.0.1:8000
uv run client-intel-api

# 2. In a second terminal: the web app, http://localhost:3000
cd ui && npm install && npm run dev
```

Needs Node 20 or newer for the web app, and `uv sync` done in the repository root for
the API. The API port comes from `CLIENT_INTEL_API_PORT` (default 8000).

| Variable | Read by | Default | Meaning |
|---|---|---|---|
| `CLIENT_INTEL_API_URL` | web app (server side) | `http://127.0.0.1:8000` | Where the web app finds the API |

For example, with the API on another port:

```bash
CLIENT_INTEL_API_PORT=8012 uv run client-intel-api
CLIENT_INTEL_API_URL=http://127.0.0.1:8012 npm run dev
```

Runs with the model need the API key in the repository's `.env` (read by the API, not
by this app). The header shows whether the API is reachable, which model it uses and
whether a key is configured. Without a key, "Use the model" starts switched off; with it
off no key is needed and nothing is charged.

If the API is not running, both pages say so: "The client-intel API is not running.
Start it with: uv run client-intel-api".

## Pages

- **Briefing** (`/`): pick a client and a trigger, add optional context, run. The
  briefing is shown with every citation as a chip; a click opens the evidence behind it
  (the fact, whether it is measured, computed, reported by a person or a gap, and its
  source rows). Lines the verifier could not support carry an "Unverified" badge. Below:
  the run trace (time, tokens, cost per step) and what each tool returned.
- **Portfolio** (`/portfolio`): all clients ranked by renewal risk, or by growth, with
  the reasons and their citations. Each row links to a briefing for that client.

## How it talks to the API

The browser only calls this app's own routes. They are a thin same-origin proxy
(`lib/api.ts`, server-side `fetch`), so the browser needs no CORS and never learns the
API's address.

| Route in this app | API call | Timeout |
|---|---|---|
| `GET /api/health` | `GET /api/health` | 30 s |
| `GET /api/list` | `GET /api/meta` | 30 s |
| `POST /api/briefing` `{client, trigger, context?, useModel}` | `POST /api/briefings` `{client, trigger, context, use_model}` | 180 s |
| `GET /api/portfolio` | `GET /api/portfolio` | 30 s |

The API's status code and JSON body are passed through unchanged: 200 for a written
briefing (also one with flagged lines, which is shown as a result), 422 for a request
that cannot be answered and 502 for a model problem (both shown as an error with the
API's own message).

The proxy adds its own answers only in these cases:

- 400: the input is rejected before the API is called. The client must match
  `^[\w .,&'()-]{1,80}$`, the trigger must be one the API lists, the context is at most
  500 characters. `useModel` must be exactly `true` for a model run; anything else is
  sent as `use_model: false`.
- 409: a briefing is already running.
- 503: the API cannot be reached.
- 504: the API did not answer within the timeout.
- 502: the API answered with something that is not JSON.

## Limits

- Local use only. There is no login and no access control, in this app or in the API;
  anyone who can reach either port can start a model run.
- One briefing at a time: a second request while one is running gets HTTP 409. The
  lock lives in this app's single process; it does not cover calls made straight to
  the API.
- No streaming or progress: the page waits for the API to finish (timeout 180 s).
- Nothing is stored here; a reload loses the result.
- The trigger list is read from the API on every briefing request, and the API status
  in the header is checked once per page load, not continuously.
