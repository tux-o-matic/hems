#!/usr/bin/env python3
from queue import Queue
from threading import Thread
import cv2


class Output:
    def __init(self, stream, width, height, queueSize=300):
        self.out = cv2.VideoWriter(stream, cv2.CAP_GSTREAMER, 0, 10, (width, height), True)
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
        while self.Q.qsize() > 0:
            self.out.write(self.Q.get())


    def update(self, frame):
        self.Q.put(frame)


    def size(self):
		return self.Q.qsize()


    def stop(self):
        self.out.release()
		self.stopped = True
