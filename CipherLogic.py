import hashlib
import pickle

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

from Frame import Frame


def hash_and_split_password(password):
    password = bytes(password, encoding='utf-8')
    password_hash = hashlib.blake2s(password, digest_size=32).digest()

    aes_key = password_hash[0:16]
    aes_iv = password_hash[16:32]

    return aes_key, aes_iv


def save_to_file(path, text):
    public_file = open(path, "wb")
    public_file.write(text)
    public_file.close()


def create_cipher(password, mode):
    if password.__len__() != 32:
        password = bytes(password, encoding='utf-8')
        password = hashlib.blake2s(password, digest_size=32).digest()

    aes_key = password[0:16]
    aes_iv = password[16:32]

    cipher = None

    if mode == "CBC":
        cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    elif mode == "ECB":
        cipher = AES.new(aes_key + aes_iv, AES.MODE_ECB)

    return cipher


def encrypt_AES(data, password, mode):
    cipher = create_cipher(password, mode)
    return cipher.encrypt(pad(data, AES.block_size))


def decrypt_AES(encrypted_data, password, mode):
    cipher = create_cipher(password, mode)
    return unpad(cipher.decrypt(encrypted_data), AES.block_size)


def create_and_save_RSA_keys(password, mode):
    key = RSA.generate(2048)

    encrypted_private_key = encrypt_AES(key.export_key(), password, mode)
    save_to_file("PrivateKey/private.bin", encrypted_private_key)

    encrypted_public_key = encrypt_AES(key.publickey().export_key(), password, mode)
    save_to_file("PublicKey/public.bin", encrypted_public_key)


def get_rsa_keys(password, mode):
    encrypted_public_key = open("PublicKey/public.bin", "rb").read()
    decrypted_public_key = decrypt_AES(encrypted_public_key, password, mode)

    encrypted_private_key = open("PrivateKey/private.bin", "rb").read()
    decrypted_private_key = decrypt_AES(encrypted_private_key, password, mode)

    return decrypted_public_key, decrypted_private_key

def sendPublicKey(client, mode, password):
    public, _ = get_rsa_keys(password, mode)
    frame = Frame("PublicKey", public)
    serialized_frame = pickle.dumps(frame)
    client.send(serialized_frame)


def create_session_key():
    return get_random_bytes(32)