#!/usr/bin/env python3
from flask import Flask, Response, render_template, request
from signal import signal, SIGINT
from sys import exit

from services.camera import VideoCapture, video_generator

app = Flask(__name__)
last_cam = None

# Routes
@app.route("/", methods=['GET'])
def root():
    fps = request.args.get("fps", default="30")
    return render_template("index.html", fps=fps)

@app.route("/video_feed", methods=['GET'])
def video_feed():
    last_cam = VideoCapture(0)
    fps = request.args.get("fps", default=30, type=int)
    return Response(
        video_generator(last_cam, fps=fps),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route("/quoi", methods=['GET'])
def quoi():
    return render_template("index.html", body="<p>feur</p>")

# Initializer
def on_sigint(sig, frame):
    if last_cam != None: last_cam.release()
    exit(0)

if __name__=="__main__":
    signal(SIGINT, on_sigint)
    app.run(host="127.0.0.1", port=4242)