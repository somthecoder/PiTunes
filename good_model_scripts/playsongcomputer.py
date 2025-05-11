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
    scope=scope,
    cache_path=".cache"
))

target_device_name = "Spotifyd@cs341-pi-18"
device_id = None

devices = sp.devices()
print("Your available devices:")
for d in devices["devices"]:
    print(f" • {d['name']}  (id: {d['id']}, active: {d['is_active']})")
    if d["name"] == target_device_name:
        device_id = d["id"]

if not device_id:
    raise Exception(f"Device '{target_device_name}' not found.")


# track_id = "6rPO02ozF3bM7NnOV4h6s2"  # Despacito
# sp.start_playback(device_id=device_id, uris=[f"spotify:track:{track_id}"])

track_id = ""
song_name = "Despacito"
results = sp.search(q=song_name, type="track", limit=1)

if results["tracks"]["items"]:
    track = results["tracks"]["items"][0]
    track_id = track["id"]
    track_uri = track["uri"]
    print(f"Track: {track['name']} by {track['artists'][0]['name']}")
    print(f"Track ID: {track_id}")
    print(f"Track URI: {track_uri}")
else:
    print("No matching track found.")

sp.start_playback(device_id=device_id, uris=[f"spotify:track:{track_id}"])