import socket
import threading
import subprocess
import cv2
from flask import Flask, Response
import sys

# ---------- PHẦN 1: SOCKET ĐIỀU KHIỂN XE ----------

HOST = '0.0.0.0'
PORT = 3000

def gui_lenh_dieu_khien(cmd_line):
    # Ở đây bạn thay bằng publish ROS/MQTT hoặc hàm gửi tới xe thực sự
    # Ví dụ: Gửi lên robot, hoặc in ra để debug
    print(f"[Publish tới robot]: {cmd_line}")

def xu_ly_lenh_socket(command):
    command = command.strip()
    # Kiểm tra cú pháp: "0 speed1 speed2"
    if command.startswith("0"):
        try:
            parts = command.split()
            if len(parts) == 3:
                speed1 = int(parts[1])
                speed2 = int(parts[2])
                # Tạo lệnh điều khiển phù hợp hệ thống thực tế của bạn
                cmd_line = f"robot/control/set_speed {speed1} {speed2}"
                gui_lenh_dieu_khien(cmd_line)
                print(f"Đã gửi lệnh: {cmd_line}")
            else:
                print("Sai cú pháp lệnh 0 speed1 speed2")
        except Exception as e:
            print("Lỗi khi xử lý tốc độ:", e)
    else:
        print("Nhận lệnh khác:", command)
        # Nếu là lệnh khác, bạn có thể xử lý hoặc gửi đi tùy mục đích
        # Ví dụ: gui_lenh_dieu_khien(command)

def handle_client(conn, addr):
    print(f"[KET NOI MOI] {addr} da ket noi.")
    try:
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    print(f"[MAT KET NOI] {addr}")
                    break
                command = data.decode('utf-8').strip()
                print(f"[NHAN] {addr}: {command}")
                # Xử lý lệnh nhận được:
                xu_ly_lenh_socket(command)
                try:
                    # Demo: echo lại lệnh nhận được
                    result = subprocess.run(['echo', command], capture_output=True, text=True)
                    output = result.stdout.strip()
                except Exception as e:
                    output = f"LOI: {e}"
                conn.sendall(output.encode('utf-8'))
    except Exception as e:
        print(f"[LOI] {addr}: {e}")

def start_socket_server():
    print("[KHOI DONG] Server socket dang chay...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"[LANG NGHE] Dia chi: {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()

# ---------- PHẦN 2: FLASK STREAM WEBCAM ----------

app = Flask(__name__)

def gen_frames():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Khong mo duoc webcam!", file=sys.stderr)
        return
    try:
        while True:
            success, frame = cap.read()
            if not success:
                break
            # Chuyển ảnh sang JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            # Stream MJPEG
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        cap.release()

@app.route('/video')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return "<h1>Webcam stream. Xem tại <a href='/video'>/video</a></h1>"

def start_flask_server():
    print("[KHOI DONG] Flask webcam stream tren http://0.0.0.0:5000/video")
    app.run(host='0.0.0.0', port=5000, threaded=True)

# ---------- MAIN: CHẠY SONG SONG 2 SERVER ----------

if __name__ == '__main__':
    t1 = threading.Thread(target=start_socket_server, daemon=True)
    t2 = threading.Thread(target=start_flask_server, daemon=True)
    t1.start()
    t2.start()
    # Giữ main thread sống
    t1.join()
    t2.join()