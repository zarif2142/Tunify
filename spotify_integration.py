from flask import Flask, request, render_template, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth

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
    top_tracks = sp.current_user_top_tracks(limit=10)
    return render_template('redirect.html', top_tracks=top_tracks['items'])



if __name__ == "__main__":
    app.run()
