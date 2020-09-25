#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from dateutil import tz  #App wont start without this 
from flask_migrate import Migrate
import datetime
import time
from flask_cors import CORS
from sqlalchemy import text
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))

  # TODO: implement any missing fields, as a database migration using Flask-Migrate
  website = db.Column(db.String())
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String())
  genres = db.Column(db.String(120))
  # shows=db.relationship('show',secondary=show)
  # artists = db.relationship('Artist',secondary=show, backref=db.backref('artists', lazy=True))

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))

  # TODO: implement any missing fields, as a database migration using Flask-Migrate
  # venues= db.relationship('Venue',secondary=show, backref=db.backref('venues', lazy=True))
  seeking_venue = db.Column(db.Boolean, default=False,nullable=True)
  seeking_description = db.Column(db.String(),default='',nullable=True)
  website=db.Column(db.String(),default='')
  
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'Show'
  
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime())
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  venue = db.relationship('Venue', backref=db.backref('shows'))
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  artist = db.relationship('Artist',backref=db.backref('shows'))

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  #states = Venue.query.distinct(Venue.city, Venue.state).all()
  sql_statement = 'SELECT DISTINCT city,state FROM "Venue";'
  result = db.engine.execute(sql_statement)
  states = [row for row in result]
  def filter_location(arg):
    # results = Venue.query.filter(Venue.city == arg.city).all()
    sql=f'SELECT name,id FROM "Venue" WHERE city LIKE \'%%{arg.city}%%\' AND state LIKE \'%%{arg.state}%%\'; '
    results =[row for row in db.engine.execute(sql)]
    return {'city': arg.city,
                'state': arg.state,
                'venues': [v for v in results]        
            }
  data=[filter_location(state) for state in states]
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  search_term = request.form.get('search_term', None)
  # venues_search = Venue.query.filter(
  #       Venue.name.ilike("%{}%".format(search_term))).all()
  sql = f'SELECT * FROM "Venue" WHERE LOWER(name) LIKE \'%%{search_term.lower()}%%\' '
  print(sql)
  venues_search = [v for v in db.engine.execute(sql)]
  print(venues_search)
  venues_count = len(venues_search)
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": venues_count,
    "data": venues_search
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #venue = Venue.query.filter(Venue.id == venue_id).all()[0]
  venue_sql = f'SELECT * FROM "Venue" AS v WHERE v.id={venue_id} ;'
  venue = [v for v in db.engine.execute(venue_sql)][0]
  
  genres = [g for g in db.engine.execute(f'SELECT genres FROM "Venue" AS v WHERE v.id={venue_id}; ')][0][-1].split(',')
  
  
  # upcoming_shows= Show.query.filter(
  #                   Show.start_time > datetime.datetime.now(),
  #                   Show.venue_id == venue_id).all()
  # #upcoming_shows=[u for u in db.engine.execute(f'SELECT * FROM "Show" AS s WHERE s.start_time>"{datetime.datetime.now()}" AND s.venue_id={venue_id};')][0]
  # for show in upcoming_shows:
  #   #show.artist_image_link = Artist.query.filter(show.artist_id == Artist.id).with_entities(Artist.image_link)[0][-1]
  #   show.artist_image_link=[res for res in db.engine.execute(f'SELECT image_link FROM "Artist" AS a WHERE a.id={show.artist_id};' )][0][-1]
  #   #show.artist_name = Artist.query.filter(show.artist_id == Artist.id).with_entities(Artist.name)[0][-1]
  #   show.artist_name=[res for res in db.engine.execute(f'SELECT name FROM "Artist" AS a WHERE a.id={show.artist_id};' )][0][-1]
  # past_shows=Show.query.filter(
  #                   Show.start_time < datetime.datetime.now(),
  #                   Show.venue_id == venue_id).all()
  # for show in past_shows:
  #   show.artist_image_link=[res for res in db.engine.execute(f'SELECT image_link FROM "Artist" AS a WHERE a.id={show.artist_id};' )][0][-1]
  #   show.artist_name=[res for res in db.engine.execute(f'SELECT name FROM "Artist" AS a WHERE a.id={show.artist_id};' )][0][-1]
  upcoming_shows=[show for show in db.engine.execute(text(f'SELECT s.start_time ,a.name AS artist_name , a.image_link AS artist_image_link FROM "Show" s JOIN "Artist" a ON a.id=s.artist_id WHERE s.venue_id = {venue_id} AND s.start_time > \'{datetime.datetime.now()}\' ;'))]
  past_shows=[show for show in db.engine.execute(text(f'SELECT s.start_time ,a.name AS artist_name , a.image_link AS artist_image_link FROM "Show" s JOIN "Artist" a ON a.id=s.artist_id WHERE s.venue_id = {venue_id} AND s.start_time < \'{datetime.datetime.now()}\' ;'))]

  
  
  
  upcoming_shows_count=len(upcoming_shows)
  past_shows_count=len(past_shows)
  return render_template('pages/show_venue.html', venue=venue,genres=genres,past_shows=past_shows,upcoming_shows=upcoming_shows,upcoming_shows_count=upcoming_shows_count,past_shows_count=past_shows_count)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  #venue_form = VenueForm(request.form)
  venue_form = request.form
  #print(venue_form['name'])
  # TODO: modify data to be the data object returned from db insertion
  
  new_list=venue_form.getlist('genres')
  
  try:
    # new_venue = Venue(
    #         name=venue_form['name'],
    #         genres=','.join(new_list),
    #         address=venue_form['address'],
    #         city=venue_form['city'],
    #         state=venue_form['state'],
    #         phone=venue_form['phone'],
    #         facebook_link=venue_form['facebook_link'],
    #         image_link=venue_form['image_link'])
    name=venue_form['name']
    genres=','.join(new_list)
    address=venue_form['address']
    city=venue_form['city']
    state=venue_form['state']
    phone=venue_form['phone']
    facebook_link=venue_form['facebook_link']
    image_link=venue_form['image_link']
    db.engine.execute(f'INSERT INTO "Venue" (name,genres,address,city,state,phone,facebook_link,image_link) VALUES(\'{name}\',\'{genres}\',\'{address}\',\'{city}\',\'{state}\',\'{phone}\',\'{facebook_link}\',\'{image_link}\');')
  # db.session.add(new_venue)
  # db.session.commit()
    flash('Venue ' + venue_form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred')
    #db.session.rollback()

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # Venue.query.filter(Venue.id == venue_id).all().delete()
  db.engine.execute(f'DELETE FROM "Venue" AS v WHERE v.id = {venue_id};')
  # db.session.commit()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  #data = Artist.query.with_entities(Artist.id, Artist.name)
  data=[a for a in db.engine.execute(f'SELECT id,name FROM "Artist" ;')]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', None)
  sql = f'SELECT * FROM "Artist" WHERE LOWER(name) LIKE \'%%{search_term.lower()}%%\' '
  artist_search = [v for v in db.engine.execute(sql)]
  artist_count = len(artist_search)
  response={
    "count": artist_count,
    "data": artist_search
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # artist = Artist.query.filter(Artist.id == artist_id).all()[0]
  # genres = artist.genres.split(',')
  # artist.genres = genres
  # artist.upcoming_shows= Show.query.filter(
  #                   Show.start_time > datetime.datetime.now(),
  #                   Show.artist_id == artist_id).all()
  # for show in artist.upcoming_shows:
  #   show.venue_image_link = Venue.query.filter(show.venue_id == Venue.id).with_entities(Venue.image_link)[0][-1]
  #   show.venue_name=Venue.query.filter(show.venue_id == Venue.id).with_entities(Venue.name)[0][-1]
  # artist.past_shows=Show.query.filter(
  #                   Show.start_time < datetime.datetime.now(),
  #                   Show.artist_id == artist_id).all()
  # for show in artist.past_shows:
  #   show.venue_image_link = Venue.query.filter(show.venue_id == Venue.id).with_entities(Venue.image_link)[0][-1]
  #   show.venue_name = Venue.query.filter(show.venue_id == Venue.id).with_entities(Venue.name)[0][-1]
  # artist.upcoming_shows_count=len(artist.upcoming_shows)
  # artist.past_shows_count = len(artist.past_shows)
  




  artist_sql = f'SELECT * FROM "Artist" AS v WHERE v.id={artist_id} ;'
  artist = [v for v in db.engine.execute(artist_sql)][0]
  
  genres = [g for g in db.engine.execute(f'SELECT genres FROM "Artist" AS a WHERE a.id={artist_id}; ')][0][-1].split(',')
  
  # upcoming_shows= Show.query.filter(
  #                   Show.start_time > datetime.datetime.now(),
  #                   Show.artist_id == artist_id).all()
  # #upcoming_shows=[u for u in db.engine.execute(f'SELECT * FROM "Show" AS s WHERE s.start_time>"{datetime.datetime.now()}" AND s.artist_id={artist_id};')][0]
  # for show in upcoming_shows:
  #   #show.artist_image_link = Artist.query.filter(show.artist_id == Artist.id).with_entities(Artist.image_link)[0][-1]
  #   show.venue_image_link=[res for res in db.engine.execute(f'SELECT image_link FROM "Venue" AS v WHERE v.id={show.venue_id};' )][0][-1]
  #   #show.artist_name = Artist.query.filter(show.artist_id == Artist.id).with_entities(Artist.name)[0][-1]
  #   show.venue_name=[res for res in db.engine.execute(f'SELECT name FROM "Venue" AS v WHERE v.id={show.venue_id};' )][0][-1]
  # # past_shows=Show.query.filter(
  # #                   Show.start_time < datetime.datetime.now(),
  # #                   Show.artist_id == artist_id).all()
  # past_shows=[show for show in db.engine.execute(text(f'SELECT * FROM "Show" s WHERE s.artist_id = {artist_id} AND s.start_time<\'{datetime.datetime.now()}\';'))][0]
  # for show in past_shows:
  #   show.venue_image_link=[res for res in db.engine.execute(f'SELECT image_link FROM "Venue" AS v WHERE v.id={show.venue_id};' )][0][-1]
  #   show.venue_name=[res for res in db.engine.execute(f'SELECT name FROM "Venue" AS v WHERE v.id={show.venue_id};' )][0][-1]
  # upcoming_shows_count=len(upcoming_shows)
  # past_shows_count=len(past_shows)
  upcoming_shows=[show for show in db.engine.execute(text(f'SELECT s.start_time ,v.name AS venue_name , v.image_link AS venue_image_link FROM "Show" s JOIN "Venue" v ON v.id=s.venue_id WHERE s.artist_id = {artist_id} AND s.start_time > \'{datetime.datetime.now()}\' ;'))]
  
  past_shows=[show for show in db.engine.execute(text(f'SELECT s.start_time ,v.name AS venue_name , v.image_link AS venue_image_link FROM "Show" s JOIN "Venue" v ON v.id=s.venue_id WHERE s.artist_id = {artist_id} AND s.start_time < \'{datetime.datetime.now()}\' ;'))]
  
  upcoming_shows_count=len(upcoming_shows)
  past_shows_count=len(past_shows)
  
  return render_template('pages/show_artist.html', genres=genres,artist=artist,upcoming_shows=upcoming_shows,past_shows=past_shows,past_shows_count=past_shows_count,upcoming_shows_count=upcoming_shows_count)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  #artist = Artist.query.filter(Artist.id == artist_id).all()[0]
  artist=[a for a in db.engine.execute(f'SELECT * FROM "Artist" AS a WHERE a.id={artist_id};')][0]
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist_form = ArtistForm(request.form)
  artist_form = request.form
  # new_artist = Artist.query.filter(Artist.id == artist_id).all()[0]
  new_list = artist_form.getlist('genres')
    
    # new_artist.name = artist_from['name']
    # new_artist.genres = ','.join(artist_from['genres']) 
    # new_artist.city = artist_from['city']
    # new_artist.state = artist_from['state']
    # new_artist.phone = artist_from['phone']
    # new_artist.facebook_link = artist_from['facebook_link']
    # new_artist.image_link = artist_from['image_link']
    # db.session.commit()


  name=artist_form['name']
  genres=','.join(new_list)
  city=artist_form['city']
  state=artist_form['state']
  phone=artist_form['phone']
  facebook_link=artist_form['facebook_link']
  image_link=artist_form['image_link']
  db.engine.execute(text("UPDATE \"Artist\" SET name='{}', genres='{}',city='{}',state='{}',phone='{}',facebook_link='{}',image_link='{}' WHERE id={} ;".format(name,genres,city,state,phone,facebook_link,image_link,artist_id)))
  
    
  
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  #venue = Venue.query.filter(Venue.id == venue_id).all()[0]
  venue=[v for v in db.engine.execute(text(f'SELECT * FROM "Venue" AS v WHERE v.id={venue_id}'))][0]
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  #new_venue = Venue.query.filter(Venue.id == venue_id).all()[0]
  venue_form = request.form
  
  new_list = venue_form.getlist('genres')
  
  
  try:
    name = venue_form['name']
    address=venue_form['address']
    genres=','.join(new_list)
    city=venue_form['city']
    state=venue_form['state']
    phone=venue_form['phone']
    facebook_link=venue_form['facebook_link']
    image_link=venue_form['image_link']
    db.engine.execute(text("UPDATE \"Venue\" SET name='{}',address='{}', genres='{}',city='{}',state='{}',phone='{}',facebook_link='{}',image_link='{}' WHERE id={} ;".format(name,address,genres,city,state,phone,facebook_link,image_link,venue_id)))
  except:
    db.session.rollback()
  #venue record with ID <venue_id> using the new attributes
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
  # artist_form = ArtistForm(request)
  #artist_form = FlaskForm(request.form)
  artist_form=request.form
  # TODO: modify data to be the data object returned from db insertion
  new_list = artist_form.getlist('genres')
  try:


    name=artist_form['name']
    genres=','.join(new_list)
    city=artist_form['city']
    state=artist_form['state']
    phone=artist_form['phone']
    facebook_link=artist_form['facebook_link']
    image_link=artist_form['image_link']
    db.engine.execute(f'INSERT INTO "Artist" (name,genres,city,state,phone,facebook_link,image_link) VALUES(\'{name}\',\'{genres}\',\'{city}\',\'{state}\',\'{phone}\',\'{facebook_link}\',\'{image_link}\');')
    
    flash('Artist ' + artist_form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred.')
  #   db.session.rollback()

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # shows = Show.query.all()
  # shows =[show for show in db.engine.execute(text(f'SELECT * FROM "Show";'))]
  # for show in shows:
  #   # show.venue_name=Venue.query.filter(show.venue_id==Venue.id).with_entities(Venue.name)[0][-1]
  #   show.venue_name=[name for name in db.engine.execute(text(f'SELECT name FROM "Venue" AS v WHERE v.id={show.venue_id}';))][0][-1]
  #   # show.artist_name = Artist.query.filter(show.artist_id == Artist.id).with_entities(Artist.name)[0][-1]
  #   show.artist_name=[name for name in db.engine.execute(text(f'SELECT name FROM "Artist" AS a WHERE a.id={show.artist_id}';))][0][-1]
  #   show.artist_image_link = Artist.query.filter(show.artist_id == Artist.id).with_entities(Artist.image_link)[0][-1]
  sql = f'SELECT s.start_time,a.name AS artist_name,v.name AS venue_name,a.image_link AS artist_image_link,a.id AS artist_id,v.id AS venue_id FROM "Show" s JOIN "Artist" a ON a.id=s.artist_id JOIN "Venue" v on v.id = s.venue_id ;'
  shows = [show for show in db.engine.execute(text(sql))]
  print(shows)
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  show_form =request.form
  try:
    # new_show = Show(
    #         artist_id=show_form['artist_id'],
    #         venue_id=show_form['venue_id'],
    #         start_time=show_form['start_time']
    #       )
    artist_id=show_form['artist_id']
    venue_id=show_form['venue_id']
    start_time=show_form['start_time']

    db.engine.execute(text(f'INSERT INTO "Show" (artist_id,venue_id,start_time) VALUES ({artist_id},{venue_id},\'{start_time}\'); '))
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
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
