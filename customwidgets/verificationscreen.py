"""
This module contains the VerificationScreen widget used by SecureLoginApp.

VerificationScreen handles sends a random code to the user via SMS
and asks them to enter it, providing two-factor authentication.

The last 4 digits of the phone number to which the code has been
sent will be displayed on this screen.
"""

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.clock import Clock
from customwidgets.alertpopup import AlertPopup
import secrets
from authcode import send_auth_code


class VerificationScreen(Screen):
    """Screen widget for verifying a log in attempt"""

    phone = StringProperty()

    def on_pre_enter(self, *args):
        """Sends SMS and performs setup"""
        # fail after too many attempts
        self.attempts = 0
        # to handle situations with more than one popup
        self.popup = None
        # generate and send the code
        self.code = send_auth_code(self.phone)

        # if the code failed to send, alert the user
        # and return to the login screen
        if not self.code:
            popup = AlertPopup(title='SMS Error',
                               label='Failed to send code',
                               button='Return to Login')
            popup.bind(on_dismiss=self.logout)
        else:
            # set code to expire in 30 seconds
            self.timeout_event = Clock.schedule_once(self.timeout, 30)

    def text_validate(self):
        """On [enter], trigger button if code_field is not empty"""
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

    def timeout(self, dt):
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



