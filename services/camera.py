#!/usr/bin/env python3
from cv2 import imencode, IMWRITE_JPEG_QUALITY, CascadeClassifier, cvtColor, COLOR_RGB2GRAY, rectangle, CAP_FFMPEG
from imutils import resize
from imutils.video import FileVideoStream
from time import time

def get_video_capture(): 
    return FileVideoStream(0).start()

def video_generator(video, quality=95, width=400, fps=60):
    face_cascade = CascadeClassifier('haarcascade_frontalface_default.xml')

    prev = 0
    while video.more():
        time_elapsed = time() - prev
        if time_elapsed > 1.0 / fps:
            prev = time()
            frame = video.read()
            if frame is None: continue
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
