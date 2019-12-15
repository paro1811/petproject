from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_bootstrap import Bootstrap	

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'b81f5afa58ce4e7e95ee46461d97e0f3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/fc/desktop/isu/forum_isu/Database/site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
#login_manager.login_message_category = 'info'

from forum_isu import routes
