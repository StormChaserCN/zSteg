# coding=utf-8
import os
import struct
import zlib

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import MD5

from Container.AudioContainer import *
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


def smash_into_bmp(key, bmppath, filepath, savepath, ver=0):
    compress_file(filepath, filepath + '.1')
    encrypt_file(key, filepath + '.1', filepath + '.2')
    filesize = os.path.getsize(filepath + '.2')
    c = BMPContainer(bmppath)
    with open(filepath + '.2', 'rb') as fdfile:
        info = fdfile.read(filesize)
        if ver == 0:
            c.smash_into(info, savepath)
        else:
            c.smash_into_with_key(info, key, savepath)
    os.remove(filepath + '.1')
    os.remove(filepath + '.2')


def split_from_bmp(key, bmppath, savepath, isize=0, ver=0):
    c = BMPContainer(bmppath)
    if ver == 0:
        c.split_from(savepath)
    else:
        c.split_from_with_key(key, isize, savepath + '.1')
    decrypt_file(key, savepath + '.1', savepath + '.2')
    decompress_file(savepath + '.2', savepath)
    os.remove(savepath + '.1')
    os.remove(savepath + '.2')


def smash_into_wav(key, wavpath, filepath, savepath, ver=0):
    compress_file(filepath, filepath + '.1')
    encrypt_file(key, filepath + '.1', filepath + '.2')
    filesize = os.path.getsize(filepath + '.2')
    c = WAVContainer(wavpath)
    with open(filepath + '.2', 'rb') as fdfile:
        info = fdfile.read(filesize)
        if ver == 0:
            c.smash_into(info, savepath)
        else:
            c.smash_into_with_key(info, key, savepath)
    os.remove(filepath + '.1')
    os.remove(filepath + '.2')


def split_from_wav(key, wavpath, savepath, isize=0, ver=0):
    c = WAVContainer(wavpath)
    if ver == 0:
        c.split_from(savepath + '.1')
    else:
        c.split_from_with_key(key, isize, savepath + '.1')
    decrypt_file(key, savepath + '.1', savepath + '.2')
    decompress_file(savepath + '.2', savepath)
    os.remove(savepath + '.1')
    os.remove(savepath + '.2')


if __name__ == '__main__':
    smash_into_bmp('key123', 'd:/1.bmp', 'd:/1.txt', 'd:/2.bmp')
    split_from_bmp('key123', 'd:/2.bmp', 'd:/2.txt')
