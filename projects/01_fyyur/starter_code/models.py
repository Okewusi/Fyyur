from email.policy import default
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import ARRAY
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys

app = Flask(__name__)
#app.config.from_pyfile('config.py')
moment = Moment(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pelcool@localhost:5432/fyyur'
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)
app.secret_key = "testingthis"


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    date_created = db.Column(db.DateTime, default = datetime.now)
    shows_venue = db.relationship('Show', backref='venue', lazy=True)


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    date_created = db.Column(db.DateTime, default= datetime.now)
    shows_artist = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
 __tablename__ = 'shows'
 id= db.Column(db.Integer, primary_key=True)
 date= db.Column(db.DateTime, default= datetime.now, nullable =False)
 artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
 venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)

  