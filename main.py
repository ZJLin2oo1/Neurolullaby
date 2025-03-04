# import required modules
from kivymd.app import MDApp
from kivymd.uix.button import MDFloatingActionButton, MDFlatButton,MDRectangleFlatButton
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.icon_definitions import md_icons
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
import cmsn_python.examples.gui.gui as bci
from kivy.clock import Clock
import sys
import multiprocessing
import threading
from tts_new import TTSStreamer,tts_new

class FirstScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Setting the background image
        bg = Image(source='resources/bg2.png', allow_stretch=True, keep_ratio=False)
        self.add_widget(bg)

        layout = FloatLayout()

        app_name_label = Label(
            text="Neuro Lullaby",
            font_size='40sp',
            bold=True,
            size_hint=(None, None),
            pos_hint={'center_x': 0.5, 'top': 0.85}
        )
        layout.add_widget(app_name_label)

        # Story Start button
        start_btn = MDRectangleFlatButton(
            text="Start Story",
            font_size='20sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.3},
            text_color="white",
            line_color="black",
            md_bg_color="pink",
            on_release=self.go_to_next_screen  # Link to the next screen on click
        )
        layout.add_widget(start_btn)

        # Add layout to the screen
        self.add_widget(layout)

    def go_to_next_screen(self, instance):
        # Change the current screen to 'second'
        self.manager.current = 'second'


# Second screen
class SecondScreen(Screen):
    def __init__(self,update_tts_params ,start_tts_streamer,**kwargs):
        super().__init__(**kwargs)
        self.update_tts_params_function = update_tts_params 
        self.start_tts_streamer_function = start_tts_streamer
        self.deeply_relaxed_timer = 0  # Timer to track how long "Deeply Relaxed" state lasts
        self.is_deeply_relaxed = False  # Boolean flag for deeply relaxed state
        bg = Image(source='resources/Front_Page_bg.png', allow_stretch=True, keep_ratio=False)
        self.add_widget(bg)

        layout = FloatLayout()

        # Label for the second screen
        self.next_page_label = Label(
            text="Brain Status",
            font_size='30sp',
            bold=True,
            size_hint=(None, None),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        layout.add_widget(self.next_page_label)

        # Add layout to the second screen
        self.add_widget(layout)

    def update_meditation_label(self, meditation_value):
        if meditation_value <= 30:
            meditation_label = "Active"
            self.deeply_relaxed_timer = 0 
            brain_state=3
        elif 30 < meditation_value <= 60:
            meditation_label = "Calm"
            brain_state=2
        elif 60 < meditation_value <= 80:
            meditation_label = "Relaxed"
            self.deeply_relaxed_timer = 0 
            brain_state=1
        else:
            meditation_label = "Deeply Relaxed"
            self.deeply_relaxed_timer = 0 
            brain_state=0
            self.is_deeply_relaxed = True
            self.deeply_relaxed_timer += 1  # Increment timer for every call 

            if self.deeply_relaxed_timer >= 10:  # If "Deeply Relaxed" for 10 seconds
                self.go_to_next_screen()

        self.next_page_label.text = f"Score: {int(meditation_value)}\nRelaxation State: {meditation_label}"
        self.update_tts_params_function(brain_state)

    def on_enter(self):
        initial_text = """In a land far far away there was a glorious kingdom. In the kingdom stood a great castle. 
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
        The End."""
        self.start_tts_streamer_function(initial_text)


    def go_to_next_screen(self):
        # Transition to the next screen (e.g., GoodNight Screen)
        self.manager.current = 'last'


# GoodNight Screen
class LastScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        bg = Image(source='resources/sleep.png', allow_stretch=True, keep_ratio=False)
        self.add_widget(bg)

        layout = FloatLayout()

        # Label for the good night screen
        next_page_label = Label(
            text="Good Night !",
            font_size='30sp',
            bold=True,
            size_hint=(None, None),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        layout.add_widget(next_page_label)

        # Add layout to the goodNight Screen
        self.add_widget(layout)

class NeuroLullaby(MDApp):
    def build(self):
        self.queue = multiprocessing.Queue()
        self.tts_streamer = None 
        # Creating the ScreenManager
        sm = ScreenManager()
        self.bci_process = multiprocessing.Process(target=bci.run_bci_app, args=(self.queue,))
        self.bci_process.start()
        # Adding the screens to the ScreenManager
        sm.add_widget(FirstScreen(name='first'))  # First screen
        self.second_screen = SecondScreen(update_tts_params=self.update_tts_params,start_tts_streamer=self.start_tts_streamer,name='second')  
        # self.second_screen = SecondScreen(name='second')  
        sm.add_widget(self.second_screen)  # Second screen
        Clock.schedule_interval(self.update_meditation_label,1) 
        sm.add_widget(LastScreen(name='last'))
        return sm
    
    def update_meditation_label(self, dt):
         if not self.queue.empty():
           meditation_label = self.queue.get()  # Get meditation label from the queue
           self.second_screen.update_meditation_label(meditation_label)
           print(f"Received meditation label: {meditation_label}")
         else:
            print("Queue is empty") 

    def start_tts_streamer(self, initial_text):
        """Initialize and start the TTS streamer."""
        self.tts_streamer = TTSStreamer(initial_text)

    def update_tts_params(self,brain_state):
        if self.tts_streamer:
            self.tts_streamer.update_tts_params(brain_state)

    def stop_tts_streamer(self):
        """Stop the TTS streamer."""
        if self.tts_streamer:
            self.tts_streamer.stop()

    def stop_tts_and_bci(self):
        # Stop TTS and BCI processes
        print("Stopping TTS and BCI...")
        # audio_queue.put(None)  # Signal the TTS thread to stop
        if self.tts_streamer:
            self.tts_streamer.stop()
        if self.bci_process is not None:
            self.bci_process.terminate()  # Stop the BCI process
            self.bci_process.join()

    def on_stop(self):
        self.stop_tts_and_bci()


if __name__ == '__main__':
    NeuroLullaby().run()
