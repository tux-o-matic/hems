#!/usr/bin/env python3
from queue import Queue
from threading import Thread
import cv2
import numpy as np


class Output:
    def __init__(self, stream, height, width, queueSize=300):
        self.out = cv2.VideoWriter(stream, cv2.CAP_GSTREAMER, 0, 10, (width, height), True)
        self.width = width
        self.height = height
        if not self.out.isOpened():
            print("Output writer isn't opened")

        self.stopped = False
        self.stream_started = False
        self.Q = Queue(maxsize=queueSize)

    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def stream(self):
        self.stream_started = True
        while True:
            if self.Q.qsize() == 0:
                blank_image = np.zeros(shape=[self.width, self.height, 3], dtype=np.uint8)
                self.out.write(blank_image)
            else:
                self.last_frame = self.Q.get()
                self.out.write(self.last_frame)


    def update(self, frame):
        self.Q.put(frame)
        if not self.stream_started:
            self.stream()


    def size(self):
        return self.Q.qsize()


    def stop(self):
        self.out.release()
        self.stopped = True
