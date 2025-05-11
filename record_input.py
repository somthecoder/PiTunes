import whisper
import numpy as np
import subprocess
import io
import wave
from scipy.io.wavfile import read
from scipy.signal import resample
import os

class AudioProcessor:
    def __init__(self):
        self.model = whisper.load_model("tiny")
        self.sample_rate = 48000
        self.output_path = "/tmp/spotify_command.txt"

    def record_to_wav_buffer(self, duration=5):
        try:
            print(f"Recording {duration}s from mic via ALSA...")
            cmd = [
                "arecord",
                "-D", "hw:2,0",
                "-f", "S16_LE",
                "-c", "1",
                "-r", str(self.sample_rate),
                "-t", "raw",
                "-d", str(duration)
            ]

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            pcm_data, stderr = process.communicate()

            if process.returncode != 0 or len(pcm_data) < 1000:
                print(f"arecord error: {stderr.decode()}")
                return None

            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(pcm_data)

            return wav_buffer.getvalue()

        except Exception as e:
            print(f"Recording exception: {e}")
            return None

    def transcribe_wav_buffer(self, wav_data):
        try:
            sr, data = read(io.BytesIO(wav_data))

            if data.ndim > 1:
                data = data.mean(axis=1)

            data = data.astype(np.float32) / np.iinfo(data.dtype).max

            if sr != 16000:
                data = resample(data, int(len(data) * 16000 / sr))

            data = np.clip(data, -1.0, 1.0)

            print("Transcribing...")
            result = self.model.transcribe(data, fp16=False, language='en')
            return result["text"]
        except Exception as e:
            print(f"Transcription error: {e}")
            return None

    def process_audio(self):
        while True:
            input("\nPress Enter to record a song name...")
            wav_data = self.record_to_wav_buffer(duration=5)
            if wav_data:
                transcription = self.transcribe_wav_buffer(wav_data)
                if transcription:
                    print(f"Transcription: {transcription}")
                    with open(self.output_path, "w") as f:
                        f.write(transcription.strip())
                else:
                    print("[Transcription failed]")
            else:
                print("[No audio recorded]")

if __name__ == "__main__":
    processor = AudioProcessor()
    processor.process_audio()
