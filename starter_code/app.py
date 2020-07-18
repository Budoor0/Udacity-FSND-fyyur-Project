#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from sqlalchemy.sql import expression
from datetime import datetime
from sqlalchemy.sql.functions import now
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# 

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(10))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(120))
     # relation to show 
    shows = db.relationship('Show', backref='venue', lazy=True)

    #def __repr__(self):
     # return f'<Venue {self.id} {self.name}>'

    def __init__(self, name,city,state,address,phone,image_link,facebook_link,genres,website,seeking_talent,seeking_description):
        self.name = name
        self.city =city
        self.state=state
        self.address=address
        self.phone=phone
        self.image_link=image_link
        self.facebook_link=facebook_link
        self.genres=genres
        self.website=website
        self.seeking_description=seeking_description
        self.seeking_talent=seeking_talent

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(20),nullable=False)
    state = db.Column(db.String(120))
    phone = db.Column(db.String(10))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(120))
    # relation to show 
    shows = db.relationship('Show', backref='artist', lazy=True)

    #def __repr__(self):
     # return f'<Venue {self.id} {self.name}>'

    def __init__(self,name,city,state,phone,image_link,facebook_link,genres,website,seeking_venue,seeking_description):
        self.name=name
        self.city=city
        self.state=state
        self.phone=phone
        self.image_link=image_link
        self.facebook_link=facebook_link
        self.genres=genres
        self.website=website
        self.seeking_description=seeking_description
        self.seeking_venue=seeking_venue

    

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# db.create_all() 

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime(), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id', ondelete='CASCADE'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id',ondelete='CASCADE'), nullable=False)

    


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
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()
  data = []
  for area in areas:
    areas = db.session.query(Venue).filter_by(state=area.state).filter_by(city=area.city).all()
    venue_data = []
    for venue in areas:
      venue_data.append({
        'id':venue.id,
        'name':venue.name,
      })
    data.append({
        'city':area.city,
        'state':area.state,
        'venues':venue_data,
      })


  return render_template('pages/venues.html', areas=data )

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  results =  Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form.get('search_term')))).all()
  
  response={
    "count": len(results),
    "data": results   }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id 
  venue = db.session.query(Venue).get(venue_id)
  past_shows=[]
  upcoming_shows=[]
  data=[]
 
  for show in venue.shows:
    if show.start_time >= datetime.today():
        upcoming_shows.append({
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")})
    if show.start_time < datetime.today():
        past_shows.append({
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")    
      })
 
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }



  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error= False
  data = request.form
  venue_name = data['name']
  venue_city = data['city']
  venue_state = data['state']
  venue_address = data['address']
  venue_phone = data['phone']
  venue_genres = data.getlist('genres')
  venue_facebook_link = data['facebook_link']
  venue_website = data['website']
  venue_image_link = data['image_link']
  #venue_seeking_talent = data['seeking_talent']
  venue_seeking_description = data['seeking_description']
  try:
    db.session.add(Venue(name=venue_name,city=venue_city,state=venue_state,address= venue_address,phone=venue_phone,
    genres=venue_genres,facebook_link=venue_facebook_link,website=venue_website,seeking_talent=False,
    seeking_description= venue_seeking_description,image_link= venue_image_link ))
    db.session.commit()

  except Exception as err:
    #return f"{err.__class__.__name__}: {err}"
    error = True
    print(sys.exc_info())
  finally:
    if not error:
      flash('Venue ' + data['name'] + ' was successfully listed!')
    else:
      flash('An error occurred. Venue ' + venue_name + ' could not be listed.')
      db.session.close()
      abort (400)


  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    if not error:
      flash('Venue ' + venue.name + ' was successfully DELETE!')
    else:
      flash('An error occurred. Venue ' + venue.name + ' could not be DELETE.')
      db.session.close()
      abort (400)

  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # same code in Venue
  results =  Artist.query.filter(Artist.name.ilike('%{}%'.format(request.form.get('search_term')))).all()
  
  response={
    "count": len(results),
    "data": results   }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = db.session.query(Artist).get(artist_id)
  past_shows=[]
  upcoming_shows=[]
  data=[]

  for show in artist.shows:
    if show.start_time >= datetime.today():
      upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S") })
    if show.start_time < datetime.today():
      past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
     
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description":artist.seeking_description ,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

 # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist= Artist.query.get(artist_id)
  artist = {
    'id': artist.id,
    'name':artist.name,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'facebook_link': artist.facebook_link,
    'genres': artist.genres,
    'website': artist.website,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description
  }
 
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist= Artist.query.get(artist_id)
  error= False
  data = request.form
  artist.name = data['name']
  artist.city = data['city']
  artist.state = data['state']
  artist.phone = data['phone']
  artist.image_link = data['image_link']
  artist.facebook_link = data['facebook_link']
  artist.genres = data.getlist('genres')
  artist.website = data['website']
  #artist.seeking_venue = data['seeking_venue']
  artist.seeking_description = data['seeking_description']
  try:
    db.session.add(Artist(name=artist.name, city=artist.city, state=artist.state, phone=artist.phone,
    genres=artist.genres, facebook_link=artist.facebook_link, website=artist.website,
    image_link=artist.image_link, seeking_venue=False, seeking_description=artist.seeking_description))
    db.session.commit()

  except Exception as err:
    #return f"{err.__class__.__name__}: {err}"
    error = True
    print(sys.exc_info())
  finally:
    if not error:
      flash('Artist ' + data['name'] + ' was successfully Update!')
    else:
      flash('An error occurred. Artist ' + artist_name + ' could not be Update.')
      db.session.close()
      abort (400)
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue = {
    'id': venue.id,
    'name':venue.name,
    'city': venue.city,
    'address': venue.address,
    'state': venue.state,
    'phone': venue.phone,
    'facebook_link': venue.facebook_link,
    'genres': venue.genres,
    'website': venue.website,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description
  }

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue= Venue.query.get(venue_id)
  error= False
  data = request.form
  venue.name = data['name']
  venue.city = data['city']
  venue.state = data['state']
  venue.phone = data['phone']
  venue.image_link = data['image_link']
  venue.facebook_link = data['facebook_link']
  venue.genres = data.getlist('genres')
  venue.website = data['website']
  #venue.seeking_talent= data['seeking_talent']
  venue.seeking_description = data['seeking_description']
  try:
    db.session.add(Venue(name=venue.name,city=venue.city,state=venue.state,address= venue.address,phone=venue.phone,
    genres=venue.genres,facebook_link=venue.facebook_link,website=venue.website,seeking_talent=False,
    seeking_description= venue.seeking_description,image_link= venue.image_link ))
    db.session.commit()

  except Exception as err:
    #return f"{err.__class__.__name__}: {err}"
    error = True
    print(sys.exc_info())
  finally:
    if not error:
      flash('Venue ' + data['name'] + ' was successfully Update!')
    else:
      flash('An error occurred. Venue ' + venue_name + ' could not be Update.')
      db.session.close()
      abort (400)
 
  return redirect(url_for('show_venue', venue_id=venue_id))

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
  error= False
  data = request.form
  artist_name = data['name']
  artist_city = data['city']
  artist_state = data['state']
  artist_phone = data['phone']
  artist_image_link = data['image_link']
  artist_facebook_link = data['facebook_link']
  artist_genres = data.getlist('genres')
  artist_website = data['website']
  #artist_seeking_venue = data['seeking_venue']
  artist_seeking_description = data['seeking_description']
  try:
    db.session.add(Artist(name=artist_name, city=artist_city, state=artist_state, phone=artist_phone,
    genres=artist_genres, facebook_link=artist_facebook_link, website=artist_website,
    image_link=artist_image_link, seeking_venue=False, seeking_description=artist_seeking_description))
    db.session.commit()

  except Exception as err:
    return f"{err.__class__.__name__}: {err}"
    #error = True
    #print(sys.exc_info())
    #print(e)
  finally:
    if not error:
      flash('Artist ' + data['name'] + ' was successfully listed!')
    else:
      flash('An error occurred. Artist ' + artist_name + ' could not be listed.')
      db.session.close()
      abort (400)

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #   num_shows should be aggregated based on number of upcoming shows per venue.
  shows = db.session.query(Show).all() 
  data =[]
  for s in shows:
      data_show=[]
      data.append({
        'venue_id': s.venue_id,
        'venue_name': s.venue.name,
        'artist_id': s.artist_id,
        'artist_name': s.artist.name,
        'artist_image_link': s.artist.facebook_link,
        'start_time': s.start_time.strftime('%Y-%m-%d %H:%M')
    })

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
  error = False
  data = request.form
  show_start_time = data['start_time']
  show_artist_id = data['artist_id']
  show_venue_id = data['venue_id']

  try:
    db.session.add(Show(start_time=show_start_time, artist_id=show_artist_id,
    venue_id=show_venue_id))
    db.session.commit()
  
  except Exception as err:
    #return f"{err.__class__.__name__}: {err}"
    db.session.rollback()
  finally:
    if not error:
      flash('Show was successfully listed!')
    else:
      flash('An error occurred. Show could not be listed.')
      db.session.close()
      abort(400)

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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
