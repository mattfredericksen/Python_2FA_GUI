"""
This module contains the CreateAccountScreen widget used by SecureLoginApp.

CreateAccountScreen handles the validation and creation of new accounts.
"""

from kivy.uix.screenmanager import Screen
from customwidgets.alertpopup import AlertPopup

from phonenumbers import format_number, is_valid_number, parse as parse_number
from phonenumbers.phonenumberutil import NumberParseException
import re

from account_management import create_user, AccountError


class CreateAccountScreen(Screen):
    """Screen Widget for creating a new account"""

    def text_validate(self):
        """On [enter] adjust focus. Trigger button if fields are not empty."""

        if not self.username_field.text:
            self.username_field.focus = True
        elif not self.password_field.text:
            self.password_field.focus = True
        elif not self.phone_field.text:
            self.phone_field.focus = True
        else:
            self.create_account_button.trigger_action()

    def attempt_creation(self):
        """Validate fields and attempt to create account"""
        self.create_account_button.disabled = True

        # list of all problems with user input
        errors = []

        if not self.username_field.text:
            errors.append('username is required')
        elif re.search(r'[^A-Za-z0-9]', self.username_field.text):
            errors.append('username can only contain letters and numbers')

        # this shouldn't be possible (field has length cap), but just in case
        if len(self.username_field.text) > 32:
            errors.append('username maximum length is 32 characters')

        if not self.password_field.text:
            errors.append('password is required')
        elif len(self.password_field.text) < 8:
            errors.append('password minimum length is 8 characters')

        if not self.phone_field.text:
            errors.append('phone number is required')
        else:
            try:
                phone = parse_number(self.phone_field.text, 'US')
            except NumberParseException:
                valid = False
            else:
                valid = is_valid_number(phone)

            if not valid:
                errors.append(f'"{self.phone_field.text}" is not a valid US phone number')

        # if all inputs are valid, attempt to create a new account
        if not errors:
            try:
                create_user(self.username_field.text, self.password_field.text,
                            format_number(phone, 'NATIONAL'))
            except AccountError as e:
                # username already exists
                errors.append(e.message)
            else:
                # account created successfully
                AlertPopup(title='Success',
                           label=f'User "{self.username_field.text}" '
                                 'has been created',
                           button='Go to Login',
                           on_dismiss=self.switch_to_login).open()
                return

        # display input errors to the user
        popup = AlertPopup(title='Errors',
                           label='\n'.join(f'\u2022 {e}' for e in errors),
                           button='Dismiss')
        popup.label.halign = 'left'
        popup.open()

        self.create_account_button.disabled = False

    def switch_to_login(self, popup=None):
        self.manager.transition.direction = 'right'
        self.manager.current = 'login'
        self.create_account_button.disabled = False
