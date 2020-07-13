import os
import pytest
from datetime import datetime, timedelta
from flaskr import create_app
from flaskr.models import Host, Game, Player, Registration, db
from flaskr.auth import verify_decode_jwt
from helpers import TEST_DB_URL
import jwts

# From the test database
# Game
#  id | max_players | num_registered
# ----+-------------+----------------
#   4 |           2 |              0
#   5 |           6 |              0
#   6 |           9 |              0
#   7 |           2 |              0
#   8 |           6 |              0
#   9 |           9 |              0
#  10 |           2 |              0
#   1 |           2 |              2
#   2 |           6 |              5
#   3 |           9 |              8

@pytest.fixture(scope='module')
def client():
    app = create_app({'TESTING': True}, dburl=TEST_DB_URL)
    host_id = verify_decode_jwt(jwts.HOST)['sub']
    player_id = verify_decode_jwt(jwts.PLAYER)['sub']
    with app.app_context():
        client = app.test_client()
        client.host_id = host_id
        client.player_id = player_id
        return client


def headers(token=None, json=False):
    headers = {}
    if json:
        headers['Content-Type'] = 'application/json'
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers

def test_register_host(client):
    # Hosts can register as hosts
    url = '/host/register'
    json = {'name': 'host person', 'email': 'host@host.com'}

    response = client.post(url,
                           headers=headers(jwts.HOST, json=True),
                           json=json)
    assert response.status_code == 200

    response = client.post(url,
                           headers=headers(jwts.PLAYER, json=True),
                           json=json)
    assert response.status_code == 401

    response = client.post(url,
                           headers=headers(token=None, json=True),
                           json=json)
    assert response.status_code == 401

    response = client.post(url,
                           headers=headers(token=jwts.EXPIRED, json=True),
                           json=json)
    assert response.status_code == 401

def test_register_player(client):
    # Hosts and players can register as player
    url = '/player/register'
    json = {'name': 'Player Person', 'email': 'player@player.com'}


    response = client.post(url,
                           headers=headers(jwts.HOST, json=True),
                           json=json)
    assert response.status_code == 200

    response = client.post(url,
                           headers=headers(jwts.PLAYER, json=True),
                           json=json)
    assert response.status_code == 200

    response = client.post(url,
                           headers=headers(token=None, json=True),
                           json=json)
    assert response.status_code == 401

    response = client.post(url,
                           headers=headers(token=jwts.EXPIRED, json=True),
                           json=json)
    assert response.status_code == 401

def test_create_game(client):
    # Hosts can create games
    url = '/game/create'
    json = {'start_time':datetime.now() + timedelta(days=+3),
            'max_players': 6, 'platform': 'nice platform'}


    response = client.post(url,
                           headers=headers(jwts.HOST, json=True),
                           json=json)
    assert response.status_code == 200

    response = client.post(url,
                           headers=headers(jwts.PLAYER, json=True),
                           json=json)
    assert response.status_code == 401

    response = client.post(url,
                           headers=headers(token=None, json=True),
                           json=json)
    assert response.status_code == 401

    response = client.post(url,
                           headers=headers(token=jwts.EXPIRED, json=True),
                           json=json)
    assert response.status_code == 401


def test_join_game(client):
    # Hosts and Players can join games

    url = '/game{}/join'
    ids = [g.id for g in Game.query.filter_by(num_registered=0)]
    urls = (url.format(i) for i in ids)
    response = client.post(next(urls),
                           headers=headers(jwts.HOST))
    assert response.status_code == 200

    response = client.post(next(urls),
                           headers=headers(jwts.PLAYER))
    assert response.status_code == 200

    response = client.post(next(urls),
                           headers=headers(token=None))
    assert response.status_code == 401

    response = client.post(next(urls),
                           headers=headers(token=jwts.EXPIRED))
    assert response.status_code == 401


def test_delete_game(client):
    url = '/game999'
    # just testing that we get past authorization
    # but the game will always be unfound
    response = client.delete(url, headers=headers(jwts.HOST))
    assert response.status_code == 404

    response = client.delete(url, headers=headers(jwts.PLAYER))
    assert response.status_code == 401

    response = client.delete(url, headers=headers(jwts.EXPIRED))
    assert response.status_code == 401

    response = client.delete(url, headers=headers(token=None))
    assert response.status_code == 401

def test_edit_game(client):
    url = '/game999/edit'
    # just testing that we get past authorization
    # but the game will always be unfound
    response = client.patch(url, headers=headers(jwts.HOST))
    assert response.status_code == 404

    response = client.patch(url, headers=headers(jwts.PLAYER))
    assert response.status_code == 401

    response = client.patch(url, headers=headers(jwts.EXPIRED))
    assert response.status_code == 401

    response = client.patch(url, headers=headers(token=None))
    assert response.status_code == 401

def test_unregister_game(client):
    url = '/game999/unregister'
    # just testing that we get past authorization
    # but the game will always be unfound
    response = client.delete(url, headers=headers(jwts.HOST))
    assert response.status_code == 404

    response = client.delete(url, headers=headers(jwts.PLAYER))
    assert response.status_code == 404

    response = client.delete(url, headers=headers(jwts.EXPIRED))
    assert response.status_code == 401

    response = client.delete(url, headers=headers(token=None))
    assert response.status_code == 401
