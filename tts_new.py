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

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] ="neurolullaby-e85d795e7662.json"
class TTSStreamer:
    def __init__(self, text, pitch=0.0, speaking_rate=1.0, volume_gain=0.0):
        # Initialize Google Cloud TTS client
        self.lock = threading.Lock() 
        self.client = texttospeech.TextToSpeechClient()
        self.text = text
        self.pitch = pitch
        self.speaking_rate = speaking_rate
        self.volume_gain = volume_gain

        # Queue to store audio chunks for playback
        self.audio_queue = queue.Queue()

        # Condition variable to signal new text being appended
        self.condition = threading.Condition()

        # Event to signal when all chunks have been processed
        self.done_event = threading.Event()

        # Split the initial text into chunks
        self.text_chunks = self.split_text(self.text)

        # Flag to indicate if we should keep generating chunks
        self.keep_running = True

        # Internal thread to handle audio playback
        self.playback_thread = threading.Thread(target=self.play_audio_stream, daemon=True)
        self.playback_thread.start()

        # Start a separate thread for generating TTS chunks
        self.generate_thread = threading.Thread(target=self.generate_chunks, daemon=True)
        self.generate_thread.start()

    def parse_wav_header(self, audio_content):
        with BytesIO(audio_content) as wav_file:
            with wave.open(wav_file, 'rb') as wav:
                channels = wav.getnchannels()
                sample_width = wav.getsampwidth()
                framerate = wav.getframerate()
                n_frames = wav.getnframes()
                audio_data = wav.readframes(n_frames)
        return audio_data, channels, sample_width, framerate

    def play_audio_stream(self):
        try:
            while True:
                audio_content = self.audio_queue.get()
                if audio_content is None:
                    break

                # Notify that this chunk is playing
                self.audio_queue.task_done()

                # Play the audio
                play(audio_content)
        finally:
            print("Audio stream closed")

    def synthesize_speech(self, text_chunk):
        with self.lock:
          input_text = texttospeech.SynthesisInput(text=text_chunk)

          # Configure voice request (e.g., gender and language)
          voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-J",
           )

           # Configure audio output settings and dynamic adjustments
          audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,  # Use linear PCM for streaming playback
            pitch=self.pitch,  # Adjust pitch
            speaking_rate=self.speaking_rate,  # Adjust pace
            # volume_gain_db=self.volume_gain  # Adjust volume
          )

          # Perform TTS synthesis request
          response = self.client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)

           # Add the synthesized audio to the queue for playback
          audio = AudioSegment.from_file(BytesIO(response.audio_content), format="mp3")
          audio += self.volume_gain
          self.audio_queue.put(audio)
          print(f"Queued speech with pitch: {self.pitch}, rate: {self.speaking_rate}, volume: {self.volume_gain}")

    def random_eeg_state(self):
        # Simulating EEG features: focus (0 to 100), relaxation (0 to 100)
        state = random.randint(0, 3)
        return state

    def eeg_to_tts_params(self, state):
        # Map focus to speaking rate (more focus = faster speech)
        self.pitch = -5 + (state / 3) * 5  # Pitch: ranges from -5st to 0st
        self.speaking_rate = 0.7 + (state / 3) * 0.3  # Rate: ranges from 0.7 (slow) to 1.0 (normal)
        self.volume_gain = -16 + (state / 3) * 16  # Volume: ranges from -16dB (quiet) to 0dB (normal)

    def split_text(self, text, chunk_size=100):
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

    def generate_chunks(self):
        while self.keep_running:
            with self.condition:
                while not self.text_chunks and self.keep_running:
                    print("No more chunks. Setting done_event")
                    self.done_event.set()

                    # Wait until new chunks are appended or stop is called
                    self.condition.wait()

                if not self.keep_running:
                    break  # Exit the loop if stopping

                # Process chunks one by one
                while self.text_chunks and self.keep_running:
                    chunk = self.text_chunks.pop(0)

                    # Generate and queue the next chunk with adjusted TTS parameters
                    self.synthesize_speech(chunk)

                    # Wait until the current chunk has started playing before processing the next
                    self.audio_queue.join()

    def update_tts_params(self, state):
        """Update pitch, speaking rate, and volume gain based on EEG state."""
        with self.lock:
          self.eeg_to_tts_params(state)
          print(f"TTS Updated: State={state}, Pitch={self.pitch}, SpeakingRate={self.speaking_rate}, VolumeGain={self.volume_gain}")

    def append_text(self, additional_text):
        """Append more text to the current TTS queue."""
        new_chunks = self.split_text(additional_text)
        with self.condition:
            self.text_chunks.extend(new_chunks)
            # Clear the done event since we have new text to process
            self.done_event.clear()
            # Notify the generator thread that new chunks are available
            self.condition.notify()

    def wait_until_complete(self):
        # Wait until all chunks are processed
        self.done_event.wait()

    def stop(self):
        """Stop the background chunk generator."""
        print("Stopping...")
        self.keep_running = False
        self.audio_queue.put(None)
        with self.condition:
            self.condition.notify()

        self.playback_thread.join()
        self.generate_thread.join()

