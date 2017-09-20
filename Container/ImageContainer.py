import numpy as np
from PIL import Image

import Container


class BMPContainer(Container.Container):
    def get_file_data(self):
        with Image.open(self.path) as img:
            self.base = np.array(img).reshape(img.size[0] * img.size[1] * 3)
            self.width = img.size[0]
            self.height = img.size[1]
        return

    def save_file_data(self, save_path):
        img1 = Image.fromarray(self.base.reshape(self.height, self.width, 3))
        img1.save(save_path)
        return


class JPEGContainer(Container.Container):
    def get_file_data(self):
        with Image.open(self.path) as img:
            self.base = np.array(img).reshape(img.size[0] * img.size[1] * 3)
            self.width = img.size[0]
            self.height = img.size[1]
        return

    def save_file_data(self, save_path):
        img1 = Image.fromarray(self.base.reshape(self.height, self.width, 3))
        img1.save(save_path)
        return
