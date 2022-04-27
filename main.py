from client import connect
from client import create_and_save_RSA_keys
from client import get_rsa_keys, start_threads, sendPublicKey, encrypt_AES, decrypt_AES, gui
from GlobalVariables import PASSWORD, MODE

if __name__ == '__main__':
    client = connect()
    create_and_save_RSA_keys(PASSWORD, MODE)
    public, private = get_rsa_keys(PASSWORD, MODE)
    #start_threads(client)
    sendPublicKey(client, MODE, PASSWORD)
    # client =5
    gui(client)

