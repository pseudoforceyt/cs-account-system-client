from cryptography.hazmat.primitives import serialization, hashes, hmac
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import padding as spadding
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
### For chat operations
#from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
#from cryptography.hazmat.primitives.asymmetric import ec
#from cryptography.hazmat.primitives.kdf.hkdf import HKDF
#from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from os import urandom
import pickle


def create_conn_key_pair():
    # Generate a 2048-bit RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    # Derive the public key
    public_key = private_key.public_key()
    return private_key, public_key

def ser_key_pem(key: rsa.RSAPublicKey, type: str):
    return key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def encrypt_packet(data, pubkey):
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

    return pickle.dumps({'skey':encrypted_skey, 'cbc':cbc, 'ciphertext':ciphertext})

def decrypt_packet(encrypted_data, privkey):
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
        return {'type':'decrypt_error','data':f'{error}'}

    
""" THIS PART OF THE MODULE IS RESERVED FOR CHAT OPERATIONS """

#def create_key_pair():
#    private_key_d = ec.generate_private_key(ec.SECP256K1())
#    public_key_d = private_key_d.public_key()
#    return private_key_d, public_key_d

#def derive_key(eprkey, epbkey, keyinfo):
#    shared_key = eprkey.exchange(
#        ec.ECDH(), epbkey)
#    # Perform key derivation.
#    derived_key = HKDF(
#        algorithm=hashes.SHA256(),
#        length=32,
#        salt=None,
#        info=keyinfo.encode(),
#    ).derive(shared_key)
#    return derived_key

#def encrypt_packet(data, key):
#    data = pickle.dumps(data)
#    aesgcm = AESGCM(key)
#    nonce = urandom(12)  # Unique nonce for each message
#    ciphertext = aesgcm.encrypt(nonce, data, None)
#    return pickle.dumps({'nonce': nonce, 'ciphertext': ciphertext})

#def decrypt_packet(data, key):
#    aesgcm = AESGCM(key)
#    nonce = data['nonce']
#    ciphertext = data['ciphertext']
#    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
#    return plaintext