#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

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
from models import db, Venue, Artist, Show

import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
#app.config.from_pyfile('config.py')
db.init_app(app)
moment = Moment(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pelcool@localhost:5432/fyyur'
app.config.from_object('config')

#db = SQLAlchemy(app)
migrate = Migrate(app,db)
app.secret_key = "testingthis"
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  all_venues = db.session.query(Venue).all()
  distinct_states = db.session.query(Venue.city, Venue.state).distinct()
  return render_template('pages/venues.html', all_venues=all_venues, distinct_states=distinct_states)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  response = {}
  # search for venues that contain the search criteria
  venuesMatch = list(Venue.query.filter(
    Venue.name.ilike(f"%{search_term}%")
  ).all())

  response["count"] = len(venuesMatch)
  response["data"] = []

  for venue in venuesMatch:
    val = {
      "id" : venue.id,
      "name" : venue.name
    }
    response["data"].append(val)
  
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

#specific details of venues
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  result = Venue.query.get(venue_id)
  upcoming_venue_shows_info = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.date>= datetime.now()).all()
  upcoming_shows = []
  for show in upcoming_venue_shows_info:
      val = {
      'start_time' : show.date.strftime('%Y-%m-%d %H:%M:%S'),
      "artist_name" : show.artist.name,
      "artist_image_link" : show.artist.image_link,
      "artist_id":show.artist_id
    }
      upcoming_shows.append(val)
  
  upcoming_shows_count = len(upcoming_shows)


  
  past_venue_shows_info = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.date < datetime.now()).all()
  past_shows = []
  for show in past_venue_shows_info:
      val = {
      'start_time' : show.date.strftime('%Y-%m-%d %H:%M:%S'),
      "artist_name" : show.artist.name,
      "artist_image_link" : show.artist.image_link,
      "artist_id":show.artist_id
    }
      past_shows.append(val)

  past_shows_count = len(past_shows)
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=result ,
  upcoming_shows=upcoming_shows, upcoming_shows_count=upcoming_shows_count, 
  past_shows=past_shows, past_shows_count=past_shows_count)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  form = VenueForm(request.form)
  error = False
  if form.validate():
    try:
      newVenue = Venue(
        name= form.name.data,
        city=form.city.data,
        state=form.state.data,
        address= form.address.data,
        phone = form.phone.data,
        genres = form.genres.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        website = form.website_link.data,
        seeking_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data
      )
      db.session.add(newVenue)
      db.session.commit()
      flash('Venue was successfully listed!')
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue could not be listed.')
    finally:
      db.session.close()
    if(error):
      abort(500)
    else:
      return render_template('pages/home.html')
  else:
    print(form.errors)
    flash("Venue could not be added")
    return render_template('pages/home.html')
    



  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

#delete venue
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash("Venue was not sucessfully deleted")
  except:
    error= True
    db.session.rollback()
    flash("Venue could not be sucessfully deleted")
  finally:
    db.session.close()
  return redirect(url_for('index'))
    
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  all_artists = db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=all_artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  response = {}
  # search for venues that contain the search criteria
  artistMatch = list(Artist.query.filter(
    Artist.name.ilike(f"%{search_term}%")
  ).all())

  response["count"] = len(artistMatch)
  response["data"] = []

  for artist in artistMatch:
    val = {
      "id" : artist.id,
      "name" : artist.name
    }
    response["data"].append(val)

  
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

#detailed artist venue
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  upcoming_artist_shows_info = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.date>=datetime.now()).all()
  upcoming_shows = []
  for show in upcoming_artist_shows_info:
      val={
        'venue_id': show.venue_id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.date.strftime('%Y-%m-%d %H:%M:%S')
    }
      upcoming_shows.append(val)

  upcoming_shows_count = len(upcoming_shows)
  past_artist_shows_info = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.date<datetime.now()).all()
  past_shows = []
  for show in past_artist_shows_info:
      val={
        'venue_id': show.venue_id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.date.strftime('%Y-%m-%d %H:%M:%S')
    }
      past_shows.append(val)
  
  past_shows_count = len(past_shows)
  return render_template('pages/show_artist.html', artist=artist,
  upcoming_shows=upcoming_shows, upcoming_shows_count=upcoming_shows_count, 
  past_shows=past_shows, past_shows_count=past_shows_count)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

#update artist
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  error = False
  if form.validate():
    try:
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres = form.genres.data
      artist.image_link = form.image_link.data
      artist.facebook_link = form.facebook_link.data
      artist.website = form.website_link.data
      artist.venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data

      db.session.add(artist)
      db.session.commit()
      flash('artist successfully updated!')
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('Unable to edit artist')
    finally:
      db.session.close()
    if(error):
      abort(500)
    else:
      return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    print(form.errors)
    flash('Unable to edit artist')

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueForm(request.form)
  venue = Venue.query.get(venue_id)
  error = False
  if form.validate():
    try:
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.address = form.address.data
      venue.phone = form.phone.data
      venue.genres = form.genres.data
      venue.image_link = form.image_link.data
      venue.facebook_link = form.facebook_link.data
      venue.website = form.website_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data

      db.session.add(venue)
      db.session.commit()
      flash('venue updated succesfully')
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('Unable to edit venue')
    finally:
      db.session.close()
    if(error):
      abort(500)
    else:
      return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    print(form.errors)
    flash('unable to edit venue')




#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  error = False
  if form.validate():
    try:
      newArtist = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        genres = form.genres.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        website = form.website_link.data,
        venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data
      )
      db.session.add(newArtist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      error = True
      db.session.rollback()
      flash('An error occured ' + request.form['name'] + ' could not be added!')
    finally:
      db.session.close()
      if(error):
        abort(500)
      else:
        return render_template('pages/home.html')
  else:
    print(form.errors)
    flash("Arist could not be added!")
  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  all_shows = Show.query.all()
  data= []
  for show in all_shows:
    val = {}
    val["venue_id"]= show.venue.id
    val["venue_name"] = show.venue.name
    val["artist_id"] = show.artist.id
    val["artist_name"] = show.artist.name
    val["artist_image_link"] = show.artist.image_link
    val["start_time"] = show.date.strftime("%m/%d/%Y, %H:%M:%S")

    data.append(val)
  print(data)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  error = False
  if form.validate():
    try:
      newShow = Show(
        date= form.start_time.data,
        artist_id = form.artist_id.data,
        venue_id = form.venue_id.data
      )
      db.session.add(newShow)
      db.session.commit()
      flash('Show was successfully listed!')
    except:
      error = True
      db.session.rollback()
      flash('Show not added successfully')
    finally:
      db.session.close()
      if(error):
        abort(500)
      else:
        return render_template('pages/home.html')
  else:
    print(form.errors)
    flash('Show not added succesfully!')


  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
