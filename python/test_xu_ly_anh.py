import threading
from flask import Flask, render_template_string, Response
import cv2
import numpy as np
import time
import sys
from ultralytics import YOLO

# ----------- CAMERA VÀ NHẬN DIỆN -----------
webcam_index = 0 # camera thường
thermal_index = 1 # camera nhiệt
latest_frame = None
frame_lock = threading.Lock()
yolo_model = YOLO("yolov8n.pt")

def webcam_reader():
    global latest_frame
    cap = cv2.VideoCapture(webcam_index)
    if not cap.isOpened():
        print("Không mở được camera!", file=sys.stderr)
        return
    while True:
        success, frame = cap.read()
        if not success:
            print("Không đọc được frame, thử lại sau 1s ...", file=sys.stderr)
            time.sleep(1)
            cap.release()
            cap = cv2.VideoCapture(webcam_index)
            continue
        with frame_lock:
            latest_frame = frame
        time.sleep(0.03)

def gen_frames():
    global latest_frame
    while True:
        with frame_lock:
            frame = latest_frame.copy() if latest_frame is not None else None
        if frame is not None:
            results = yolo_model(frame, verbose=False)
            boxes = results[0].boxes.xyxy.cpu().numpy()
            confs = results[0].boxes.conf.cpu().numpy()
            clss = results[0].boxes.cls.cpu().numpy().astype(int)
            for (x1, y1, x2, y2), conf, cls in zip(boxes, confs, clss):
                label = f"{results[0].names[cls]} {conf:.2f}"
                color = (0,255,0)
                cv2.rectangle(frame, (int(x1),int(y1)), (int(x2),int(y2)), color, 2)
                cv2.putText(frame, label, (int(x1),int(y1)-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.1)

def detect_fire(frame, fire_threshold=200):
    if len(frame.shape) == 3:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    else:
        gray = frame
    thresh = cv2.threshold(gray, fire_threshold, 255, cv2.THRESH_BINARY)[1]
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,0,255), 2)
            cv2.putText(frame, "FIRE", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
    return frame

def gen_thermal_frames():
    cap = cv2.VideoCapture(thermal_index)
    if not cap.isOpened():
        print("Không mở được camera nhiệt!", file=sys.stderr)
        return
    try:
        while True:
            success, frame = cap.read()
            if not success:
                break
            frame = detect_fire(frame, fire_threshold=200)
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        cap.release()

# ----------- FLASK WEB SERVER -----------
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Robot Camera Web</title>
    <style>
        body { background: #222; color: #fff; font-family: sans-serif; }
        .container { max-width: 900px; margin: auto; }
        h1 { text-align: center; }
        .row { display: flex; justify-content: space-between; margin: 20px 0; }
        .video-box { flex: 1; margin: 0 10px; }
        .video-box h3 { text-align: center; }
        img { width: 100%; border-radius: 8px; }
    </style>
</head>
<body>
<div class="container">
    <h1>Robot Camera Web</h1>
    <div class="row">
        <div class="video-box">
            <h3>Camera nhận diện (YOLOv8)</h3>
            <img src="{{ url_for('video_feed') }}" />
        </div>
        <div class="video-box">
            <h3>Camera nhiệt phát hiện cháy</h3>
            <img src="{{ url_for('video1_feed') }}" />
        </div>
    </div>
</div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/video')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video1')
def video1_feed():
    return Response(gen_thermal_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    t_cam = threading.Thread(target=webcam_reader, daemon=True)
    t_cam.start()
    app.run(host='0.0.0.0', port=5555, threaded=True)