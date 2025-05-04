import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

with open(".env", "r") as f:
    cfg = json.load(f)
CLIENT_ID     = cfg["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = cfg["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI  = "http://127.0.0.1:8080" 

scope = "user-read-playback-state user-modify-playback-state"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope
))

devices = sp.devices()
print("Your available devices:")
for d in devices["devices"]:
    print(f" • {d['name']}  (id: {d['id']}, active: {d['is_active']})")

device_id = None
if devices["devices"]:
    active = [d for d in devices["devices"] if d["is_active"]]
    device_id = active[0]["id"] if active else devices["devices"][0]["id"]

track_id = "6habFhsOp2NvshLv26DqMb"  # Despacito
sp.start_playback(device_id=device_id, uris=[f"spotify:track:{track_id}"])