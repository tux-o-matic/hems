#!/usr/bin/env python3
from queue import Queue
from threading import Thread
import numpy as np
import cv2


class Net:
    def __init__(self, model, prototxt, queueSize=50):
        self.neural_net = cv2.dnn.readNetFromCaffe(prototxt, model)
        self.latest_detection = None
        self.Q = Queue(maxsize=queueSize)

    def start(self):
        t = Thread(target=self.forward, args=())
        t.daemon = True
        t.start()
        return self


    def forward(self):
        while True:
            if self.Q.qsize() > 0:
                blob = cv2.dnn.blobFromImage(cv2.resize(self.Q.get(), (300, 300)), 0.007843, (300, 300), 127.5)
                self.neural_net.setInput(blob)
                self.latest_detection = net.forward()


    def update(self, frame):
        if self.Q.full():
            discarded_frame = self.Q.get()
            print("Dropped oldest item from queue")
        self.Q.put(frame)


    def read(self):
        return self.latest_detection


    def size(self):
        return self.Q.qsize()
