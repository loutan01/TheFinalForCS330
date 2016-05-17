from flask import Flask


app = Flask(__name__)
#app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://loutan01:Robbie911@localhost/database'

app.config['WTF_CSRF_SECRET_KEY'] = 'this-should-be-more-random'
app.secret_key = '140735111582464'


from views import *
if __name__ == '__main__':
    app.debug = True
    app.run()
    