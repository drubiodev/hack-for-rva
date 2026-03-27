"""
Parallel.ai client for the deep-research prompt runner.

No external dependencies — uses stdlib urllib.
API key:  PARALLEL_API_KEY in .env (see .env.example)

Uses the Task API in text-schema mode so each research prompt returns
a markdown report with inline citations.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = "https://api.parallel.ai/v1/tasks/runs"


class ParallelClient:
    def __init__(
        self,
        api_key: str | None = None,
        processor: str = "pro",
    ):
        self.api_key = api_key or os.getenv("PARALLEL_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "PARALLEL_API_KEY not set. "
                "Copy .env.example → .env and add your key, or export PARALLEL_API_KEY."
            )
        self.processor = processor

    def _request(self, method: str, path: str = "", data: Any = None, timeout: int = 60) -> dict:
        url = BASE_URL + path
        body = json.dumps(data).encode("utf-8") if data is not None else None
        req = Request(url, data=body, method=method)
        req.add_header("x-api-key", self.api_key)
        req.add_header("Content-Type", "application/json")
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def submit(self, input_text: str, processor: str | None = None) -> str:
        """Submit a task and return the run_id immediately."""
        resp = self._request("POST", "", {
            "input": input_text,
            "processor": processor or self.processor,
            "task_spec": {"output_schema": {"type": "text"}},
        })
        return resp["run_id"]

    def poll_status(self, run_id: str) -> str:
        resp = self._request("GET", f"/{run_id}")
        return resp.get("status", "unknown")

    def fetch_result(self, run_id: str) -> dict:
        return self._request("GET", f"/{run_id}/result")

    def create_response(
        self,
        *,
        input_text: str,
        processor: str | None = None,
        poll_interval: int = 15,
        api_timeout: int = 3600,
        **_kwargs: Any,
    ) -> Dict[str, Any]:
        """Submit a task, block until complete, return normalized response dict.

        Returns:
          output_text – markdown research report with inline citations
          model       – processor used
        """
        eff_processor = processor or self.processor
        run_id = self.submit(input_text, eff_processor)

        deadline = time.time() + api_timeout
        while time.time() < deadline:
            status = self.poll_status(run_id)
            if status == "completed":
                break
            if status == "failed":
                raise RuntimeError(f"Task {run_id} failed")
            time.sleep(poll_interval)
        else:
            raise TimeoutError(f"Task {run_id} did not complete within {api_timeout}s")

        raw = self.fetch_result(run_id)
        output = raw.get("output", {})

        # In text-schema mode, content is a markdown string
        content = output.get("content", "")
        output_text = content if isinstance(content, str) else json.dumps(content, indent=2)

        return {
            "output_text": output_text,
            "model": eff_processor,
        }
