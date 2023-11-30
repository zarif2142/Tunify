from flask import Flask, request, render_template, redirect, jsonify, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with your real secret key

# Spotify OAuth settings
SPOTIPY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = "http://localhost:5000/redirect"

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
        # Redirect to login if the user doesn't have an access token
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
        if access_token:
            sp = spotipy.Spotify(auth=access_token)
            return jsonify(get_song_recommendation(sp))
        else:
            return jsonify({'error': 'User not authenticated'}), 401
    except Exception as e:
        app.logger.error(f'An error occurred: {e}')
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

if __name__ == "__main__":
    app.run(debug=True)


