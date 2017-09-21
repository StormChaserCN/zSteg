# coding=utf-8
import os
import struct
import zlib

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import MD5

from Container.ImageContainer import *

BUF_SIZE = 10485760  # 10MB


def compress_file(srcpath, dstpath):
    cobj = zlib.compressobj(9)
    with open(srcpath, 'rb') as fdin, open(dstpath, 'wb') as fdout:
        data = fdin.read(BUF_SIZE)
        while data:
            fdout.write(cobj.compress(data))
            data = fdin.read(BUF_SIZE)
        fdout.write(cobj.flush())


def decompress_file(srcpath, dstpath):
    dobj = zlib.decompressobj()
    with open(srcpath, 'rb') as fdin, open(dstpath, 'wb') as fdout:
        data = fdin.read(BUF_SIZE)
        while data:
            fdout.write(dobj.decompress(data))
            data = fdin.read(BUF_SIZE)
        fdout.write(dobj.flush())


def encrypt_file(key, srcpath, dstpath):
    iv = Random.new().read(AES.block_size)
    filesize = os.path.getsize(srcpath)
    m = MD5.new()
    m.update(key)
    key = m.digest()
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    with open(srcpath, 'rb') as fdin, open(dstpath, 'wb') as fdout:
        fdout.write(iv)
        fdout.write(struct.pack('<Q', filesize))
        data = fdin.read(BUF_SIZE)
        while data:
            if len(data) % AES.block_size != 0:
                data += '\x00' * (AES.block_size - len(data) % AES.block_size)
            fdout.write(encryptor.encrypt(data))
            data = fdin.read(BUF_SIZE)


def decrypt_file(key, srcpath, dstpath):
    m = MD5.new()
    m.update(key)
    key = m.digest()
    with open(srcpath, 'rb') as fdin, open(dstpath, 'wb') as fdout:
        iv = fdin.read(AES.block_size)
        origsize = struct.unpack('<Q', fdin.read(struct.calcsize('Q')))[0]
        decryptor = AES.new(key, AES.MODE_CBC, iv)
        data = fdin.read(BUF_SIZE)
        while data:
            fdout.write(decryptor.decrypt(data))
            data = fdin.read(BUF_SIZE)
        fdout.truncate(origsize)


def smash_into(container, info_path, save_path, key, ver=0):
    try:
        compress_file(info_path, info_path + '.1')
        encrypt_file(key, info_path + '.1', info_path + '.2')
        file_size = os.path.getsize(info_path + '.2')
        with open(info_path + '.2', 'rb') as fdfile:
            info = fdfile.read(file_size)
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
    c = PNGContainer('d:/1.png')
    smash_into(c, 'd:/1.txt', 'd:/2.png', 'key123321')