import cv2
import numpy as np

import Container


class AVIContainer(Container.Container):
    def get_file_data(self):
        cap = cv2.VideoCapture(self.path)
        success, frame = cap.read()
        if success is True:
            self.size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            self.color = frame.shape[2]
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            self.codecs = cap.get(cv2.CAP_PROP_FOURCC)

        while success:
            if hasattr(self, 'base'):
                self.base = np.hstack((self.base, frame.reshape(frame.shape[0] * frame.shape[1] * frame.shape[2])))
                self.cnt += 1
            else:
                self.base = frame.reshape(frame.shape[0] * frame.shape[1] * frame.shape[2])
                self.cnt = 1
            success, frame = cap.read()
        cap.release()
        return

    def save_file_data(self, save_path):
        cap = cv2.VideoWriter(save_path, int(self.codecs), int(self.fps), self.size)
        for aframe in self.base.reshape((self.cnt, self.size[1], self.size[0], self.color)):
            cap.write(aframe)
        cap.release()
        return
