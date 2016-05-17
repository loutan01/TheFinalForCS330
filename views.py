import sys
import io
from run4meBaby import *
from database import db, Sport, Team, Player
from os.path import abspath, dirname, join
from flask import flash, Flask, Markup, redirect, render_template, url_for, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from wtforms import fields, validators
import requests
import random
import json
import httplib2
from wtforms.ext.sqlalchemy.fields import QuerySelectField




class GenForm(Form):
    sports = QuerySelectField(query_factory = Sport.query.all)
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



@app.route("/randomPlayer", methods = ("POST", "GET"))
def add_random_player():
    form = PlayerForm()
    helloJson = request()
    player = Player()
    player.name = helloJson['name']
    player.birthdate = helloJson['birth_data']
    player.height = helloJson['height']
    player.weight = helloJson['weight'] 
    becauseDebugging = random.randint(1,Team.query.count())
    player.team_id = becauseDebugging
    db.session.add(player)
    db.session.commit()
    flash("Random player " + player.name + " was born on " + player.birthdate )
    return redirect(url_for("index"))


def request():
    uri = 'http://api.namefake.com/'
    try:
        uResponse = requests.get(uri)
    except requests.ConnectionError:
        return "Error!"
    Jresponse = uResponse.text
    data = json.loads(Jresponse)        
    return data


_LINK = Markup('<a href="{url}">{name}</a>')

@app.route("/viewData")
def view_sports():
    query = Sport.query.filter(Sport.id >=0)
    data = query_to_list(query)
    data = [next(data)] + [[makeLink2(cell) if i == 0 else cell for i, cell in enumerate(row)] for row in data]
    return render_template("data.html", data=data, type="Sports")

def makeLink2(id):
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
    data = [next(data)] + [[makeLink(cell) if i == 0 else cell for i, cell in enumerate(row)] for row in data]
    return render_template("data.html", data = data, type="Teams")

def makeLink(id):
    url = url_for("view_players", team_id = id)
    return _LINK.format(url=url, name=id)

@app.route("/viewPlayers/<int:team_id>")
def view_players(team_id):
    query = Player.query.filter(Player.team_id == team_id)
    data = query_to_list(query)
    data = [next(data)] + [[makeLink3(cell) if i == 0 else cell for i, cell in enumerate(row)] for row in data]
    return render_template("data.html", data = data, type="Players")

def makeLink3(id):
    url = url_for("remove_player", player_id = id)
    return _LINK.format(url=url, name=id)

@app.route("/removePlayer/<int:player_id>")
def remove_player(player_id):
    player = Player.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    flash(player.name +  " deleted!")
    return redirect(url_for("index"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.errorhandler(StopIteration)
def emptyDatabase(error):
    return render_template("errors.html", form = PlayerForm())