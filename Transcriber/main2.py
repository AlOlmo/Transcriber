import speech_recognition as sr
from pydub import AudioSegment
import os
import shutil
#from punctuation import PunctuationModel
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline



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
    model_name = "ckiplab/bert-base-chinese-ws"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(model_name)
    nlp = pipeline("ner", model=model, tokenizer=tokenizer)
    punctuated_text = nlp(text)
    return punctuated_text


# Comprobar dependencias
check_ffmpeg()

# Ruta objetivo al archivo mp3
audio_file_path = 'test1.mp3'

# Split the audio into segments of 1 minute each
segments = split_audio(audio_file_path)

# Initialize recognizer
recognizer = sr.Recognizer()

# Transcribe each segment and concatenate the results
full_transcription = ""
for wav_path in segments:
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        transcription = recognizer.recognize_google(audio_data, language='es-ES')
        full_transcription += transcription + " "

# Add punctuation to the transcription
# model = PunctuationModel()
# punctuated_transcription = model.restore_punctuation(full_transcription)

# Add punctuation to the transcription
#punctuated_transcription = add_punctuation(full_transcription)

print(full_transcription)