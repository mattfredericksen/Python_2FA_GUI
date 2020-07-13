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
        # generate and send the code
        self.code = send_auth_code(self.phone)

        # if the code failed to send, alert the user
        # and return to the login screen
        if not self.code:
            AlertPopup(title='SMS Error',
                       label='Failed to send code',
                       button='Return to Login',
                       on_dismiss=self.logout).open()
        else:
            # set code to expire in 30 seconds
            self.timeout_event = Clock.schedule_once(self.timeout, 30)

    def text_validate(self):
        """On [enter], trigger button if code_field is not empty"""
        if self.code_field.text:
            self.submit_button.trigger_action()

    def verify_code(self):
        if not self.code_field.text:
            return

        self.attempts += 1

        # compare_digest protects against timing attacks
        if secrets.compare_digest(self.code, self.code_field.text):
            self.timeout_event.cancel()
            AlertPopup(title='Success!',
                       label=f'You have been authenticated.',
                       button='Log Out',
                       on_dismiss=self.logout).open()
        elif self.attempts < 3:
            AlertPopup(title='Incorrect Code',
                       label=f'{3 - self.attempts} attempt'
                             f'{"s" if self.attempts < 2 else ""} remaining.',
                       button='Try Again').open()
        else:
            self.timeout_event.cancel()
            AlertPopup(title='Authentication Failed',
                       label='Too many failed attempts.',
                       button='Return to Login',
                       on_dismiss=self.logout).open()

        self.code_field.text = ''

    def timeout(self, dt):
        AlertPopup(title='Authentication Failed',
                   label='The SMS code has expired.',
                   button='Return to Login',
                   on_dismiss=self.logout).open()

    def logout(self, *args):
        self.manager.transition.direction = 'up'
        self.manager.current = 'login'
