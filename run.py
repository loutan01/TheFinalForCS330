from os.path import abspath, dirname, join

from flask import flash, Flask, Markup, redirect, render_template, url_for, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from wtforms import fields, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField
import random

#//\\//\\//\\//\\INIT//\\//\\//\\//\\

_cwd = dirname(abspath(__file__))

SECRET_KEY = 'flask-session-insecure-secret-key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + join(_cwd, 'contacts.db')
SQLALCHEMY_ECHO = True
WTF_CSRF_SECRET_KEY = 'this-should-be-more-random'


app = Flask(__name__)
app.config.from_object(__name__)

db = SQLAlchemy(app)

#//\\//\\//\\//\\Database Setup//\\//\\//\\//\\

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String)
    groups = db.relationship('Group', backref='users', lazy='select')

    def __repr__(self):
        return self.user_name
    def __str__(self):
        return self.user_name

class Contact(db.Model):
    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)
    phone = db.Column(db.String)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

    def __repr__(self):
        return '{0}, {1}, {2}'.format(name, address, phone)

class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    contact = db.relationship('Contact', backref='groups', lazy='select')

    def __repr__(self):
        return self.group_name
    def __str__(self):
        return self.group_name

#//\\//\\//\\//\\Forms//\\//\\//\\//\\

class GenForm(Form):
    user = QuerySelectField(query_factory=User.query.all)
    group = QuerySelectField(query_factory=Group.query.all)

    name = fields.StringField('Name', validators=[validators.required()])
    address = fields.StringField('Address', validators=[validators.required()])
    phone = fields.StringField('Phone', validators=[validators.required()])



#    caps = fields.BooleanField('Add Capital Letters')
#
#    swap = fields.BooleanField('Substitute: (3 == E...$ == S...etc)')

class UserForm(Form):
    user_name = fields.StringField()

class GroupForm(Form):
    group_name = fields.StringField()
    user = QuerySelectField(query_factory=User.query.all)

#//\\//\\//\\//\\Views//\\//\\//\\//\\

@app.route("/")
def index():
    user_form = UserForm()
    gen_form = GenForm()
    group_form = GroupForm()
    return render_template("index.html",
                           user_form=user_form,
                           gen_form=gen_form,
                           group_form=group_form)


@app.route("/user", methods=("POST", "GET"))
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        flash("Added user")
        return redirect(url_for("index"))
    return render_template("errors.html", form=form)


@app.route("/add", methods=("POST", "GET"))
def get_param():
    form = GenForm()
    if form.validate_on_submit():
        pw = Password()
        PW = make(form)
        pw.password = PW
        pw.user_id = form.user.data.id
        db.session.add(pw)
        db.session.commit()
        flash("Added password for " + form.user.data.user_name)
        return redirect(url_for("index"))
    return render_template("errors.html", form=form)

@app.route("/group", methods=("POST", "GET"))
def add_group():
    form = GroupForm()
    if form.validate_on_submit():
        group = Group()
        form.populate_obj(group)
        group.group_name = form.group_name.data
        db.session.add(group)
        db.session.commit()
        flash("Added " + form.group_name.data + " for " + form.user.data.user_name)
        return redirect(url_for("index"))
    return render_template("errors.html", form=form)

#//\\//\\//\\//\\Making the Contact//\\//\\//\\//\\

def make(form):
    minL = int(request.form['minL'])
    maxL = int(request.form['maxL'])
    totL = int(request.form['totL'])
    s = request.form['swap']
    c = request.form['caps']

    pw = ''
    tLen = 0

    for i in range(0,4):
        word, t = getWord(minL, maxL, totL, tLen, s, c)

        pw = word + ' ' + pw
        tLen = t

    return pw

