import random
import struct


class Container(object):
    def __init__(self, file_path, buf_size=102400):
        self.path = file_path
        self.buf_size = buf_size

    def convert2bin(self, info):
        for a_byte in info:
            yield bin(ord(a_byte))[2:].zfill(8)

    def smash_into(self, info, save_path):
        self.get_file_data()

        base_index = 0
        info_size = len(info) * 8

        for i in xrange(64):
            bit = info_size % 2
            self.base[base_index] = self.base[base_index] & 254 | bit
            base_index += 1
            info_size = info_size >> 1

        for a_byte in self.convert2bin(info):
            for a_char in a_byte:
                self.base[base_index] = self.base[base_index] & 254 | int(a_char)
                base_index += 1
        self.save_file_data(save_path)
        return

    def smash_into_with_key(self, info, key, save_path):
        self.get_file_data()

        base_index = 0
        base_size = len(self.base)
        info_size = len(info) * 8
        random.seed(key)
        rlist = list()
        for i in xrange(info_size):
            pos = random.randint(0, base_size)
            if pos not in rlist:
                rlist.append(pos)
            else:
                i -= 1

        for a_byte in self.convert2bin(info):
            for a_char in a_byte:
                self.base[rlist[base_index]] = self.base[rlist[base_index]] & 254 | int(a_char)
                base_index += 1
        self.save_file_data(save_path)
        return info_size

    def split_from(self, save_path):
        self.get_file_data()
        filesize = 0
        for i in xrange(63):
            filesize += (self.base[63 - i] & 1)
            filesize = filesize << 1
        filesize += self.base[0] & 1

        self.info = ''
        for i in xrange(64, filesize + 64, 8):
            value = (self.base[i] & 1) * 128 + (self.base[i + 1] & 1) * 64 + (self.base[i + 2] & 1) * 32 + (self.base[
                                                                                                                i + 3] & 1) * 16 + \
                    (self.base[i + 4] & 1) * 8 + (self.base[i + 5] & 1) * 4 + (self.base[i + 6] & 1) * 2 + (
                    self.base[i + 7] & 1)
            self.info += struct.pack('B', value)
        self.save_secret(save_path)
        return

    def split_from_with_key(self, key, info_size, save_path):
        self.get_file_data()
        random.seed(key)
        base_len = len(self.base)
        rlist = list()
        for i in xrange(info_size):
            pos = random.randint(0, base_len)
            if pos not in rlist:
                rlist.append(pos)
            else:
                i -= 1

        self.info = ''
        for i in xrange(0, info_size, 8):
            value = (self.base[rlist[i]] & 1) * 128 + (self.base[rlist[i + 1]] & 1) * 64 + (self.base[rlist[
                i + 2]] & 1) * 32 + \
                    (self.base[rlist[i + 3]] & 1) * 16 + (self.base[rlist[i + 4]] & 1) * 8 + (self.base[rlist[
                i + 5]] & 1) * 4 + \
                    (self.base[rlist[i + 6]] & 1) * 2 + (self.base[rlist[i + 7]] & 1)
            self.info += struct.pack('B', value)
        self.save_secret(save_path)
        return

    def get_file_data(self):
        return

    def save_file_data(self, save_path):
        return

    def save_secret(self, save_path):
        with open(save_path, 'wb') as fd:
            fd.write(self.info)
        return
