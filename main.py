from kivy import Config
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition


from menu.menu import MenuScreen
from translator.translator import TranslatorScreen


class UtilitiesApp(App):

    def build(self):
        Config.set('graphics', 'resizable', '1')
        # Create the screen manager
        sm = ScreenManager(transition=NoTransition())
        sm.transition.duration = .2
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(TranslatorScreen(name='translator'))

        return sm


if __name__ == '__main__':
    UtilitiesApp().run()

