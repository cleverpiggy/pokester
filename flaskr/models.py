from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (Column, String, Integer, DateTime,
                        CheckConstraint, ForeignKey)

db = SQLAlchemy()

def setup_db(app, database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # let's see if it works without this line
    db.app = app
    db.init_app(app)
    # this line will be used in case of a test db not set up in migrate
    db.create_all()


def commit():
    db.session.commit()

def rollback():
    db.session.rollback()

def close_session():
    db.session.close()


class BaseModel(db.Model):
    __abstract__ = True

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, mapping=None, **kwargs):
        if mapping is None:
            mapping = kwargs
        for k, v in mapping.items():
            setattr(self, k, v)
        db.session.commit()


class Host(BaseModel):
    __tablename__ = 'host'

    id = Column(String(40), primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)

    #without a host there is no game, thus 'delete-orphan'
    games = db.relationship('Game', backref='host', lazy=True,
                            cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Host {self.id} {self.name}>'


class Game(BaseModel):
    __tablename__ = 'game'
    __table_args__ = (CheckConstraint('num_registered<=max_players'),)

    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    max_players = Column(Integer,
                         CheckConstraint('max_players<10'),
                         CheckConstraint('max_players>1'),
                         nullable=False)
    num_registered = Column(Integer, default=0, nullable=False)
    platform = Column(String(50), nullable=False)
    host_id = Column(String, ForeignKey('host.id'), nullable=False)
    #when deleteing the game, we want all entries in the registry to delete
    registrations = db.relationship('Registration', backref='game', lazy=True,
                                    cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Game {self.id}>'

    def format(self):
        return {
            'id': self.id,
            'start_time': self.start_time.ctime(),
            'platform': self.platform,
            'max_players': self.max_players,
            'num_registered': self.num_registered,
            'host_id': self.host_id
        }

class Player(BaseModel):
    __tablename__ = 'player'

    id = Column(String, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    registrations = db.relationship('Registration', backref='player', lazy=True,
                                    cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Player {self.id} {self.name}>'

    def format(self):
        return {
            'name': self.name,
            'email': self.email,
            'id': self.id
        }


#wherein we have lists of players registered for various games
class Registration(BaseModel):
    __tablename__ = 'registration'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'), nullable=False)
    player_id = Column(String, ForeignKey('player.id'), nullable=False)

    def __repr__(self):
        return f'<Registry: game {self.game_id}, player {self.player_id}>'
