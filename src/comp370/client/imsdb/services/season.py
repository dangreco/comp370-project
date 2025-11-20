import re
from datetime import datetime

from .__service__ import Service
from ..models import Season
from ..models import Episode


class SeasonService(Service):
    def get(self) -> list[Season]:
        soup, cached = self.session.get("/TV/Seinfeld.html")

        tables = soup.select("body > table")
        assert tables and len(tables) == 3, "Expected three tables on Seinfeld page"

        table = tables[1]
        seasons = []

        for h2 in table.find_all("h2"):
            match = re.match(r"^Series (\d+)$", h2.text.strip())
            if not match:
                continue

            number = int(match.group(1))
            episodes = []
            for el in h2.next_elements:
                if el.name == "h2":
                    break
                if el.name == "p":
                    match = re.match(
                        r"^(.+)\s*\((\d{4}-\d{2}-\d{2})\)\s*Written by\s*(.*)$",
                        el.text.strip(),
                    )
                    assert match, "Expected episode details"
                    title = match.group(1).strip()
                    date = datetime.strptime(match.group(2).strip(), "%Y-%m-%d").date()
                    writers = list(
                        filter(
                            lambda x: len(x),
                            map(lambda x: x.strip(), match.group(3).split(",")),
                        )
                    )
                    a = el.find("a")
                    assert a, "Expected an anchor tag"

                    episodes.append(
                        Episode(
                            number=len(episodes) + 1,
                            title=title,
                            date=date,
                            writers=writers,
                        )
                    )

            seasons.append(Season(number, episodes))

        return seasons
