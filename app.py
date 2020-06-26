# takes the user's input (song, gets its track id and audio features, then adds it to a DB)
import os
from pprint import pprint
from dotenv import load_dotenv
from flask import Flask, Blueprint, jsonify, request, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import spotipy
import time
import sys
import json
load_dotenv()
from spotipy.oauth2 import SpotifyClientCredentials
client_credentials_manager = SpotifyClientCredentials(client_id = os.getenv("client_id"), 
client_secret= os.getenv("client_secret"))
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
sp.trace = True

APP = Flask(__name__)
migrate = Migrate()
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spotify_songs.db'
db = SQLAlchemy(APP)
db.init_app(APP)
migrate.init_app(APP, db)
class Track(db.Model):
    id = db.Column(db.String, primary_key=True)
    danceability = db.Column(db.Float)
    energy = db.Column(db.Float)
    key = db.Column(db.Float)
    loudness = db.Column(db.Float)
    mode = db.Column(db.Float)
    speechiness = db.Column(db.Float)
    acousticness = db.Column(db.Float)
    instrumentalness = db.Column(db.Float)
    liveness = db.Column(db.Float)
    valence = db.Column(db.Float)
    tempo = db.Column(db.Float)
    uri = db.Column(db.String)
    track_href = db.Column(db.String)
    duration_ms = db.Column(db.Integer)
    time_signature = db.Column(db.Float)

def create_app():
    APP = Flask(__name__)
    migrate = Migrate()
    APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spotify_songs.db'
    db = SQLAlchemy(APP)
    db.init_app(APP)
    migrate.init_app(APP, db)

    @APP.route('/')
    def user_query():
        return render_template('user_query.html')

    @APP.route('/suggestions', methods=['POST']) #returns html page with recos
    def get_suggestions():
        print('GETTING SPOTIFY TRACK INFO...')
        print('USER QUERY:', dict(request.form))
        artist_name= request.form['artist_name']
        song_name= request.form['song_name']
        if artist_name=='' or song_name=='':
            return render_template('user_query.html', message='please enter your song and artist')
        search_str = (artist_name+" "+song_name)
        result = sp.search(q=search_str, type='track', limit=1)
        print (search_str)
        #pprint(result)
        #print(type(result)) ->dict
        
        track_id = result['tracks']['items'][0]['id']
        #print(type(track_id)) ->string
        pprint(track_id)
        print("-----------------")
        print("GETTING RECOMMENDATIONS...")
        recommendations = sp.recommendations(limit=7, seed_tracks = [track_id])
        recommended_tracks = recommendations['tracks']
        pprint(recommended_tracks)  
        top7_recos = [t['name']for t in recommended_tracks] # a list of top 7 recommended track names
        return render_template("suggestions.html", recommended_songs=top7_recos)
    return APP

if __name__ =='__main__':
    APP.debug = True
    APP.run()


"""
The following code is for use with a database:
##########################################################
@APP.route('/test')
def get_track_features():

    search_str = "The Scientist Cold Play" #NEED TO INTERFACE WITH FRONT END TO GET THE USER INPUT
    # run search query and return top result only (if usery query is 'ARTIST SONG' this will work)
    result = sp.search(q=search_str, type='track', limit=1)
    pprint(result)
    #print(type(result)) ->dict
    track_id = result['tracks']['items'][0]['id']
    #print(type(track_id)) ->string
    pprint(track_id)

    start = time.time()
    #get audio features for given track
    features = sp.audio_features(track_id)
    delta = time.time() - start
    print(json.dumps(features, indent=4))
    print("features retrieved in %.2f seconds" % (delta,))

    #add user queried track to database:
    db.drop_all()
    db.create_all()
    db_track = Track()
    db_track.id = features[0]['id']
    db_track.key = features[0]['key']
    db_track.instrumentalness = features[0]['instrumentalness']
    db_track.liveness = features[0]['liveness']
    db_track.loudness = features[0]['loudness']
    db_track.mode = features[0]['mode']
    db_track.speechiness = features[0]['speechiness']
    db_track.tempo = features[0]['tempo']
    db_track.time_signature = features[0]['time_signature']
    db_track.track_href = features[0]['track_href']
    db_track.valence = features[0]['valence']
    db_track.energy = features[0]['energy']
    db_track.danceability = features[0]['danceability']
    db_track.duration_ms = features[0]['duration_ms']
    db_track.acousticness =features[0]['acousticness']
    db_track.uri = features[0]['uri']
    db.session.add(db_track)
    print(db_track)
    print("________________")
    db.session.commit()
    return "User Track added to DB"

@APP.route('/suggest') #returns json list of recos

def get_track_suggestions():
    recommendations = sp.recommendations(limit=7, seed_tracks = [track_id])
    print (type(track_id))
    print (track_id)
    pprint (recommendations['tracks'])
    recommended_tracks = recommendations['tracks']
    #TOP_recommended_track_name = recommended_tracks[0]['name'] #returns top result track name
    top7_recos = [t['name']for t in recommended_tracks] # a list of top 7 recommended track names
    pprint (top7_recos)
    #to get a dictionary result:
    keys=['recommendation 1:', 'recommendation 2:', 'recommendation 3:', 'recommendation 4:', 'recommendation 5:', 'recommendation 6:', 'recommendation 7:']
    dict_top7=dict(zip(keys, top7_recos))
    print(dict_top7)
    # to retun json:
    top7_recos_json = json.dumps(dict_top7)
    print(top7_recos_json)
    return top7_recos_json
#################################################################################
"""