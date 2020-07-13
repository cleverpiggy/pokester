import sys
from functools import wraps
from flask import (request, jsonify, abort,
                   render_template, redirect, url_for)
from .models import Host, Game, Player, Registration, rollback, close_session
from .auth import requires_auth as req_auth
from .auth import requires_auth_dummy, AuthError

PAGE_LENGTH = 10



def register_views(app):

    testing_without_auth = app.config.get('TEST_WITHOUT_AUTH')
    if testing_without_auth:
        requires_auth = requires_auth_dummy
    else:
        requires_auth = req_auth

    def get_id(jwt_payload):
        id_ = jwt_payload.get('sub')
        #in case of testing without auth
        if id_ is None and testing_without_auth:
            id_ = request.args.get('user_id', type=str)
        return id_

    @app.route('/home')
    def index():
        return render_template('index.html')

    @app.route('/games', methods=['GET'])
    def games():
        # Return a list of games paginated
        # @TODO Optional json filters
        # default sorted by start time and n players

        # @TODO check out Model.paginate
        page = request.args.get('page', 1, type=int)
        page_length = request.args.get("page_length", PAGE_LENGTH, type=int)
        offset = (page - 1) * page_length
        # @TODO add order by number of players
        q = Game.query.order_by(Game.start_time)
        if offset > q.count():
            abort(404, description=f'Page number {page} is out of bounds')
        games = q.limit(page_length).offset(offset)
        formatted_games = [g.format() for g in games]
        return jsonify({
            'success': True,
            'games': formatted_games
        })

    @app.route('/game<int:game_id>/players')
    def players(game_id):
        # return the players in a game
        if Game.query.get(game_id) is None:
            abort(404, description=f'Game id {game_id} not found.')
        players = Player.query.\
                         join(Registration).\
                         filter(Registration.game_id==game_id)
        formatted_players = [p.format() for p in players]
        return jsonify({
            'success': True,
            'players': formatted_players
            })

    @app.route('/host/register', methods=['POST'])
    @requires_auth('create:game')
    def register_host(jwt_payload):
        host_id = get_id(jwt_payload)
        if Host.query.get(host_id):
            abort(403, description='Host already registered.')
        column_vals = {}
        for kword in ['name', 'email']:
            value = request.json.get(kword)
            if value is None:
                abort(422, description=f'{kword} required')
            column_vals[kword] = value

        error = False
        try:
            host = Host(id=host_id, **column_vals)
            host.add()
        except Exception:
            error = True
            rollback()
            print(sys.exc_info())
        finally:
            close_session()

        if error:
            # @TODO maybe that's the message.  check the exceptions
            abort(422, description='Invalid data')

        return jsonify({
            'success': True,
            'host': column_vals
            })

    @app.route('/host/edit', methods=['PATCH'])
    @requires_auth('create:game')
    def edit_host(jwt_payload):
        host_id = get_id(jwt_payload)
        host = Host.query.get(host_id)
        if host is None:
            abort(404, description='Host must register before creating a game.')

        updates = {k: request.json[k] for k in ['name', 'email'] if k in request.json}

        error = False
        try:
            host.update(updates)
            formatted_host = host.format()
        except Exception:
            error = True
            rollback()
            print(sys.exc_info())
        finally:
            close_session()

        if error:
            # @TODO maybe that's the message.  check the exceptions
            abort(422, description='Invalid data')

        return jsonify({
            'success': True,
            'host': formatted_host
            })

    @app.route('/player/register', methods=['POST'])
    @requires_auth('join:game')
    def register_player(jwt_payload):
        player_id = get_id(jwt_payload)
        if Player.query.get(player_id):
            abort(403, description='Player already registered')
        column_vals = {}
        for kword in ['name', 'email']:
            value = request.json.get(kword)
            if value is None:
                abort(422, description=f'{kword} required')
            column_vals[kword] = value

        error = False
        try:
            player = Player(id=player_id, **column_vals)
            player.add()
        except Exception:
            error = True
            rollback()
            print(sys.exc_info())
        finally:
            close_session()

        if error:
            # @TODO maybe that's the message.  check the exceptions
            abort(422, description='Invalid data')

        return jsonify({
            'success': True,
            'player': column_vals
            })

    @app.route('/player/edit', methods=['PATCH'])
    @requires_auth('join:game')
    def edit_player(jwt_payload):
        player_id = get_id(jwt_payload)
        player = Player.query.get(player_id)
        if player is None:
            abort(404, description='Player must register first.')

        updates = {k: request.json[k] for k in ['name', 'email'] if k in request.json}

        error = False
        try:
            player.update(updates)
            formatted_player = player.format()
        except Exception:
            error = True
            rollback()
            print(sys.exc_info())
        finally:
            close_session()

        if error:
            # @TODO maybe that's the message.  check the exceptions
            abort(422, description='Invalid data')

        return jsonify({
            'success': True,
            'player': formatted_player
            })

    @app.route('/game/create', methods=['POST'])
    @requires_auth('create:game')
    def create_game(jwt_payload):
        # requires json with all game attributes
        column_vals = {}
        for kword in ['start_time', 'max_players', 'platform']:
            value = request.json.get(kword)
            if value is None:
                abort(422, description=f'{kword} required')
            column_vals[kword] = value

        host_id = get_id(jwt_payload)

        error = False

        try:
            game = Game(host_id=host_id, **column_vals)
            game.add()
        except Exception:
            error = True
            rollback()
            print(sys.exc_info())
        finally:
            close_session()

        if error:
            # @TODO maybe that's the message.  check the exceptions
            abort(422, description='Invalid data')

        return jsonify({
            'success': True,
            'game': column_vals
            })

    @app.route('/game<int:game_id>/join', methods=['POST'])
    @requires_auth('join:game')
    def join_game(jwt_payload, game_id):
        # the user id has to be in the jwt_payload

        player_id = get_id(jwt_payload)

        game = Game.query.get(game_id)
        if game is None:
            abort(404, description=f"Game {game_id} not found.")
        if game.num_registered >= game.max_players:
            abort(422, description=f'Game {game_id} is full.')
        if Registration.query.filter(
                Registration.game_id == game_id,
                Registration.player_id == player_id
                ).one_or_none():
            abort(422, description=f"Player already registered for game {game_id}")
        game.num_registered += 1
        formatted_game = game.format()

        error = False
        try:
            reg = Registration(player_id=player_id, game_id=game_id)
            #this commits the game as well
            reg.add()
        except Exception:
            error = True
            rollback()
            print(sys.exc_info())
        finally:
            close_session()
        if error:
            # This might happen if player_id isn't a real player
            # or ???
            abort(422)

        return jsonify({
            'success': True,
            'game': formatted_game
            })

    @app.route('/game<int:game_id>', methods=['DELETE'])
    @requires_auth('delete:game')
    def delete_game(jwt_payload, game_id):

        host_id = get_id(jwt_payload)
        game = Game.query.get(game_id)
        if game is None:
            abort(404, description=f'Game {game_id} not found.')
        if game.host_id != host_id:
            abort(403, description="Cannot delete someone else's game")
        game.delete()

        return jsonify({
            'success': True,
            'game_id': game_id
            })

    @app.route('/game<int:game_id>/edit', methods=['PATCH'])
    @requires_auth('edit:game')
    def edit_game(jwt_payload, game_id):

        host_id = get_id(jwt_payload)

        game = Game.query.get(game_id)
        if game is None:
            abort(404, description=f'Game {game_id} not found.')
        if game.host_id != host_id:
            abort(403, description="Cannot edit someone else's game")

        updates = {k: request.json[k] for k in ['start_time', 'max_players', 'platform'] if k in request.json}

        error = False
        try:
            game.update(updates)
            # format may not work before commit because of string/datetime coersion
            formatted_game = game.format()
        except Exception:
            error = True
            rollback()
            print(sys.exc_info())
        finally:
            close_session()

        if error:
            # @TODO maybe that's the message.  check the exceptions
            abort(422, description='Invalid data')

        return jsonify({
            'success': True,
            'game': formatted_game
            })

    @app.route('/game<int:game_id>/unregister', methods=['DELETE'])
    @requires_auth('join:game')
    def unregister(jwt_payload, game_id):

        player_id = get_id(jwt_payload)

        reg = Registration.query.filter_by(game_id=game_id, player_id=player_id).one_or_none()
        if reg is None:
            abort(404, description=f'Player not registered for game {game_id}')
        game = Game.query.get(game_id)
        game.num_registered -= 1
        #this commits
        reg.delete()
        formatted_game = game.format()
        close_session()

        return jsonify({
            'success': True,
            'game': formatted_game
            })

    def error_handler(error):
        return jsonify({
            'success': False,
            'code': error.code,
            'description': error.description,
            'name': error.name
            }), error.code

    for code in (400, 403, 404, 422, 500, AuthError):
        app.register_error_handler(code, error_handler)
