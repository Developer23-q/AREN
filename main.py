from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from addsub import ArenMathEngine  # Import your state engine

class HomeScreen(Screen):
    def __init__(self, engine, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Aesthetic Header (Placeholder for your logo)
        layout.add_widget(MDLabel(text="AREN", font_style="H3", halign="center"))
        
        # Operation Grid Panels
        add_btn = MDRaisedButton(text="+ ADDITION", size_hint=(1, 0.2))
        add_btn.bind(on_release=lambda x: self.start_op("ADDITION"))
        
        sub_btn = MDRaisedButton(text="- SUBTRACTION", size_hint=(1, 0.2))
        sub_btn.bind(on_release=lambda x: self.start_op("SUBTRACTION"))
        
        # Coming Soon Multi/Div Buttons
        mul_btn = MDRaisedButton(text="× MULTIPLICATION (Coming Soon)", size_hint=(1, 0.2), md_bg_color=(0.5, 0.5, 0.5, 1))
        
        layout.add_widget(add_btn)
        layout.add_widget(sub_btn)
        layout.add_widget(mul_btn)
        self.add_widget(layout)

    def start_op(self, op_type):
        self.engine.select_operation(op_type)
        # Shift screen manager to the Practice Screen layout
        self.manager.current = 'practice'

class ArenApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        
        # Initialize your engine
        self.engine = ArenMathEngine()
        
        sm = ScreenManager()
        sm.add_widget(HomeScreen(self.engine, name='home'))
        # You will append your practice and breakdown screens right here...
        
        return sm

if __name__ == "__main__":
    ArenApp().run()