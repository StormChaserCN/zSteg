# coding=utf-8
import os
import struct
import zlib

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import MD5

from Container.VideoContainer import *

BUF_SIZE = 10485760  # 10MB


def compress_file(src_path, dst_path):
    compress_obj = zlib.compressobj(9)
    with open(src_path, 'rb') as fd_in, open(dst_path, 'wb') as fd_out:
        data = fd_in.read(BUF_SIZE)
        while data:
            fd_out.write(compress_obj.compress(data))
            data = fd_in.read(BUF_SIZE)
        fd_out.write(compress_obj.flush())


def decompress_file(src_path, dst_path):
    decompress_obj = zlib.decompressobj()
    with open(src_path, 'rb') as fd_in, open(dst_path, 'wb') as fd_out:
        data = fd_in.read(BUF_SIZE)
        while data:
            fd_out.write(decompress_obj.decompress(data))
            data = fd_in.read(BUF_SIZE)
        fd_out.write(decompress_obj.flush())


def encrypt_file(key, src_path, dst_path):
    iv = Random.new().read(AES.block_size)
    file_size = os.path.getsize(src_path)
    m = MD5.new()
    m.update(key)
    key = m.digest()
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    with open(src_path, 'rb') as fd_in, open(dst_path, 'wb') as fd_out:
        fd_out.write(iv)
        fd_out.write(struct.pack('<Q', file_size))
        data = fd_in.read(BUF_SIZE)
        while data:
            if len(data) % AES.block_size != 0:
                data += '\x00' * (AES.block_size - len(data) % AES.block_size)
            fd_out.write(encryptor.encrypt(data))
            data = fd_in.read(BUF_SIZE)


def decrypt_file(key, src_path, dst_path):
    m = MD5.new()
    m.update(key)
    key = m.digest()
    with open(src_path, 'rb') as fd_in, open(dst_path, 'wb') as fd_out:
        iv = fd_in.read(AES.block_size)
        original_size = struct.unpack('<Q', fd_in.read(struct.calcsize('Q')))[0]
        decryptor = AES.new(key, AES.MODE_CBC, iv)
        data = fd_in.read(BUF_SIZE)
        while data:
            fd_out.write(decryptor.decrypt(data))
            data = fd_in.read(BUF_SIZE)
        fd_out.truncate(original_size)


def smash_into(container, info_path, save_path, key, ver=0):
    try:
        compress_file(info_path, info_path + '.1')
        encrypt_file(key, info_path + '.1', info_path + '.2')
        file_size = os.path.getsize(info_path + '.2')
        with open(info_path + '.2', 'rb') as fd_file:
            info = fd_file.read(file_size)
            if ver == 0:
                container.smash_into(info, save_path)
            else:
                container.smash_into_with_key(info, key, save_path)
    finally:
        os.remove(info_path + '.1')
        os.remove(info_path + '.2')


def split_from(container, save_path, key, isize=0, ver=0):
    try:
        if ver == 0:
            container.split_from(save_path + '.1')
        else:
            container.split_from_with_key(key, isize, save_path + '.1')
        decrypt_file(key, save_path + '.1', save_path + '.2')
        decompress_file(save_path + '.2', save_path)
    finally:
        os.remove(save_path + '.1')
        os.remove(save_path + '.2')


if __name__ == '__main__':
    c = AVIContainer('d:/1.avi')
    smash_into(c, 'd:/zteg_test_info.txt', 'd:/2.avi', 'key123321')

    # c1 = AVIContainer('d:/2.avi')
    # split_from(c1, 'd:/2.txt', 'key123321')





