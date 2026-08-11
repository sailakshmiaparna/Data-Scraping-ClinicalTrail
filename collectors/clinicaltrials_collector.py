"""Raw ClinicalTrials.gov API collection only; no medical parsing or storage."""

import json
import time
from collections.abc import Iterator
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class ClinicalTrialsCollector:
    def __init__(self, config: dict[str, Any], logger, retries: int = 4, rate_limit_seconds: float = 0.15):
        self.api_base = config["source"].get("api_base", "https://clinicaltrials.gov/api/v2/studies")
        self.terms = config["search"].get("terms", [])
        self.page_size = min(int(config["search"].get("page_size", 100)), 1000)
        self.logger = logger
        self.retries = retries
        self.rate_limit_seconds = rate_limit_seconds

    def _request(self, params: dict[str, str]) -> dict[str, Any]:
        url = f"{self.api_base}?{urlencode(params)}"
        last_error: Exception | None = None
        for attempt in range(self.retries):
            try:
                request = Request(url, headers={"Accept": "application/json", "User-Agent": "MedicalKnowledgeAcquisitionAgent/1.0"})
                with urlopen(request, timeout=60) as response:
                    return json.loads(response.read().decode("utf-8"))
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
                last_error = error
                if isinstance(error, HTTPError) and 400 <= error.code < 500 and error.code != 429:
                    raise
                delay = 2**attempt
                self.logger.warning("ClinicalTrials.gov request failed (%s); retrying in %ss", error, delay)
                time.sleep(delay)
        raise RuntimeError("ClinicalTrials.gov request failed after retries") from last_error

    def search(self, page_token: str | None = None) -> dict[str, Any]:
        # The official v2 API accepts a free-text query.term expression.
        params = {"query.term": " OR ".join(f'"{term}"' for term in self.terms), "pageSize": str(self.page_size)}
        if page_token:
            params["pageToken"] = page_token
        response = self._request(params)
        time.sleep(self.rate_limit_seconds)
        return response

    def paginate(self, start_page_token: str | None = None) -> Iterator[tuple[list[dict[str, Any]], str | None]]:
        """Yield every page until the API no longer supplies nextPageToken."""
        token = start_page_token
        while True:
            response = self.search(token)
            yield response.get("studies", []), response.get("nextPageToken")
            token = response.get("nextPageToken")
            if not token:
                break

    def fetch(self, nct_id: str) -> dict[str, Any]:
        """Fetch one raw study record for targeted retries or future collectors."""
        original_base = self.api_base
        try:
            self.api_base = f"{original_base.rstrip('/')}/{nct_id}"
            return self._request({})
        finally:
            self.api_base = original_base
