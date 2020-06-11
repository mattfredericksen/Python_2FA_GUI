from passlib.hash import bcrypt, hex_sha256, sha256_crypt
from cryptography.fernet import Fernet
import base64
import sqlite3
from pprint import pprint

DB_NAME = 'accounts.db'


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

    # get (somewhat random) 16 characters to use as salt
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
        con.execute('''CREATE TABLE accounts
                       (username VARCHAR UNIQUE NOT NULL, 
                        password VARCHAR NOT NULL, 
                        phone VARCHAR NOT NULL);''')
    except sqlite3.OperationalError:
        print('create_db: table already exists')
    else:
        con.commit()
    finally:
        con.close()


def display():
    con = sqlite3.connect(DB_NAME)
    user_data = con.execute('SELECT * FROM accounts').fetchall()
    con.close()
    pprint({u[0]: {'password': u[1], 'phone': u[2]} for u in user_data})


def create_user(username: str, password: str, phone: str):
    phone = Fernet(create_fernet_key(username, password)).encrypt(phone.encode())
    password = bcrypt.hash(password)

    con = sqlite3.connect(DB_NAME)
    try:
        con.execute('INSERT INTO accounts VALUES (?, ?, ?)', (username, password, phone))
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in e.args[0]:
            raise BadUsernameError(f'user "{username}" already exists')
        else:
            raise
    else:
        con.commit()
    finally:
        con.close()


def decode_phone(phone: bytes, username: str, password: str) -> str:
    return Fernet(create_fernet_key(username, password)).decrypt(phone).decode()


def authenticate_user(phone: str):
    # generate code
    # text code
    # expire code after 60 seconds
    pass


def login(username: str, password: str) -> str:
    con = sqlite3.connect(DB_NAME)

    # allows indexing rows by column name
    con.row_factory = sqlite3.Row

    # retrieve user information from the database
    # using '?' as a placeholder prevents injection attacks
    user_data = con.execute('SELECT * FROM accounts WHERE username = ?', (username,)).fetchone()
    con.close()

    # if no matching username was found
    if not user_data:
        raise BadUsernameError(f'user "{username}" does not exist')

    # if the password was incorrect
    if not bcrypt.verify(password, user_data['password']):
        raise BadPasswordError(f'incorrect password for user "{username}"')

    # matching username and password, print the decrypted phone number
    phone = decode_phone(user_data['phone'], username, password)
    print(f'Successful login, phone = {phone}')

    return phone


if __name__ == '__main__':
    create_db()
    try:
        create_user('username', 'password', 'a_real_phone_number')
        create_user('user', 'pass', 'a_real_phone_number')
        create_user('u', 'p', 'a_real_phone_number')
        create_user('password', 'username', 'a_real_phone_number')
    except Exception as e:
        print(e)
    display()

