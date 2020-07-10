from kivy.uix.screenmanager import Screen
import db_stuff


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
            phone = db_stuff.login(self.username_field.text, self.password_field.text)
        except db_stuff.Error as e:
            print(e)
        else:
            self.manager.transition.direction = 'down'
            self.manager.get_screen('verification').phone = phone
            self.manager.current = 'verification'

        self.login_button.disabled = False
