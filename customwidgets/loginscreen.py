from kivy.uix.screenmanager import Screen
from customwidgets.alertpopup import AlertPopup
import account_management


class LoginScreen(Screen):
    # TODO: implement on_enter_validate
    def text_validate(self):
        if not self.username_field.text:
            self.username_field.focus = True
        elif not self.password_field.text:
            self.password_field.focus = True
        else:
            self.login_button.trigger_action()

    def attempt_login(self):
        self.login_button.disabled = True
        # TODO: sanitize inputs
        try:
            phone = account_management.login(self.username_field.text, self.password_field.text)
        except account_management.AccountError as error:
            popup = AlertPopup(title='Error')
            popup.label.text = error.message
            popup.button.text = 'Dismiss'
            popup.open()
        else:
            self.manager.transition.direction = 'down'
            self.manager.get_screen('verification').phone = phone
            self.manager.current = 'verification'

        self.login_button.disabled = False
