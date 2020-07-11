from passlib.hash import bcrypt, hex_sha256, sha256_crypt
from cryptography.fernet import Fernet
import base64
import sqlite3
from pprint import pprint

DB_NAME = 'account.db'


class AccountError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'{self.__class__.__name__}: {self.message}'


def create_fernet_key(username: str, password: str) -> bytes:
    """Transforms a username/password pair into a fernet encryption key"""

    # Get unique 16 characters to use as salt.
    # Note: getting the salt from the username was only done
    #       to avoid creating another column in the database.
    salt = hex_sha256.hash(username)[:16]

    # The fernet key needs to be 32 base64-encoded bytes,
    # so we get the last 32 characters of the hashed password.
    # Somehow breaking the encryption would not reveal the user's
    # password, and the user does not need to store the key anywhere.
    key = sha256_crypt.hash(password, salt=salt)[-32:]
    return base64.encodebytes(key.encode())


def setup_db():
    con = sqlite3.connect(DB_NAME)

    try:
        con.execute('''CREATE TABLE account
                       (username VARCHAR UNIQUE NOT NULL, 
                        password VARCHAR NOT NULL, 
                        phone VARCHAR NOT NULL);''')
    except sqlite3.OperationalError as e:
        print(f'setup_db(): {e}')
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
    con = sqlite3.connect(DB_NAME)

    # check if username already exists
    if con.execute('SELECT username FROM account WHERE username = ?', (username,)).fetchone():
        raise AccountError(f'user "{username}" already exists')

    phone = Fernet(create_fernet_key(username, password)).encrypt(phone.encode())
    password = bcrypt.hash(password)

    con.execute('INSERT INTO account VALUES (?, ?, ?)', (username, password, phone))
    con.commit()
    con.close()


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
        raise AccountError(f'user "{username}" does not exist')

    # if the password was incorrect
    if not bcrypt.verify(password, user_data['password']):
        raise AccountError(f'incorrect password for user "{username}"')

    # matching username and password: return the decrypted phone number
    return Fernet(create_fernet_key(username, password)).decrypt(user_data['phone']).decode()
