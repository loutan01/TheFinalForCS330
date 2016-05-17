from flask import Flask
import os

app = Flask(__name__)
#app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['HEROKU_POSTGRESQL_WHITE_URL']
app.config['WTF_CSRF_SECRET_KEY'] = 'this-should-be-more-random'
app.secret_key = '140735111582464'


from views import *
if __name__ == '__main__':
    app.debug = True
    app.run()
