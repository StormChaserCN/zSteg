import os
import struct

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import MD5

import Cipher


class AESCipher(Cipher.Cipher):
    def encrypt_file(self, key, src_file_path, dest_file_path):
        iv = Random.new().read(AES.block_size)
        file_size = os.path.getsize(src_file_path)
        m = MD5.new()
        m.update(key)
        key = m.digest()
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        with open(src_file_path, 'rb') as fd_in, open(dest_file_path, 'wb') as fd_out:
            fd_out.write(iv)
            fd_out.write(struct.pack('<Q', file_size))
            data = fd_in.read(self.BUF_SIZE)
            while data:
                if len(data) % AES.block_size != 0:
                    data += '\x00' * (AES.block_size - len(data) % AES.block_size)
                fd_out.write(encryptor.encrypt(data))
                data = fd_in.read(self.BUF_SIZE)

    def decrypt_file(self, key, src_file_path, dest_file_path):
        m = MD5.new()
        m.update(key)
        key = m.digest()
        with open(src_file_path, 'rb') as fd_in, open(dest_file_path, 'wb') as fd_out:
            iv = fd_in.read(AES.block_size)
            original_size = struct.unpack('<Q', fd_in.read(struct.calcsize('Q')))[0]
            decryptor = AES.new(key, AES.MODE_CBC, iv)
            data = fd_in.read(self.BUF_SIZE)
            while data:
                fd_out.write(decryptor.decrypt(data))
                data = fd_in.read(self.BUF_SIZE)
            fd_out.truncate(original_size)
