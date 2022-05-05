import socket

from CipherLogic import create_session_key, encrypt_AES, get_rsa_keys, decrypt_AES
from Frame import Frame
import pickle
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from GlobalVariables import PASSWORD, MODE

import tkinter as tk

host = '127.0.0.1'
port = 55555
OTHER_PUBLIC_KEY = None
ACTUAL_SESSION_KEY = None


def connect():
    try:
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect((host, port))
        print("SIEMA JA KLIENT")
        return c

    except:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen()
        c, _ = s.accept()
        print("SIEMA JA SERWER")
        return c


def receive(client, chatbox):
    global OTHER_PUBLIC_KEY
    global ACTUAL_SESSION_KEY
    while True:
        try:
            message = client.recv(20000)
            deserialized_frame = pickle.loads(message)
            if deserialized_frame.type == "PublicKey":
                OTHER_PUBLIC_KEY = deserialized_frame.data
                print("Wymiana kluczy publicznych przebiegła pomyślnie")
            elif deserialized_frame.type == "Text":
                str = deserialized_frame.nickname + ": " + decrypt_AES(deserialized_frame.data, ACTUAL_SESSION_KEY,
                                                                       deserialized_frame.mode).decode() + "\n"
                chatbox.insert(tk.END, str)
            elif deserialized_frame.type == "SessionKey":
                _, private = get_rsa_keys(PASSWORD, MODE)
                private = RSA.import_key(private)
                cipher = PKCS1_OAEP.new(private)
                ACTUAL_SESSION_KEY = cipher.decrypt(deserialized_frame.data)


        except:
            print("ERROR")
            client.close()
            break


def write2(client, msg_to_send, mode, nickname, chatbox):
    global OTHER_PUBLIC_KEY
    message = bytes(msg_to_send, encoding='utf-8')

    session_key = create_session_key()
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(OTHER_PUBLIC_KEY))  # stworzenie ciphera
    encrypted_session_key = cipher_rsa.encrypt(session_key)  # zaszyfrowanie klucza sesyjnego
    session_frame = Frame("SessionKey", encrypted_session_key)  # stworzenie ramki z kluczem sesyjnym
    serialized_frame = pickle.dumps(session_frame)  # serializacja ramki z kluczem sesyjnym
    client.send(serialized_frame)  # wyslanie klucza sesyjnego

    encrypted_message = encrypt_AES(message, session_key, mode)  # zaszyfrowanie wiadomosci
    text_frame = Frame("Text", encrypted_message, nickname, mode)
    serialized_frame2 = pickle.dumps(text_frame)
    client.send(serialized_frame2)

    chatbox.insert(tk.END, nickname + ": " + msg_to_send + "\n")
