import os
from moviepy.editor import VideoFileClip, AudioFileClip
import speech_recognition as sr
from gtts import gTTS
from googletrans import Translator
from pydub import AudioSegment
from pydub.utils import which
import time
import wave
import json
import vosk
from vosk import Model, KaldiRecognizer

# Define folder for processed files
PROCESSED_FOLDER = 'processed'

# Set ffmpeg path for pydub
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffmpeg = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

def extract_audio(video_path, audio_path):
    print(f"Extracting audio from {video_path} to {audio_path}")
    try:
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(audio_path, codec='pcm_s16le')
        video.close()
        time.sleep(1)
        print(f"Audio extraction completed successfully.")
    except Exception as e:
        print(f"Error extracting audio: {e}")

def convert_audio_to_mono(audio_path, output_path):
    try:
        audio = AudioSegment.from_wav(audio_path)
        mono_audio = audio.set_channels(1)

        mono_audio.export(output_path, format="wav")
        print(f"Audio converted to mono and saved to {output_path}")
    except Exception as e:
        print(f"Error converting audio to mono: {e}")

def check_and_resample_audio(input_path, output_path, target_rate=16000):
    """Ensure audio is resampled to the target rate."""
    from pydub import AudioSegment
    audio = AudioSegment.from_file(input_path)
    current_rate = audio.frame_rate
    if current_rate != target_rate:
        audio = audio.set_frame_rate(target_rate)
        audio.export(output_path, format="wav")
    else:
        audio.export(output_path, format="wav")

def transcribe_audio(audio_path):
    model_path = "vosk-model-small-en-us-0.15"
    if not os.path.exists(model_path):
        print(f"Model directory does not exist: {model_path}")
        return ""

    mono_audio_path = os.path.join(PROCESSED_FOLDER, "mono_temp_audio.wav")
    resampled_audio_path = os.path.join(PROCESSED_FOLDER, "resampled_temp_audio.wav")

    # Convert the audio to mono
    convert_audio_to_mono(audio_path, mono_audio_path)
    
    # Resample to 16000 Hz if necessary
    check_and_resample_audio(mono_audio_path, resampled_audio_path, target_rate=16000)
    
    try:
        # Load the audio file and prepare it for Vosk
        wf = wave.open(resampled_audio_path, "rb")
        model = vosk.Model(model_path)
        recognizer = vosk.KaldiRecognizer(model, wf.getframerate())

        text = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text += json.loads(result).get('text', '')

        # Finalize the transcription
        final_result = recognizer.FinalResult()
        text += json.loads(final_result).get('text', '')

        return text
    except Exception as e:
        print(f"Error during transcription: {e}")
    return ""
# def transcribe_audio(audio_path):
#     recognizer = sr.Recognizer()
#     with sr.AudioFile(audio_path) as source:
#         audio = recognizer.record(source)
    
#     try:
#         with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
#             temp_audio_path = temp_file.name
#             temp_file.write(audio.get_wav_data())

#         text = recognizer.recognize_google(audio)
#         return text
#     except sr.UnknownValueError:
#         print("Google Speech Recognition could not understand audio")
#     except sr.RequestError as e:
#         print(f"Could not request results from Google Speech Recognition service; {e}")
#     except Exception as e:
#         print(f"Error during transcription: {e}")
#     finally:
#         if temp_audio_path and os.path.exists(temp_audio_path):
#             os.remove(temp_audio_path)

#     return ""

def translate_text(text, target_language='es'):
    translator = Translator()
    translated = translator.translate(text, dest=target_language)
    return translated.text

def text_to_speech(text, audio_path, lang='es'):
    tts = gTTS(text=text, lang=lang)
    tts.save(audio_path)

def adjust_audio_duration(audio_path, target_duration, output_path):
    audio = AudioSegment.from_file(audio_path)
    current_duration = len(audio) / 1000.0
    if current_duration < target_duration:
        silence = AudioSegment.silent(duration=(target_duration - current_duration) * 1000)
        audio = audio + silence
    elif current_duration > target_duration:
        audio = audio[:int(target_duration * 1000)]
    audio.export(output_path, format="mp3")

def merge_audio_with_video(video_path, translated_audio_path, output_path):
    video = VideoFileClip(video_path)

    target_duration = video.duration
    translated_audio_path_adjusted = os.path.join(PROCESSED_FOLDER, "adjusted_" + os.path.basename(translated_audio_path))
    adjust_audio_duration(translated_audio_path, target_duration, translated_audio_path_adjusted)

    translated_audio = AudioFileClip(translated_audio_path_adjusted)
    video = video.set_audio(translated_audio)
    video.write_videofile(output_path, codec='libx264', audio_codec='aac')
    video.close()
    translated_audio.close()

def process_video(video_path, output_path, target_language='es'):
    temp_audio_path = os.path.join(PROCESSED_FOLDER, "temp_audio.wav")
    translated_audio_path = os.path.join(PROCESSED_FOLDER, "translated_audio.mp3")
    
    try:
        if not os.path.exists(PROCESSED_FOLDER):
            os.makedirs(PROCESSED_FOLDER)
        
        extract_audio(video_path, temp_audio_path)
        print(f"Audio extracted to {temp_audio_path}")

        text = transcribe_audio(temp_audio_path)
        print(f"Transcribed Text: {text}")

        translated_text = translate_text(text, target_language)
        print(f"Translated Text: {translated_text}")

        text_to_speech(translated_text, translated_audio_path, lang=target_language)
        print(f"Translated audio saved to {translated_audio_path}")

        merge_audio_with_video(video_path, translated_audio_path, output_path)
        print(f"Processed video saved to {output_path}")

    except Exception as e:
        print(f"Error during processing: {e}")

    finally:
        if os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
                print(f"Removed {temp_audio_path}")
            except Exception as e:
                print(f"Error removing {temp_audio_path}: {e}")

        if os.path.exists(translated_audio_path):
            try:
                os.remove(translated_audio_path)
                print(f"Removed {translated_audio_path}")
            except Exception as e:
                print(f"Error removing {translated_audio_path}: {e}")
# Example usage
# process_video('uploads/your_video.mp4', 'processed/translated_video.mp4', target_language='hi')
