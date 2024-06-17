import speech_recognition as sr
from pydub import AudioSegment
import os
import shutil
#from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from deepmultilingualpunctuation import PunctuationModel

def check_ffmpeg():
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise EnvironmentError("ffmpeg and/or ffprobe are not installed. Please install them to proceed.")

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

def add_punctuation(text):
    model = PunctuationModel()
    punctuated_text = model.restore_punctuation(text)
    return punctuated_text

# Comprobar dependencias
check_ffmpeg()

# Ruta objetivo al archivo mp3
audio_file_path = 'test1.mp3'

# Dividir el audio en segmentos de 1 minuto cada uno
segments = split_audio(audio_file_path)

# Inicializar el reconocedor
recognizer = sr.Recognizer()

# Transcribir cada segmento y concatenar los resultados
full_transcription = ""
for wav_path in segments:
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        transcription = recognizer.recognize_google(audio_data, language='es-ES')

        # Agregar un marcador para pausas largas
        pauses = transcription.split()
        for i in range(len(pauses)):
            if len(pauses[i]) > 0 and pauses[i][-1] in ['.', '!', '?']:
                pauses[i] += '\n\n'  # Puntos y aparte para pausas largas

        full_transcription += " ".join(pauses) + " "

# Agregar puntuación a la transcripción
punctuated_transcription = add_punctuation(full_transcription)

print(punctuated_transcription)
