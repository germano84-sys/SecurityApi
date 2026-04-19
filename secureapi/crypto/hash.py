import hashlib
import bcrypt

def hash_sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()

def hash_bcrypt(text):
    return bcrypt.hashpw(text.encode(), bcrypt.gensalt()).decode()