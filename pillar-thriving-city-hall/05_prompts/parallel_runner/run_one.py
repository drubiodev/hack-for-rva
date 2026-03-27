#!/usr/bin/env python3
"""Run a single research prompt through Parallel.ai and save the output.

Usage:
    python 05_prompts/parallel_runner/run_one.py 05_prompts/research/A1_problem_landscape_foo.txt
    python 05_prompts/parallel_runner/run_one.py 05_prompts/research/A1_problem_landscape_foo.txt --processor ultra
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

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
    parser = argparse.ArgumentParser(description="Run one research prompt via Parallel.ai")
    parser.add_argument("prompt_file", help="Path to .txt prompt file")
    parser.add_argument("--processor", default=os.getenv("PARALLEL_PROCESSOR", "pro"))
    parser.add_argument("--output-dir", default="research")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    load_env_file(Path("05_prompts/parallel_runner/.env"))

    prompt_path = Path(args.prompt_file)
    if not prompt_path.exists():
        print(f"Prompt file not found: {prompt_path}", file=sys.stderr)
        return 2

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / f"{prompt_path.stem}.md"

    if not args.overwrite and md_path.exists():
        print(f"Output already exists (use --overwrite to replace): {md_path}")
        return 0

    client = ParallelClient(processor=args.processor)
    content = prompt_path.read_text(encoding="utf-8").strip()

    print(f"Submitting: {prompt_path.name}  [processor={args.processor}]")
    result = client.create_response(input_text=content)

    md_path.write_text(result["output_text"], encoding="utf-8")
    print(f"Done → {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
