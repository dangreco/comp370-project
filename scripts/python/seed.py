import os
import argparse

from comp370.seeder import Seeder
from comp370.client.fandom.models import Character as FCharacter
from comp370.client.imsdb.models import Season as ISeason
from comp370.client.imsdb.models import Line as ILine


def main():
    workers = os.cpu_count() or 4
    workers = min(workers, 8)
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--workers", type=int, default=workers)
    args = parser.parse_args()
    workers = args.workers

    print(f"(Using {workers} worker{'' if workers == 1 else 's'})")
    with Seeder(max_workers=workers) as seeder:
        print("== Scraping seinfeld.fandom.com")
        paths: list[str] = seeder.get_character_paths()
        characters: list[FCharacter] = seeder.get_character_data(paths)
        popularity: dict[str, int] = seeder.get_character_paths_popularity(paths)

        print("== Scraping imsdb.com")
        seasons: list[ISeason] = seeder.get_seasons()
        scripts: dict[tuple[int, int], list[ILine]] = seeder.get_scripts(seasons)

        print("== Organizing data")
        writers = set()
        for season in seasons:
            for episode in season.episodes:
                writers.update(episode.writers)

        actors = set()
        for character in characters:
            actors.update(character.portrayed_by)

        print("== Writing data to database")
        __seasons__ = seeder.write_seasons(seasons)
        __writers__ = seeder.write_writers(list(writers))
        __actors__ = seeder.write_actors(list(actors))
        __characters__ = seeder.write_characters(characters, popularity, __actors__)
        __episodes__ = seeder.write_episodes(
            seasons,
            characters,
            popularity,
            scripts,
            __seasons__,
            __writers__,
            __actors__,
            __characters__,
        )
        __lines__ = seeder.write_lines(
            characters,
            popularity,
            scripts,
            __characters__,
            __episodes__,
        )

        print("== Done!")
        print(f"Seasons: {len(__seasons__.keys())}")
        print(f"Writers: {len(__writers__.keys())}")
        print(f"Actors: {len(__actors__.keys())}")
        print(f"Characters: {len(__characters__.keys())}")
        print(f"Episodes: {len(__episodes__.keys())}")
        print(f"Lines: {len(__lines__.keys())}")


if __name__ == "__main__":
    main()
