"""
This module contains the LoginScreen widget used by SecureLoginApp.

LoginScreen handles attempts to log in, moving the user to
VerificationScreen if the username and password are valid.
"""

from kivy.uix.screenmanager import Screen
from customwidgets.alertpopup import AlertPopup
from account_management import login, AccountError


class LoginScreen(Screen):
    """Screen Widget for logging in to an account"""

    def text_validate(self):
        """On [enter] adjust focus. Trigger button if fields are not empty."""

        if not self.username_field.text:
            self.username_field.focus = True
        elif not self.password_field.text:
            self.password_field.focus = True
        else:
            self.login_button.trigger_action()

    def attempt_login(self):
        """Attempt to log in. On success, authenticate. On fail, alert user."""

        # disable the button so the user can't spam it
        self.login_button.disabled = True

        # attempt to log in
        try:
            phone = login(self.username_field.text, self.password_field.text)
        except AccountError as error:
            popup = AlertPopup(title='Error',
                               label=error.message,
                               button='Dismiss')
            popup.open()
        else:
            # valid credentials: authenticate via SMS
            self.manager.transition.direction = 'down'
            self.manager.get_screen('verification').phone = phone
            self.manager.current = 'verification'

        # enable the button after processing is complete
        self.login_button.disabled = False
