from flask import Flask
from flask_migrate import Migrate
from app.model import tables
from app.model.tables import db, login_manager, bcrypt



app = Flask(__name__)

app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)
login_manager.init_app(app)
bcrypt.init_app(app)

login_manager.login_view = "login"
login_manager.login_message = "You need to be logged in to access this page"


from app.controller import routes





