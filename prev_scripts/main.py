import whisper
import numpy as np
import subprocess
import io
import soundfile as sf
import os
import re
import subprocess
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import librosa

class AudioProcessor:
    def __init__(self):
        self.model = whisper.load_model("tiny")
        self.sample_rate = 48000
        self.channels = 2  # Stereo (CD format)
        
        # Verified ALSA commands
        self.record_cmd = [
            'arecord',
            '-D', 'plughw:2,0',
            '-f', 'cd',          # 16-bit stereo little-endian
            '-r', str(self.sample_rate),
            '-t', 'wav',
            '-c', '2'           # Explicit stereo
        ]
        
        # self.playback_cmd = [
        #     'aplay',
        #     '-D', 'hdmi:0',
        #     '-f', 'cd',
        #     '-c', '2'
        # ]

        self.playback_cmd = [
            'aplay',
            '-D', 'pulse'
        ]

    def record_to_wav_buffer(self, duration=5):
        """Record to in-memory WAV file"""
        cmd = self.record_cmd + [
            '-d', str(duration),
            '-'
        ]
        
        print(f"Recording {duration}s...")
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            wav_data, stderr = process.communicate()
            
            if process.returncode != 0:
                print(f"arecord error: {stderr.decode()}")
                raise RuntimeError("Recording failed")
                
            if len(wav_data) < 44:  # Minimum WAV header size
                raise RuntimeError("Recording too short")
                
            return wav_data
            
        except Exception as e:
            print(f"Recording exception: {str(e)}")
            raise

    def play_wav_buffer(self, wav_data):
        """Play in-memory WAV file"""
        try:
            process = subprocess.Popen(
                self.playback_cmd + ['-'],  # Read from stdin
                stdin=subprocess.PIPE
            )
            process.stdin.write(wav_data)
            process.stdin.close()
            process.wait()
        except Exception as e:
            print(f"Playback error: {str(e)}")
            raise

    def transcribe_wav_buffer(self, wav_data):
        """Transcribe from in-memory WAV"""
        try:
            # Convert WAV to numpy array with explicit float32 dtype
            with io.BytesIO(wav_data) as wav_buffer:
                data, sr = sf.read(wav_buffer, dtype='float32')
                
            # Convert stereo to mono by averaging channels
            if len(data.shape) > 1:
                data = data.mean(axis=1)
                
            # Resample to 16kHz if needed (with explicit float32)
            if sr != 16000:
                data = librosa.resample(
                    data.astype('float32'),  # Ensure float32
                    orig_sr=sr,
                    target_sr=16000
                )
                
            # Verify data range (-1 to 1)
            data = np.clip(data, -1.0, 1.0)
            
            # Limit to 30 seconds of audio
            max_samples = 30 * 16000
            if len(data) > max_samples:
                data = data[:max_samples]
                
            return self.model.transcribe(
                data,
                fp16=False,
                language='en',
                no_speech_threshold=0.6
            )["text"]
            
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            return "[Transcription failed]"

    def process_audio(self):
        """Main processing loop"""
        try:
            while True:
                input("\nPress Enter to record (5 seconds)...")
                
                try:
                    # 1. Record to memory
                    wav_data = self.record_to_wav_buffer(duration=5)
                    print(f"Recorded {len(wav_data)} bytes WAV data")
                    
                    # 2. Verify playback
                    print("Playing back...")
                    self.play_wav_buffer(wav_data)
                    
                    # 3. Transcribe
                    print("Transcribing...")
                    text = self.transcribe_wav_buffer(wav_data)
                    print(f"Transcription: {text}")
                    
                except Exception as e:
                    print(f"Processing error: {str(e)}")
                    continue
                    
        except KeyboardInterrupt:
            print("\nExiting...")



# Spotify Configuration
spotify_info = "abcd"
with open(".env", "r") as f:
    spotify_info = json.load(f)
SPOTIFY_CLIENT_ID = spotify_info["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = spotify_info["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI = 'http://localhost:8080/callback'
SCOPE = 'user-modify-playback-state user-read-playback-state'

# Initialize Spotipy
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

def process_command(command):
    # Extract song and artist using regex
    match = re.search(r'play (.+?) by (.+?)$', command, re.IGNORECASE)
    if not match:
        match = re.search(r'play (.+?)$', command, re.IGNORECASE)
        if not match:
            return False
        song = match.group(1)
        artist = None
    else:
        song = match.group(1)
        artist = match.group(2)
    
    # Search Spotify
    query = f'track:{song}'
    if artist:
        query += f' artist:{artist}'
    results = sp.search(q=query, type='track', limit=1)
    
    if results['tracks']['items']:
        track_uri = results['tracks']['items'][0]['uri']
        # Start playback on Raspberry Pi's Spotifyd
        devices = sp.devices()
        pi_device = next((d for d in devices['devices'] if d['name'] == 'raspberrypi'), None)
        if pi_device:
            sp.start_playback(device_id=pi_device['id'], uris=[track_uri])
            return True
    return False


if __name__ == "__main__":

    # sample_rate = 48000
    # channels = 2  # Stereo (CD format)
    # duration = 5

    # # Verified ALSA commands
    # record_cmd = [
    #     'arecord',
    #     '-D', 'plughw:2,0',
    #     '-f', 'cd',          # 16-bit stereo little-endian
    #     '-r', str(sample_rate),
    #     '-t', 'wav',
    #     '-c', '2',           # Explicit stereo
    #     '-d', str(duration),
    #     '-'
    # ]

    # # Record audio and transcribe with Whisper.cpp
    # subprocess.run(record_cmd)
    # result = subprocess.check_output(['./whisper.cpp/main', '-m', './whisper.cpp/models/ggml-base.en.bin', '-f', 'input.wav'])
    # command = result.decode().strip()

    # # Process command
    # if 'play' in command.lower():
    #     process_command(command)

    processor = AudioProcessor()
    processor.process_audio()