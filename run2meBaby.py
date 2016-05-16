from os.path import abspath, dirname, join

from flask import flash, Flask, Markup, redirect, render_template, url_for, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from wtforms import fields, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField

_cwd = dirname(abspath(__file__))
SECRET_KEY = 'flask-session-insecure-secret-key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + join(_cwd, 'centralDatabase.db')
SQLALCHEMY_ECHO = True
WTF_CSRF_SECRET_KEY = 'this-should-be-more-random'


app = Flask(__name__)
app.config.from_object(__name__)

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




class GenForm(Form):
    sports = QuerySelectField(query_factory=Sport.query.all)
    teams = QuerySelectField(query_factory=Team.query.all)
    players = QuerySelectField(query_factory=Player.query.all)



class TeamForm(Form):
    team_name = fields.StringField('Team', validators=[validators.required()])
    add_sport = QuerySelectField(query_factory=Sport.query.all, get_label = 'sport_name')

class PlayerForm(Form):
    name = fields.StringField('Player', validators=[validators.required()])
    birthdate = fields.StringField('Birthdate', validators=[validators.required()])
    height = fields.StringField('Height in cm', validators=[validators.required()])
    weight = fields.StringField('Weight in kg',validators=[validators.required()])
    add_team = QuerySelectField(query_factory=Team.query.all, get_label = 'team_name')

class SportForm(Form):
    sport_name = fields.StringField('Sport', validators = [validators.required()])

@app.route("/")
def index():
    gen_form = GenForm()
    team_form = TeamForm()
    player_form = PlayerForm()
    sport_form = SportForm()
    return render_template("index.html",gen_form=gen_form, sport_form=sport_form,team_form=team_form,player_form=player_form)

@app.route("/sport", methods = ("POST", "GET"))
def add_sport():
    form = SportForm()
    if form.validate_on_submit():
        sport = Sport()
        form.populate_obj(sport)
        db.session.add(sport)
        db.session.commit()
        flash("New sport added")
        return redirect(url_for("index"))
    return render_template("errors.html", form = form)

@app.route("/team", methods = ("POST", "GET"))
def add_team():
    form = TeamForm()
    if form.validate_on_submit():
        team = Team()
        team.sport_id = form.add_sport.data.id
        db.session.add(team)
        form.populate_obj(team)
        db.session.commit()
        flash("Added team")
        return redirect(url_for("index"))
    return render_template("errors.html", form = form)


@app.route("/player", methods = ("POST", "GET"))
def add_player():
    form = PlayerForm()
    if form.validate_on_submit():
        player = Player()
        player.team_id = form.add_team.data.id
        db.session.add(player)
        form.populate_obj(player)
        db.session.commit()
        flash("Added player")
        return redirect(url_for("index"))
    return render_template("errors.html", form = form)


_LINK = Markup('<a href="{url}">{name}</a>')

@app.route("/viewData")
def view_sports():
    query = Sport.query.filter(Sport.id >=0)
    data = query_to_list(query)
    data = [next(data)] + [[_make_link2(cell) if i == 0 else cell for i, cell in enumerate(row)] for row in data]
    return render_template("data.html", data=data, type="Sports")

def _make_link2(id):
    url = url_for("view_teams", sport_id=id)
    return _LINK.format(url=url, name=id)

def query_to_list(query, include_field_names=True):
    column_names = []
    for i, obj in enumerate(query.all()):
        if i == 0:
            column_names = [c.name for c in obj.__table__.columns]
            if include_field_names:
                yield column_names
        yield obj_to_list(obj, column_names)

def obj_to_list(sa_obj, field_order): #returns a list of data from a SQL object
    return [getattr(sa_obj, field_name, None) for field_name in field_order]

@app.route("/viewTeams/<int:sport_id>")
def view_teams(sport_id):
    query = Team.query.filter(Team.sport_id == sport_id)
    data = query_to_list(query)
    data = [next(data)] + [[_make_link(cell) if i == 0 else cell for i, cell in enumerate(row)] for row in data]
    return render_template("data.html", data = data, type="Teams")

def _make_link(id):
    url = url_for("view_players", team_id = id)
    return _LINK.format(url=url, name=id)

@app.route("/viewPlayers/<int:team_id>")
def view_players(team_id):
    query = Player.query.filter(Player.team_id == team_id)
    data = query_to_list(query)
    data = [next(data)] + [[cell if i == 0 else cell for i, cell in enumerate(row)] for row in data]
    return render_template("data.html", data = data, type="Players")



if __name__ == "__main__":
    app.debug = True
    db.create_all()
    app.run()



