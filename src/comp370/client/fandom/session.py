from typing import Optional

import time
import threading
from hashlib import sha256
from datetime import timedelta
from requests import Session
from requests import PreparedRequest
from requests_cache import CachedSession
from bs4 import BeautifulSoup

from comp370.constants import DIR_CACHE
from comp370.utils import in_github_actions
from .constants import BASE_URL


def cache_key(request: PreparedRequest, **kwargs) -> str:
    key = sha256()

    key.update(str(request.method).encode())
    key.update(str(request.url).encode())

    digest = key.hexdigest()
    return digest


CACHE = CachedSession(
    cache_name=f"{DIR_CACHE}/requests.fandom.com.db",
    expire_after=timedelta(days=30 if in_github_actions() else 1),
    backend="sqlite",
    key_fn=cache_key,
)


class Session:
    def __init__(
        self,
        base_url: str = BASE_URL,
        session: Session = CACHE,
        rate: float = 0.25,
    ):
        self.base_url = base_url
        self.session = session
        self.rate = rate
        self.lock = threading.Lock()
        self.last = None

    def _request(
        self,
        method: str,
        path: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        retries: int = 5,
    ) -> tuple[BeautifulSoup, bool]:
        url = f"{self.base_url}/{path}"

        for attempt in range(retries):
            try:
                response = self.session.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                    data=data,
                )

                if not response.from_cache:
                    with self.lock:
                        if self.last is not None:
                            elapsed = time.time() - self.last
                            if elapsed < self.rate:
                                time.sleep(self.rate - elapsed)
                        self.last = time.time()

                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                return soup, response.from_cache
            except Exception:
                if attempt == retries - 1:
                    raise
                time.sleep(2**attempt)

        raise RuntimeError("Maximum retries exceeded")

    def get(self, path: str, **kwargs) -> tuple[BeautifulSoup, bool]:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> tuple[BeautifulSoup, bool]:
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> tuple[BeautifulSoup, bool]:
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> tuple[BeautifulSoup, bool]:
        return self._request("DELETE", path, **kwargs)
