from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from phoneinput import PhoneInput
from loginscreen import LoginScreen
from verificationscreen import VerificationScreen
from createaccountscreen import CreateAccountScreen


class SecureLoginApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(CreateAccountScreen(name='create_account'))
        sm.add_widget(VerificationScreen(name='verification'))
        return sm


if __name__ == '__main__':
    SecureLoginApp().run()
