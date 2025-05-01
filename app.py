from flask import Flask, session, request, jsonify
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_migrate import Migrate
from hashlib import sha256
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_jwt_extended import JWTManager, get_jwt, get_jwt_identity, jwt_required, create_access_token
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'abc123')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config['FLASK_ADMIN_SWATCH'] = 'darkly'
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY', 'abc123')
# Building and designing the database
# Sorry I didn't get enough time to change the SqlAlchemy settings to Postgres :(
# print(app.config)

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(app, model_class=Base)
migrate = Migrate(app, db)
jwt = JWTManager(app)

class User(db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(db.String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(db.String, nullable=False)
    email: Mapped[str] = mapped_column(db.String, nullable=False, unique=True)

class Speaker(db.Model):
    __tablename__='speakers'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(db.String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(db.String, nullable=False)
    email: Mapped[str] = mapped_column(db.String, nullable=False)

with app.app_context():
    db.create_all()

# Add views to the admin panel
admin = Admin(app, name='Admin Page', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Speaker, db.session))

# Routes
@app.route('/')
def home():
    return jsonify({'message':'Navigate to /api/docs to get started'}),200

@app.route('/api/user/register', methods=['POST'])
def register_user():
    if request.is_json:
        data = request.get_json()
        data = dict(data)
        if 'username' not in data or 'password' not in data or 'email' not in data:
            return jsonify({'error':'Please specify the username, password and email in JSON'}), 400
        exists_username = db.session.query(db.session.query(User).filter_by(username=data['username']).exists()).scalar()
        exists_email = db.session.query(db.session.query(User).filter_by(email=data['email']).exists()).scalar()
        if exists_username or exists_email:
            return jsonify({'error': 'username or email already exists!!'}), 409
        user = User(username=data['username'], email=data['email'], password=sha256(data['password'].encode()).hexdigest())
        db.session.add(user)
        db.session.commit()
        return jsonify({'success':True}), 200
    else:
        return jsonify({"error":"Invalid content"}), 400

@app.route('/api/speaker/register', methods=['POST'])
def register_speaker():
    if request.is_json:
        data = request.get_json()
        data = dict(data)
        if 'username' not in data or 'password' not in data or 'email' not in data:
            return jsonify({'error':'Please specify the username, password, and email in JSON'}), 400
        exists_username = db.session.query(db.session.query(Speaker).filter_by(username=data['username']).exists()).scalar()
        exists_email = db.session.query(db.session.query(Speaker).filter_by(email=data['email']).exists()).scalar()
        if exists_username or exists_email:
            return jsonify({'error': 'username or email already exists!!'}), 409
        user = Speaker(username=data['username'], email=data['email'], password=sha256(data['password'].encode()).hexdigest())
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        return jsonify({"error":"Invalid content"}), 400


@app.route('/api/user/login', methods=['POST'])
def login_user():
    if request.is_json:
        data = dict(request.get_json())
        exists_username = db.session.query(db.session.query(User).filter_by(username=data['username']).exists()).scalar()
        exists_email = db.session.query(db.session.query(User).filter_by(email=data['email']).exists()).scalar()
        pass_hash = sha256(data['password'].encode()).hexdigest()
        if not exists_email or not exists_username:
            return jsonify({"error":"The given credentials don't exist"}), 401
        user = User.query.filter_by(username=data['username']).first()
        if user.password != pass_hash:
            return jsonify({"error": "Invalid username or password"}), 401
        additional_claims = {"role":"user"}
        access_token = create_access_token(identity=data['username'], additional_claims=additional_claims)
        return jsonify({"success":True, "access_token":access_token}), 200
    else:
        return jsonify({"error":"Invalid content"}), 400


@app.route('/api/speaker/login', methods=['POST'])
def login_speaker():
    if request.is_json:
        data = dict(request.get_json())
        exists_username = db.session.query(db.session.query(Speaker).filter_by(username=data['username']).exists()).scalar()
        exists_email = db.session.query(db.session.query(Speaker).filter_by(email=data['email']).exists()).scalar()
        pass_hash = sha256(data['password'].encode()).hexdigest()
        if not exists_email or not exists_username:
            return jsonify({"error":"The given credentials don't exist"}), 401
        speaker = Speaker.query.filter_by(username=data['username']).first()
        if speaker.password != pass_hash:
            return jsonify({"error": "Invalid username or password"}), 401
        additional_claims = {"role":"speaker"}
        access_token = create_access_token(identity=data['username'], additional_claims=additional_claims)
        return jsonify({"success":True, "access_token":access_token}), 200
    else:
        return jsonify({"error":"Invalid content"}), 400

# https://flask-jwt-extended.readthedocs.io/en/stable/add_custom_data_claims.html allows me to check the role and shi
@app.route('/api/user/profile')
@jwt_required()
def user_profile():
    user = get_jwt_identity()
    claims = get_jwt()
    if claims['role'] != 'user':
        return jsonify({'error': 'Not a user'}), 401
    user_profile = User.query.filter_by(username=user).first()
    return jsonify({'username': user_profile.username, 'email': user_profile.email}), 200

@app.route('/api/speaker/profile')
@jwt_required()
def speaker_profile():
    speaker = get_jwt_identity()
    speaker_profile = Speaker.query.filter_by(username=speaker).first()
    claims = get_jwt()
    if claims['role'] != 'speaker':
        return jsonify({'error': 'Not a speaker'}), 401
    return jsonify({'username': speaker_profile.username, 'email': speaker_profile.email}), 200

# Session Booking: Once a slot is booked, it can't be booked in by another user, schedule a calendar event or smth and send an email when the process is done
@app.route('/api/book_session')
def book_session():
    return

if __name__=="__main__":
    app.run(debug=True)

# TODO: Register the thingies into the db and add methods for login and delete. Also create flask session tokens on login to validate speakers and users and also add a rudimentary event booking system. Add OTP and other shit in the end

#TODO: Remove the admin panel during production (or add some sort of admin authentication)
