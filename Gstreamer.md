## WIP

Use the following command to find out what video format is generated by your video source:
```shell
v4l2-ctl --all
```
This utility requires the *v4l-utils* package.

```shell
gst-launch-1.0 v4l2src device=/dev/video0 ! "video/x-raw,format=YUY2,width=640,height=480,type=video,framerate=(fraction)30/1" ! videoscale ! videoconvert ! x264enc tune=zerolatency
```