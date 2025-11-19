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

REQUESTS_LOCK = threading.Lock()
REQUESTS_LAST = None
REQUESTS_DELAY = 1


def cache_key(request: PreparedRequest, **kwargs) -> str:
    key = sha256()

    key.update(str(request.method).encode())
    key.update(str(request.url).encode())

    digest = key.hexdigest()
    return digest


CACHE = CachedSession(
    cache_name=f"{DIR_CACHE}/requests.imsdb.com.db",
    expire_after=timedelta(days=30 if in_github_actions() else 1),
    backend="sqlite",
    key_fn=cache_key,
)


class Session:
    def __init__(
        self,
        base_url: str = BASE_URL,
        session: Session = CACHE,
    ):
        self.base_url = base_url
        self.session = session

    def _request(
        self,
        method: str,
        path: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> tuple[BeautifulSoup, bool]:
        global REQUESTS_LAST
        with REQUESTS_LOCK:
            if REQUESTS_LAST is not None:
                elapsed = time.time() - REQUESTS_LAST
                if elapsed < REQUESTS_DELAY:
                    time.sleep(REQUESTS_DELAY - elapsed)

            url = f"{self.base_url}/{path}"
            response = self.session.request(
                method,
                url,
                params=params,
                headers=headers,
                data=data,
            )

            # Only delay next request if this one was not cached
            if not response.from_cache:
                REQUESTS_LAST = time.time()

            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

        return soup, response.from_cache

    def get(self, path: str, **kwargs) -> tuple[BeautifulSoup, bool]:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> tuple[BeautifulSoup, bool]:
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> tuple[BeautifulSoup, bool]:
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> tuple[BeautifulSoup, bool]:
        return self._request("DELETE", path, **kwargs)
