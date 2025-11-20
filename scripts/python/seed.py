import tqdm
import string
import editdistance

from comp370.db import Client as Db
from comp370.db.models import (
    Season,
    Episode,
    Person,
    Character,
    Line,
)
from comp370.client.fandom import Client as Fandom
from comp370.client.imsdb import Client as Imsdb


def main():
    db = Db()
    fandom = Fandom()
    imsdb = Imsdb()

    # ----------------------------------------
    # Scrape data
    # ----------------------------------------

    print("======== SCRAPING ========")
    print("Scraping characters...")

    # Get character paths from Fandom
    paths = set()
    letters = string.ascii_uppercase
    for i in tqdm.tqdm(range(len(letters))):
        paths_ = fandom.characters().get_paths_by_letter(letters[i])
        paths.update(paths_)
    paths = list(paths)

    # Get character data from Fandom
    characters = {}
    for i in tqdm.tqdm(range(len(paths))):
        path = paths[i]
        character = fandom.characters().get(path)
        characters[(character.name, character.episode)] = character

    # Get lines
    seasons = imsdb.seasons().get()  # [ season1, season2, ... ]
    episodes = {}  # { (s.number, e.number) : e, ... }
    lines = {}  # { (s.number, e.number, l.number, c.name) : l, ... }

    # Scrape lines
    for season in seasons:
        print(f"Scraping season {season.number}...")
        for i in tqdm.tqdm(range(len(season.episodes))):
            episode = season.episodes[i]
            episodes[(season.number, episode.number)] = episode
            for line in imsdb.episodes().get(episode.title):
                lines[(season.number, episode.number, line.number, line.character)] = (
                    line
                )

    print("Resolving character names...")
    resolved = {}  # { (name, episode title) : canonical name }

    def resolve(sn: int, en: int, name: str):
        COMMON = {
            "jerry": "Jerry Seinfeld",
            "george": "George Costanza",
            "elaine": "Elaine Benes",
            "kramer": "Cosmo Kramer",
            "newman": "Newman",
            "ruthie": "Ruthie Cohen",
            "morty": "Morty Seinfeld",
            "helen": "Helen Seinfeld",
            "frank": "Frank Costanza",
            "estelle": "Estelle Costanza",
            "leo": "Uncle Leo",
            "babs": "Babs Kramer",
            "david": "David Puddy",
            "puddy": "David Puddy",
            "tim": "Tim Whatley",
            "kenny": "Kenny Bania",
            "lloyd": "Lloyd Braun",
            "jackie": "Jackie Chiles",
            "jacopo": "Jacopo Peterman",
            "justin": "Justin Pitt",
            "robin": "Robin",
            "babu": "Babu Bhatt",
            "soup nazi": "Yev Kassem",
        }
        ln = name.lower()
        episode_title = episodes[(sn, en)].title.lower()
        if ln in COMMON:
            resolved[(sn, en, name)] = COMMON[ln]
            return
        else:
            possible = []
            for c, e in characters.keys():
                if e and not e.lower() == episode_title.lower():
                    continue
                parts = c.lower().split()
                for p in parts:
                    distance = editdistance.eval(ln, p)
                    if distance < 3:
                        possible.append((c, distance))

            if possible:
                best = min(possible, key=lambda x: x[1])
                resolved[(sn, en, name)] = best[0]
                return

    for (sn, en, _, c), line in lines.items():
        resolve(sn, en, c)

    # Collect writers
    print("Resolving writers...")
    writers = set()
    for episode in episodes.values():
        writers.update(episode.writers)

    # Collect actors
    print("Resolving actors...")
    actors = set()
    for character in characters.values():
        actors.update(character.portrayed_by)

    # ----------------------------------------
    # Write to database
    # ----------------------------------------

    print("======== WRITING ========")
    with db.session() as session:
        pass

        # People
        print("Writing people...")
        people__ = {}

        for writer in writers:
            if writer not in people__:
                person = Person(name=writer)
                people__[writer] = person
                session.add(person)

        for actor in actors:
            if actor not in people__:
                person = Person(name=actor)
                people__[actor] = person
                session.add(person)

        session.commit()

        # Seasons
        print("Writing seasons...")
        seasons__ = {}
        for season in seasons:
            if season.number not in seasons__:
                __season__ = Season(number=season.number)
                seasons__[season.number] = __season__
                session.add(__season__)

        session.commit()

        # Characters
        print("Writing characters...")
        characters__ = {}
        for character in characters.values():
            if character.name not in characters__:
                __actors__ = [people__[actor] for actor in character.portrayed_by]
                __character__ = Character(
                    name=character.name,
                    gender=character.gender,
                    occupation=character.occupation,
                    actors=__actors__,
                )

                characters__[character.name] = __character__
                session.add(__character__)

        session.commit()

        # Episodes
        print("Writing episodes...")
        episodes__ = {}
        for (sn, en), episode in episodes.items():
            __characters__ = []
            for sn_, en_, _, c in lines.keys():
                if sn_ == sn and en_ == en:
                    if (sn_, en_, c) in resolved:
                        __characters__.append(characters__[resolved[(sn_, en_, c)]])

            __writers__ = [people__[w] for w in episode.writers]

            __episode__ = Episode(
                title=episode.title,
                number=episode.number,
                date=episode.date,
                season=seasons__[sn],
                writers=__writers__,
                characters=__characters__,
            )
            episodes__[(sn, en)] = __episode__
            session.add(__episode__)

        session.commit()

        # Lines
        print("Writing lines...")
        for (sn, en, ln, c), line in lines.items():
            if (sn, en, c) in resolved:
                __episode__ = episodes__[(sn, en)]
                __character__ = characters__[resolved[(sn, en, c)]]

                __line__ = Line(
                    number=line.number,
                    dialogue=line.dialogue,
                    episode=__episode__,
                    character=__character__,
                )
                session.add(__line__)

        session.commit()

    print("Done!")


if __name__ == "__main__":
    main()
