import os
from moviepy.editor import VideoFileClip, AudioFileClip
import speech_recognition as sr
from gtts import gTTS
from googletrans import Translator
from pydub import AudioSegment
from pydub.utils import which
import time
from pydub.silence import detect_nonsilent
import librosa
import soundfile as sf
from transformers import AutoProcessor, WhisperForConditionalGeneration

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
    audio = AudioSegment.from_file(input_path)
    current_rate = audio.frame_rate
    if current_rate != target_rate:
        audio = audio.set_frame_rate(target_rate)
        audio.export(output_path, format="wav")
    else:
        audio.export(output_path, format="wav")

def transcribe_audio(audio_path):
    # Paths for intermediate audio processing
    mono_audio_path = os.path.join(PROCESSED_FOLDER, "mono_temp_audio.wav")
    resampled_audio_path = os.path.join(PROCESSED_FOLDER, "resampled_temp_audio.wav")

    # Convert audio to mono and export as MP3
    convert_audio_to_mono(audio_path, mono_audio_path)
    # Resample audio to 16kHz and export as MP3
    check_and_resample_audio(mono_audio_path, resampled_audio_path, target_rate=16000)

    print(f"Checking if resampled audio exists: {os.path.exists(resampled_audio_path)}")

    processor = AutoProcessor.from_pretrained("openai/whisper-small.en")  # Try "whisper-small.en" for better accuracy
    model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small.en")

    # Check if the file exists
    if not os.path.exists(resampled_audio_path):
        print(f"Error: The file '{resampled_audio_path}' does not exist.")
    else:
    # Load audio file
        audio_array, sampling_rate = librosa.load(resampled_audio_path, sr=16000)

    # Split audio into 30-second chunks
        chunk_size = 30 * sampling_rate  # 30 seconds worth of audio
        audio_chunks = [audio_array[i:i + chunk_size] for i in range(0, len(audio_array), chunk_size)]

        # Process each chunk separately
        full_transcription = []

        for chunk in audio_chunks:
            inputs = processor(chunk, sampling_rate=16000, return_tensors="pt", padding=True)
            input_features = inputs.input_features
            # Generate transcription for each chunk
            generated_ids = model.generate(input_features=input_features, max_length=500, num_beams=5)
            transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            full_transcription.append(transcription)

        # Join all chunk transcriptions
        final_transcription = " ".join(full_transcription)
        # Print the final transcription
        return final_transcription


def translate_text(text, target_language='es'):
    translator = Translator()
    translated = translator.translate(text, dest=target_language)
    return translated.text

def calculate_audio_start_time(audio_path, silence_thresh=-50, chunk_size=10):
    try:
        # Load the original audio
        audio = AudioSegment.from_file(audio_path)

        # Detect non-silent parts of the audio
        nonsilent_ranges = detect_nonsilent(audio, min_silence_len=chunk_size, silence_thresh=silence_thresh)

        # Check if any non-silent portion is detected
        if nonsilent_ranges:
            # Get the start time of the first non-silent range in milliseconds (start of the first non-silent section)
            audio_start_time = nonsilent_ranges[0][0] / 1000.0  # Convert to seconds
        else:
            # If no non-silent range is found, assume start time as 0
            audio_start_time = 0.0

        print(f"Calculated audio start time: {audio_start_time} seconds")
        return audio_start_time
    except Exception as e:
        print(f"Error calculating audio start time: {e}")
        return 0.0

def text_to_speech(text, audio_path, target_duration, lang='es', start_delay=0.0):
    # Step 1: Convert the text to speech using gTTS
    tts = gTTS(text=text, lang=lang)
    
    # Step 2: Save the TTS output as a temporary file (e.g., as .wav)
    temp_audio_path = audio_path.replace(".mp3", ".wav")
    tts.save(temp_audio_path)
    
    # Step 3: Load the generated speech audio using librosa for time-stretching
    y, sr = librosa.load(temp_audio_path, sr=None)
    speech_duration = librosa.get_duration(y=y, sr=sr)
    
    # Step 4: Calculate the available duration after applying the start delay
    remaining_duration = target_duration - start_delay
    
    # Step 5: Adjust the speech speed using time-stretching without changing pitch
    if remaining_duration > 0 and speech_duration != remaining_duration:
        stretch_factor = speech_duration / remaining_duration
        y_stretched = librosa.effects.time_stretch(y, rate=stretch_factor)
        
        # Save the time-stretched audio to a new file
        stretched_audio_path = temp_audio_path.replace(".wav", "_stretched.wav")
        sf.write(stretched_audio_path, y_stretched, sr)
    else:
        stretched_audio_path = temp_audio_path  # No stretching needed

    # Step 6: Load the time-stretched audio with pydub
    speech_audio = AudioSegment.from_file(stretched_audio_path)
    
    # Step 7: Add the start delay as silence (if start_delay > 0)
    if start_delay > 0:
        silence = AudioSegment.silent(duration=start_delay * 1000)  # convert seconds to milliseconds
        speech_audio = silence + speech_audio  # Add the silence before the speech audio
    
    # Step 8: Export the final audio with the delay and adjusted speed to the desired output path (as mp3)
    speech_audio.export(audio_path, format="mp3")
    
    # Optional: Clean up temporary files
    os.remove(temp_audio_path)
    if stretched_audio_path != temp_audio_path:
        os.remove(stretched_audio_path)


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

        if not os.path.exists(temp_audio_path):
            raise Exception(f"Audio extraction failed, file not found: {temp_audio_path}")

        text = transcribe_audio(temp_audio_path)
        if not text:
            raise Exception("Transcription failed or returned empty text.")
        print(f"Transcribed Text: {text}")

        translated_text = translate_text(text, target_language)
        print(f"Translated Text: {translated_text}")
        
        # male_speaker_embedding = torch.randn(1, 512)  # Replace with real male embedding
        # female_speaker_embedding = torch.randn(1, 512)  # Replace with real female embedding

        
        # Calculate the audio start time from the original audio
        audio_start_time = calculate_audio_start_time(temp_audio_path)

        # Load the original audio to get the target duration
        original_audio = AudioSegment.from_file(temp_audio_path)
        target_duration = len(original_audio) / 1000.0  # Duration in seconds

        # Call the text-to-speech function with the calculated start delay
        text_to_speech(translated_text, translated_audio_path, target_duration, lang=target_language, start_delay=audio_start_time)
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

        # if os.path.exists(translated_audio_path):
        #     try:
        #         os.remove(translated_audio_path)
        #         print(f"Removed {translated_audio_path}")
        #     except Exception as e:
        #         print(f"Error removing {translated_audio_path}: {e}")
# Example usage
# process_video('uploads/your_video.mp4', 'processed/translated_video.mp4', target_language='hi')
