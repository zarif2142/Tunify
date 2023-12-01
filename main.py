from flask import Flask, request, render_template, redirect, jsonify, session, url_for
from flask_cors import CORS  # Import the CORS object
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from datetime import timedelta #inactivity timer
import logging #log user access tokens, making sure they're unique to each user


# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes, helps with recommendations

# Load environment variables
load_dotenv()

app.secret_key = os.getenv("FLASK_SECRET_KEY")  

# Spotify OAuth settings
SPOTIPY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = "https://tunify-89a2e48d4f34.herokuapp.com/redirect"

# Initialize Spotipy with OAuth
sp_oauth = SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope="user-top-read playlist-modify-private")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/spotify-login")
def spotify_login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def spotify_redirect():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['access_token'] = token_info['access_token']  # Save the access token in the session
    return redirect("/recommendation")

@app.route('/recommendation')
def recommendation():
    access_token = session.get('access_token')
    if not access_token:
        return redirect("/spotify-login")
    
    sp = spotipy.Spotify(auth=access_token)
    user_profile = sp.current_user()
    username = user_profile['display_name']
    top_tracks = sp.current_user_top_tracks(limit=10)
    top_artists = sp.current_user_top_artists(limit=10)
    return render_template('redirect.html', username=username, top_artists=top_artists['items'], top_tracks=top_tracks['items'])

@app.route('/get-song-recommendation')
def get_song_recommendation_route():
    try:
        access_token = session.get('access_token')
        if not access_token:
            return jsonify({'error': 'User not authenticated'}), 401
        
        sp = spotipy.Spotify(auth=access_token)
        recommendation = get_song_recommendation(sp)
        return jsonify(recommendation)
    except Exception as e:
        print(f"An error occurred: {e}")  # Log any exception
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

def get_song_recommendation(sp):
    top_tracks = sp.current_user_top_tracks(limit=10)['items']
    seed_tracks = [track['id'] for track in top_tracks[:5]]  # Using the top 5 tracks for seeds

    recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=1)['tracks']
    if recommendations:
        recommended_track = recommendations[0]
        return {
            'title': recommended_track['name'],
            'artist': recommended_track['artists'][0]['name'],
            'spotify_url': recommended_track['external_urls']['spotify']  # Spotify URL of the track
        }
    else:
        return None

@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    return redirect(url_for('index'))  # Redirect to the index page

 
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',  # or 'Strict'
)


# Set permanent session lifetime, for example, 10 minutes of inactivity
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)


print(f"Access token for session: {session['access_token']}")

if __name__ == "__main__":
    logging.basicConfig(filename='app.log', level=logging.DEBUG)
    app.run()
