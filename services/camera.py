#!/usr/bin/env python3
from cv2 import VideoCapture, imencode, IMWRITE_JPEG_QUALITY, CAP_PROP_FPS
from imutils import resize
from time import time

VideoCapture = VideoCapture

def video_generator(video, quality=95, width=400, fps=60):
    prev = 0
    while video.isOpened():
        time_elapsed = time() - prev
        if time_elapsed > 1.0 / fps:
            prev = time()
            (_, frame) = video.read()
            frame = resize(frame, width=width)
            (_, buffer) = imencode(".jpg", frame, [IMWRITE_JPEG_QUALITY, quality])
            yield (b'--frame\r\n' +
                b'Content-Type: image/jpeg\r\n\r\n' +
                bytes(buffer) +
                b'\r\n')
