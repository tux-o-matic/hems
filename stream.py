import numpy as np
import argparse
import cv2
import os
import socket
import time
from classes.input import Input
from classes.net import Net
from classes.output import Output


def load_label(path, encoding='utf-8'):
    with open(path, 'r', encoding=encoding) as f:
        lines = f.readlines()
        if not lines:
            return {}
        if lines[0].split(' ', maxsplit=1)[0].isdigit():
            pairs = [line.split(' ', maxsplit=1) for line in lines]
            return {int(index): label.strip() for index, label in pairs}
        else:
            return {index: line.strip() for index, line in enumerate(lines)}


def scan(args):
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
    "sofa", "train", "tvmonitor"]

    LABELS = os.getenv("LABELS", "LOCAL")
    if LABELS == 'LOCAL':
        pass
    else:
        CLASSES = load_label(LABELS)

    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

    print("[INFO] loading model...")
    net = Net(args["prototxt"], args["model"]).start()

    print("[INFO] starting video stream...")
    input_src= 'udpsrc multicast-group=' + args['src_ip'] + ' port=' + str(args['src_port']) + ' auto-multicast=true caps = "application/x-rtp, clock-rate=90000, encoding-name=H264, payload=96" ! rtpjitterbuffer ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! appsink'
    input = Input(input_src).start()


    OUTPUT = os.getenv('OUTPUT_METHOD', 'HLS')
    PLAYLIST_ROOT = os.getenv('PLAYLIST_ROOT', socket.getfqdn())
    if OUTPUT == 'HLS':
        out_stream = 'appsrc ! videoconvert ! ' + str(args['encoder']) + ' ! mpegtsmux ! hlssink playlist-root=http://' + PLAYLIST_ROOT + ':8080 playlist-location="/var/www/playlist.m3u8" location=/var/www/segment_%05d.ts target-duration=5 max-files=5'
    elif OUTPUT == 'RTP':
        out_stream = 'appsrc ! videoconvert ! ' + str(args['encoder']) + ' ! rtph264pay config-interval=1 pt=96 ! queue ! udpsink host=' + args['output_ip'] + ' port=' + str(args['output_port']) + ' auto-multicast=true'
    output = Output(out_stream, args['height'], args['width']).start()

    last_detected = None
    last_decteted_use_count = 0

    while(True):
      frame = input.read()
      (h, w) = frame.shape[:2]

      if not last_detected or last_decteted_use_count > 5:
        net.update(frame)
        detections = net.read()
        if not detections:
            continue
        last_detected = detections
        last_decteted_use_count = 0
      else:
        detections = last_detected
        last_decteted_use_count += 1

      boxes = detections[0]
      classes = detections[1]
      scores = detections[2]

      for i in range(len(scores)):
            if ((scores[i] > args["confidence"]) and (scores[i] <= 1.0)):
                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                ymin = int(max(1, (boxes[i][0] * h)))
                xmin = int(max(1, (boxes[i][1] * w)))
                ymax = int(min(h, (boxes[i][2] * h)))
                xmax = int(min(w, (boxes[i][3] * w)))

                cv2.rectangle(frame, (xmin, ymin),
                              (xmax, ymax), (10, 255, 0), 4)

                object_name = CLASSES[int(classes[i])]
                label = '%s: %d%%' % (object_name, int(scores[i]*100))
                labelSize, baseLine = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                # Make sure not to draw label too close to top of window
                label_ymin = max(ymin, labelSize[1] + 10)
                cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (
                    xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED)
                cv2.putText(frame, label, (xmin, label_ymin-7),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

      output.update(frame)

      # if the `q` key was pressed, break from the loop
      key = cv2.waitKey(1) & 0xFF
      if key == ord("q"):
        break

    input.stop()
    output.stop()


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
