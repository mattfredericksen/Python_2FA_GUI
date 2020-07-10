import db_stuff
from phonenumbers import AsYouTypeFormatter, format_number,  \
                         parse as parse_number, is_valid_number
from phonenumbers.phonenumberutil import NumberParseException
import re
import secrets

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput


class PhoneInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.formatter = AsYouTypeFormatter('US')

    def format_number_field(self):
        # get the text left of the cursor position,
        # filter out non-digits, and store the length
        digits_before_cursor = len(re.sub(r'\D', '', self.text[:self.cursor_index()]))

        # reset the formatter's stored result
        self.formatter.clear()

        # input all digits from the text field to the formatter
        # this is inefficient and not how the formatter is meant
        # to be used, but it works.
        number = re.sub(r'\D', '', self.text)
        for d in number:
            self.formatter.input_digit(d)
        self.text = self.formatter._current_output

        # modifying self.text resets cursor position, so here
        # we correct the cursor position by ensuring the same
        # number of digits are to the left of the cursor
        digit_count = 0
        for i, c in enumerate(self.text):
            if digit_count == digits_before_cursor:
                self.cursor = (i, 0)
                break
            elif c.isdigit():
                digit_count += 1

    def insert_text(self, substring, from_undo=False):
        # limit text length to 16 characters
        substring = substring[:16 - len(self.text)]

        # remove non-digits from user input
        substring = re.sub(r'\D', '', substring)

        # insert the text
        super().insert_text(substring, from_undo)

        # reformat the field
        self.format_number_field()

    def keyboard_on_key_up(self, window, keycode):
        super().keyboard_on_key_up(window, keycode)

        # if the text field was modified, we need to reformat it
        if keycode[1] == 'backspace':
            self.format_number_field()


class LoginScreen(Screen):
    # TODO: implement on_enter_validate
    def on_enter(self):
        if not self.username:
            self.ids.username_field.focus = True
        elif not self.password:
            self.ids.password_field.focus = True
        else:
            self.ids.login_button.trigger_action()

    def attempt_login(self):
        self.ids.login_button.disabled = True
        # TODO: sanitize inputs
        try:
            phone = db_stuff.login(self.ids.username_field.text, self.ids.password_field.text)
        except db_stuff.Error as e:
            print(e)
        else:
            # TODO: check if this screen needs to be deleted later
            self.manager.switch_to(VerificationScreen(phone))
            self.manager.transition.direction = 'down'

        self.ids.login_button.disabled = False

    def switch_to_create_account(self):
        self.ids.username_field.text = ''
        self.ids.password_field.text = ''
        self.manager.transition.direction = 'left'
        self.manager.current = 'create_account'


class VerificationScreen(Screen):
    def __init__(self, phone, **kwargs):
        super().__init__(**kwargs)
        self.ids.label.text = self.ids.label.text.format(phone[-4:])
        self.code = '0'  # db_stuff.authenticate_user(phone)

    def on_enter(self):
        if self.ids.code_field.text:
            self.ids.submit_button.trigger_action()

    def verify_code(self):
        if secrets.compare_digest(self.code, self.ids.code_field.text):
            print('success')
        else:
            print('fail')


class CreateAccountScreen(Screen):
    # TODO: implement on_enter_validate
    def on_enter(self):
        if not self.username:
            self.ids.username_field.focus = True
        elif not self.password:
            self.ids.password_field.focus = True
        elif not self.phone:
            self.ids.phone_field.focus = True
        else:
            self.ids.create_account_button.trigger_action()

    def switch_to_login(self):
        # clear any user input
        self.ids.username_field.text = ''
        self.ids.password_field.text = ''
        self.ids.phone_field.text = ''

        # switch to login screen
        self.manager.transition.direction = 'right'
        self.manager.current = 'login'

    def attempt_creation(self):
        self.ids.create_account_button.disabled = True

        # create a list of all problems with user input
        errors = []
        if not self.username:
            errors.append('username is required')
        if not self.password:
            errors.append('password is required')
        if re.search(r'[^A-Za-z0-9]', self.username):
            errors.append('username can only contain letters and numbers')
        if len(self.username) > 36:
            errors.append('username maximum length is 32 characters')

        if not self.phone:
            errors.append('phone number is required')
        else:
            try:
                phone = parse_number(self.phone, 'US')
                valid = is_valid_number(phone)
            except NumberParseException:
                valid = False
            if not valid:
                errors.append(f'"{self.phone}" is not a valid US phone number')

        if not errors:
            try:
                # TODO: put up a spinner so the program doesn't seem frozen
                db_stuff.create_user(self.username, self.password, format_number(phone, 'NATIONAL'))
            except db_stuff.Error as e:
                errors.append(e.message)
            else:
                # TODO: display account creation success screen
                print(f'SUCCESS: created user "{self.username}"')
                self.switch_to_login()
                return

        print('ERRORS:')
        for error in errors:
            print(f'\t{error}')

        self.create_account_button.disabled = False


class SecureLoginApp(App):

    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(CreateAccountScreen(name='create_account'))
        return sm


if __name__ == '__main__':
    SecureLoginApp().run()