# coding=utf-8
from Cipher.AESCipher import *
from Compressor.ZLibCompressor import *
from Container.ImageContainer import *

BUF_SIZE = 10485760  # 10MB


def smash_into(container, info_path, save_path, key, ver=0):
    try:
        compressor = ZLibCompressor()
        compressor.compress_file(info_path, info_path + '.1')
        cipher = AESCipher()
        cipher.encrypt_file(key, info_path + '.1', info_path + '.2')
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
        cipher = AESCipher()
        cipher.decrypt_file(key, save_path + '.1', save_path + '.2')
        compressor = ZLibCompressor()
        compressor.decompress_file(save_path + '.2', save_path)
    finally:
        os.remove(save_path + '.1')
        os.remove(save_path + '.2')


if __name__ == '__main__':
    bmpc = BMPContainer(r'C:\Users\fhyd\Desktop\Project\1.bmp')
    smash_into(bmpc, r'C:\Users\fhyd\Desktop\Project\1.txt', r'C:\Users\fhyd\Desktop\Project\2.bmp', 'abcd123', 0)
    bmpc = BMPContainer(r'C:\Users\fhyd\Desktop\Project\2.bmp')
    split_from(bmpc, r'C:\Users\fhyd\Desktop\Project\2.txt', 'abcd123')
