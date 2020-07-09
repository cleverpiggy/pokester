import os
from datetime import datetime, timedelta
from functools import wraps
import pytest
import populate_test_db
from flaskr import create_app
from flaskr.models import Host, Game, Player, Registration

# You do it like this
# response = client.post('/xyz', json={'foo'})
# response.status_code
# response.json

@pytest.fixture(scope='module')
def app():
    db_url = 'postgresql://cleverpiggy@localhost:5432/pokester_test_db'
    os.environ['DATABASE_URL'] = db_url
    os.system('dropdb pokester_test_db')
    os.system('createdb pokester_test_db')

    app = create_app('test_config_without_auth')
    populate_test_db.do_it(db_url)
    app.app_context().push()
    return app


@pytest.fixture(scope='module')
def client(app):
    return app.test_client()




def test_games(client):
    response = client.get('/games')
    assert response.status_code == 200
    assert len(response.json['games']) > 0

    response2 = client.get('/games?page_length=3')
    assert response2.status_code == 200
    assert len(response2.json['games']) == 3

    response3 = client.get('/games?page_length=3&page=2')
    assert response3.json['games'] != response2.json['games']


def test_players(client):
    game = Game.query.filter_by(num_registered=5).first()
    num_registered = game.num_registered
    game_id = game.id
    response = client.get(f'/game/players{game_id}')

    assert response.status_code == 200
    assert len(response.json['players']) == num_registered


def test_create_game(client, app):

    host = Host.query.first()
    url = f'/game/create?user_id={host.id}'

    # Success ----------------------------------------------------------
    # @TODO once i get jwts working i will get host id from there (i hope)
    json = {
        'start_time': datetime.now() + timedelta(days=+3),
        'max_players': 5,
        'platform': 'funky_test_platform'
    }

    # @TODO erase request args once i get jwts working
    response = client.post(url, json=json)
    assert response.status_code == 200

    #see if the new game is in the database
    game = Game.query.filter_by(platform='funky_test_platform').one_or_none()
    assert game


    # Failures -------------------------------------------------------
    # Fields missing
    json = {
        'max_players': 5,
        'platform': 'funky_test_platform'
    }
    response = client.post(url, json=json)
    assert response.status_code == 422

    # Wrong types
    json = {
        'start_time': 'pretty soon',
        'max_players': 5,
        'platform': 'funky_test_platform'
    }
    response = client.post(url, json=json)
    assert response.status_code == 422


def test_join_game(client):
    # @TODO once i get jwts working i will get user id from there (i hope)
    player_id = Player.query.first().id

    # Success ----------------------------------------------------------
    game = Game.query.filter_by(num_registered=0).first()
    assert game
    url = f'/game/join/{game.id}?user_id={player_id}'

    # Use these to check on the game after request.
    num_registered = game.num_registered
    game_id = game.id

    response = client.post(url)
    assert response.status_code == 200
    game = Game.query.get(game_id)
    assert game.num_registered == num_registered + 1
    reg = Registration.query.filter(
        Registration.game_id == game_id,
        Registration.player_id == player_id).one_or_none()
    assert reg

    # Failures -------------------------------------------------------
    # player already registered
    response = client.post(url)
    assert response.status_code == 422

    # game not found
    response = client.post(f'/game/join/9999?user_id={player_id}')
    assert response.status_code == 404

    # full game
    game = Game.query.filter(Game.max_players == Game.num_registered).\
                      join(Registration).\
                      filter(Registration.player_id != player_id).first()
    response = client.post(f'/game/join/{game.id}?user_id={player_id}')
    assert response.status_code == 422


def test_delete_game(client):
    # @TODO once i get jwts working i will get host id from there (i hope)
    host_id = Host.query.first().id

    # Success ----------------------------------------------------------
    game = Game.query.filter_by(num_registered=0, host_id=host_id).first()
    assert game
    game_id = game.id

    url = f'/game{game_id}?user_id={host_id}'
    response = client.delete(url)
    assert response.status_code == 200
    game = Game.query.get(game_id)
    assert game is None

    # Failures -------------------------------------------------------
    # host doesn't own game
    game = Game.query.filter(
        Game.num_registered == 0,
        Game.host_id != host_id).first()
    response = client.delete(f'/game{game.id}?user_id={host_id}')
    assert response.status_code == 403

def test_edit_game(client):
    # @TODO once i get jwts working i will get host id from there (i hope)
    host_id = Host.query.first().id

    # Success ----------------------------------------------------------
    game = Game.query.filter_by(host_id=host_id).first()
    game_id = game.id
    url = f'/game/edit{game_id}?user_id={host_id}'
    #throw out microseconds because client/jsonify automatically
    #curtails datetime for some reason
    new_time = game.start_time.replace(microsecond=0) + timedelta(days=+1)
    response = client.patch(url, json={'start_time': new_time})
    assert response.status_code == 200
    game = Game.query.get(game_id)
    assert game.start_time == new_time

    # Failures -------------------------------------------------------
    # host doesn't own game
    wrong_game = Game.query.filter(Game.host_id != host_id).first()
    wrong_url = f'/game/edit{wrong_game.id}?user_id={host_id}'
    response = client.patch(wrong_url, json={'start_time': new_time})
    assert response.status_code == 403

    # invalid data type
    response = client.patch(url, json={'start_time': 'pretty soon'})
    assert response.status_code == 422

def test_unregister(client):
    # @TODO once i get jwts working i will get user id from there (i hope)
    player_id = Player.query.first().id
    reg = Registration.query.filter(Registration.player_id == player_id).first()
    reg_id = reg.id
    game = Game.query.get(reg.game_id)
    game_id = game.id
    num_reged = game.num_registered

    url = f'/game/unregister{game_id}?user_id={player_id}'
    # Success ----------------------------------------------------------
    response = client.delete(url)

    assert response.status_code == 200
    assert Registration.query.get(reg_id) is None

    # Failures -------------------------------------------------------
    # Now that the registration is gone, try it again
    response = client.delete(url)
    assert response.status_code == 404
