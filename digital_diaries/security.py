from cryptography.fernet import Fernet


def encrypt(message: str, key: bytes) -> str:
    message = str.encode(message)
    return Fernet(key).encrypt(message).decode()


def decrypt(token: str, key: bytes) -> str:
    token = str.encode(token)
    token = Fernet(key).decrypt(token)
    return token.decode()


def decrypt_extract_timestamp(token: bytes, key: bytes) -> str:
    token = str.encode(token)
    return Fernet(key).extract_timestamp(token)
