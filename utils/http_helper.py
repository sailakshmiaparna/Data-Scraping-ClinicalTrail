import requests
from typing import Any, Dict, Optional
import time


def http_post_json(url: str, json_body: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 30):
    for attempt in range(5):
        try:
            resp = requests.post(url, json=json_body, headers=headers or {}, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            wait = 2 ** attempt
            time.sleep(wait)
            last_err = e
    raise last_err


def http_get_json(url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, timeout: int = 30):
    for attempt in range(5):
        try:
            resp = requests.get(url, params=params or {}, headers=headers or {}, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            wait = 2 ** attempt
            time.sleep(wait)
            last_err = e
    raise last_err
