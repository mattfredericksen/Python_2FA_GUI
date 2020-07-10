from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import AliasProperty

from phonenumbers import format_number, is_valid_number, parse as parse_number
from phonenumbers.phonenumberutil import NumberParseException
import re
import db_stuff


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
                valid = is_valid_number(phone)
            except NumberParseException:
                valid = False
            if not valid:
                errors.append(f'"{self.phone_field.text}" is not a valid US phone number')

        if not errors:
            try:
                # TODO: put up a spinner so the program doesn't seem frozen
                db_stuff.create_user(self.username_field.text, self.password_field.text,
                                     format_number(phone, 'NATIONAL'))
            except db_stuff.Error as e:
                errors.append(e.message)
            else:
                # TODO: display account creation success screen
                self.manager.transition.direction = 'right'
                self.manager.current = 'login'
                return

        for i, error in enumerate(errors):
            errors[i] = f'\u2022 {error}'

        popup = Popup(title='Errors',
                      content=Label(text='\n'.join(errors), line_height=1.2),
                      size_hint=(.5, .5))
        popup.open()

        self.create_account_button.disabled = False
