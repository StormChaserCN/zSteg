from scipy.io import wavfile

import Container


class WAVContainer(Container.Container):
    def get_file_data(self):
        rate, data = wavfile.read(self.path)
        self.base = data.reshape(len(data) * 2)
        self.rate = rate
        return

    def save_file_data(self, save_path):
        wavfile.write(save_path, self.rate, self.base.reshape((len(self.base), 2)))
        return
