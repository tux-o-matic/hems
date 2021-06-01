#!/usr/bin/env python3
from queue import Queue
from threading import Thread
import cv2
import numpy as np


class Output:
    def __init__(self, stream, height, width, queueSize=300):
        self.out = cv2.VideoWriter(stream, cv2.CAP_GSTREAMER, 0, 15, (width, height), True)
        self.width = width
        self.height = height
        if not self.out.isOpened():
            print("Output writer isn't opened")

        self.last_frame = None
        self.Q = Queue(maxsize=queueSize)

    def start(self):
        t = Thread(target=self.stream, args=())
        t.daemon = True
        t.start()
        return self

    def stream(self):
        while True:
            if self.Q.qsize() < 1 and self.last_frame is None:
                blank_image = np.zeros(shape=[self.height, self.width, 3], dtype=np.uint8)
                self.out.write(blank_image)
            else:
                self.last_frame = self.Q.get()
                self.out.write(self.last_frame)


    def update(self, frame):
        if self.Q.full():
            discarded_frame = self.Q.get()
            print("Dropped oldest frame from output queue")
        self.Q.put(frame)


    def size(self):
        return self.Q.qsize()


    def stop(self):
        self.out.release()
