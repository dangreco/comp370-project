import re
from collections import defaultdict

from .__service__ import Service
from ..models import Character

PRONOUNS = {
    "male": ["he", "him", "his"],
    "female": ["she", "her", "hers"],
    "non-binary": ["they", "them", "their"],
}

PRONOUNS_R = {}
for gender, pronouns in PRONOUNS.items():
    for pronoun in pronouns:
        PRONOUNS_R[pronoun] = gender


class CharacterService(Service):
    def get_paths_by_letter(self, letter: str) -> list[str]:
        """Get paths of character wiki pages starting with a given letter.

        Args:
            letter (str): The letter to filter characters by.

        Returns:
            list[str]: A list of paths to character wiki pages starting with the given letter.
        """
        assert letter.isalpha(), "Letter must be a single alphabetic character"
        letter = letter.upper()

        soup, cached = self.session.get(f"/wiki/Category:Characters?from={letter}")

        paths = set()
        for li in soup.find_all("li", class_="category-page__member"):
            a = li.find("a")
            if not a:
                continue

            href = a["href"]
            if href.startswith("/wiki/Category:"):
                continue

            paths.add(href)

        return list(paths)

    def get(self, path: str) -> Character:
        """Get the content of a character wiki page.

        Args:
            path (str): The path to the character wiki page.

        Returns:
            str: The content of the character wiki page.
        """
        soup, cached = self.session.get(path)

        # Parse data
        data = {}
        for label in soup.find_all("h3", class_="pi-data-label"):
            key = label.text.strip()
            value = label.find_next_sibling("div", class_="pi-data-value")
            data[key] = value

        # Name
        name = soup.find("h1", id="firstHeading").text.strip()

        # Episode
        match = re.search(r"(.+) \((.+)\)", name)
        if match:
            name = match.group(1)
            episode = match.group(2)
        else:
            episode = None

        # Gender
        gender = data.get("Gender", None)
        if gender:
            gender = gender.text.strip().lower()
        else:
            content = soup.find("div", id="mw-content-text")
            if content:
                words = map(lambda x: x.lower(), content.text.split())

                counts = defaultdict(int)
                for word in words:
                    gender_ = PRONOUNS_R.get(word, None)
                    if gender_:
                        counts[gender_] += 1

                if counts:
                    gender = max(counts, key=counts.get)
            gender = gender or "unknown"

        # Occupation
        occupation = data.get("Occupation", None)
        if occupation:
            occupation = occupation.text.strip().lower()
        else:
            occupation = "unknown"

        # Actors
        actors = data.get("Portrayed by", None)
        if actors:
            crawlable = actors.find_all("a")
            uncrawlable = actors.find_all("span")
            actors = [el.text.strip() for el in crawlable + uncrawlable]
        else:
            actors = []

        return Character(
            path=path,
            name=name,
            gender=gender,
            occupation=occupation,
            portrayed_by=actors,
            episode=episode,
        )
