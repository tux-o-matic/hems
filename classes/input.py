#!/usr/bin/env python3
from queue import Queue
from threading import Thread
import cv2


class Input:
    def __init(self, src, queueSize=300):
        self.cap = cv2.VideoCapture(src, cv2.CAP_GSTREAMER)
        self.stopped = False
        self.Q = Queue(maxsize=queueSize)

    def start(self):
		t = Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self

    def update(self):
		while True:
			if self.stopped:
				return

			if not self.Q.full():
				(grabbed, frame) = self.stream.read()
				if not grabbed: # For live stream should feed blank frame
					self.stop()
					return

				self.Q.put(frame)


    def read(self):
		return self.Q.get()


    def size(self):
		return self.Q.qsize()


    def stop(self):
        self.cap.release()
		self.stopped = True
