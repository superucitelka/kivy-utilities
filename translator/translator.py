import requests
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

Builder.load_file('translator/translator.kv')


class TranslatorScreen(Screen):
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