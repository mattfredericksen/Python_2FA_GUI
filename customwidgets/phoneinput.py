"""
This module contains the PhoneInput class, which inherits from TextInput.

PhoneInput does fancy stuff for actively formatting phone number input.
"""

from kivy.uix.textinput import TextInput
from phonenumbers import AsYouTypeFormatter
import re


class PhoneInput(TextInput):
    text_validate_unfocus = False

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
