#!/usr/bin/env python3
from flask import Flask, Response, render_template, request, redirect, url_for
from signal import signal, SIGINT
from sys import exit
from os import listdir
from imghdr import what

from services.camera import VideoCapture, video_generator
from services.process import Process

app = Flask(__name__)
processor = Process()
last_cam = None

# Routes
@app.route("/", methods=['GET'])
def root():
    images = listdir('static')
    return render_template("base.html", images=images)

@app.route("/live", methods=['GET'])
def live():
    fps = request.args.get("fps", default="30")
    return render_template("video.html", fps=fps)

@app.route("/images/<name>", methods=['GET'])
def images(name):
    return render_template("image.html", image=name)

@app.route("/quoi", methods=['GET'])
def quoi():
    return render_template("raw.html", body="<p>feur</p>")

@app.route("/process", methods=['GET', 'POST'])
def process():
    if request.method == 'POST':
        if 'file' in request.files and request.files.get("file").filename != '':
            file = request.files.get('file')
            processor.add_image_from_buffer(file.filename, file)
        elif 'url' in request.form:
            processor.add_image_from_url(request.form.get("url"))

        return redirect(url_for('process'))
    else:
        images = processor.get_images()
        return render_template("process.html", images=images)

# Internal routes
@app.route("/process/<image_hash>", methods=['GET'])
def image_by_hash(image_hash):
    image = processor.get_image(image_hash)
    return Response(
        image,
        mimetype=what(image)
    )

@app.route("/video_feed.mjpg", methods=['GET'])
def video_feed():
    last_cam = VideoCapture(0)
    fps = request.args.get("fps", default=30, type=int)
    return Response(
        video_generator(last_cam, fps=fps),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

# Initializer
def on_sigint(sig, frame):
    if last_cam != None: last_cam.release()
    exit(0)

def main():
    signal(SIGINT, on_sigint)
    app.run(host="127.0.0.1", port=4242, debug=True)

if __name__=="__main__":
    main()