# import required modules
from kivymd.app import MDApp
from kivymd.uix.button import MDFloatingActionButton, MDFlatButton,MDRectangleFlatButton
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.icon_definitions import md_icons
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout

# class First_Screen(MDApp):
# 	def build(self):
		
# 		# create screen object
# 		screen = Screen()

# 		bg = Image(source='resources/bg2.png', allow_stretch=True, keep_ratio=False)
# 		screen.add_widget(bg) 

# 		layout = FloatLayout()
	
# 		app_name_label = Label(text="Neuro Lullaby", font_size='40sp', bold=True, size_hint=(None, None), 
#                                pos_hint={'center_x': 0.5, 'top': 0.85}) 
# 		layout.add_widget(app_name_label)

# 	    # create buttons
# 		start_btn = MDRectangleFlatButton(text="Start Story",
# 									font_size='20sp',
# 									pos_hint={'center_x': 0.5, 
# 											'center_y': 0.3},
# 									text_color= "white",
# 									line_color="black",
# 									md_bg_color="pink",
# 									)
		
# 		# add buttons
# 		screen.add_widget(layout)
# 		screen.add_widget(start_btn)
		
# 		return screen

	
# # run application
# First_Screen().run()


class FirstScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set the background image
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

        # Create "Start" button
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


# Define the second screen
class SecondScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        bg = Image(source='resources/sleep.png', allow_stretch=True, keep_ratio=False)
        self.add_widget(bg)

        layout = FloatLayout()

        # Label for the second screen
        next_page_label = Label(
            text="Good Night !",
            font_size='30sp',
            bold=True,
            size_hint=(None, None),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        layout.add_widget(next_page_label)

        # Add layout to the second screen
        self.add_widget(layout)


class DemoApp(MDApp):
    def build(self):
        # Create the ScreenManager
        sm = ScreenManager()

        # Add the screens to the ScreenManager
        sm.add_widget(FirstScreen(name='first'))  # First screen
        sm.add_widget(SecondScreen(name='second'))  # Second screen

        return sm


if __name__ == '__main__':
    DemoApp().run()