# Example usage
def tts_new():
    initial_text = """
    In a land far far away there was a glorious kingdom. In the kingdom stood a great castle. 
    And inside the castle lived a handsome Prince. 
    The Prince was sad. 
    He longed for a true Princess to share his castle and kingdom, but he couldn't find one. 
    This was not because there was a lack of Princesses. 
    In fact, the kingdom was full of fair maidens all claiming to be Princesses.
    The Prince scoured the kingdom, meeting every one of these so-called Princesses. 
    But he returned sad and empty handed.
    “It is impossible to tell whether these are true Princesses!” he said to his Father, the King.
    “You must be patient my son. You will know when you know” said the King, with a knowing smile.
    The Prince smiled back, then went to his chamber. 
    That evening a huge storm came.
    Thunder clapped. 
    Lightning flashed. 
    And the rain clattered down on the castle roof like the sound of a thousand horses charging into battle.
    Suddenly, came a loud knock at the castle door. 
    The King put on his robe and opened the door to find a cold, soggy young lady standing in front of him.
    “I am a true Princess,” she said, “Please can I have some dry clothes and a bed for the night?”
    The King let her in.
    “She says she is a true Princess,” said the King to the old Queen-mother.
    The Queen-mother didn't say a word.
    Instead, she thought to herself, “We'll soon see about that”. 
    She then handed the Princess a nightgown and said, “put this on while I prepare your chamber.”
    The Queen-mother began preparing the chamber—but in a very peculiar way.
    First, she took the covers, sheets and mattress off the bed.
    Then she placed a single garden pea on the bedstead.
    And then she laid twenty mattresses on top of the pea taking care to separate each layer with a soft eiderdown quilt.
    After this she replaced the bedclothes on the top mattress and said to the Princess, “Your chamber is ready!”
    The bed was now so high off the ground that the Princess needed to climb a ladder to get into the bed. So the Princess climbed up the ladder, got under the covers and blew out her candle.
    At breakfast the next morning the Queen-mother turned to the Princess and asked, “My dear Princess, how did you sleep?”
    “Oh, not at all well,” said the Princess. “I mean to say, I am extremely grateful for your kindness in putting me up for the night, but there seemed to be something ever so hard and uncomfortable under my mattress. I didn’t sleep a wink.”
    “My my!” replied the Queen-mother, “is that so?”
    The Queen-mother turned to the Prince and said, “I believe we have found your true Princess, for none but a true Princess possesses such a delicate sense to feel a single pea through twenty mattresses and twenty of my finest quilts. You must wed immediately!”
    The Prince was overjoyed.
    He turned to the Princess and said, “Dear Princess, would you do me the great honour of becoming my wife?”
    She blushed, then taking a moment to finish a mouthful of cereal, said, “On one condition.”
    “Anything!” replied the Prince.
    She looked at the Prince with a cheeky grin and said, “That you promise, dear Prince, that from this day forward any pea that should enter this castle is simply for eating. And not for sleeping upon.”
    The Prince looked back at her, chuckled and said, “I promise!”
    The End.

    """
    
    # Initialize TTSStreamer
    tts_streamer = TTSStreamer(initial_text)

    # Simulate appending more text asynchronously
    time.sleep(5)

    # Example of updating TTS params and appending more text
    # new_state = tts_streamer.random_eeg_state()
    # tts_streamer.update_tts_params(new_state)

    # Append more text
    # tts_streamer.append_text("Is this working? I need to double check adding multiple times. I hope there are no concurrency issues.")
    # tts_streamer.append_text("Dylan, this part was added successfully. Thank you for your hard work.")

    # Wait until all checks are processed, then terminate the TTS
    tts_streamer.wait_until_complete()
    tts_streamer.stop()

