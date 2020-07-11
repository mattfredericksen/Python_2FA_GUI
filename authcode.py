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

    # Super secret - don't share - I will cancel the token if
    # my account starts seeing unexpected activity
    account_sid = "ACc45b3c8aec14c2ed56d30f7afbf4c1d7"
    auth_token = "b1ca44a2eec02ed3c184956438231f16"
    client = Client(account_sid, auth_token)

    # secrets uses the most secure RNG available to the OS
    code = f'{secrets.randbelow(1000000):06}'

    # send SMS containing the code
    try:
        client.messages.create(
            to=f'+1{phone}',
            from_='+12058982226',
            body=f'Your SecureLogin verification code is {code}')
    except TwilioRestException:
        return None
    else:
        return code
