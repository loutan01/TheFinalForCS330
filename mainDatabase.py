from flask.ext.sqlalchemy import SQLAlchemy
from run4meBaby import app
import sys
import io

db = SQLAlchemy(app)

class Sport(db.Model):
    __tablename__ = 'sports'

    id = db.Column(db.Integer, primary_key=True)
    sport_name = db.Column(db.Unicode)
    teams = db.relationship("Team", backref = "sports")



class Team(db.Model):

    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.Unicode)
    sport_id = db.Column(db.Integer, db.ForeignKey('sports.id'))
    players = db.relationship("Player", backref = "teams")


class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    birthdate = db.Column(db.Unicode)
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    
    