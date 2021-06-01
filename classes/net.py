#!/usr/bin/env python3
from tflite_runtime.interpreter import Interpreter
from tflite_runtime.interpreter import load_delegate
from queue import Queue
from threading import Thread
import numpy as np
import cv2


class Net:
    def __init__(self, classes, model, queueSize=50):
        self.interpreter = Interpreter(model, experimental_delegates=[
                                  load_delegate('libedgetpu.so.1')])
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.width = self.input_details[0]['shape'][2]
        self.height = self.input_details[0]['shape'][1]
        self.labels = classes

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
                frame_rgb = cv2.cvtColor(self.Q.get(), cv2.COLOR_BGR2RGB)
                frame_resized = cv2.resize(frame_rgb, (self.width, self.height))
                input_data = np.expand_dims(frame_resized, axis=0)

                self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
                self.interpreter.invoke()
                boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
                classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
                scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0]
                self.latest_detection = (boxes, classes, scores)




    def update(self, frame):
        if self.Q.full():
            discarded_frame = self.Q.get()
            print("Dropped oldest item from queue")
        self.Q.put(frame)


    def read(self):
        return self.latest_detection


    def size(self):
        return self.Q.qsize()
