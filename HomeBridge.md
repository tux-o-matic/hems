## Rasbian 

### System changes
#### If using the official Raspberry Pi camera module (v2)
- Activate Camera module in the interface list (raspi-config).
- In '/etc/modules' add the following module
```shell
bcm2835-v4l2
```
To reduce noises (glare/reflection) from the Pi's LED, run as root the following commands to turn off the 'Power' and 'Activity' lights respectively :
```shell
echo 0 > /sys/class/leds/led1/brightness
echo 0 > /sys/class/leds/led0/brightness

```

### Dependencies for HomeBridge
```shell
sudo apt-get install git npm nodejs-legacy ffmpeg libavahi-compat-libdnssd-dev
```

### HomeBridge camera install
```shell
sudo mkdir /opt/homebridge-camera-rpi
sudo chown pi /opt/homebridge-camera-rpi
cd /opt
git clone https://github.com/moritzmhmk/homebridge-camera-rpi
cd homebridge-camera-rpi
npm install
```

### HomeBridge camera config
In /etc/homebridge-camera-rpi.conf.json
```json
{
  "name": "Camera",
  "id": "Camera",
  "pincode": "021-23-456",
  "username": "EC:23:3D:D3:52:D2"
}
```

### Systemd service
Assuming the NodeJS app and module are installled in '/opt/homebridge-camera-rpi'.
Create the file '/etc/systemd/system/homebridge-camera.service'
```ìni
[Unit]
Description=HomeBridge Camera

[Service]
ExecStart=/usr/bin/node /opt/homebridge-camera-rpi/standalone.js -c /etc/homebridge-camera-rpi.conf.json
WorkingDirectory=/opt/homebridge-camera-rpi
Restart=always
RestartSec=10
User=pi

[Install]
WantedBy=multi-user.target
```
Then enable the service to start with the OS and start the service:
```shell
sudo systemctl enable homebridge-camera
sudo systemctl start homebridge-camera
```
