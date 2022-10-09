from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
db = SQLAlchemy()
login_manager = LoginManager()

# manager do usuario
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

# criacao da classe do usuário para cadastrar no postgresSQL
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    missing_people = db.relationship('MissingPeople', backref='user')
    profile_pic = db.relationship('Images', uselist=False)

    def verify_password(self, pwd):
        return bcrypt.check_password_hash(self.password_hash, pwd)

    def __repr__(self):
        return '<User %r>' % self.name

# criacao da classe pessoa desaparecida para inserir no banco de dados
class MissingPeople(db.Model):
    __tablename__ = "missing_people"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    birthday = db.Column(db.DateTime, nullable=False)
    birthplace = db.Column(db.String(50), nullable=False)
    place_of_disappearance = db.Column(db.String(100), nullable=True)
    disappearance_details = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pics = db.relationship('Images', backref='missing_person')

    def __repr__(self):
        return '<MissingPerson %r>' % self.name

# criacao da classe para cadastrar uma foto de um usuário no banco de dados
class Images(db.Model):
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    picture = db.Column(db.LargeBinary, unique=False, nullable=False)
    filename = db.Column(db.String(25), unique=False, nullable=False)
    mimetype = db.Column(db.String(15), unique=False, nullable=False)
    isUserProfile = db.Column(db.Boolean, nullable=False)
    isMissingPersonProfile = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    missing_person_id = db.Column(db.Integer, db.ForeignKey('missing_people.id'), nullable=True)

    def __repr__(self):
        return '<Image %r>' % self.id
