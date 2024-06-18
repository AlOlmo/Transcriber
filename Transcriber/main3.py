import speech_recognition as sr
from pydub import AudioSegment, silence
import os
import shutil
from deepmultilingualpunctuation import PunctuationModel
from docx import Document


def check_ffmpeg():
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise EnvironmentError("ffmpeg and/or ffprobe are not installed. Please install them to proceed.")


def split_audio_by_silence(audio_path, min_silence_len=1320, silence_thresh=-40, keep_silence=500):
    audio = AudioSegment.from_mp3(audio_path)
    segments = silence.split_on_silence(audio,
                                        min_silence_len=min_silence_len,
                                        silence_thresh=silence_thresh,
                                        keep_silence=keep_silence)
    segment_paths = []
    for i, segment in enumerate(segments):
        segment_path = f"{os.path.splitext(audio_path)[0]}_segment_{i}.wav"
        segment.export(segment_path, format="wav")
        segment_paths.append(segment_path)
    return segment_paths


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
audio_file_path = 'testFinal.mp3'
docx_file_path = os.path.splitext(audio_file_path)[0] + ".docx"

# Dividir el audio en segmentos basados en pausas de al menos 1 segundo
segments = split_audio_by_silence(audio_file_path)

# Inicializar el reconocedor
recognizer = sr.Recognizer()

# Transcribe cada segmento y concatena los resultados
full_transcription = ""
for wav_path in segments:
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        transcription = recognizer.recognize_google(audio_data, language='es-ES')
        #print(f"Transcription for {wav_path}: {transcription}")
        full_transcription += transcription + " <PAUSE> "  # Marcar las pausas con una etiqueta especial

# Añadir puntuación a la transcripción
punctuated_transcription = add_punctuation(full_transcription)

# Reemplazar las etiquetas de pausa por saltos de línea dobles
formatted_transcription = punctuated_transcription.replace(" <PAUSE>.", "\n\n")
formatted_transcription2 = formatted_transcription.replace(" <PAUSE> ", " ")
formatted_transcription3 = formatted_transcription2.replace(" <PAUSE>,", ",")

# Guardar la transcripción como un documento DOCX
save_as_docx(formatted_transcription3, docx_file_path)

print(formatted_transcription3)
print("Transcription saved to:", docx_file_path)