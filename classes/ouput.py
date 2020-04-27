#!/usr/bin/env python3
from queue import Queue
from threading import Thread
import cv2
import numpy as np


class Output:
    def __init(self, stream, height, width, queueSize=300):
        self.out = cv2.VideoWriter(stream, cv2.CAP_GSTREAMER, 0, 10, (width, height), True)
        self.width = width
        self.height = height
        if not self.out.isOpened():
            print("Output writer isn't opened")

        self.stopped = False
        self.Q = Queue(maxsize=queueSize)

    def start(self):
		t = Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self

    def stream(self):
        while True:
            if self.Q.qsize() == 0:
                blank_image = np.zeros(shape=[elf.width, elf.height, 3], dtype=np.uint8)
                self.out.write(blank_image)
            else:
                frame =  self.Q.get()
                for i in range(15):
                    self.out.write(frame)


    def update(self, frame):
        self.Q.put(frame)


    def size(self):
		return self.Q.qsize()


    def stop(self):
        self.out.release()
		self.stopped = True
