import zlib

import Compressor


class ZLibCompressor(Compressor.Compressor):

    def compress_file(self, src_file_path, dest_file_path):
        compress_obj = zlib.compressobj(9)
        with open(src_file_path, 'rb') as fd_in, open(dest_file_path, 'wb') as fd_out:
            data = fd_in.read(self.BUF_SIZE)
            while data:
                fd_out.write(compress_obj.compress(data))
                data = fd_in.read(self.BUF_SIZE)
            fd_out.write(compress_obj.flush())

    def decompress_file(self, src_file_path, dest_file_path):
        decompress_obj = zlib.decompressobj()
        with open(src_file_path, 'rb') as fd_in, open(dest_file_path, 'wb') as fd_out:
            data = fd_in.read(self.BUF_SIZE)
            while data:
                fd_out.write(decompress_obj.decompress(data))
                data = fd_in.read(self.BUF_SIZE)
            fd_out.write(decompress_obj.flush())
