from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os
import base64

backend = default_backend()
salt = os.urandom(16)  # Should be stored securely in production

def generate_key(user_id):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=backend
    )
    return kdf.derive(user_id.encode())

def encrypt_message(message, recipient_id):
    iv = os.urandom(16)
    key = generate_key(recipient_id)
    
    # Pad the message
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(message.encode()) + padder.finalize()
    
    # Encrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded_data) + encryptor.finalize()
    
    # Return IV + ciphertext
    return base64.b64encode(iv + ct).decode()

def decrypt_message(encrypted_message, sender_id):
    data = base64.b64decode(encrypted_message.encode())
    iv = data[:16]
    ct = data[16:]
    
    key = generate_key(sender_id)
    
    # Decrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ct) + decryptor.finalize()
    
    # Unpad
    unpadder = padding.PKCS7(128).unpadder()
    message = unpadder.update(padded_data) + unpadder.finalize()
    
    return message.decode()
