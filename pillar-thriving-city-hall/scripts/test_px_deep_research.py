#!/usr/bin/env python3
"""
Minimal Perplexity deep-research test without external dependencies.

Reads the prompt from 05_prompts/research/01_master_research_prompt.txt
Loads PERPLEXITY_API_KEY from environment or 05_prompts/perplexity_runner/.env
Calls the Perplexity Sonar endpoint with model=sonar-deep-research
Saves outputs under 05_prompts/research-output/
"""

import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            if k and v and k not in os.environ:
                os.environ[k.strip()] = v.strip()


def main() -> int:
    # Try to load the runner .env so we avoid requiring python-dotenv
    load_env_file(Path("05_prompts/perplexity_runner/.env"))

    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("PERPLEXITY_API_KEY not set. Set it or add to 05_prompts/perplexity_runner/.env", file=sys.stderr)
        return 2

    prompt_path = Path("05_prompts/research/01_master_research_prompt.txt")
    if not prompt_path.exists():
        print(f"Prompt not found: {prompt_path}", file=sys.stderr)
        return 2

    input_text = prompt_path.read_text(encoding="utf-8").strip()

    payload = {
        "model": "sonar-deep-research",
        "messages": [
            {"role": "user", "content": input_text}
        ],
    }

    url = os.getenv("PERPLEXITY_BASE_URL", "https://api.perplexity.ai/v1/sonar")
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")

    try:
        with urlopen(req, timeout=300) as resp:
            resp_body = resp.read().decode("utf-8")
            raw = json.loads(resp_body)
    except HTTPError as e:
        try:
            body = e.read().decode("utf-8")
        except Exception:
            body = None
        print(f"HTTP error {e.code}: {e.reason}\nBody: {body}", file=sys.stderr)
        return 1
    except URLError as e:
        print(f"Network error: {e}", file=sys.stderr)
        return 1

    # Extract assistant text
    output_text = ""
    try:
        if isinstance(raw.get("choices"), list) and raw["choices"]:
            output_text = raw["choices"][0].get("message", {}).get("content") or ""
        elif isinstance(raw.get("output_text"), str):
            output_text = raw["output_text"]
    except Exception:
        pass

    out_dir = Path("05_prompts/research-output")
    out_dir.mkdir(parents=True, exist_ok=True)
    base = "01_master_research_prompt"
    (out_dir / f"{base}.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")
    (out_dir / f"{base}.md").write_text(output_text or "", encoding="utf-8")

    print(f"Saved: {out_dir / f'{base}.md'}\nSaved: {out_dir / f'{base}.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
