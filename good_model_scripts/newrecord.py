import whisper
import numpy as np
import subprocess
import io
import soundfile as sf
import librosa
import wave
from scipy.io.wavfile import read
from scipy.io.wavfile import read
from scipy.signal import resample

class AudioProcessor:
    def __init__(self):
        self.model = whisper.load_model("tiny")
        self.sample_rate = 48000

        # Record using PipeWire-compatible pw-record
        self.record_cmd = [
            "pw-record",
            "--rate", str(self.sample_rate),
            "--channels", "1",
            "--format", "s16",
            "-",  # output to stdout
        ]

        # Playback via PulseAudio or PipeWire-compatible player
        self.playback_cmd = ["aplay", "-D", "pulse"]


    
    def record_to_wav_buffer(self, duration=5):
        try:
            print(f"Recording {duration}s from USB mic via ALSA...")

            # Use arecord with working parameters
            cmd = [
                "arecord",
                "-D", "hw:2,0",           # ✅ your working ALSA mic
                "-f", "S16_LE",           # 16-bit PCM
                "-c", "1",                # Mono
                "-r", "48000",            # 48kHz
                "-t", "raw",              # Raw PCM output
                "-d", str(duration)
            ]

            # Run and capture raw PCM output
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            pcm_data, stderr = process.communicate()

            if process.returncode != 0 or len(pcm_data) < 1000:
                print(f"arecord error: {stderr.decode()}")
                raise RuntimeError("Recording failed or too short")

            # Wrap into proper WAV file
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)       # 2 bytes for 16-bit
                wf.setframerate(48000)
                wf.writeframes(pcm_data)

            return wav_buffer.getvalue()

        except Exception as e:
            print(f"Recording exception: {e}")
            return None


    def play_wav_buffer(self, wav_data):
        """Play in-memory WAV data"""
        try:
            print("Playing back audio...")
            p = subprocess.Popen(self.playback_cmd + ["-"], stdin=subprocess.PIPE)
            p.stdin.write(wav_data)
            p.stdin.close()
            p.wait()
        except Exception as e:
            print(f"Playback error: {e}")


    def transcribe_wav_buffer(self, wav_data):
        try:
            import numpy as np
            import io

            with open("debug.wav", "wb") as f:
                f.write(wav_data)

            sr, data = read(io.BytesIO(wav_data))

            if data.ndim > 1:
                data = data.mean(axis=1)

            if data.dtype != np.float32:
                data = data.astype(np.float32) / np.iinfo(data.dtype).max

            # Resample using scipy instead of librosa
            if sr != 16000:
                num_samples = int(len(data) * 16000 / sr)
                data = resample(data, num_samples)

            data = np.clip(data, -1.0, 1.0)

            print("Transcribing...")
            result = self.model.transcribe(data, fp16=False, language='en')
            return result["text"]

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Transcription error: {e}")
            return "[Transcription failed]"


    def process_audio(self):
        while True:
            input("\nPress Enter to record...")
            wav_data = self.record_to_wav_buffer(duration=5)

            if wav_data:
                # self.play_wav_buffer(wav_data)
                transcription = self.transcribe_wav_buffer(wav_data)
                print("Transcription:", transcription)
            else:
                print("[No audio recorded]")

if __name__ == "__main__":
    processor = AudioProcessor()
    processor.process_audio()
