from kivy.uix.popup import Popup


class AlertPopup(Popup):
    def __init__(self, label='', button='', **kwargs):
        super().__init__(**kwargs)

        self.label.text = label
        self.button.text = button