def getWord(minL, maxL, totL, tLen, s, c): #  returns a word to be appended to a string held in the above function
                                     #  the word is pulled from a database, and checked that it meets the
                                     #  parameters.
    words = getDB()

    go = False

    while go is False:
        index = random.randint(0,5000)
        word = words[index]

        if len(word) <= maxL:
            if len(word) >= minL:
                aLen = tLen + len(word)
                if aLen < totL:
                    if request.form['swap'] == 'y':
                        if request.form['caps'] == 'y':
                            print('got caps + swap')
                            word = caps(word)
                            word = swap(word)
                            tLen += len(word)
                            go = True
                        else:
                            print('got swap')
                            word = swap(word)
                            tLen += len(word)
                            go = True
                    elif request.form['caps'] == 'y':
                        print('got caps')
                        word = caps(word)
                        tLen += len(word)
                        go = True
                    else:
                        tLen += len(word)
                        go = True
    return word, tLen

def swap(word):
    ol = ['A','I','E','O','L','S']
    sl = ['@','!','3','0','1','$']

    result = ''

    r = random.randint(0,4)

    slist = [ol[r],sl[r]]

    print(slist)

    for letter in word:
        LETTER = letter.upper()

        if LETTER == slist[0]:
            LETTER = slist[1]
            result += LETTER
        else:
            result += letter

    print(result)
    return result

def caps(word):
    result = ''
    for letter in word:
        r = random.randint(0,1)
        if r == 1:
            LETTER = letter.upper()
            result += LETTER
        else:
            result += letter
    print(result)
    return result



#//\\//\\//\\//\\Viewing the Users//\\//\\//\\//\\

@app.route("/users")
def view_users():  #shows all of the users in the db
    query = User.query.filter(User.id >= 0)
    data = query_to_list(query)
    data = [next(data)] + [[_make_link(cell) if i == 0 else cell for i, cell in enumerate(row)] for row in data]
    return render_template("contacts.html", data=data, type="Users")

#//\\//\\//\\//\\Links//\\//\\//\\//\\

#  This section simplifies making links across the environment
#  It allows me to have a standard way of making links
#  One function returns an object directing to the view page,
#  The other returns a page that just runs the script to remove the user key in the db
#  then redirects to the main page ("index").

_LINK = Markup('<a href="{url}">{name}</a>')


def _make_link(user_id):
    url = url_for("view_user_pw", user_id=user_id)
    return _LINK.format(url=url, name=user_id)

def _make_rm(user_id):
    url = url_for("rm_user", user_id=user_id)
    return _LINK.format(url=url, name=user_id)

#//\\//\\//\\//\\Viewing the Users Passwords//\\//\\//\\//\\

@app.route("/user/<int:user_id>")
def view_user_pw(user_id): #shows a list of the users passwords
    user = User.query.get_or_404(user_id)
    query = Password.query.filter(Password.user_id == user_id)
    data = query_to_list(query)
    title = "Passwords for " + user.user_name

    return render_template("contacts.html", data=data, type=title)

def query_to_list(query, include_field_names=True): #reads user information from the db
    column_names = []
    for i, obj in enumerate(query.all()):
        if i == 0:
            column_names = [c.name for c in obj.__table__.columns]
            if include_field_names:
                yield column_names
        yield obj_to_list(obj, column_names)


def obj_to_list(sa_obj, field_order): #returns a list of data from a SQL object
    return [getattr(sa_obj, field_name, None) for field_name in field_order]

#//\\//\\//\\//\\Removing a user//\\//\\//\\//\\

@app.route("/rm")
def rm(): #redirects to a page showing the active users
    query = User.query.filter(User.id >= 0)
    data = query_to_list(query)
    data = [next(data)] + [[_make_rm(cell) if i == 0 else cell for i, cell in enumerate(row)] for row in data]

    return render_template("rm_user.html", data=data, type="Users")

@app.route("/rm/<int:user_id>")
def rm_user(user_id): #a page just to run a script to remove the selected user from the db
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    flash(user.user_name + " deleted")

    return redirect(url_for("index"))


#//\\//\\//\\//\\RUN//\\//\\//\\//\\

if __name__ == "__main__":
    app.debug = True
    db.create_all()
    app.run()
