import random
from des import encryption_dynamic, decryption_dynamic
import base64
from sympy import randprime

def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True

def generate_prime_in_range(start, end):
    prime = random.randint(start, end)
    while not is_prime(prime):
        prime = random.randint(start, end)
    return prime

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def mod_inverse(e, phi):
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y

    _, x, _ = extended_gcd(e, phi)
    return x % phi

def generate_keypair(keysize=2048):
    # Generate two large prime numbers
    p = randprime(2**(keysize//2 - 1), 2**(keysize//2))
    q = randprime(2**(keysize//2 - 1), 2**(keysize//2))

    n = p * q
    phi = (p - 1) * (q - 1)

    # 2 pangkat 16 + 1
    e = 65537

    d = mod_inverse(e, phi)
    return ((e, n), (d, n))

def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, byteorder='big')

def bytes_to_int(x: bytes) -> int:
    return int.from_bytes(x, byteorder='big')

def rsa_encrypt_des_key(des_key: str, public_key):
    try:
        e, n = public_key
        # Convert DES key to integer directly
        des_key_int = int.from_bytes(des_key.encode('utf-8'), byteorder='big')

        if des_key_int >= n:
            raise ValueError("DES key too large for RSA key size")

        encrypted_int = pow(des_key_int, e, n)
        return base64.b64encode(str(encrypted_int).encode('utf-8'))

    except Exception as e:
        raise ValueError(f"Error encrypting DES key: {str(e)}")

def rsa_decrypt_des_key(encrypted_des_key: bytes, private_key):
    try:
        d, n = private_key
        # Decode the encrypted integer
        encrypted_int = int(base64.b64decode(encrypted_des_key).decode('utf-8'))

        # Decrypt using RSA
        decrypted_int = pow(encrypted_int, d, n)

        # Convert back to bytes and decode
        decrypted_bytes = decrypted_int.to_bytes((decrypted_int.bit_length() + 7) // 8, byteorder='big')
        return decrypted_bytes.decode('utf-8')

    except Exception as e:
        raise ValueError(f"Error decrypting DES key: {str(e)}")

def hybrid_encrypt(message: str, des_key: str, recipient_public_key):
    try:
        # 1. Encrypt message using DES
        encrypted_message = encryption_dynamic(message, des_key)

        # 2. Encrypt DES key using recipient's RSA public key
        encrypted_des_key = rsa_encrypt_des_key(des_key, recipient_public_key)

        return encrypted_message, encrypted_des_key

    except Exception as e:
        raise Exception(f"Encryption failed: {str(e)}")

def hybrid_decrypt(encrypted_message, encrypted_des_key: bytes, private_key):
    try:
        # 1. Decrypt DES key using RSA private key
        des_key = rsa_decrypt_des_key(encrypted_des_key, private_key)

        # 2. Decrypt message using decrypted DES key
        decrypted_message = decryption_dynamic(encrypted_message, des_key)

        return decrypted_message

    except Exception as e:
        raise Exception(f"Decryption failed: {str(e)}")
