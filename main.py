from CipherLogic import create_and_save_RSA_keys, get_rsa_keys, sendPublicKey
from Client import connect
from GlobalVariables import PASSWORD, MODE
from Gui import gui


def main():
    client = connect()
    create_and_save_RSA_keys(PASSWORD, MODE)
    public, private = get_rsa_keys(PASSWORD, MODE)
    # start_threads(client)
    sendPublicKey(client, MODE, PASSWORD)
    # client =5
    gui(client)
    # test


if __name__ == '__main__':
    main()
