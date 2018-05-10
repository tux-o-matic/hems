from flask import Flask, render_template
from flask_restful import Api
from flask_restful_swagger import swagger
import configparser
import cv2
import imutils
import numpy as np
import socket
import time

application = Flask(__name__)

config = configparser.ConfigParser()

url = config['server']['protocol'] + '://' + config['server']['hostname'] + ':' +  config['server']['port']
api = swagger.docs(Api(application), apiVersion='0.1',
                   basePath=url,
                   resourcePath='/',
                   produces=["application/json", "text/html"],
                   api_spec_url='/api/spec', description='API Spec')


@application.route("/")
def index():
    return render_template('index.html', title='Home')


@application.route("/status")
def status():
    return "I'm alive on " + str(socket.gethostbyname(socket.gethostname()))


if __name__ == "__main__":
    application.run()