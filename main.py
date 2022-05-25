from CipherLogic import create_and_save_RSA_keys, sendPublicKey
from Client import connect
from Gui import gui
from Storage import Storage


def main():
    storage = Storage(password="rakieta", mode="CBC", buffer_size=1048576)  # 1048576

    client = connect('127.0.0.1', 55555)
    create_and_save_RSA_keys(storage)
    sendPublicKey(client, storage)
    gui(client, storage)


if __name__ == '__main__':
    main()
