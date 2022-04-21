from client import connect
from client import create_and_save_RSA_keys
from client import get_rsa_keys


if __name__ == '__main__':
    # client = connect()
    create_and_save_RSA_keys("gibon", "ECB")
    x1,x2 = get_rsa_keys("gibon", "ECB")




