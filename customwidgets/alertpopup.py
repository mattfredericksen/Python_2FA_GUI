"""
This module contains the AlertPopup widget, which inherits from Popup.

More information about its behavior can be found in securelogin.kv.
"""

from kivy.uix.popup import Popup


class AlertPopup(Popup):
    instance = None

    def __init__(self, label='', button='', **kwargs):
        # only allow one alert at a time
        if self.__class__.instance:
            self.__class__.instance.dismiss()
        self.__class__.instance = self

        super().__init__(**kwargs)

        self.label.text = label
        self.button.text = button

    def on_pre_dismiss(self):
        # this function is not necessary, but allows any
        # module to detect if an alert is open by checking
        # AlertPopup.instance
        self.__class__.instance = None
