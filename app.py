from flask import Flask, session, request, jsonify
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
# Building and designing the database
# Sorry I didn't get enough time to change the SqlAlchemy settings to Postgres :(

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class=Base)
migrate = Migrate(app, db)

class User(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(db.String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(db.String, nullable=False)
    email: Mapped[str] = mapped_column(db.String, nullable=False, unique=True)
    role: Mapped[str] = mapped_column(db.String, nullable=False, unique=True)

@app.route('/api/register', methods=['POST'])
def register():
    if request.is_json:
        data = request.get_json()
        data = dict(data)
        if 'username' not in data or 'password' not in data or 'email' not in data or 'role' not in data:
            return jsonify({'error':'Please specify the username,password,email and role in JSON'}), 400
        if data['role'].lower() not in ['speaker', 'user']:
            return jsonify({'error':'Role can only be speaker or user'}), 400
        return jsonify(data), 200
    else:
        return jsonify({"error":"Invalid content"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    return

# Speaker listing and expertise: Create a speaker table referring to the user id if it is speaker as a foreign key. Use this to gather their expertise and shit. Route is protected and only speakers can access it.
@app.route('/api/speaker_profile')
def speaker_profile():
    return

# Session Booking: Once a slot is booked, it can't be booked in by another user, schedule a calendar event or smth and send an email when the process is done
@app.route('/api/book_session')
def book_session():
    return

if __name__=="__main__":
    app.run(debug=True)

# TODO: Register the thingies into the db and add methods for login and delete. Also create flask session tokens on login to validate speakers and users and also add a rudimentary event booking system. Add OTP and other shit in the end
