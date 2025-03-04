import time
import random
from pydub import AudioSegment
from pydub.playback import play
from google.cloud import texttospeech
import re
import threading
import queue
from io import BytesIO
import wave
import os

# Initialize Google Cloud TTS client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] ="neurolullaby-e85d795e7662.json"
client = texttospeech.TextToSpeechClient()

# Create a queue to store audio chunks for playback
audio_queue = queue.Queue()

def parse_wav_header(audio_content):
    with BytesIO(audio_content) as wav_file:
        with wave.open(wav_file, 'rb') as wav:
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            framerate = wav.getframerate()
            n_frames = wav.getnframes()
            audio_data = wav.readframes(n_frames)
    return audio_data, channels, sample_width, framerate

# Modify the play_audio_stream function
def play_audio_stream():
    stream = None
    try:
        while True:
            audio_content = audio_queue.get()
            if audio_content is None:
                break

            # Notify that this chunk is playing
            audio_queue.task_done()

            # Play the audio
            play(audio_content)
    finally:
        if stream:
            stream.stop_stream()
            stream.close()

# Function to synthesize speech using dynamic TTS parameters
def synthesize_speech(text_chunk, pitch, speaking_rate, volume_gain):
    input_text = texttospeech.SynthesisInput(text=text_chunk)

    # Configure voice request (e.g., gender and language)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Wavenet-J",
    )

    # Configure audio output settings and dynamic adjustments
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,  # Use linear PCM for streaming playback
        pitch=pitch,  # Adjust pitch
        speaking_rate=speaking_rate,  # Adjust pace
        # volume_gain_db=volume_gain  # Adjust volume
    )

    # Perform TTS synthesis request
    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)

    # Add the synthesized audio to the queue for playback
    audio = AudioSegment.from_file(BytesIO(response.audio_content), format="mp3")
    audio += volume_gain
    audio_queue.put(audio)
    print(f"Queued speech with pitch: {pitch}, rate: {speaking_rate}, volume: {volume_gain}")

# Placeholder function to simulate EEG data collection
# In a real-world scenario, you would integrate with an EEG API
def get_eeg_data():
    # Simulating EEG features: focus (0 to 100), relaxation (0 to 100)
    focus_level = random.randint(0, 100)
    relaxation_level = random.randint(0, 100)
    return focus_level, relaxation_level

# Function to map EEG data to TTS parameters
def eeg_to_tts_params(focus, relaxation):
    # Map focus to speaking rate (more focus = faster speech)
    pitch = -5 + (relaxation / 100) * 5  # Pitch: ranges from -5st to 0st
    rate = 0.7 + (focus / 100) * 0.3  # Rate: ranges from 0.7 (slow) to 1.0 (normal)
    volume = -16 + (relaxation / 100) * 16  # Volume: ranges from -10dB (quiet) to 0dB (normal)
    
    return pitch, rate, volume

# Function to split larger text into chunks for streaming
def split_text(text, chunk_size=100):
    # Split text by sentence or fixed word count to avoid cutting sentences in half
    sentences = re.split(r'(?<=[.!?]) +', text)  # Split on punctuation with a space
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    
    # Append the final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

# Function to manage chunk generation and EEG-based adjustments in real-time
def generate_chunks(text_chunks):
    for i, chunk in enumerate(text_chunks):
        # Collect EEG data for the current chunk
        focus, relaxation = get_eeg_data()
        print(f"EEG Focus: {focus}, Relaxation: {relaxation}")
        
        # Map EEG data to TTS parameters
        pitch, speaking_rate, volume_gain = eeg_to_tts_params(focus, relaxation)
        
        # Generate and queue the next chunk with adjusted TTS parameters
        synthesize_speech(chunk, pitch, speaking_rate, volume_gain)
        
        # Wait until the current chunk has started playing before generating the next one
        audio_queue.join()

# Main function to orchestrate the real-time TTS streaming process
def tts():
    text = """
    In a land far far away there was a glorious kingdom. In the kingdom stood a great castle. 
    And inside the castle lived a handsome Prince. 
    The Prince was sad. 
    He longed for a true Princess to share his castle and kingdom, but he couldn't find one. 
    This was not because there was a lack of Princesses. 
    In fact, the kingdom was full of fair maidens all claiming to be Princesses.
    The Prince scoured the kingdom, meeting every one of these so-called Princesses. 
    But he returned sad and empty handed.
    """
    
    # Split the large text into smaller chunks for smoother streaming
    chunks = split_text(text, chunk_size=120)
    
    # Start a separate thread for audio playback so that it runs concurrently
    playback_thread = threading.Thread(target=play_audio_stream, daemon=True)
    playback_thread.start()
    
    # Generate and queue chunks dynamically as they are played
    generate_chunks(chunks)
    
    # Wait until all audio chunks have been played before terminating
    audio_queue.join()
    audio_queue.put(None)  # Signal the playback thread to exit

# if __name__ == "__main__":
#     try:
#         tts()
#     finally:
#         audio_queue.put(None)  # Send a signal to terminate the playback thread
