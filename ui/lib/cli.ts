import { execFile } from "node:child_process";
import path from "node:path";

// The UI lives in <repo>/ui and is started from there, so the Python project is one level up.
const REPO_ROOT = process.env.CLIENT_INTEL_ROOT ?? path.resolve(process.cwd(), "..");

export interface CliResult {
  exitCode: number;
  json: unknown | null;
  stderr: string;
}

/** Runs `uv run client-intel <args>` without a shell and parses stdout as one JSON object. */
export function runCli(args: string[]): Promise<CliResult> {
  return new Promise((resolve) => {
    execFile(
      "uv",
      ["run", "client-intel", ...args],
      { cwd: REPO_ROOT, maxBuffer: 64 * 1024 * 1024, timeout: 180_000 },
      (err, stdout, stderr) => {
        // Exit codes 1 and 2 are part of the contract and still carry JSON on stdout,
        // so a non-zero exit is not treated as a failure by itself.
        let exitCode = 0;
        let extra = "";
        if (err) {
          const code = (err as NodeJS.ErrnoException).code;
          exitCode = typeof code === "number" ? code : -1;
          if (typeof code !== "number") extra = err.killed ? "timed out after 180 s" : err.message;
        }
        let json: unknown | null = null;
        try {
          json = JSON.parse(stdout);
        } catch {
          json = null;
        }
        resolve({ exitCode, json, stderr: [extra, stderr].filter(Boolean).join("\n") });
      },
    );
  });
}

/** Last lines of stderr, enough to say what went wrong without dumping a traceback into the page. */
export function stderrTail(stderr: string, lines = 4): string {
  return stderr.trim().split("\n").slice(-lines).join("\n").slice(0, 1000);
}
