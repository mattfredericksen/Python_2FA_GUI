from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import secrets


def send_auth_code(phone: str):
    # Super secret - don't share - I will cancel the token if
    # my account starts seeing unexpected activity
    account_sid = "ACc45b3c8aec14c2ed56d30f7afbf4c1d7"
    auth_token = "b1ca44a2eec02ed3c184956438231f16"
    client = Client(account_sid, auth_token)

    code = f'{secrets.randbelow(1000000):06}'
    try:
        client.messages.create(
            to=f'+1{phone}',
            from_='+12058982226',
            body=f'Your SecureLogin verification code is {code}')
    except TwilioRestException:
        return None
    else:
        return code
