from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"

# Building and designing the database

class Base(DeclarativeBase):
    pass
