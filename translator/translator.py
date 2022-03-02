import requests
from googletrans import Translator
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from gtts import gTTS
from kivy.uix.slider import Slider
from kivy.factory import Factory


Builder.load_file('translator/translator.kv')


class PopupBox(Popup):
    pop_up_text = ObjectProperty()
    def update_pop_up_text(self, p_message):
        self.pop_up_text.text = p_message


class PlaySlider(Slider):
    sound = ObjectProperty(None)

    def on_touch_move(self, touch):
        print(App.get_running_app().root.children[0].lang)
        # Když byl zaregistrován dotyk spojený s tažením
        if touch.grab_current == self:
            # volání metody předka a uložení návratové hodnoty
            ret_val = super(PlaySlider, self).on_touch_up(touch)

            # vyhledání pozice ve zvukovém souboru podle pozice ukazatele slideru
            self.sound.seek(self.max * self.value_normalized)

            # jestliže došlo k zastavení přehrávání zvuku, bude přehrávání nastaveno na začátek
            if self.sound.state == 'stop':
                 App.get_running_app().root.children[0].stop_player(self.lang)

            # vrací uloženou návratovou hodnotu
            return ret_val
        # V případě pouhého dotyku
        else:
            # pouze volání metody předka bez změny pozice ve zvukovém souboru
            return super(PlaySlider, self).on_touch_up(touch)


class LangButton(Button):
    def __init__(self, lang, **kwargs):
        super(LangButton, self).__init__(**kwargs)
        self.text = lang
        self.size_hint_y = None
        self.height = 44

    def on_release(self):
        self.parent.parent.select(self.text)


class LanguageDropDown(DropDown):
    languages = ['cs', 'en', 'de', 'fr', 'ru', 'pl', 'it', 'es', 'pt', 'sk', 'ar', 'ja', 'sv', 'no', 'fi', 'da', 'nl']

    def __init__(self, **kwargs):
        super(LanguageDropDown, self).__init__(**kwargs)
        for lang in self.languages:
            # btn = Button(text=lang, size_hint_y=None, height=44)
            # btn.bind(on_release=lambda btn: self.select(btn.text))
            btn = LangButton(lang)
            self.add_widget(btn)

    def on_select(self, data):
        self.attach_to.text = data


class TranslatorScreen(Screen):
    language_dropdown = LanguageDropDown()
    timer = None
    lang = None
    slider = None

    def lindat_translate(self):
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

    def google_translate(self):
        src = self.ids['src'].text
        tgt = self.ids['tgt'].text
        text = self.ids['src_text'].text
        trans = Translator()
        result = trans.translate(text, src=src, dest=tgt)
        return result.text

    def text_to_speech(self, lang, txt):
        tts = gTTS(text=self.ids[txt].text, lang=self.ids[lang].text, slow=False)
        tts.speed = .5
        tts.save(f'tts-{self.ids[lang].text}.mp3')
        self.ids[f'{lang}_play'].disabled = False
        self.ids[f'{lang}_stop'].disabled = False
        self.ids[f'{lang}_slider'].disabled = False
        self.ids[f'{lang}_slider'].sound = SoundLoader.load(f'tts-{self.ids[lang].text}.mp3')
        self.stop_player(lang)

    def start_player(self, lang):
        if self.slider:
            self.slider.sound.stop()
            self.ids[f'{self.lang}_play'].source = 'resources/img/play.png'
        if lang != self.lang:
            self.lang = lang
            self.slider = self.ids[f'{lang}_slider']
            # self.slider.sound = SoundLoader.load(f'tts-{self.ids[lang].text}.mp3')

        if self.slider.sound:
            self.slider.max = self.slider.sound.length
            # self.slider.sound.pitch = .5
            self.slider.sound.play()
            self.slider.sound.seek(self.slider.value)
            self.ids[f'{lang}_play'].source = 'resources/img/pause.png'

            if self.timer is None:
                self.timer = Clock.schedule_interval(self.update_slider, 0.1)

    def update_slider(self, dt):
        # update slider
        self.slider.value = self.slider.sound.get_pos()
        self.ids[f'{self.lang}_time'].text = f'{int(self.slider.value / 60)}:{str(int(self.slider.value) % 60).zfill(2)}'

        # if the sound has finished, stop the updating
        if self.slider.sound.state == 'stop':
            self.timer.cancel()
            self.timer = None
            print(self.slider.sound.length, self.slider.sound.get_pos())
            if self.slider.sound.get_pos() > self.slider.sound.length - 0.5:
                self.stop_player(self.lang)

    def pause_player(self, lang):
        if self.slider == self.ids[f'{lang}_slider'] and self.slider.sound:
            self.ids[f'{lang}_play'].source = 'resources/img/play.png'
            self.slider.sound.stop()

    def stop_player(self, lang):
        if self.slider == self.ids[f'{lang}_slider'] and self.slider.sound:
            self.ids[f'{lang}_play'].source = 'resources/img/play.png'
            self.slider.sound.stop()
            self.slider.sound.seek(0)
            self.slider.value = 0
            self.ids[f'{self.lang}_time'].text = '0:00'

    def show_popup(self, message):
        self.pop_up = Factory.PopupBox()
        self.pop_up.update_pop_up_text(message)
        self.pop_up.open()
