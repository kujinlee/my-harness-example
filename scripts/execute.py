#!/usr/bin/env python3
"""
Harness Step Executor — runs steps in a phase sequentially with self-correction.

Orchestration (index.json)
  phases/<phase-dir>/index.json is the control plane. It lists steps (each has at
  least step, name, status). The executor only *reads* which step to run next; it
  does not infer success from Claude's exit code.

  - status "pending": eligible to run. The executor picks the first pending step
    in array order, sets started_at on first entry, runs Claude with stepN.md.
  - After each run it re-reads the same file. The *agent* (via Claude) is expected
    to edit index.json and the repo to reflect reality:
      "completed" (+ summary, timestamps) → executor commits and advances.
      "blocked" (+ blocked_reason) → executor stops (exit 2), updates optional rollup.
      anything else (still pending, error, or unchanged) → retry up to MAX_RETRIES
      with the last error text in the next prompt; then force "error" and exit 1.
  - _check_blockers() refuses to start if a later tail of the list is error/blocked
    in a way that implies the phase must be fixed by hand (see that method).

  Optional phases/index.json: per-phase rollup (status + completed_at / failed_at /
  blocked_at). Updated when the phase finishes or aborts.

  stepN.md holds the step instructions; index.json holds machine-readable progress.

Flow (read top-down in StepExecutor.run):
  validate phase → git branch → load CLAUDE.md/docs into prompt → for each
  pending step: call Claude with preamble + stepN.md → re-read index.json for
  that step's status (completed / blocked / retry) → git commit; finally mark
  phase complete and optional push.

Uses `claude --dangerously-skip-permissions` for unattended runs; only use in a
trusted repo and environment.

Usage:
    python3 scripts/execute.py <phase-dir> [--push]
"""

import argparse
import contextlib
import json
import subprocess
import sys
import threading
import time
import types
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent


@contextlib.contextmanager
def progress_indicator(label: str):
    """Show a stderr spinner for the ``with`` body; clear the line on exit.

    Yields a ``SimpleNamespace``; ``.elapsed`` is set in ``finally`` (read it after
    the ``with`` block ends).
    """
    frames = "◐◓◑◒"
    stop = threading.Event()
    t0 = time.monotonic()

    def _animate():
        """Overwrite one stderr line until ``stop`` is set."""
        idx = 0
        while not stop.wait(0.12):
            sec = int(time.monotonic() - t0)
            sys.stderr.write(f"\r{frames[idx % len(frames)]} {label} [{sec}s]")
            sys.stderr.flush()
            idx += 1
        sys.stderr.write("\r" + " " * (len(label) + 20) + "\r")
        sys.stderr.flush()

    th = threading.Thread(target=_animate, daemon=True)
    th.start()
    info = types.SimpleNamespace(elapsed=0.0)
    try:
        yield info
    finally:
        stop.set()
        th.join()
        info.elapsed = time.monotonic() - t0


