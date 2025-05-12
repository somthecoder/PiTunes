# songplayer.py
import json
import spotipy
import time
import os
from spotipy.oauth2 import SpotifyOAuth

COMMAND_PATH = "/tmp/spotify_command.txt"

with open(".env", "r") as f:
    cfg = json.load(f)

CLIENT_ID = cfg["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = cfg["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI = "http://127.0.0.1:8080"
SCOPE = "user-read-playback-state user-modify-playback-state"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=".cache"
))

target_device_name = "Spotifyd@cs341-pi-18"

def get_device_id():
    devices = sp.devices()["devices"]
    for d in devices:
        if d["name"] == target_device_name:
            return d["id"]
    raise RuntimeError(f"Device '{target_device_name}' not found.")

def play_song(song_name):
    if "rick" in song_name.lower() and "roll" in song_name.lower():
        song_name = "Never Gonna Give You Up Rick Astley"
    results = sp.search(q=song_name, type="track", limit=1)
    if results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        print(f"Playing: {track['name']} by {track['artists'][0]['name']}")
        sp.start_playback(device_id=get_device_id(), uris=[track["uri"]])
    else:
        print("No matching track found.")

def watch_for_commands():
    print("Watching for new commands...")
    last_command = ""
    while True:
        try:
            if os.path.exists(COMMAND_PATH):
                with open(COMMAND_PATH, "r") as f:
                    command = f.read().strip()

                if command and command != last_command:
                    print(f"New command detected: {command}")
                    play_song(command)
                    last_command = command

            time.sleep(2)
        except Exception as e:
            print(f"Playback error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    watch_for_commands()
