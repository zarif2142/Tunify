from flask import Flask, request, render_template, redirect, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random

app = Flask(__name__)

# Spotify API credentials
SPOTIPY_CLIENT_ID = "298e09f0d6594fa599cff0b1e36f9222"
SPOTIPY_CLIENT_SECRET = "bf366f460b9e4496a29b6ebdcd495844"
SPOTIPY_REDIRECT_URI = "http://localhost:5000/redirect"

# Initialize Spotipy with OAuth
sp_oauth = SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope="user-top-read")

@app.route("/")
def index():
    return render_template("index.html")

# Route for initiating Spotify authentication
@app.route("/spotify-login")
def spotify_login():
    # Generate the Spotify authorization URL and redirect the user
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)




# Other routes and functions for handling the Spotify callback and data retrieval go here




@app.route('/redirect')
def spotify_redirect():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    sp = spotipy.Spotify(auth=token_info['access_token'])
    session['access_token'] = token_info['access_token']  # Save the access token in the session


    # Fetch the user's profile data to get the username
    user_profile = sp.current_user()
    username = user_profile['display_name']  # or user_profile['id'] if display_name is not available

    # Get the top tracks
    top_tracks = sp.current_user_top_tracks(limit=10)

    # Get the top artists
    top_artists = sp.current_user_top_artists(limit=10)



    # Pass both top tracks and top artists to the template
    return render_template('redirect.html', username=username, top_artists=top_artists['items'], top_tracks=top_tracks['items'])



if __name__ == "__main__":
    app.run()


@app.route('/get-song-recommendation')
def get_song_recommendation_route():
    access_token = session.get('access_token')
    if access_token:
        sp = spotipy.Spotify(auth=access_token)
        song_recommendation = get_song_recommendation(sp)
        return jsonify(song_recommendation)
    else:
        return jsonify({'error': 'User not authenticated'}), 401

