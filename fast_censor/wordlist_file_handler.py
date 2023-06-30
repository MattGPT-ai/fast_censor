from os import path
from typing import Generator

import cryptography
from cryptography.fernet import Fernet


keyfile_path = "keyfile"
infile_path = "profanity_wordlist.txt"
outfile_path = "profanity_wordlist_encrypted.txt"
write_bytes = True

write_opts = 'wb' if write_bytes else 'w'
if write_bytes:
    newline = b'\n'
    read_opts = 'rb'
    write_opts = 'wb'
else:
    newline = '\n'
    read_opts = 'r'
    write_opts = 'w'
    
outfile = open(outfile_path, write_opts) 

class Encrypter:
    pass

if path.isfile(keyfile_path):
    keyfile = open(keyfile_path, 'rb')
    with open(keyfile_path, 'rb') as keyfile:
        key = keyfile.read()
else:
    key = Fernet.generate_key()  # this is your "password"
    with open(keyfile_path, 'wb') as keyfile:
        keyfile.write(key)

cipher_suite = Fernet(key)


#def encrypt(igen: Generator, cipher):
with open(infile_path) as infile: 
    for line in infile.readlines():
        encrypted_line = cipher_suite.encrypt(line.encode())
        if not write_bytes:
            encrypted_line = encrypted_line.decode()
        outfile.write(encrypted_line)
        outfile.write(newline)

outfile.close()


def decrypt(lines, read_bytes: bool = False) -> None:
    pass

decoded_file = open("decoded.txt", 'w')
with open(outfile_path, read_opts) as encrypted_file:
    for encrypted_line in encrypted_file.readlines():
        decrypted_line = cipher_suite.decrypt(encrypted_line)
        decoded_file.write(decrypted_line.decode())
decoded_file.close()


if __name__ == "__main__":  # decrypt 
    decrypt(5, True)
