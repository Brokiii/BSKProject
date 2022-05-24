from CipherLogic import create_and_save_RSA_keys, sendPublicKey
from Client import connect
from Gui import gui
from Storage import Storage

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


def main():
    storage = Storage(password="rakieta", mode="CBC", buffer_size=4096) #108

    client = connect('127.0.0.1', 55555)
    create_and_save_RSA_keys(storage)
    sendPublicKey(client, storage)
    gui(client, storage)


if __name__ == '__main__':
    main()
