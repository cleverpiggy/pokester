import sys
from functools import wraps
from flask import request, jsonify, abort
from .models import Host, Game, Player, Registration

PAGE_LENGTH = 10

# placeholder
# @TODO delete this
def requires_auth(auth):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            jwt = {}
            return f(jwt, *args, **kwargs)
        return wrapper
    return requires_auth_decorator


def register_views(app):

    @app.route('/games', methods=['GET'])
    def games():
        # Return a list of games paginated
        # @TODO Optional json filters
        # default sorted by start time and n players
        #     (but not full)

        # @TODO check out Model.paginate
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

    @app.route('/game/create', methods=['POST'])
    @requires_auth('create:game')
    def create_game(jwt):
        # requires json with all game attributes
        # the host id has to be in there somewhere as well
        # -- the jwt?

        column_vals = {}
        for kword in ['start_time', 'max_players', 'platform']:
            value = request.json.get(kword)
            if value is None:
                f'{kword} needed'
                abort(422)
            column_vals[kword] = value

        # @TODO update this once i get it working
        host_id = jwt.get('host_id')
        if host_id is None:
            host_id = int(request.args['host_id'])

        error = False
        try:
            game = Game(host_id=host_id, **column_vals)
            game.add()
        except Exception:
            error = True
            game.rollback()
            print(sys.exc_info())
        finally:
            game.close_session()

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
    def join_game(jwt, game_id):
        # the user id has to be in the jwt

        # @TODO update this once i get it working
        player_id = jwt.get('player_id')
        if player_id is None:
            # this is for testing @TODO write some kind of error
            player_id = int(request.args['player_id'])

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
            game.commit()
            reg.add()
        except Exception:
            error = True
            game.rollback()
            print(sys.exc_info())
        finally:
            reg.close_session()
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
    def delete_game(jwt, game_id):

        # @TODO update this once i get it working
        host_id = jwt.get('host_id')
        if host_id is None:
            host_id = int(request.args['host_id'])

        game = Game.query.get(game_id)
        if game.host_id != host_id:
            abort(403)
        game.delete()

        return jsonify({
            'success': True,
            'game_id': game_id
            })

    @app.route('/game/edit<int:game_id>', methods=['PATCH'])
    @requires_auth('edit:game')
    def edit_game(jwt, game_id):
        # @TODO update this once i get it working
        host_id = jwt.get('host_id')
        if host_id is None:
            host_id = int(request.args['host_id'])

        game = Game.query.get(game_id)
        if game.host_id != host_id:
            abort(403)

        for kword in ['start_time', 'max_players', 'platform']:
            val = request.json.get(kword)
            if val:
                setattr(game, kword, val)

        error = False
        try:
            game.commit()
            # format may not work before commit because of string/datetime coersion
            formatted_game = game.format()
        except Exception:
            error = True
            game.rollback()
            print(sys.exc_info())
        finally:
            game.close_session()

        if error:
            # @TODO maybe that's the message.  check the exceptions
            'Invalid data'
            abort(422)

        return jsonify({
            'success': True,
            'game': formatted_game
            })

    @app.route('/game/unregister<int:game_id>', methods=['DELETE'])
    @requires_auth('unregister:game')
    def unregister(jwt, game_id):
        # @TODO update this once i get it working
        player_id = jwt.get('player_id')
        if player_id is None:
            # this is for testing @TODO write some kind of error
            player_id = int(request.args['player_id'])


        reg = Registration.query.filter_by(game_id=game_id, player_id=player_id).one_or_none()
        if reg is None:
            abort(404)
        game = Game.query.get(game_id)
        game.num_registered -= 1
        game.commit()
        formatted_game = game.format()
        reg.delete()
        reg.close_session()

        return jsonify({
            'success': True,
            'game': formatted_game
            })
