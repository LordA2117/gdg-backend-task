from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"

# Building and designing the database
# Sorry I didn't get enough time to change the SqlAlchemy settings to Postgres :(

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class=Base)

class User(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(db.String, nullable=False)
    password: Mapped[str] = mapped_column(db.String, nullable=False)
