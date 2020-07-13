from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from .alertpopup import AlertPopup


class PasswordInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.timeout_trigger = Clock.create_trigger(self.timeout, 30)

    def on_text(self, instance, value):
        # reset the timeout when the user interacts with the field
        self.timeout_trigger.cancel()
        if value:
            self.timeout_trigger()

    def timeout(self, dt):
        self.text = ''
        AlertPopup(title='Timeout',
                   label='Password cleared for security purposes.',
                   button='Dismiss').open()
