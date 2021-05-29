# hems

## Centralized object detection for video streams

### Hardware
Focuses on Raspberry Pi, can run on different hardware with the right packages and h264 encoder.

### Launching stream on Pi with cam (source)
```shell
ffmpeg -i /dev/video0 -vcodec h264_omx -pix_fmt yuv420p -f rawvideo -tune zerolatency -vf scale=1280:720 -r 30 -b:v 500k -bufsize 500k -maxrate 500k -payload_type 96 -max_delay 5000 -f rtp 'udp://224.1.1.2:5000'
```

### Credits
pyimagesearch.com for OpenCV examples
