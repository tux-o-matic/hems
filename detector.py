from PIL import Image
import cv2
import json
import io
import numpy as np


class Detector():

    def __init__(self, classes_path, model, prototxt):
        with open(classes_path, 'r') as classes_file:
            self.classes = json.load(classes_file)['classes']
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
        self.net = cv2.dnn.readNetFromCaffe(prototxt, model)

    def detect_in_image(self, data, confidence_min, type_to_return='list'):
        file_bytes = np.asarray(bytearray(data), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        (h, w) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)
        print("[INFO] computing object detections...")
        self.net.setInput(blob)
        detections = self.net.forward()

        found_objects = []

        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with the
            # prediction
            confidence = detections[0, 0, i, 2]

            if confidence > (confidence_min / 100):
                # extract the index of the class label from the `detections`,
                # then compute the (x, y)-coordinates of the bounding box for
                # the object
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                label = "{}: {:.2f}%".format(self.classes[idx], confidence * 100)
                cv2.rectangle(image, (startX, startY), (endX, endY), self.colors[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(image, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors[idx], 2)

                found_objects.append({"object": self.classes[idx], "confidence": confidence * 100})

        if type_to_return == 'image':
            # ret, im_thresh = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)
            # strIO = io.StringIO()
            # imsave(strIO, image, plugin='pil', format_str='png')
            # strIO.write(image)
            # strIO.seek(0)
            # io.BytesIO(processed_image)
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            byte_io = io.BytesIO()
            pil_image.save(byte_io, 'PNG')
            byte_io.seek(0)
            return byte_io
        else:
            return found_objects
