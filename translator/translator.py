import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen
from gtts import gTTS
from kivy.uix.slider import Slider


Builder.load_file('translator/translator.kv')


class PlaySlider(Slider):
    sound = ObjectProperty(None)

    def on_touch_move(self, touch):
        # Když byl zaregistrován dotyk spojený s tažením
        if touch.grab_current == self:
            # volání metody předka a uložení návratové hodnoty
            ret_val = super(PlaySlider, self).on_touch_up(touch)

            # vyhledání pozice ve zvukovém souboru podle pozice ukazatele slideru
            self.sound.seek(self.max * self.value_normalized)

            # jestliže došlo k zastavení přehrávání zvuku, bude přehrávání nastaveno na začátek
            if self.sound.state == 'stop':
                App.get_running_app().root.children[0].start_player()

            # vrací uloženou návratovou hodnotu
            return ret_val
        # V případě pouhého dotyku
        else:
            # pouze volání metody předka bez změny pozice ve zvukovém souboru
            return super(PlaySlider, self).on_touch_up(touch)


class LanguageDropDown(DropDown):
    def on_select(self, data):
        self.attach_to.text = data


class TranslatorScreen(Screen):
    language_dropdown = LanguageDropDown()
    timer = None
    slider = None
    sound = None

    def translate(self):
        src = self.ids['src'].text
        tgt = self.ids['tgt'].text
        text = self.ids['src_text'].text
        apiurl = f'https://lindat.mff.cuni.cz/services/translation/api/v2/languages/?src={src}&tgt={tgt}'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {"input_text": text}
        res = requests.post(apiurl, data=data, headers=headers)
        result = ''
        for r in res.json():
            result += r + ' '
        return result

    def text_to_speech(self, lang, txt):
        tts = gTTS(text=self.ids[txt].text, lang=self.ids[lang].text, slow=False)
        tts.speed = .5
        tts.save(f'tts-{self.ids[lang].text}.mp3')
        self.slider = self.ids[f'{lang}_slider']
        self.sound = SoundLoader.load(f'tts-{self.ids[lang].text}.mp3')
        self.slider.sound = self.sound

    def start_player(self, *args):
        if self.sound:
            print("Sound found at %s" % self.sound.source)
            print("Sound is %.3f seconds" % self.sound.length)
            self.slider.max = self.sound.length
            self.sound.pitch = .5
            self.sound.play()

            if self.timer is None:
                self.timer = Clock.schedule_interval(self.update_slider, 0.1)

    def update_slider(self, dt):
        # update slider
        self.slider.value = self.sound.get_pos()

        # if the sound has finished, stop the updating
        if self.sound.state == 'stop':
            self.timer.cancel()
            self.timer = None

    def pause_player(self):
        if self.sound:
            self.sound.stop()

    def stop_player(self):
        if self.sound:
            self.sound.stop()
            self.sound.seek(0)
            self.slider.value = 0