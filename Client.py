import socket
import pickle
import tqdm
import os
import tkinter as tk
import time

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
            message = client.recv(storage.buffer_size_recv)
            deserialized_frame = pickle.loads(message)
            if deserialized_frame.type == "Size":
                storage.buffer_size_recv = deserialized_frame.data
            elif deserialized_frame.type == "File":
                decrypted_message = decrypt_AES(deserialized_frame.data, storage.actual_session_key
                                                , deserialized_frame.mode)
                with open("Files/" + storage.filename, "a+b") as f:
                    f.write(decrypted_message)
            elif deserialized_frame.type == "SessionKey":
                _, private = get_rsa_keys(storage)
                private = RSA.import_key(private)
                cipher = PKCS1_OAEP.new(private)
                storage.actual_session_key = cipher.decrypt(deserialized_frame.data)
            elif deserialized_frame.type == "PublicKey":
                storage.other_public_key = deserialized_frame.data
            elif deserialized_frame.type == "Text":
                decrypted_message = decrypt_AES(deserialized_frame.data, storage.actual_session_key
                                                , deserialized_frame.mode).decode()
                message_to_chatbox = f"{deserialized_frame.nickname}: {decrypted_message}\n"
                chatbox.insert(tk.END, message_to_chatbox)
            elif deserialized_frame.type == "PreFile":
                decrypted_message = decrypt_AES(deserialized_frame.data, storage.actual_session_key
                                                , deserialized_frame.mode).decode()
                storage.filename = decrypted_message
            elif deserialized_frame.type == "AfterFile":
                decrypted_message = decrypt_AES(deserialized_frame.data, storage.actual_session_key
                                                , deserialized_frame.mode).decode()
                chatbox.insert(tk.END, f"Receive: {decrypted_message}\n")
        except:
            print("Receive error!")
            client.close()
            break


def create_session_key_frame(client, storage):
    session_key = create_session_key()
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(storage.other_public_key))  # stworzenie ciphera
    encrypted_session_key = cipher_rsa.encrypt(session_key)  # zaszyfrowanie klucza sesyjnego
    session_frame = Frame("SessionKey", encrypted_session_key)  # stworzenie ramki z kluczem sesyjnym
    serialized_frame = pickle.dumps(session_frame)  # serializacja ramki z kluczem sesyjnym

    return session_key, serialized_frame


def create_and_send_size_frame(client, frame):
    frame = Frame(type="Size",
                  data=frame.__len__())
    serialized_frame = pickle.dumps(frame)
    client.sendall(serialized_frame)


def create_and_send_frame(client, storage, mode, nickname, data, type):
    session_key, serialized_session_key_frame = create_session_key_frame(client, storage)
    encrypted_data = encrypt_AES(data, session_key, mode)  # zaszyfrowanie wiadomosci

    text_frame = Frame(type=type,
                       data=encrypted_data,
                       nickname=nickname,
                       mode=mode)
    serialized_frame = pickle.dumps(text_frame)

    create_and_send_size_frame(client, serialized_session_key_frame)
    time.sleep(0.1)
    client.sendall(serialized_session_key_frame)

    time.sleep(0.1)

    create_and_send_size_frame(client, serialized_frame)
    time.sleep(0.1)
    client.sendall(serialized_frame)


def write(client, msg_to_send, mode, nickname, chatbox, storage):
    message = bytes(msg_to_send, encoding='utf-8')
    create_and_send_frame(client=client,
                          storage=storage,
                          mode=mode,
                          nickname=nickname,
                          data=message,
                          type="Text")
    chatbox.insert(tk.END, nickname + ": " + msg_to_send + "\n")


def send_file(client, filepath, storage, progress_bar, nickname, mode, chatbox):
    filesize = os.path.getsize(filepath)
    filename = os.path.basename(filepath)

    create_and_send_frame(client, storage, mode, nickname, bytes(filename, encoding='utf-8'), "PreFile")
    progress_bar['value'] = 0
    progress = tqdm.tqdm(range(filesize), f"Sending {filepath}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filepath, "rb") as f:
        while True:
            bytes_read = f.read(storage.buffer_size)

            if not bytes_read:
                break

            create_and_send_frame(client, storage, mode, nickname, bytes_read, "File")
            progress_bar['value'] += (len(bytes_read) / filesize) * 100
            progress.update(len(bytes_read))

    chatbox.insert(tk.END, f"Send {filename}\n")
    create_and_send_frame(client, storage, mode, nickname, bytes(filename, encoding='utf-8'), "AfterFile")
