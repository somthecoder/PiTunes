# auth_comp.py
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import json

with open(".env", "r") as f:
    cfg = json.load(f)
CLIENT_ID     = cfg["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = cfg["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI  = "http://127.0.0.1:8080"

scope="user-read-playback-state user-modify-playback-state"

auth_manager = SpotifyOAuth(
    client_id = CLIENT_ID,
    client_secret = CLIENT_SECRET,
    redirect_uri = REDIRECT_URI,
    scope = scope
)

sp = spotipy.Spotify(auth_manager=auth_manager)

# Trigger login flow (will auto-save .cache file)
sp.current_playback()
