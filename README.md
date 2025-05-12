# PiTunes

Somrishi: Integration of Spotifyd daemon with Pi and ALSA and syncing Whisper and Spotify search together  
Cygnus: Spotify API and song search based on given text, Rust binary installation assistance  
Rishi: Whisper STT sppech transcription with microphone, sound system debugging  

## Overview:
The goal for this project was to avoid having to type out a song you wanted to listen to and instead be able to speak it and have it automatically play, similar to that of a Amazon Alexa or Google Home. As long as the Pi is connected to a speaker via USB or bluetooth, we can play music. 

## Pre-requirements:
  Spotify Premium <br>
  Raspberry Pi 5 <br>
  Device with Browser Access <br>
  Speaker to connect to Pi (wired/wireless)
  

## Installation:
  Clone this repo on to the Pi. Go to your Spotify premium account and create a developer account with client id and secret along with the redirect uri. Create a .env file and in json format, input in these things. On a separate device with browser access, run the auth_comp.py script and then the command ```scp .cache pi@ip_address:repo_path``` to transfer the unique cache file to the Pi. Ensure your speaker and microphone are connected to the Pi.<br>
  Given the instructions on [the Spotifyd documentation](https://docs.spotifyd.rs/installation/index.html) and the [Spotifyd releases page](https://github.com/spotifyd/spotifyd/releases), find your right release and follow the underneath the Architecture section. You should then be able to run Spotifyd.

## Usage:
  Create a venv and install the appropriate requirements for the python scripts. Have 3 terminals open. On the first, run the command ```spotifyd --no-daemon```. On the second, run ```record_input.py``` and on the third, run ```play_song.py```. You can ignore the first and third terminals. On the second one, whenever you want to play a song, you will press the enter key and have 5 seconds to speak a song name into the microphone. After that, the song should play within a couple seconds and you can enjoy some music.

