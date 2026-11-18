# Web view for client-intel

A thin view over the command-line tool in the parent folder. Every figure, check and
score is computed in Python; this app only starts the command, reads the JSON it prints
and displays it. It has no logic of its own to trust or to test.

## Run

```bash
cd ui
npm install
npm run dev        # http://localhost:3000
```

Needs Node 20 or newer and `uv` on the PATH (the app runs `uv run client-intel ...` in
the parent folder, so `uv sync` must have been done there). Runs with the model need
the API key in the repository's `.env`; with "Use the model" switched off no key is
needed and nothing is charged.

## Pages

- **Briefing** (`/`): pick a client and a trigger, add optional context, run. The
  briefing is shown with every citation as a chip; a click opens the evidence behind it
  (the fact, whether it is measured, computed, reported by a person or a gap, and its
  source rows). Lines the verifier could not support carry an "Unverified" badge. Below:
  the run trace (time, tokens, cost per step) and what each tool returned.
- **Portfolio** (`/portfolio`): all clients ranked by renewal risk, or by growth, with
  the reasons and their citations. Each row links to a briefing for that client.

## How it talks to the tool

| Route | Command |
|---|---|
| `GET /api/list` | `uv run client-intel --list` |
| `POST /api/briefing` `{client, trigger, context?, useModel}` | `uv run client-intel --client=... --trigger=... --json [--context=...] [--no-llm]` |
| `GET /api/portfolio` | `uv run client-intel --portfolio` |

The command is started with `execFile` and an argument list, never through a shell.
The client must match `^[\w .,&'()-]{1,80}$`, the trigger must be one the tool lists,
the context is at most 500 characters. `useModel` must be exactly `true` for a model
run; anything else adds `--no-llm`. A run that ends with flagged lines (exit code 1)
is shown as a result; a request that cannot be answered (exit code 2) is shown as an
error with the tool's own message.

## Limits

- Local use only. There is no login and no access control; anyone who can reach the
  port can start a model run.
- One briefing at a time: a second request while one is running gets HTTP 409.
- No streaming or progress: the page waits for the command to finish (timeout 180 s).
- Nothing is stored; a reload loses the result. The tool itself still writes its files
  to `runs/`.
- Client and trigger lists are read from the tool on every request, which costs about
  a second each time.
