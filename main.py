# coding=utf-8
import os
import random
import struct
import zlib

import numpy as np
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from PIL import Image
from scipy.io import wavfile

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


def smash_into(base, info):
    base_index = 0
    info_size = len(info) * 8

    for i in xrange(64):
        bit = info_size % 2
        base[base_index] = base[base_index] & 254 | bit
        base_index += 1
        info_size = info_size >> 1

    for info_index in xrange(len(info)):
        byte = struct.unpack('B', info[info_index])[0]
        for i in xrange(8):
            bit = byte % 2
            base[base_index] = base[base_index] & 254 | bit
            base_index += 1
            byte = byte >> 1
    return base


def smash_into_r(base, info, key):
    base_index = 0
    info_size = len(info) * 8
    print info_size
    random.seed(key)
    rlist = []
    for i in xrange(info_size):
        rlist.append(random.randint(0, len(base)))

    for info_index in xrange(len(info)):
        byte = struct.unpack('B', info[info_index])[0]
        for i in xrange(8):
            bit = byte % 2
            base[rlist[base_index]] = base[rlist[base_index]] & 254 | bit
            base_index += 1
            byte = byte >> 1
    return base


def split_from(base):
    filesize = 0
    for i in xrange(63):
        filesize += (base[63 - i] & 1)
        filesize = filesize << 1
    filesize += base[0] & 1

    info = ''
    for i in xrange(64, filesize + 64, 8):
        value = (base[i] & 1) + (base[i + 1] & 1) * 2 + (base[i + 2] & 1) * 4 + (base[i + 3] & 1) * 8 + \
                (base[i + 4] & 1) * 16 + (base[i + 5] & 1) * 32 + (base[i + 6] & 1) * 64 + (base[i + 7] & 1) * 128
        info += struct.pack('B', value)
    return info


def split_from_r(base, key, info_size):
    random.seed(key)
    rlist = []
    for i in xrange(info_size):
        rlist.append(random.randint(0, len(base)))

    info = ''
    for i in xrange(0, info_size, 8):
        value = (base[rlist[i]] & 1) + (base[rlist[i + 1]] & 1) * 2 + (base[rlist[i + 2]] & 1) * 4 + \
                (base[rlist[i + 3]] & 1) * 8 + (base[rlist[i + 4]] & 1) * 16 + (base[rlist[i + 5]] & 1) * 32 + \
                (base[rlist[i + 6]] & 1) * 64 + (base[rlist[i + 7]] & 1) * 128
        info += struct.pack('B', value)
    return info


def smash_into_bmp(key, bmppath, filepath, savepath, ver=0):
    compress_file(filepath, filepath + '.1')
    encrypt_file(key, filepath + '.1', filepath + '.2')
    filesize = os.path.getsize(filepath + '.2')
    with Image.open(bmppath) as img, open(filepath + '.2', 'rb') as fdfile:
        info = fdfile.read(filesize)
        if ver == 0:
            img1 = Image.fromarray(smash_into(np.array(img).reshape(img.size[0] * img.size[1] * 3), info).reshape(
                (img.size[1], img.size[0], 3)))
        else:
            img1 = Image.fromarray(
                smash_into_r(np.array(img).reshape(img.size[0] * img.size[1] * 3), info, key).reshape(
                    (img.size[1], img.size[0], 3)))
        img1.save(savepath)
    os.remove(filepath + '.1')
    os.remove(filepath + '.2')


def split_from_bmp(key, bmppath, savepath, isize=0, ver=0):
    with Image.open(bmppath) as img, open(savepath + '.1', 'wb') as fdfile:
        if ver == 0:
            info = split_from(np.array(img).reshape(img.size[0] * img.size[1] * 3))
        else:
            info = split_from_r(np.array(img).reshape(img.size[0] * img.size[1] * 3), key, isize)
        fdfile.write(info)
    decrypt_file(key, savepath + '.1', savepath + '.2')
    decompress_file(savepath + '.2', savepath)
    os.remove(savepath + '.1')
    os.remove(savepath + '.2')


def smash_into_wav(key, wavpath, filepath, savepath, ver=0):
    compress_file(filepath, filepath + '.1')
    encrypt_file(key, filepath + '.1', filepath + '.2')
    rate, data = wavfile.read(wavpath)
    filesize = os.path.getsize(filepath + '.2')
    with open(filepath + '.2', 'rb') as fdfile:
        info = fdfile.read(filesize)
        if ver == 0:
            data1 = smash_into(data.reshape(len(data) * 2), info).reshape((len(data), 2))
        else:
            data1 = smash_into_r(data.reshape(len(data) * 2), info, key).reshape((len(data), 2))
    wavfile.write(savepath, rate, data1)
    os.remove(filepath + '.1')
    os.remove(filepath + '.2')


def split_from_wav(key, wavpath, savepath, isize=0, ver=0):
    rate, data = wavfile.read(wavpath)
    if ver == 0:
        info = split_from(data.reshape(len(data) * 2))
    else:
        info = split_from_r(data.reshape(len(data) * 2), key, isize)
    with open(savepath + '.1', 'wb') as fdfile:
        fdfile.write(info)
    decrypt_file(key, savepath + '.1', savepath + '.2')
    decompress_file(savepath + '.2', savepath)
    os.remove(savepath + '.1')
    os.remove(savepath + '.2')


if __name__ == '__main__':

    pass
