import jetson.inference
import jetson.utils
import numpy as np
import cv2
from flask import Flask, Response

app = Flask(__name__)

net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = jetson.utils.videoSource("/dev/video0")

def gen_frames():
    while True:
        img = camera.Capture()
        detections = net.Detect(img)
        # Chuyển jetson.utils.cudaImage thành numpy array
        frame = jetson.utils.cudaToNumpy(img)
        # Vẽ bounding box người
        for det in detections:
            if net.GetClassDesc(det.ClassID) == "person":
                x1, y1, x2, y2 = int(det.Left), int(det.Top), int(det.Right), int(det.Bottom)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        # Chuyển BGR -> JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '<h1>Jetson Person Detection</h1><img src="/video_feed">'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)