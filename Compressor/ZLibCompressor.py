import zlib
import Compressor


class ZlibCompressor(Compressor):
    def __init__(self, buffer_size=10485760):
        self.BUF_SIZE = buffer_size

    def compress_file(self, src_file_path, dest_file_path):
        compress_obj = zlib.compressobj(9)
        with open(src_file_path, 'rb') as fd_in, open(dest_file_path, 'wb') as fd_out:
            data = fd_in.read(self.BUF_SIZE)
            while data:
                fd_out.write(compress_obj.compress(data))
                data = fd_in.read(self.BUF_SIZE)
            fd_out.write(compress_obj.flush())