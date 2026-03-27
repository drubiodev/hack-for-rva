#!/usr/bin/env python3
"""Batch-run all research prompts through Parallel.ai.

Usage:
    python 05_prompts/parallel_runner/run_all.py
    python 05_prompts/parallel_runner/run_all.py --processor ultra --overwrite
    python 05_prompts/parallel_runner/run_all.py --limit 5 --delay 2

Outputs land in research/<prompt_basename>.md.
Skips prompts that already have outputs unless --overwrite is set.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from time import sleep

sys.path.insert(0, str(Path(__file__).parent))
from parallel_client import ParallelClient


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch-run research prompts via Parallel.ai")
    parser.add_argument("prompts_dir", nargs="?", default="05_prompts/research")
    parser.add_argument("--processor", default=os.getenv("PARALLEL_PROCESSOR", "pro"),
                        help="Parallel.ai processor (default: pro). Options: pro, pro-fast, ultra, ultra-fast, etc.")
    parser.add_argument("--output-dir", default="research")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="Max prompts to run (0 = all)")
    parser.add_argument("--delay", type=float, default=0.0,
                        help="Seconds to wait between submissions (default: 0)")
    args = parser.parse_args()

    load_env_file(Path("05_prompts/parallel_runner/.env"))

    prompts_path = Path(args.prompts_dir)
    if not prompts_path.is_dir():
        print(f"Not a directory: {prompts_path}", file=sys.stderr)
        return 2

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    all_prompts = sorted(p for p in prompts_path.iterdir() if p.suffix == ".txt")

    def has_output(p: Path) -> bool:
        return (out_dir / f"{p.stem}.md").exists()

    if args.limit > 0:
        pending = [p for p in all_prompts if not has_output(p)]
        to_run = pending[: args.limit]
    else:
        to_run = all_prompts if args.overwrite else [p for p in all_prompts if not has_output(p)]
        if not args.overwrite:
            skipped = len(all_prompts) - len(to_run)
            if skipped:
                print(f"Skipping {skipped} prompts that already have outputs (use --overwrite to re-run)")

    if not to_run:
        print("Nothing to run.")
        return 0

    client = ParallelClient(processor=args.processor)
    print(f"Running {len(to_run)} prompts  [processor={args.processor}]")

    ok = skipped = errors = 0
    for i, p in enumerate(to_run, 1):
        md_path = out_dir / f"{p.stem}.md"

        if not args.overwrite and has_output(p):
            print(f"[{i}/{len(to_run)}] {p.name}: skipped (exists)")
            skipped += 1
            continue

        content = p.read_text(encoding="utf-8").strip()
        print(f"[{i}/{len(to_run)}] {p.name} ...", end=" ", flush=True)
        try:
            result = client.create_response(input_text=content)
            md_path.write_text(result["output_text"], encoding="utf-8")
            print(f"ok")
            ok += 1
        except Exception as e:
            print(f"ERROR: {e}")
            errors += 1

        if args.delay > 0 and i < len(to_run):
            sleep(args.delay)

    print(f"\nDone: {ok} ok, {skipped} skipped, {errors} errors")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
