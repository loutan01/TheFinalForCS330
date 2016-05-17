from flask import Flask


app = Flask(__name__)
#app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['WTF_CSRF_SECRET_KEY'] = 'this-should-be-more-random'
app.secret_key = '140735111582464'


from views import *
if __name__ == '__main__':
    app.debug = True
    app.run()
