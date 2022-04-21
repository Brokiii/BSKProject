import hashlib
import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

host = '127.0.0.1'
port = 55555


def connect():
    try:
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect((host, port))
        return c

    except:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen()
        return s


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


def create_and_save_RSA_keys(password, mode):
    aes_key, aes_iv = hash_and_split_password(password)
    key = RSA.generate(2048)
    cipher = None
    cipher2 = None

    if mode == "CBC":
        cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
        cipher2 = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    elif mode == "ECB":
        cipher = AES.new(aes_key + aes_iv, AES.MODE_ECB)
        cipher2 = AES.new(aes_key + aes_iv, AES.MODE_ECB)

    encrypted_private_key = cipher.encrypt(pad(key.export_key(), AES.block_size))
    save_to_file("PrivateKey/private.bin", encrypted_private_key)

    encrypted_public_key = cipher2.encrypt(pad(key.publickey().export_key(), AES.block_size))
    save_to_file("PublicKey/public.bin", encrypted_public_key)

    print(key.export_key())
    print(key.publickey().export_key())


def get_rsa_keys(password, mode):
    aes_key, aes_iv = hash_and_split_password(password)
    cipher = None
    cipher2 = None

    if mode == "CBC":
        cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
        cipher2 = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    elif mode == "ECB":
        cipher = AES.new(aes_key + aes_iv, AES.MODE_ECB)
        cipher2 = AES.new(aes_key + aes_iv, AES.MODE_ECB)

    encrypted_public_key = open("PublicKey/public.bin", "rb").read()
    decrypted_public_key = unpad(cipher.decrypt(encrypted_public_key), AES.block_size)

    encrypted_private_key = open("PrivateKey/private.bin", "rb").read()
    decrypted_private_key = unpad(cipher2.decrypt(encrypted_private_key), AES.block_size)

    print(decrypted_public_key)
    print(decrypted_private_key)

    return decrypted_public_key, decrypted_private_key
