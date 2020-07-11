from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from customwidgets.loginscreen import LoginScreen
from customwidgets.verificationscreen import VerificationScreen
from customwidgets.createaccountscreen import CreateAccountScreen

from account_management import setup_db
import sqlite3


class SecureLoginApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(CreateAccountScreen(name='create_account'))
        sm.add_widget(VerificationScreen(name='verification'))
        return sm


if __name__ == '__main__':
    try:
        setup_db()
    except sqlite3.Error as error:
        print(error, '\n')
        input('Unable to connect to database. Press [enter] to exit.')
    else:
        SecureLoginApp().run()
