from typing import Callable
from typing import Optional

import string
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.progress import BarColumn
from rich.progress import TaskProgressColumn

from comp370.db import Client as Db
from comp370.db.models import Person
from comp370.db.models import Season
from comp370.db.models import Character
from comp370.db.models import Episode
from comp370.db.models import Line
from comp370.client.fandom import Client as Fandom
from comp370.client.fandom.models import Character as FCharacter
from comp370.client.imsdb import Client as Imsdb
from comp370.client.imsdb.models import Season as ISeason
from comp370.client.imsdb.models import Line as ILine
from .name import Resolver


class Seeder:
    def __init__(
        self,
        db: Db = Db(),
        fandom: Fandom = Fandom(),
        imsdb: Imsdb = Imsdb(),
        max_workers: int = 4,
    ):
        self.db = db
        self.fandom = fandom
        self.imsdb = imsdb
        self.max_workers = max_workers
        self.executor = None

    def __enter__(self):
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.executor:
            self.executor.shutdown(wait=True)
        return False

    def _pool(self) -> ThreadPoolExecutor:
        if not self.executor:
            raise RuntimeError("Seeder not initialized")
        return self.executor

    def get_character_paths(self, log: bool = True) -> list[str]:
        def go(tick: Optional[Callable] = None) -> list[str]:
            paths = set()
            letters = string.ascii_uppercase

            pool = self._pool()

            futures = [
                pool.submit(
                    self.fandom.characters().get_paths_by_letter,
                    letter,
                )
                for letter in letters
            ]

            for future in as_completed(futures):
                paths.update(future.result())
                if tick:
                    tick()

            return list(paths)

        if log:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
            ) as bar:
                task = bar.add_task("Characters...", total=len(string.ascii_uppercase))
                return go(tick=lambda: bar.update(task, advance=1))
        else:
            return go()

    def get_character_paths_popularity(
        self,
        paths: list[str],
        log: bool = True,
    ) -> dict[str, int]:
        def go(tick: Optional[Callable] = None) -> dict[str, int]:
            hits = defaultdict(int)

            pool = self._pool()
            futures = [
                pool.submit(
                    self.fandom.characters().get_out_paths,
                    path,
                )
                for path in paths
            ]

            for future in as_completed(futures):
                out = future.result()
                for path in out:
                    if path in paths:
                        hits[path] += 1
                if tick:
                    tick()

            total = sum(hits.values())
            share = [
                (path, hits[path] / total if path in hits else 0.0) for path in paths
            ]

            share.sort(key=lambda x: x[1], reverse=True)
            popularity = {}
            for i, (path, _) in enumerate(share):
                popularity[path] = i + 1

            return popularity

        if log:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
            ) as bar:
                task = bar.add_task("Character popularity...", total=len(paths))
                return go(tick=lambda: bar.update(task, advance=1))
        else:
            return go()

    def get_character_data(
        self, paths: list[str], log: bool = True
    ) -> list[FCharacter]:
        def go(tick: Optional[Callable] = None) -> list[FCharacter]:
            characters = []
            pool = self._pool()
            futures = [
                pool.submit(
                    self.fandom.characters().get,
                    path,
                )
                for path in paths
            ]

            for future in as_completed(futures):
                characters.append(future.result())
                if tick:
                    tick()

            return characters

        if log:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
            ) as bar:
                task = bar.add_task(
                    "Character data...",
                    total=len(paths),
                )
                return go(tick=lambda: bar.update(task, advance=1))
        else:
            return go()

    def get_seasons(self, log: bool = True) -> list[ISeason]:
        def go(tick: Optional[Callable] = None) -> list[ISeason]:
            seasons = self.imsdb.seasons().get()
            if tick:
                tick()

            return seasons

        if log:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
            ) as bar:
                task = bar.add_task(
                    "Seasons...",
                    total=1,
                )
                return go(tick=lambda: bar.update(task, advance=1))
        else:
            return go()

    def get_scripts(
        self,
        seasons: list[ISeason],
        log: bool = True,
    ) -> dict[tuple[int, int], list[ILine]]:
        def go(tick: Optional[Callable] = None) -> dict[tuple[int, int], list[ILine]]:
            scripts = {}

            def get(season, episode):
                return (season, episode, self.imsdb.episodes().get(episode.title))

            pool = self._pool()
            futures = [
                pool.submit(
                    get,
                    season,
                    episode,
                )
                for season in seasons
                for episode in season.episodes
            ]

            for future in as_completed(futures):
                season, episode, script = future.result()
                scripts[(season.number, episode.number)] = script
                if tick:
                    tick()

            return scripts

        if log:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
            ) as bar:
                total = int(sum([len(season.episodes) for season in seasons]))
                task = bar.add_task(
                    "Scripts...",
                    total=total,
                )
                return go(tick=lambda: bar.update(task, advance=1))
        else:
            return go()

    def write_writers(self, writers: list[str], log: bool = True) -> dict[str, Person]:
        def go(tick: Optional[Callable] = None) -> dict[str, Person]:
            people = {}

            with self.db.session() as db:
                for writer in writers:
                    if writer not in people:
                        person = Person(name=writer)
                        people[writer] = person
                        db.add(person)

                    if tick:
                        tick()

                db.commit()

            return people

        if log:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
            ) as bar:
                task = bar.add_task("Writers...", total=len(writers))
                return go(tick=lambda: bar.update(task, advance=1))
        else:
            return go()

    def write_actors(self, actors: list[str], log: bool = True) -> dict[str, Person]:
        def go(tick: Optional[Callable] = None) -> dict[str, Person]:
            people = {}

            with self.db.session() as db:
                for actor in actors:
                    if actor not in people:
                        person = Person(name=actor)
                        people[actor] = person
                        db.add(person)

                    if tick:
                        tick()

                db.commit()

            return people

        if log:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
            ) as bar:
                task = bar.add_task("Actors...", total=len(actors))
                return go(tick=lambda: bar.update(task, advance=1))
        else:
            return go()

    def write_seasons(
        self,
        seasons: list[ISeason],
        log: bool = True,
    ) -> dict[int, Season]:
        def go(tick: Optional[Callable] = None) -> dict[int, Season]:
            __seasons__ = {}

            with self.db.session() as db:
                for season in seasons:
                    if season.number not in __seasons__:
                        __season__ = Season(number=season.number)
                        __seasons__[season.number] = __season__
                        db.add(__season__)

                    if tick:
                        tick()

                db.commit()

            return __seasons__

        if log:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
            ) as bar:
                task = bar.add_task("Seasons...", total=len(seasons))
                return go(tick=lambda: bar.update(task, advance=1))
        else:
            return go()

    def write_characters(
        self,
        characters: list[FCharacter],
        popularity: dict[str, int],
        __actors__: dict[str, Person],
        log: bool = True,
    ) -> dict[str, Season]:
        def go(tick: Optional[Callable] = None) -> dict[str, Season]:
            __characters__ = {}

            with self.db.session() as db:
                for character in characters:
                    if character.name not in __characters__:
                        __character__ = Character(
                            name=character.name,
                            gender=character.gender,
                            occupation=character.occupation,
                            popularity=popularity[character.path],
                            actors=[
                                __actors__[actor] for actor in character.portrayed_by
                            ],
                        )
                        __characters__[character.name] = __character__
                        db.add(__character__)

                    if tick:
                        tick()

                db.commit()

            return __characters__

        if log:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
            ) as bar:
                task = bar.add_task("Characters...", total=len(characters))
                return go(tick=lambda: bar.update(task, advance=1))
        else:
            return go()

    def write_episodes(
        self,
        seasons: list[ISeason],
        characters: list[FCharacter],
        popularity: dict[str, int],
        scripts: dict[tuple[int, int], list[ILine]],
        __seasons__: dict[int, Season],
        __writers__: dict[str, Person],
        __actors__: dict[str, Person],
        __characters__: dict[str, Character],
        log: bool = True,
    ) -> dict[tuple[int, int], Episode]:
        def go(tick: Optional[Callable] = None) -> dict[tuple[int, int], Episode]:
            __episodes__ = {}
            resolver = Resolver(characters, popularity)

            with self.db.session() as db:
                for season in seasons:
                    for episode in season.episodes:
                        # Resolve characters
                        __cs__ = {}
                        for line in scripts[(season.number, episode.number)]:
                            result = resolver.resolve(line.character)
                            if result:
                                _, c = result
                                if c.name not in __cs__:
                                    __cs__[c.name] = __characters__[c.name]
                        # Resolve writers
                        __ws__ = [__writers__[writer] for writer in episode.writers]

                        __episode__ = Episode(
                            title=episode.title,
                            number=episode.number,
                            date=episode.date,
                            season=__seasons__[season.number],
                            writers=list(__ws__),
                            characters=list(__cs__.values()),
                        )
                        __episodes__[(season.number, episode.number)] = __episode__
                        db.add(__episode__)

                        if tick:
                            tick()

                db.commit()

            return __episodes__

        if log:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
            ) as bar:
                total = sum([len(season.episodes) for season in seasons])
                task = bar.add_task("Episodes...", total=total)
                return go(tick=lambda: bar.update(task, advance=1))
        else:
            return go()

    def write_lines(
        self,
        characters: list[FCharacter],
        popularity: dict[str, int],
        scripts: dict[tuple[int, int], list[ILine]],
        __characters__: dict[str, Character],
        __episodes__: dict[tuple[int, int], Episode],
        log: bool = True,
    ) -> dict[tuple[int, int, int, str], Line]:
        def go(
            tick: Optional[Callable] = None,
        ) -> dict[tuple[int, int, int, str], Line]:
            __lines__ = {}
            resolver = Resolver(characters, popularity)

            with self.db.session() as db:
                for (sn, en), lines in scripts.items():
                    __episode__ = __episodes__[(sn, en)]
                    for line in lines:
                        result = resolver.resolve(line.character)
                        if result:
                            _, c = result
                            __character__ = __characters__[c.name]

                            __line__ = Line(
                                number=line.number,
                                dialogue=line.dialogue,
                                character=__character__,
                                episode=__episode__,
                            )
                            __lines__[(sn, en, line.number, c.name)] = __line__
                            db.add(__line__)

                        if tick:
                            tick()

                db.commit()

            return __lines__

        if log:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
            ) as bar:
                total = sum([len(lines) for lines in scripts.values()])
                task = bar.add_task("Lines...", total=total)
                return go(tick=lambda: bar.update(task, advance=1))
        else:
            return go()
