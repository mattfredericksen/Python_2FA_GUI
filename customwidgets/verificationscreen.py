from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from customwidgets.alertpopup import AlertPopup
from kivy.clock import Clock
import secrets
from authcode import send_auth_code


class VerificationScreen(Screen):
    phone = StringProperty()

    def on_pre_enter(self, *args):
        self.attempts = 0
        self.popup = None
        self.code = send_auth_code(self.phone)
        if not self.code:
            popup = AlertPopup(title='SMS Error',
                               label='Failed to send code',
                               button='Return to Login')
            popup.bind(on_dismiss=self.logout)
        else:
            # set code to expire in 30 seconds
            self.timeout_event = Clock.schedule_once(self.code_timeout, 30)

    def text_validate(self):
        if self.code_field.text and not self.popup:
            self.submit_button.trigger_action()

    def verify_code(self):
        if not self.code_field.text:
            return

        self.attempts += 1

        # compare_digest protects against timing attacks
        if secrets.compare_digest(self.code, self.code_field.text):
            Clock.unschedule(self.timeout_event)
            popup = AlertPopup(title='Success!',
                               label=f'You have been authenticated.',
                               button='Log Out')
            popup.bind(on_dismiss=self.logout)
            popup.open()

        elif self.attempts < 3:
            popup = AlertPopup(title='Incorrect Code',
                               label=f'{3 - self.attempts} attempt'
                                     f'{"s" if self.attempts < 2 else ""} remaining.',
                               button='Try Again')
            popup.bind(on_open=self.popup_opened, on_dismiss=self.popup_dismissed)
            popup.open()

        else:
            Clock.unschedule(self.timeout_event)
            popup = AlertPopup(title='Authentication Failed',
                               label='Too many failed attempts.',
                               button='Return to Login')
            popup.bind(on_dismiss=self.logout)
            popup.open()

        self.code_field.text = ''

    def code_timeout(self, dt):
        popup = AlertPopup(title='Authentication Failed',
                           label='The SMS code has expired.',
                           button='Return to Login')
        popup.bind(on_open=self.popup_opened, on_dismiss=self.logout)
        popup.open()

    def logout(self, *args):
        self.manager.transition.direction = 'up'
        self.manager.current = 'login'

    def popup_opened(self, popup):
        if self.popup:
            self.popup.dismiss()
        self.popup = popup

    def popup_dismissed(self, popup):
        self.popup = None
        self.code_field.focus = True



