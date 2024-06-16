import speech_recognition as sr
from pydub import AudioSegment
import os

def split_audio(audio_path, segment_length_ms=60000):
    audio = AudioSegment.from_mp3(audio_path)
    duration_ms = len(audio)
    segments = []
    for start_ms in range(0, duration_ms, segment_length_ms):
        segment = audio[start_ms:start_ms + segment_length_ms]
        segment_path = f"{os.path.splitext(audio_path)[0]}_segment_{start_ms // 1000}.wav"
        segment.export(segment_path, format="wav")
        segments.append(segment_path)
    return segments

# Define the path to the MP3 file
audio_file_path = 'Rehenes de la preocupación.mp3'

# Convert the entire MP3 file to WAV
audio = AudioSegment.from_mp3(audio_file_path)
wav_path = 'Rehenes_de_la_preocupacion.wav'
audio.export(wav_path, format='wav')

# Split the WAV file into segments of 1 minute each
segments = split_audio(wav_path)

# Initialize recognizer
recognizer = sr.Recognizer()

# Transcribe each segment and concatenate the results
full_transcription = ""
for segment_path in segments:
    with sr.AudioFile(segment_path) as source:
        audio_data = recognizer.record(source)
        transcription = recognizer.recognize_google(audio_data, language='es-ES')
        full_transcription += transcription + " "

print(full_transcription)
