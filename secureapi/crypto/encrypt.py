from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_text(text):
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(token):
    return cipher.decrypt(token.encode()).decode()