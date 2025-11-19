"""
Client for scraping Seinfeld data from the Internet Movie Script Database.

This module provides a Client class that handles HTTP requests with caching
and parses HTML to extract structured episode and script data.
"""

import re
from datetime import datetime
from requests import Session
from requests_cache import CachedSession
from bs4 import BeautifulSoup
from typing import Optional

from comp370.constants import DIR_DATA
from .constants import IMSDB_BASE_URL
from .models import Season, Episode, Script
from .utils import clean, is_character


class Client:
    """
    A client for scraping Seinfeld episode data from IMSDB.

    This client uses HTTP caching to minimize requests and provides methods
    to extract season information, episode metadata, and full scripts.

    Attributes:
        session: HTTP session with caching enabled
        base_url: Base URL for IMSDB website
    """

    session: Session
    base_url: str

    def __init__(
        self,
        session: Optional[Session] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the IMSDB scraper client.

        Args:
            session: Optional custom HTTP session. If not provided, creates
                    a cached session with 1-hour expiration
            base_url: Optional base URL for IMSDB. Defaults to https://imsdb.com
        """
        if session is None:
            session = CachedSession(DIR_DATA / "requests.db", expire_after=3600)
            session.headers.update({"User-Agent": "comp370-project/0.1"})

        self.session = session
        self.base_url = base_url or IMSDB_BASE_URL

    def get_seasons(self) -> list[Season]:
        """
        Scrape and return all Seinfeld seasons with episode titles.

        Returns:
            List of Season objects, each containing the season number
            and list of episode titles

        Raises:
            requests.HTTPError: If the HTTP request fails
            AssertionError: If expected HTML elements are not found
        """

        url = f"{self.base_url}/TV/Seinfeld.html"
        response = self.session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Get containing table
        table = soup.select_one("body > table:not(.body)")
        assert table is not None, "Table not found"

        # Get containing td
        td = next(
            filter(
                lambda x: "Seinfeld Transcripts" in x.text,
                table.findAll("td"),
            )
        )
        assert td is not None, "td not found"

        # Iterate over children of td
        number = 0
        seasons: list[Season] = []
        episodes: list[str] = []
        for child in td.descendants:
            if child.name == "h2":
                match = re.match(r"^Series (\d+)$", child.text.strip())
                if not match:
                    continue

                seasons.append(Season(number, episodes))
                episodes = []
                number = int(match.group(1))

            if child.name == "a" and child["href"].startswith("/TV Transcripts"):
                title = child.text.strip()
                episodes.append(title)

        if episodes:
            seasons.append(Season(number, episodes))

        seasons = list(filter(lambda x: len(x.episodes), seasons))
        return seasons

    def get_episode(self, title: str) -> Episode:
        """
        Scrape and return metadata for a specific episode.

        Args:
            title: The episode title (e.g., "The Pilot")

        Returns:
            Episode object containing title, writers, and air date

        Raises:
            requests.HTTPError: If the HTTP request fails
            AssertionError: If expected HTML elements are not found
        """

        url = f"{self.base_url}/TV Transcripts/Seinfeld - {title} Script.html"
        response = self.session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Get writers
        writers = filter(
            lambda x: x.get("href", "").startswith("/writer.php?"),
            soup.findAll("a"),
        )
        writers = list(
            sorted(
                filter(
                    lambda x: len(x),
                    map(
                        lambda x: x.text.strip(),
                        writers,
                    ),
                )
            )
        )

        # Get air date
        b = next(
            filter(
                lambda x: x.text.strip() == "Episode Air Date",
                soup.findAll("b"),
            )
        )
        match = re.search("[A-Za-z]+ \d{2}, \d{4}", b.next_sibling.text.strip())
        assert match, f"Failed to find air date for episode {title}"
        air_date = datetime.strptime(match.group(), "%B %d, %Y").date()

        return Episode(title, writers, air_date)

    def get_script(self, title: str) -> Script:
        """
        Scrape and parse the full script for an episode.

        Args:
            title: The episode title (e.g., "The Pilot")

        Returns:
            Script object containing list of (character, line) tuples

        Raises:
            requests.HTTPError: If the HTTP request fails
        """

        url = f"{self.base_url}/transcripts/Seinfeld-{title.replace(' ', '-')}.html"
        response = self.session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        pre = soup.find("pre")
        bs = pre.findAll("b")

        lines = []
        for b in bs:
            if is_character(title, b):
                character = b.text.strip()
                line = []

                current = b.next_sibling
                while current and not is_character(title, current):
                    line.append(current.text.strip())
                    current = current.next_sibling

                line = [text for text in line if text and not text == "THE END"]
                line = "".join(line)
                line = clean(line)
                lines.append((character, line))

        return Script(lines)
