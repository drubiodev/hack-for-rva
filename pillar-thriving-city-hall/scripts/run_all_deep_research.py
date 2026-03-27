#!/usr/bin/env python3
"""
Batch-run Parallel.ai deep research on all prompts under 05_prompts/research.

Requirements:
    pip install parallel-ai

Setup:
    Copy 05_prompts/parallel_runner/.env.example → 05_prompts/parallel_runner/.env
    Set PARALLEL_API_KEY in that file (or export it in your shell).

Usage:
    python scripts/run_all_deep_research.py
    python scripts/run_all_deep_research.py --processor pro-fast
    python scripts/run_all_deep_research.py --processor ultra --limit 5
    python scripts/run_all_deep_research.py --overwrite

Outputs land in research/<prompt_basename>.md and research/<prompt_basename>.json.
Skips prompts that already have outputs unless --overwrite is set.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from time import sleep


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() and k.strip() not in os.environ:
            os.environ[k.strip()] = v.strip()


def run_batch(
    prompts: list[Path],
    out_dir: Path,
    processor: str,
    overwrite: bool,
    delay: float,
) -> list[tuple[Path, str]]:
    try:
        from parallel import Parallel
        from parallel.types import TaskSpecParam, TextSchemaParam
    except ImportError:
        raise SystemExit(
            "parallel-ai SDK not installed. Run: pip install parallel-ai"
        )

    api_key = os.getenv("PARALLEL_API_KEY")
    if not api_key:
        raise SystemExit(
            "PARALLEL_API_KEY not set. "
            "Add it to 05_prompts/parallel_runner/.env or export it."
        )

    client = Parallel(api_key=api_key)
    out_dir.mkdir(parents=True, exist_ok=True)
    results: list[tuple[Path, str]] = []

    for p in prompts:
        md_path = out_dir / f"{p.stem}.md"

        if not overwrite and md_path.exists():
            results.append((p, "skipped (exists)"))
            continue

        content = p.read_text(encoding="utf-8").strip()
        try:
            task_run = client.task_run.create(
                input=content,
                processor=processor,
                task_spec=TaskSpecParam(output_schema=TextSchemaParam()),
            )
            run_result = client.task_run.result(task_run.run_id, api_timeout=3600)
            output = run_result.output

            output_text = ""
            if hasattr(output, "content"):
                output_text = (
                    output.content
                    if isinstance(output.content, str)
                    else str(output.content or "")
                )
            else:
                output_text = str(output or "")

            md_path.write_text(output_text, encoding="utf-8")
            results.append((p, "ok"))

        except Exception as e:
            results.append((p, f"error: {e}"))

        if delay > 0:
            sleep(delay)

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Parallel.ai deep research on all prompts in a folder"
    )
    parser.add_argument("prompts_dir", nargs="?", default="05_prompts/research")
    parser.add_argument("--output-dir", default="research")
    parser.add_argument(
        "--processor",
        default=os.getenv("PARALLEL_PROCESSOR", "pro"),
        help="Parallel.ai processor (default: pro). Options: pro, pro-fast, ultra, ultra-fast, etc.",
    )
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="Max prompts to run (0 = all)")
    parser.add_argument("--delay", type=float, default=0.0,
                        help="Seconds between submissions (default: 0)")
    args = parser.parse_args()

    load_env_file(Path("05_prompts/parallel_runner/.env"))

    prompts_path = Path(args.prompts_dir)
    if not prompts_path.exists() or not prompts_path.is_dir():
        print(f"Not a directory: {prompts_path}", file=sys.stderr)
        return 2

    out_dir = Path(args.output_dir)

    all_prompts = sorted(p for p in prompts_path.iterdir() if p.suffix == ".txt")

    def has_output(p: Path) -> bool:
        return (out_dir / f"{p.stem}.md").exists() or (out_dir / f"{p.stem}.json").exists()

    if args.limit > 0:
        pending = [p for p in all_prompts if not has_output(p)]
        to_run = pending[: args.limit]
    else:
        to_run = all_prompts if args.overwrite else [p for p in all_prompts if not has_output(p)]

    skipped_count = len(all_prompts) - len(to_run)
    if skipped_count and not args.overwrite:
        print(f"Skipping {skipped_count} prompts with existing outputs (--overwrite to re-run)")

    if not to_run:
        print("Nothing to run.")
        return 0

    print(f"Running {len(to_run)} prompts  [processor={args.processor}]")

    results = run_batch(to_run, out_dir, args.processor, args.overwrite, args.delay)

    ok = sum(1 for _, s in results if s == "ok")
    skipped = sum(1 for _, s in results if s.startswith("skipped"))
    errors = sum(1 for _, s in results if s.startswith("error"))

    for p, status in results:
        symbol = "✓" if status == "ok" else ("·" if status.startswith("skipped") else "✗")
        print(f"  {symbol} {p.name}: {status}")

    print(f"\nDone: {ok} ok, {skipped} skipped, {errors} errors")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
