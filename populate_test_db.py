import os
from sys import argv
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flaskr.models import Host, Game, Player, Registration


HOST_NAMES = [
    "Fred",
    "Mark",
    "Jones"
]

PLAYER_NAMES = [
    "Smith",
    "Edgar",
    "Sally",
    "Bridette",
    "Brandon",
    "Paul",
    "Peter",
    "Mary",
    "Francis",
    "Catherine",
    "Li",
    "Timmy",
    "Jesus",
    "Skylar",
    "Slartibartfast"
]


PLATFORMS = [
    "Cool Poker App",
    "Poker.com",
    "Raise'm'up",
    "iwinyoulose.com"
]


def do_it(db_url, ngames=10):
    engine = create_engine(db_url, echo=False)
    session = sessionmaker(bind=engine)()

    # get some fake auth0 ids ready
    ids = (f"auth0|{i}" for i in range(1000))
    # --------------------------------------------
    # add players and hosts
    players = [
        Player(id=next(ids), name=name, email=f"{name}@gmail.com")
        for name in PLAYER_NAMES
    ]

    hosts = [
        Host(id=next(ids), name=name, email=f"{name}@gmail.com")
        for name in HOST_NAMES
    ]

    session.add_all(players)
    session.add_all(hosts)
    # ---------------------------------------------

    # ---------------------------------------------
    # Add games, cycling through max players, hosts, platforms --
    # new game every 8 hours.
    now = datetime.now()
    delta = timedelta(hours=+8)
    maxes = [2, 6, 9]
    host_ids = session.query(Host.id).all()
    games = [
        Game(start_time=now + (delta * i),
             max_players=maxes[i % 3],
             platform=PLATFORMS[i % len(PLATFORMS)],
             host_id=host_ids[i % len(hosts)])
        for i in range(ngames)
    ]

    session.add_all(games)
    # ---------------------------------------------

    # ---------------------------------------------
    # Register players to games.
    # Do one full game then
    # continue registering max - 1 players to each game in
    # succession until we run out of players.
    player_ids = iter(session.query(Player.id).all())
    game_columns = session.query(Game).all()
    game = game_columns[0]
    registrations = [
        Registration(game_id=game.id, player_id=next(player_ids))
        for _ in range(game.max_players)
    ]
    game.num_registered = game.max_players
    session.add(game)
    session.add_all(registrations)
    for game in game_columns[1:]:
        try:
            registrations = [
                Registration(game_id=game.id, player_id=next(player_ids))
                for _ in range(game.max_players - 1)
            ]
        except StopIteration:
            break
        game.num_registered = game.max_players - 1
        session.add(game)
        session.add_all(registrations)
    # ----------------------------------------------
    session.commit()


def main():
    if len(argv) < 2:
        print ("Usage:  populate_test_db <database url>")
        return 1
    db_url = argv[1]
    do_it(db_url)
    return 0

if __name__ == '__main__':
    main()
