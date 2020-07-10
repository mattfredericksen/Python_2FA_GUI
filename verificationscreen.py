from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
import secrets
import db_stuff


class VerificationScreen(Screen):
    phone = StringProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.code = ''

    def on_pre_enter(self, *args):
        # TODO: catch exceptions
        # self.code = db_stuff.send_auth_code(self.phone)
        self.code = '0'

    def text_validate(self):
        if self.code_field.text:
            self.submit_button.trigger_action()

    def verify_code(self):
        if secrets.compare_digest(self.code, self.ids.code_field.text):
            print('success')
        else:
            print('fail')
