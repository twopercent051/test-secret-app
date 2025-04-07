from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os
import base64

import hashlib
import hmac

from config import config


def encrypt_passphrase(passphrase: str) -> str:
    key = config.crypto.passphrase_key
    key_bytes = key.encode("utf-8")
    passphrase_bytes = passphrase.encode("utf-8")
    hashed = hmac.new(key=key_bytes, msg=passphrase_bytes, digestmod=hashlib.sha256)
    return hashed.hexdigest()


def encrypt_secret(secret: str) -> str:
    key = config.crypto.secret_key
    secret_bytes = secret.encode("utf-8")
    key_bytes = key.encode("utf-8")
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(secret_bytes) + padder.finalize()
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_data).decode("utf-8")


def decrypt_secret(encrypted_secret: str) -> str:
    key = config.crypto.secret_key
    encrypted_secret_bytes = base64.b64decode(encrypted_secret)
    key_bytes = key.encode("utf-8")
    iv = encrypted_secret_bytes[:16]
    encrypted_content = encrypted_secret_bytes[16:]
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_content) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data_bytes = unpadder.update(padded_data) + unpadder.finalize()
    return data_bytes.decode("utf-8")