class StepExecutor:
    """Drive one phase under phases/<dir>/.

    Orchestration is described in the module docstring: phases/<dir>/index.json
    drives which step runs and how the loop advances; stepN.md is the prompt body.
    Optional phases/index.json rolls up phase status. Git uses branch feat-<phase>.
    """

    MAX_RETRIES = 3
    FEAT_MSG = "feat({phase}): step {num} — {name}"
    CHORE_MSG = "chore({phase}): step {num} output"
    # Fixed UTC-8 (US Pacific Standard); does not follow PDT. Use zoneinfo
    # ZoneInfo("America/Los_Angeles") if you need DST.
    TZ = timezone(timedelta(hours=-8))

    def __init__(self, phase_dir_name: str, *, auto_push: bool = False):
        """Resolve ``phases/<phase_dir_name>/`` paths and load step count from ``index.json``.

        Exits the process if the directory, ``index.json``, or ``steps`` array is missing/invalid.
        """
        self._root = str(ROOT)
        self._phases_dir = ROOT / "phases"
        self._phase_dir = self._phases_dir / phase_dir_name
        self._phase_dir_name = phase_dir_name
        self._top_index_file = self._phases_dir / "index.json"
        self._auto_push = auto_push

        if not self._phase_dir.is_dir():
            print(f"ERROR: {self._phase_dir} not found")
            sys.exit(1)

        self._index_file = self._phase_dir / "index.json"
        if not self._index_file.exists():
            print(f"ERROR: {self._index_file} not found")
            sys.exit(1)

        idx = self._read_json(self._index_file)
        if "steps" not in idx or not isinstance(idx["steps"], list):
            print(f"ERROR: {self._index_file} must contain a JSON array \"steps\"")
            sys.exit(1)
        self._project = idx.get("project", "project")
        self._phase_name = idx.get("phase", phase_dir_name)
        self._total = len(idx["steps"])

    def run(self):
        """Run the full harness for this phase (validate → git → steps → finalize)."""
        # Order matters: refuse bad state before branch switch; load docs once;
        # run all pendings; then phase-level git + index completion.
        self._print_header()
        self._check_blockers()
        self._checkout_branch()
        guardrails = self._load_guardrails()
        self._ensure_created_at()
        self._execute_all_steps(guardrails)
        self._finalize()

    # --- timestamps ---

    def _stamp(self) -> str:
        """Current wall time as ISO-8601 with offset (``self.TZ``)."""
        return datetime.now(self.TZ).strftime("%Y-%m-%dT%H:%M:%S%z")

    # --- JSON I/O ---

    @staticmethod
    def _read_json(p: Path) -> dict:
        """Load a JSON object from UTF-8 file ``p``."""
        return json.loads(p.read_text(encoding="utf-8"))

    @staticmethod
    def _write_json(p: Path, data: dict):
        """Write ``data`` as indented UTF-8 JSON to ``p``."""
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # --- git ---

    def _run_git(self, *args) -> subprocess.CompletedProcess:
        """Run ``git <args>`` in ``self._root`` with captured text stdout/stderr."""
        cmd = ["git"] + list(args)
        return subprocess.run(cmd, cwd=self._root, capture_output=True, text=True)

    def _checkout_branch(self):
        """Ensure HEAD is ``feat-<phase_name>`` (create branch if missing). Exits on failure."""
        branch = f"feat-{self._phase_name}"

        r = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
        if r.returncode != 0:
            print(f"  ERROR: git is not available or this is not a git repository.")
            print(f"  {r.stderr.strip()}")
            sys.exit(1)

        if r.stdout.strip() == branch:
            return

        r = self._run_git("rev-parse", "--verify", branch)
        r = self._run_git("checkout", branch) if r.returncode == 0 else self._run_git("checkout", "-b", branch)

        if r.returncode != 0:
            print(f"  ERROR: failed to check out branch '{branch}'.")
            print(f"  {r.stderr.strip()}")
            print(f"  Hint: stash or commit your changes, then try again.")
            sys.exit(1)

        print(f"  Branch: {branch}")

    def _commit_step(self, step_num: int, step_name: str):
        """Commit step changes: ``feat`` for repo work, then ``chore`` for index/output JSON."""
        # Unstage harness artifacts so first commit is "code"; second add/commit picks up index + output.
        output_rel = f"phases/{self._phase_dir_name}/step{step_num}-output.json"
        index_rel = f"phases/{self._phase_dir_name}/index.json"

        self._run_git("add", "-A")
        self._run_git("reset", "HEAD", "--", output_rel)
        self._run_git("reset", "HEAD", "--", index_rel)

        if self._run_git("diff", "--cached", "--quiet").returncode != 0:
            msg = self.FEAT_MSG.format(phase=self._phase_name, num=step_num, name=step_name)
            r = self._run_git("commit", "-m", msg)
            if r.returncode == 0:
                print(f"  Commit: {msg}")
            else:
                print(f"  ERROR: code commit failed: {r.stderr.strip()}")
                sys.exit(1)

        self._run_git("add", "-A")
        if self._run_git("diff", "--cached", "--quiet").returncode != 0:
            msg = self.CHORE_MSG.format(phase=self._phase_name, num=step_num)
            r = self._run_git("commit", "-m", msg)
            if r.returncode != 0:
                print(f"  ERROR: housekeeping commit failed: {r.stderr.strip()}")
                sys.exit(1)

    # --- top-level index ---

    def _update_top_index(self, status: str):
        """If ``phases/index.json`` exists, set this phase's ``status`` and terminal timestamp."""
        if not self._top_index_file.exists():
            return
        top = self._read_json(self._top_index_file)
        ts = self._stamp()
        for phase in top.get("phases", []):
            if phase.get("dir") == self._phase_dir_name:
                phase["status"] = status
                ts_key = {"completed": "completed_at", "error": "failed_at", "blocked": "blocked_at"}.get(status)
                if ts_key:
                    phase[ts_key] = ts
                break
        self._write_json(self._top_index_file, top)

    # --- guardrails & context ---

    def _load_guardrails(self) -> str:
        """Return CLAUDE.md plus sorted ``docs/*.md`` joined for prompt injection (may be empty)."""
        sections = []
        claude_md = ROOT / "CLAUDE.md"
        if claude_md.exists():
            sections.append(f"## Project rules (CLAUDE.md)\n\n{claude_md.read_text()}")
        docs_dir = ROOT / "docs"
        if docs_dir.is_dir():
            for doc in sorted(docs_dir.glob("*.md")):
                sections.append(f"## {doc.stem}\n\n{doc.read_text()}")
        return "\n\n---\n\n".join(sections) if sections else ""

    @staticmethod
    def _build_step_context(index: dict) -> str:
        """Markdown list of completed steps that have a ``summary`` (context for the next step)."""
        lines = [
            f"- Step {s['step']} ({s['name']}): {s['summary']}"
            for s in index["steps"]
            if s["status"] == "completed" and s.get("summary")
        ]
        if not lines:
            return ""
        return "## Previous step outputs\n\n" + "\n".join(lines) + "\n\n"

    def _build_preamble(self, guardrails: str, step_context: str,
                        prev_error: Optional[str] = None) -> str:
        """Instructions prepended to ``stepN.md``: rules, prior summaries, optional retry error."""
        commit_example = self.FEAT_MSG.format(
            phase=self._phase_name, num="N", name="<step-name>"
        )
        retry_section = ""
        if prev_error:
            retry_section = (
                f"\n## ⚠ Previous attempt failed — fix using the error below\n\n"
                f"{prev_error}\n\n---\n\n"
            )
        return (
            f"You are a developer on the {self._project} project. Complete the step below.\n\n"
            f"{guardrails}\n\n---\n\n"
            f"{step_context}{retry_section}"
            f"## Working rules\n\n"
            f"1. Review code from prior steps and keep it consistent.\n"
            f"2. Do only what this step specifies. Do not add features or extra files.\n"
            f"3. Do not break existing tests.\n"
            f"4. Run the acceptance criteria (AC) checks yourself.\n"
            f"5. Update the matching step `status` in /phases/{self._phase_dir_name}/index.json:\n"
            f"   - AC pass → set \"completed\" and one-line \"summary\" of this step's output\n"
            f"   - Still failing after {self.MAX_RETRIES} fix attempts → set \"error\" and record \"error_message\"\n"
            f"   - User intervention needed (API keys, auth, manual setup, etc.) → set \"blocked\" and \"blocked_reason\", then stop immediately\n"
            f"6. Commit all changes:\n"
            f"   {commit_example}\n\n---\n\n"
        )

    # --- Claude invocation ---

    def _invoke_claude(self, step: dict, preamble: str) -> dict:
        """Run ``claude -p`` once for ``step``; write ``stepN-output.json`` and return the same dict."""
        step_num, step_name = step["step"], step["name"]
        step_file = self._phase_dir / f"step{step_num}.md"

        if not step_file.exists():
            print(f"  ERROR: {step_file} not found")
            sys.exit(1)

        prompt = preamble + step_file.read_text()
        # Print mode: one shot. Caller decides success by re-reading index.json after this returns.
        try:
            result = subprocess.run(
                ["claude", "-p", "--dangerously-skip-permissions", "--output-format", "json", prompt],
                cwd=self._root, capture_output=True, text=True, timeout=1800,
            )
        except subprocess.TimeoutExpired as e:
            print(f"\n  ERROR: Claude subprocess timed out after 1800s (step {step_num})")
            raw_out = e.stdout if e.stdout is not None else b""
            raw_err = e.stderr if e.stderr is not None else b""
            out_stdout = raw_out if isinstance(raw_out, str) else raw_out.decode("utf-8", errors="replace")
            out_stderr = raw_err if isinstance(raw_err, str) else raw_err.decode("utf-8", errors="replace")
            tail = "\n[harness] subprocess.TimeoutExpired after 1800s\n"
            output = {
                "step": step_num,
                "name": step_name,
                "exitCode": 124,
                "stdout": out_stdout or "",
                "stderr": (out_stderr or "") + tail,
            }
            out_path = self._phase_dir / f"step{step_num}-output.json"
            with open(out_path, "w") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            return output

        if result.returncode != 0:
            print(f"\n  WARN: Claude exited abnormally (code {result.returncode})")
            if result.stderr:
                print(f"  stderr: {result.stderr[:500]}")

        output = {
            "step": step_num, "name": step_name,
            "exitCode": result.returncode,
            "stdout": result.stdout or "",
            "stderr": result.stderr or "",
        }
        out_path = self._phase_dir / f"step{step_num}-output.json"
        with open(out_path, "w") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        return output

    # --- Header & validation ---

    def _print_header(self):
        """Print phase name, step count, and optional auto-push flag."""
        print(f"\n{'='*60}")
        print(f"  Harness Step Executor")
        print(f"  Phase: {self._phase_name} | Steps: {self._total}")
        if self._auto_push:
            print(f"  Auto-push: enabled")
        print(f"{'='*60}")

    def _check_blockers(self):
        """Refuse to start if ``index.json`` tail implies error/blocked needing human fix."""
        # Last index → first: abort if we see error or blocked; break on any other non-pending (e.g. completed).
        index = self._read_json(self._index_file)
        for s in reversed(index["steps"]):
            if s["status"] == "error":
                print(f"\n  ✗ Step {s['step']} ({s['name']}) failed.")
                print(f"  Error: {s.get('error_message', 'unknown')}")
                print(f"  Fix and reset status to 'pending' to retry.")
                sys.exit(1)
            if s["status"] == "blocked":
                print(f"\n  ⏸ Step {s['step']} ({s['name']}) blocked.")
                print(f"  Reason: {s.get('blocked_reason', 'unknown')}")
                print(f"  Resolve and reset status to 'pending' to retry.")
                sys.exit(2)
            if s["status"] != "pending":
                break

    def _ensure_created_at(self):
        """Set top-level ``created_at`` on the phase ``index.json`` when absent."""
        index = self._read_json(self._index_file)
        if "created_at" not in index:
            index["created_at"] = self._stamp()
            self._write_json(self._index_file, index)

    # --- Run loop ---

    def _execute_single_step(self, step: dict, guardrails: str) -> bool:
        """Run ``step`` with up to ``MAX_RETRIES`` attempts; return True only if status becomes completed.

        Re-reads ``index.json`` after each Claude run. Exits the process on blocked or terminal error.
        """
        # Each attempt: fresh preamble (with prior completed summaries; on retry, inject prev_error).
        step_num, step_name = step["step"], step["name"]
        done = sum(1 for s in self._read_json(self._index_file)["steps"] if s["status"] == "completed")
        prev_error = None

        for attempt in range(1, self.MAX_RETRIES + 1):
            index = self._read_json(self._index_file)
            step_context = self._build_step_context(index)
            preamble = self._build_preamble(guardrails, step_context, prev_error)

            denom = max(self._total - 1, 1)
            tag = f"Step {step_num}/{denom} ({done} done): {step_name}"
            if attempt > 1:
                tag += f" [retry {attempt}/{self.MAX_RETRIES}]"

            with progress_indicator(tag) as pi:
                self._invoke_claude(step, preamble)
            elapsed = int(pi.elapsed)

            index = self._read_json(self._index_file)
            status = next((s.get("status", "pending") for s in index["steps"] if s["step"] == step_num), "pending")
            ts = self._stamp()

            if status == "completed":
                for s in index["steps"]:
                    if s["step"] == step_num:
                        s["completed_at"] = ts
                self._write_json(self._index_file, index)
                self._commit_step(step_num, step_name)
                print(f"  ✓ Step {step_num}: {step_name} [{elapsed}s]")
                return True

            if status == "blocked":
                for s in index["steps"]:
                    if s["step"] == step_num:
                        s["blocked_at"] = ts
                self._write_json(self._index_file, index)
                reason = next((s.get("blocked_reason", "") for s in index["steps"] if s["step"] == step_num), "")
                print(f"  ⏸ Step {step_num}: {step_name} blocked [{elapsed}s]")
                print(f"    Reason: {reason}")
                self._update_top_index("blocked")
                sys.exit(2)

            err_msg = next(
                (s.get("error_message", "Step did not update status") for s in index["steps"] if s["step"] == step_num),
                "Step did not update status",
            )

            if attempt < self.MAX_RETRIES:
                # Clear error so the next Claude run is a clean attempt; preamble still carries err_msg.
                for s in index["steps"]:
                    if s["step"] == step_num:
                        s["status"] = "pending"
                        s.pop("error_message", None)
                self._write_json(self._index_file, index)
                prev_error = err_msg
                print(f"  ↻ Step {step_num}: retry {attempt}/{self.MAX_RETRIES} — {err_msg}")
            else:
                for s in index["steps"]:
                    if s["step"] == step_num:
                        s["status"] = "error"
                        s["error_message"] = f"[Failed after {self.MAX_RETRIES} attempts] {err_msg}"
                        s["failed_at"] = ts
                self._write_json(self._index_file, index)
                self._commit_step(step_num, step_name)
                print(f"  ✗ Step {step_num}: {step_name} failed after {self.MAX_RETRIES} attempts [{elapsed}s]")
                print(f"    Error: {err_msg}")
                self._update_top_index("error")
                sys.exit(1)

        return False  # unreachable

    def _execute_all_steps(self, guardrails: str):
        """Repeatedly run the first ``pending`` step until none remain."""
        # Always take the first pending step in index order (steps should stay ordered).
        while True:
            index = self._read_json(self._index_file)
            pending = next((s for s in index["steps"] if s["status"] == "pending"), None)
            if pending is None:
                print("\n  All steps completed!")
                return

            step_num = pending["step"]
            for s in index["steps"]:
                if s["step"] == step_num and "started_at" not in s:
                    s["started_at"] = self._stamp()
                    self._write_json(self._index_file, index)
                    break

            self._execute_single_step(pending, guardrails)

    def _finalize(self):
        """Set ``completed_at``, update rollup index, commit, and optionally ``git push``."""
        # Called only when every step is already non-pending (normally all completed).
        index = self._read_json(self._index_file)
        index["completed_at"] = self._stamp()
        self._write_json(self._index_file, index)
        self._update_top_index("completed")

        self._run_git("add", "-A")
        if self._run_git("diff", "--cached", "--quiet").returncode != 0:
            msg = f"chore({self._phase_name}): mark phase completed"
            r = self._run_git("commit", "-m", msg)
            if r.returncode == 0:
                print(f"  ✓ {msg}")
            else:
                print(f"  ERROR: phase completion commit failed: {r.stderr.strip()}")
                sys.exit(1)

        if self._auto_push:
            branch = f"feat-{self._phase_name}"
            r = self._run_git("push", "-u", "origin", branch)
            if r.returncode != 0:
                print(f"\n  ERROR: git push failed: {r.stderr.strip()}")
                sys.exit(1)
            print(f"  ✓ Pushed to origin/{branch}")

        print(f"\n{'='*60}")
        print(f"  Phase '{self._phase_name}' completed!")
        print(f"{'='*60}")


def main():
    """Parse CLI ``<phase_dir> [--push]`` and run ``StepExecutor.run()``."""
    parser = argparse.ArgumentParser(description="Harness Step Executor")
    parser.add_argument("phase_dir", help="Phase directory name (e.g. 0-mvp)")
    parser.add_argument("--push", action="store_true", help="Push branch after completion")
    args = parser.parse_args()

    StepExecutor(args.phase_dir, auto_push=args.push).run()


if __name__ == "__main__":
    main()
