# hems

## Running the API
From within the same folder:
```bash
gunicorn -b localhost:8080 --worker-class gevent --threads 2 --worker-connections 200 app:app
```

## Calling the API
To get the image back with boxes around detected objects:
```bash
curl -X POST http://127.0.0.1:8080/image --upload-file /path/to/image/to/scan.jpg -i
```

To get a JSON list of objects detected:
```bash
curl -H "Accept: application/json" -X POST http://127.0.0.1:8080/image --upload-file /path/to/image/to/scan.jpg -i
```



### Credits
pyimagesearch.com for OpenCV examples