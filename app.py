from detector import Detector
from flask import Flask, jsonify, render_template, request, send_file
from flask_restful import Api
# from flask_restful_swagger import swagger
import configparser
import socket

app = Flask(__name__)

config = configparser.ConfigParser()
config.read("config.ini")
detector = Detector(config['models']['classes_json_path'], config['models']['model_path'],
                    config['models']['prototxt_path'])


# url = config['server']['protocol'] + '://' + config['server']['hostname'] + ':' +  config['server']['port']
# api = swagger.docs(Api(app), apiVersion='0.1',
#                   basePath=url,
#                   resourcePath='/',
#                   produces=["application/json", "text/html"],
#                   api_spec_url='/api/spec', description='API Spec')


@app.route("/")
def index():
    return render_template('index.html', title='Home')


@app.route('/image', methods=['POST'])
def post_image():
    received_image = request.data

    confidence_min = int(config['models']['confidence_min'])
    if 'confidence_min' in request.args:
        confidence_min = int(request.args.get(config['models']['confidence_min']))

    if 'application/json' in request.accept_mimetypes:
        return jsonify(detector.detect_in_image(received_image, confidence_min))
    else:
        return send_file(detector.detect_in_image(received_image, confidence_min, type_to_return='image'),
                         mimetype='image/png')


@app.route("/status")
def status():
    return "I'm alive on " + str(socket.gethostbyname(socket.gethostname()))


if __name__ == "__main__":
    app.run()
