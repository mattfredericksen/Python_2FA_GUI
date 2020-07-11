"""
Main module for SecureLoginApp.

Author: Matthew Fredericksen
Date: 7/11/2020

SecureLoginApp was created for the final project assignment
in CSCE 3550.070. It allows the user to securely create and
sign in to an account using two-factor authentication.

Accounts contain a username, password, and phone number.
The password is stored as a hash, using the bcrypt algorithm.
The phone number is encrypted using a key generated from hashed
values of the username and password. Implementation details
are contained in account_management.py.

All user inputs are validated before being used. When a user
attempts to sign in, an authentication code will be securely
generated and sent to the user's phone via SMS. This code will
expire after 30 seconds, or after 3 failed attempts to enter it.

The GUI implementation mostly occurs in securelogin.kv. Important
security features (such as password-masking) are implemented there
as well as in other project modules.

The application is only meant to provide sign-in capabilities.
Once the sign-in verification has occurred, the user's only
option is to sign out.
"""

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
    # make sure the database exists
    # create it if it does not exist
    # start the app

    try:
        setup_db()
    except sqlite3.Error as error:
        print(error, '\n')
        input('Unable to connect to database. Press [enter] to exit.')
    else:
        SecureLoginApp().run()
