from passlib.hash import bcrypt, hex_sha256, sha256_crypt
from cryptography.fernet import Fernet
import base64
import sqlite3
from twilio.rest import Client
import secrets
from pprint import pprint

DB_NAME = 'account.db'

account_sid = "ACc45b3c8aec14c2ed56d30f7afbf4c1d7"
auth_token = "b1ca44a2eec02ed3c184956438231f16"
client = Client(account_sid, auth_token)


class Error(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'{self.__class__.__name__}: {self.message}'


class BadUsernameError(Error):
    pass


class BadPasswordError(Error):
    pass


def create_fernet_key(username: str, password: str) -> bytes:
    """Transforms a username/password pair into a fernet encryption key"""

    # get unique 16 characters to use as salt
    # note: getting the salt from the username was only done
    # to avoid creating another column in the database
    salt = hex_sha256.hash(username)[:16]

    # the fernet key needs to be 32 base64-encoded bytes,
    # so we get the last 32 characters of the hashed password.
    # somehow breaking the encryption would not reveal the user's
    # password, and the user does not need to store the key anywhere.
    key = sha256_crypt.hash(password, salt=salt)[-32:]
    return base64.encodebytes(key.encode())


def create_db():
    con = sqlite3.connect(DB_NAME)
    # cur = con.cursor()
    try:
        con.execute('''CREATE TABLE account
                       (username VARCHAR UNIQUE NOT NULL, 
                        password VARCHAR NOT NULL, 
                        phone VARCHAR NOT NULL);''')
    except sqlite3.OperationalError as e:
        print(f'create_db: table already exists\n\t{e}')
    else:
        con.commit()
    finally:
        con.close()


def display():
    con = sqlite3.connect(DB_NAME)
    user_data = con.execute('SELECT * FROM account').fetchall()
    con.close()
    pprint({u[0]: {'password': u[1], 'phone': u[2]} for u in user_data})


def create_user(username: str, password: str, phone: str):
    phone = Fernet(create_fernet_key(username, password)).encrypt(phone.encode())
    password = bcrypt.hash(password)

    con = sqlite3.connect(DB_NAME)
    try:
        con.execute('INSERT INTO account VALUES (?, ?, ?)', (username, password, phone))
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in e.args[0]:
            raise BadUsernameError(f'user "{username}" already exists')
        else:
            raise
    else:
        con.commit()
    finally:
        con.close()


def authenticate_user(phone: str):
    code = f'{secrets.randbelow(1000000):06}'
    message = client.messages.create(
        to=f'+1{phone}',
        from_='+12058982226',
        body=f'Your CSCE3550 verification code is {code}')
    return code


def login(username: str, password: str) -> str:
    con = sqlite3.connect(DB_NAME)

    # allows indexing rows by column name
    con.row_factory = sqlite3.Row

    # retrieve user information from the database
    # using '?' as a placeholder prevents injection attacks
    user_data = con.execute('SELECT * FROM account WHERE username = ?', (username,)).fetchone()
    con.close()

    # if no matching username was found
    if not user_data:
        raise BadUsernameError(f'user "{username}" does not exist')

    # if the password was incorrect
    if not bcrypt.verify(password, user_data['password']):
        raise BadPasswordError(f'incorrect password for user "{username}"')

    # matching username and password, print the decrypted phone number
    phone = Fernet(create_fernet_key(username, password)).decrypt(user_data['phone']).decode()
    print(f'Successful login, phone = {phone}')

    return phone


if __name__ == '__main__':
    create_db()
    try:
        create_user('username', 'password', '9726704514')
        create_user('user', 'pass', '9726704514')
        create_user('u', 'p', '9726704514')
        create_user('password', 'username', '9726704514')
    except Exception as e:
        print(e)
    display()

