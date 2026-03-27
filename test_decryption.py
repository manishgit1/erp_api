import base64
import json
try:
    from Cryptodome.Cipher import AES
    from Cryptodome.Util.Padding import pad, unpad
except ImportError:
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad, unpad
    except ImportError:
        AES = None
        pad = None
        unpad = None

def encrypt_payload(data_dict, key_str="1234567890123456"):
    key = key_str.encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    ciphertext = cipher.encrypt(pad(json.dumps(data_dict).encode('utf-8'), AES.block_size))
    return base64.b64encode(iv + ciphertext).decode('utf-8')

def decrypt_payload(encrypted_payload, key_str="1234567890123456"):
    encrypted_data = base64.b64decode(encrypted_payload)
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    key = key_str.encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ciphertext), AES.block_size).decode('utf-8')

# Test data
test_data = {"username": "admin", "password": "password123"}
encrypted = encrypt_payload(test_data)
print(f"Encrypted Payload: {encrypted}")

decrypted = decrypt_payload(encrypted)
print(f"Decrypted Data: {decrypted}")

if json.loads(decrypted) == test_data:
    print("Verification Successful!")
else:
    print("Verification Failed!")
