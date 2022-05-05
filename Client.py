import socket
import pickle
import tqdm
import os
import tkinter as tk

from CipherLogic import create_session_key, encrypt_AES, get_rsa_keys, decrypt_AES
from Frame import Frame
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


def connect(host, port):
    try:
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect((host, port))
        return c

    except:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen()
        c, _ = s.accept()
        return c


def receive(client, chatbox, storage):
    while True:
        try:
            message = client.recv(storage.buffer_size)
            deserialized_frame = pickle.loads(message)
            if deserialized_frame.type == "PublicKey":
                storage.other_public_key = deserialized_frame.data
            elif deserialized_frame.type == "Text":
                decrypted_message = decrypt_AES(deserialized_frame.data, storage.actual_session_key
                                                , deserialized_frame.mode).decode()
                message_to_chatbox = f"{deserialized_frame.nickname}: {decrypted_message}\n"
                chatbox.insert(tk.END, message_to_chatbox)
            elif deserialized_frame.type == "SessionKey":
                _, private = get_rsa_keys(storage)
                private = RSA.import_key(private)
                cipher = PKCS1_OAEP.new(private)
                storage.actual_session_key = cipher.decrypt(deserialized_frame.data)
            elif deserialized_frame.type == "PreFile":
                filename = deserialized_frame.filename
                filesize = deserialized_frame.filesize
                with open(filename, "wb") as f:
                    while True:
                        file_frame = client.recv(storage.buffer_size)
                        frame = pickle.loads(file_frame)
                        if frame.type != "File":
                            continue
                        if not frame.data:
                            break
                        f.write(frame.data)
        except:
            print("Receive error!")
            client.close()
            break


def write(client, msg_to_send, mode, nickname, chatbox, storage):
    message = bytes(msg_to_send, encoding='utf-8')

    session_key = create_session_key()
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(storage.other_public_key))  # stworzenie ciphera
    encrypted_session_key = cipher_rsa.encrypt(session_key)  # zaszyfrowanie klucza sesyjnego
    session_frame = Frame("SessionKey", encrypted_session_key)  # stworzenie ramki z kluczem sesyjnym
    serialized_frame = pickle.dumps(session_frame)  # serializacja ramki z kluczem sesyjnym
    client.send(serialized_frame)  # wyslanie klucza sesyjnego

    encrypted_message = encrypt_AES(message, session_key, mode)  # zaszyfrowanie wiadomosci
    text_frame = Frame("Text", encrypted_message, nickname, mode)
    serialized_frame2 = pickle.dumps(text_frame)
    client.send(serialized_frame2)

    chatbox.insert(tk.END, nickname + ": " + msg_to_send + "\n")


def send_file(client, filepath, storage):
    filesize = os.path.getsize(filepath)
    filename = os.path.basename(filepath)

    prefile_frame = Frame("PreFile", "", filesize=filesize, filename=filename)
    serialized_prefile_frame = pickle.dumps(prefile_frame)
    client.send(serialized_prefile_frame)

    progress = tqdm.tqdm(range(filesize), f"Sending {filepath}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filepath, "rb") as f:
        while True:
            bytes_read = f.read(2048)
            if not bytes_read:
                break
            frame = Frame("File", bytes_read, filename=filename, filesize=filesize)
            serialized_frame = pickle.dumps(frame)
            client.send(serialized_frame)
            progress.update(len(bytes_read))
