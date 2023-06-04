#!/usr/bin/env python3
from cv2 import imencode, imdecode, IMWRITE_JPEG_QUALITY, CascadeClassifier, cvtColor, COLOR_RGB2GRAY, rectangle, CAP_FFMPEG
from imutils import resize
from time import time
from websockets.sync.client import connect
import numpy as np

def video_generator(quality=95, width=400, fps=60, host="127.0.0.1", port="6969"):
    face_cascade = CascadeClassifier('haarcascade_frontalface_default.xml')

    prev = 0
    with connect("ws://%s:%s" % (host, port)) as websocket:
        for frame in websocket:
            frame = imdecode(np.frombuffer(frame, dtype=np.uint8), 1)
            time_elapsed = time() - prev
            if time_elapsed > 1.0 / fps:
                prev = time()
                frame = resize(frame, width=width)

                gray = cvtColor(frame, COLOR_RGB2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                for (x,y,w,h) in faces:
                    # To draw a rectangle in a face 
                    rectangle(frame,(x,y),(x+w,y+h),(219,112,147),2) 

                (_, buffer) = imencode(".jpg", frame, [IMWRITE_JPEG_QUALITY, quality])
                yield (b'--frame\r\n' +
                    b'Content-Type: image/jpeg\r\n\r\n' +
                    bytes(buffer) +
                    b'\r\n')
