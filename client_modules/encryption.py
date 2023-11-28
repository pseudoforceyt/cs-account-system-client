from cryptography.hazmat.primitives import serialization, hashes, hmac
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import padding as spadding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from os import urandom
from getpass import getpass
from base64 import urlsafe_b64encode
import pickle
import i18n


def create_rsa_key_pair():
    # Generate a 2048-bit RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    # Derive the public key
    public_key = private_key.public_key()
    return private_key, public_key


def ser_key_pem(key, type: str):
    if type == 'public':
        return key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    elif type == 'private':
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )


def deser_pem(key, type):
    if type == 'public':
        return serialization.load_pem_public_key(key)
    elif type == 'private':
        return serialization.load_pem_private_key(key, password=None)


def encrypt_data(data, pubkey):
    data = pickle.dumps(data)
    # Generate symmetric key and encrypt it
    skey = urandom(32)
    encrypted_skey = pubkey.encrypt(
        skey,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    # Encrypt packet data with symmetric key
    cbc = urandom(16)
    # Add the padding to the data
    padder = spadding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    # Encrypting the padded_data
    cipher = Cipher(algorithms.AES(skey), modes.CBC(cbc))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return pickle.dumps({'skey': encrypted_skey, 'cbc': cbc, 'ciphertext': ciphertext})


def decrypt_data(encrypted_data, privkey):
    try:
        # Decrypt our symmetric key
        packet = pickle.loads(encrypted_data)
        de_skey = privkey.decrypt(
            packet['skey'],
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        # And then use the decrypted symmetric key to decrypt our data

        cipher = Cipher(algorithms.AES(de_skey), modes.CBC(packet['cbc']))
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(packet['ciphertext']) + decryptor.finalize()

        # Create an unpadder object
        unpadder = spadding.PKCS7(algorithms.AES.block_size).unpadder()
        # Remove the padding from the data
        data = unpadder.update(decrypted_data) + unpadder.finalize()
        return pickle.loads(data)
    except Exception as error:
        return {'type': 'decrypt_error', 'data': f'{error}'}
