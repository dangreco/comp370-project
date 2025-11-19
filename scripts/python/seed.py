"""
Database seeding script for Seinfeld episode data.

This script scrapes all Seinfeld episodes from IMSDB and populates
the database with seasons, episodes, writers, characters, and dialogue lines.
"""

import tqdm
import time
from functools import reduce

from comp370.db import Client as Db
from comp370.db.models import (
    Season,
    Writer,
    Character,
    Episode,
    Line,
)
from comp370.scraper import Client as Scraper


def main():
    """
    Scrape Seinfeld data and populate the database.

    This function:
    1. Scrapes all seasons and episodes from IMSDB
    2. Extracts episode metadata, scripts, writers, and characters
    3. Writes all data to the SQLite database with proper relationships

    The script includes a small delay between requests to be respectful
    to the IMSDB server and uses caching to avoid redundant requests.
    """
    db = Db()
    scraper = Scraper()

    # ----------------------------------------
    # Scrape data
    # ----------------------------------------

    print("Scraping seasons...")
    seasons_ = scraper.get_seasons()

    print("Scraping episodes...")
    episodes_ = {}

    total = reduce(lambda acc, s: acc + len(s.episodes), seasons_, 0)
    pbar = tqdm.tqdm(total, unit=" episodes", ncols=100)

    for season in seasons_:
        for i, title in enumerate(season.episodes):
            episode = scraper.get_episode(title)
            script = scraper.get_script(title)
            episodes_[(season.number, i + 1)] = (episode, script)
            pbar.update(1)
            time.sleep(0.1)

    pbar.close()

    # Collect writers
    writers_ = set()
    for _, (episode, _) in episodes_.items():
        writers_.update(episode.writers)

    # Collect characters
    characters_ = set()
    for _, (_, script) in episodes_.items():
        for character, _ in script.lines:
            characters_.add(character)

    # ----------------------------------------
    # Write to database
    # ----------------------------------------

    with db.session() as session:
        # Seasons
        print("Writing seasons...")
        seasons = {s.number: Season(number=s.number) for s in seasons_}
        session.add_all(seasons.values())
        session.commit()

        # Writers
        print("Writing writers...")
        writers = {}
        for name in writers_:
            names = name.split()
            if len(names) == 2:
                first, last = names
                middle = None
            elif len(names) == 3:
                first, middle, last = names
            else:
                raise ValueError(f"Invalid writer name: {name}")
            writers[name] = Writer(first_name=first, middle_name=middle, last_name=last)

        session.add_all(writers.values())
        session.commit()

        # Characters
        print("Writing characters...")
        characters = {name: Character(name=name) for name in characters_}
        session.add_all(characters.values())
        session.commit()

        # Episodes
        print("Writing episodes...")
        episodes = {}

        for (sn, en), (episode, script) in episodes_.items():
            # Determine all characters that appear in the episode
            character_names = {c for (c, _) in script.lines}

            episodes[(sn, en)] = Episode(
                title=episode.title,
                number=en,
                air_date=episode.air_date,
                season=seasons[sn],
                writers=[writers[w] for w in episode.writers],
                characters=[characters[c] for c in character_names],
            )

        session.add_all(episodes.values())
        session.commit()

        # Lines
        print("Writing lines...")

        for (sn, en), (_, script) in episodes_.items():
            ep = episodes[(sn, en)]
            for i, (character, text) in enumerate(script.lines):
                session.add(
                    Line(
                        number=i + 1,
                        text=text,
                        episode=ep,
                        character=characters[character],
                    )
                )

        session.commit()

    print("Done!")


if __name__ == "__main__":
    main()
