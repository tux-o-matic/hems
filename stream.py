import numpy as np
import argparse
import cv2
import os
import time
from classes.input import Input
from classes.output import Output


def scan(args):
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
    "sofa", "train", "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

    print("[INFO] starting video stream...")
    input_src= 'udpsrc multicast-group=' + args['src_ip'] + ' port=' + str(args['src_port']) + ' auto-multicast=true caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! decodebin ! videoconvert ! appsink'
    input = Input(input_src).start()

    captureTime = time.time()

    out_stream = 'appsrc ! videoconvert ! video/x-raw, width=' + str(args['width']) + ', height=' + str(args['height']) + ', framerate=30/1 ! queue ! ' + str(args['encoder']) + ' ! rtph264pay ! queue ! udpsink host=' + args['output_ip'] + ' port=' + str(args['output_port']) + ' auto-multicast=true'

    output = Output(out_stream, args['height'], args['width']).start()


    while(input.size() > 0):
      frame = input.read()
      (h, w) = frame.shape[:2]

      blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
      net.setInput(blob)
      detections = net.forward()

      for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > args["confidence"]:
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # draw the prediction on the frame
            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
            cv2.rectangle(frame, (startX, startY), (endX, endY), COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

      if frame not None:
          print("Frame Width:" + frame.size().width + ", height:" + frame.size().height)
          output.update(frame)


      # if the `q` key was pressed, break from the loop
      key = cv2.waitKey(1) & 0xFF
      if key == ord("q"):
        break


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--encoder", default="x264enc", help="Gstreamer h264 encoder to use ('omxh264enc') on Pi")
    ap.add_argument("-p", "--prototxt", required=True, help="path to Caffe 'deploy' prototxt file")
    ap.add_argument("-m", "--model", required=True, help="path to Caffe pre-trained model")
    ap.add_argument("-c", "--confidence", type=float, default=0.2, help="minimum probability to filter weak detections")
    ap.add_argument("-i", "--output_ip", default="127.0.0.1", help="IP address of the generated RTP stream")
    ap.add_argument("-o", "--output_port", type=int, default=5001, help="UDP port of the generated RTP stream")
    ap.add_argument("-s", "--src_ip", default="127.0.0.1", help="IP address of the source RTP stream")
    ap.add_argument("-u", "--src_port", type=int, default=5000, help="UDP port of the source RTP stream")
    ap.add_argument("-w", "--width", type=int, default=1280, help="Pixel width of the video stream")
    ap.add_argument("-t", "--height", type=int, default=720, help="Pixel height of the video stream")
    args = vars(ap.parse_args())

    scan(args)
