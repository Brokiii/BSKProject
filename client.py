import hashlib
import socket
import threading
from Frame import Frame
import pickle
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
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


def receive(client,chatbox):
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
                str = deserialized_frame.nickname+ ": " + decrypt_AES(deserialized_frame.data, ACTUAL_SESSION_KEY, deserialized_frame.mode).decode() +"\n"
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


def write(client):
    global OTHER_PUBLIC_KEY
    while True:
        message = input("Napisz cos:")
        message = bytes(message, encoding='utf-8')
        session_key = create_session_key()
        cipher_rsa = PKCS1_OAEP.new(RSA.import_key(OTHER_PUBLIC_KEY))  # stworzenie ciphera
        encrypted_session_key = cipher_rsa.encrypt(session_key)  # zaszyfrowanie klucza sesyjnego
        session_frame = Frame("SessionKey", encrypted_session_key)  # stworzenie ramki z kluczem sesyjnym
        serialized_frame = pickle.dumps(session_frame)  # serializacja ramki z kluczem sesyjnym
        client.send(serialized_frame)  # wyslanie klucza sesyjnego

        encrypted_message = encrypt_AES(message, session_key, MODE)  # zaszyfrowanie wiadomosci
        text_frame = Frame("Text", encrypted_message, MODE)
        serialized_frame2 = pickle.dumps(text_frame)
        client.send(serialized_frame2)

def write2(client,msg_to_send, mode, nickname, chatbox):
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

def start_threads(client):
    receive_thread = threading.Thread(target=receive, args=(client,))
    receive_thread.start()

    # write_thread = threading.Thread(target=write, args=(client,))
    # write_thread.start()



def sendPublicKey(client, mode, password):
    public, _ = get_rsa_keys(password, mode)
    frame = Frame("PublicKey", public)
    serialized_frame = pickle.dumps(frame)
    client.send(serialized_frame)


def create_session_key():
    return get_random_bytes(32)

def gui(client):
    root = tk.Tk()
    root.title("Chatbox 1.0")

    canvas = tk.Canvas(root, width=700, height=450)
    canvas.grid(columnspan=4, rowspan =16)

    #chatbox
    label = tk.Label(root, text="Chatbox")
    label.grid(columnspan = 2, column = 2, row = 0)

    chatbox = tk.Text(root, height=20, width=30, padx=15, pady=15)
    chatbox.grid(columnspan=2, column=2, row=1, rowspan=14)

    #nick użytkownika
    label4 = tk.Label(root, text="Enter your nickname")
    label4.grid(columnspan=2, column=0, row=0)
    nickname = tk.Entry(root, width=30)
    nickname.grid(columnspan=2, column=0, row=1)
    nickname.insert(tk.END, "Default nickname")

    # radiobuttony
    label3 = tk.Label(root, text="Choose encryption mode")
    label3.grid(columnspan=2, column=0, row=2)

    var1 = tk.StringVar()
    radio1 = tk.Radiobutton(root, text="CBC", variable=var1, value="CBC")
    radio2 = tk.Radiobutton(root, text="ECB", variable=var1, value="ECB")
    radio1.grid(column=0, row=3)
    radio2.grid(column=1, row=3)
    radio1.invoke()


    #pole na wiadomosc
    label2 = tk.Label(root, text="Enter your message")
    label2.grid(columnspan=2, column=0, row=4)
    message = tk.Entry(root, width=55)
    message.grid(columnspan=2, column=0, row=5)

    #przycisk
    button_text = tk.StringVar()
    button_text.set("Wyślij")
    send_button = tk.Button(root, textvariable=button_text, bg="red", fg="white", height=2, width=15,
                                    command=lambda: write2(client, message.get(), var1.get(), nickname.get(), chatbox))
    send_button.grid(columnspan=2, column=0, row=6)

    receive_thread = threading.Thread(target=receive, args=(client, chatbox))
    receive_thread.start()

    root.mainloop()