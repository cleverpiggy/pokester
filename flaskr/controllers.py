import sys
from functools import wraps
from flask import request, jsonify, abort, render_template, redirect, url_for
from .models import Host, Game, Player, Registration, rollback, close_session
from .auth import requires_auth as req_auth
from .auth import requires_auth_dummy

PAGE_LENGTH = 10

def get_id(jwt_payload):
    id_ = jwt_payload.get('sub')
    #in case of testing without auth
    if id_ is None:
        id_ = request.args.get('user_id', type=str)
    return id_


def register_views(app):

    if app.config.get('TEST_WITHOUT_AUTH'):
        requires_auth = requires_auth_dummy
    else:
        requires_auth = req_auth

    @app.route('/home')
    def index():
        return render_template('index.html')

    @app.route('/games', methods=['GET'])
    def games():
        # Return a list of games paginated
        # @TODO Optional json filters
        # default sorted by start time and n players
        #     (but not full)

        # @TODO check out Model.paginate
        # print (request.__dict__)
        page = request.args.get('page', 1, type=int)
        page_length = request.args.get("page_length", PAGE_LENGTH, type=int)
        offset = (page - 1) * page_length
        # @TODO add order by number of players
        q = Game.query.order_by(Game.start_time)
        if offset > q.count():
            abort(404)
        games = q.limit(page_length).offset(offset)
        formatted_games = [g.format() for g in games]
        return jsonify({
            'success': True,
            'games': formatted_games
        })

    @app.route('/game/players<int:game_id>')
    def players(game_id):
        # return the players in a game
        if Game.query.get(game_id) is None:
            abort(404)
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
            'host already registered'
            abort(403)
        column_vals = {}
        for kword in ['name', 'email']:
            value = request.json.get(kword)
            if value is None:
                f'{kword} needed'
                abort(422)
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
            'Invalid data'
            abort(422)

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
            'must register first'
            abort(404)

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
            'Invalid data'
            abort(422)

        return jsonify({
            'success': True,
            'host': formatted_host
            })

    @app.route('/player/register', methods=['POST'])
    @requires_auth('join:game')
    def register_player(jwt_payload):
        player_id = get_id(jwt_payload)
        if Player.query.get(player_id):
            'player already registered'
            abort(403)
        column_vals = {}
        for kword in ['name', 'email']:
            value = request.json.get(kword)
            if value is None:
                f'{kword} needed'
                abort(422)
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
            'Invalid data'
            abort(422)

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
            'must register first'
            abort(404)

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
            'Invalid data'
            abort(422)

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
                f'{kword} needed'
                abort(422)
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
            'Invalid data'
            abort(422)

        return jsonify({
            'success': True,
            'game': column_vals
            })

    @app.route('/game/join/<int:game_id>', methods=['POST'])
    @requires_auth('join:game')
    def join_game(jwt_payload, game_id):
        # the user id has to be in the jwt_payload

        player_id = get_id(jwt_payload)

        game = Game.query.get(game_id)
        if game is None:
            abort(404)
        if game.num_registered >= game.max_players:
            'Game full'
            abort(422)
        if Registration.query.filter(
                Registration.game_id == game_id,
                Registration.player_id == player_id
                ).one_or_none():
            'Already registered'
            abort(422)
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
            abort(404)
        if game.host_id != host_id:
            abort(403)
        game.delete()

        return jsonify({
            'success': True,
            'game_id': game_id
            })

    @app.route('/game/edit<int:game_id>', methods=['PATCH'])
    @requires_auth('edit:game')
    def edit_game(jwt_payload, game_id):

        host_id = get_id(jwt_payload)

        game = Game.query.get(game_id)
        if game is None:
            abort(404)
        if game.host_id != host_id:
            abort(403)

        # for kword in ['start_time', 'max_players', 'platform']:
        #     val = request.json.get(kword)
        #     if val:
        #         setattr(game, kword, val)

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
            'Invalid data'
            abort(422)

        return jsonify({
            'success': True,
            'game': formatted_game
            })

    @app.route('/game/unregister<int:game_id>', methods=['DELETE'])
    @requires_auth('join:game')
    def unregister(jwt_payload, game_id):

        player_id = get_id(jwt_payload)

        reg = Registration.query.filter_by(game_id=game_id, player_id=player_id).one_or_none()
        if reg is None:
            abort(404)
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
