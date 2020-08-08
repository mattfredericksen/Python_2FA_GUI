"""
This module contains the send_auth_code function.

send_auth_code() generates a code with the secrets module, which provides
access to the most secure source of randomness available to the OS.

The code is delivered via SMS using Twilio.
"""

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import secrets


def send_auth_code(phone: str):
    """Generate and send a random code. Returns the code."""

    # Replace with credentials from your Twilio account
    account_sid = "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    auth_token = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    client = Client(account_sid, auth_token)

    # secrets uses the most secure RNG available to the OS
    code = f'{secrets.randbelow(1000000):06}'

    # send SMS containing the code
    try:
        client.messages.create(
            to=f'+1{phone}',
            from_='+1XXXXXXXXXX',
            body=f'Your SecureLogin verification code is {code}')
    except TwilioRestException:
        return None
    else:
        return code
