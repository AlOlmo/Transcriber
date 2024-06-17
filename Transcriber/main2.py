import speech_recognition as sr
from pydub import AudioSegment
import os
import shutil
#from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from deepmultilingualpunctuation import PunctuationModel
from docx import Document

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

def save_as_docx(text, output_path):
    doc = Document()
    paragraphs = text.split("\n\n")
    for para in paragraphs:
        doc.add_paragraph(para)
    doc.save(output_path)


# Comprobar dependencias
check_ffmpeg()

# Ruta objetivo al archivo mp3
audio_file_path = 'test3.mp3'
docx_file_path = os.path.splitext(audio_file_path)[0] + ".docx"

# Dividir el audio en segmentos de 1 minuto cada uno
segments = split_audio(audio_file_path)

# Inicializar el reconocedor
recognizer = sr.Recognizer()

# Transcribe each segment and concatenate the results
full_transcription = ""
for wav_path in segments:
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        transcription = add_punctuation(recognizer.recognize_google(audio_data, language='es-ES'))

        # Add double newline after every 5 consecutive dots
        dots_count = 0
        transcribed_text = ""
        for char in transcription:
            transcribed_text += char
            if char == '.':
                dots_count += 1
                if dots_count == 5:
                    transcribed_text += '\n\n'
                    dots_count = 0

        full_transcription += transcribed_text + " "

# Add punctuation to the transcription
#punctuated_transcription = add_punctuation(full_transcription)

# Save the transcription as a DOCX document
save_as_docx(full_transcription, docx_file_path)

print(full_transcription)
print("Transcription saved to:", docx_file_path)
