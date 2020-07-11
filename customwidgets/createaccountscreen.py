from kivy.uix.screenmanager import Screen
from customwidgets.alertpopup import AlertPopup

from phonenumbers import format_number, is_valid_number, parse as parse_number
from phonenumbers.phonenumberutil import NumberParseException
import re

from account_management import create_user, AccountError


class CreateAccountScreen(Screen):
    def text_validate(self):
        if not self.username_field.text:
            self.username_field.focus = True
        elif not self.password_field.text:
            self.password_field.focus = True
        elif not self.phone_field.text:
            self.phone_field.focus = True
        else:
            self.create_account_button.trigger_action()

    def attempt_creation(self):
        self.create_account_button.disabled = True

        # create a list of all problems with user input
        errors = []

        if not self.username_field.text:
            errors.append('username is required')
        if re.search(r'[^A-Za-z0-9]', self.username_field.text):
            errors.append('username can only contain letters and numbers')
        if len(self.username_field.text) > 32:
            errors.append('username maximum length is 32 characters')

        if not self.password_field.text:
            errors.append('password is required')

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

        if not errors:
            try:
                create_user(self.username_field.text, self.password_field.text,
                                               format_number(phone, 'NATIONAL'))
            except AccountError as e:
                errors.append(e.message)
            else:
                popup = AlertPopup(title='Success')
                popup.label.text = f'user "{self.username_field.text}" has been created'
                popup.button.text = 'Go to Login'
                popup.open()
                self.manager.transition.direction = 'right'
                self.manager.current = 'login'
                self.create_account_button.disabled = False
                return

        popup = AlertPopup(title='Errors')
        popup.label.text = '\n'.join(f'\u2022 {e}' for e in errors)
        popup.button.text = 'Dismiss'
        popup.open()

        self.create_account_button.disabled = False
