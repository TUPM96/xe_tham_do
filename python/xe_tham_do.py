import socket
import threading
import subprocess
import cv2
from flask import Flask, Response
import sys

# ROS2 import
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

# ---------- ROS2 PUBLISHER NODE ----------

MAX_MOTOR = 100.0  # motor nhận giá trị từ -100 đến 100
MAX_LINEAR = 0.5   # m/s (tốc độ tối đa thực tế của xe bạn)
WHEEL_BASE = 0.3   # mét (khoảng cách giữa 2 bánh, chỉnh theo xe)

class CmdVelPublisher(Node):
    def __init__(self):
        super().__init__('socket_cmd_vel_bridge')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

    def speed_to_twist(self, speed_left, speed_right):
        v_l = speed_left / MAX_MOTOR * MAX_LINEAR
        v_r = speed_right / MAX_MOTOR * MAX_LINEAR
        v = (v_r + v_l) / 2.0
        omega = (v_r - v_l) / WHEEL_BASE
        twist = Twist()
        twist.linear.x = float(v)
        twist.angular.z = float(omega)
        return twist

    def gui_lenh_dieu_khien_cmd_vel(self, speed1, speed2):
        twist = self.speed_to_twist(speed1, speed2)
        self.publisher.publish(twist)
        print(f"[Publish /cmd_vel] linear.x={twist.linear.x:.2f} angular.z={twist.angular.z:.2f}")

# ---------- PHẦN 1: SOCKET ĐIỀU KHIỂN XE ----------

HOST = '0.0.0.0'
PORT = 3000

cmd_vel_node = None

def xu_ly_lenh_socket(command):
    command = command.strip()
    if command.startswith("0"):
        try:
            parts = command.split()
            if len(parts) == 3:
                speed1 = int(parts[1])
                speed2 = int(parts[2])
                if cmd_vel_node is not None:
                    cmd_vel_node.gui_lenh_dieu_khien_cmd_vel(speed1, speed2)
            else:
                print("Sai cú pháp lệnh 0 speed1 speed2")
        except Exception as e:
            print("Lỗi khi xử lý tốc độ:", e)
    else:
        print("Nhận lệnh khác:", command)
        # Xử lý các lệnh khác nếu cần

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
                xu_ly_lenh_socket(command)
                try:
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
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = buffer.tobytes()
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

# ---------- MAIN: CHẠY SONG SONG 2 SERVER + ROS2 ----------
if __name__ == '__main__':
    rclpy.init()
    cmd_vel_node = CmdVelPublisher()
    t1 = threading.Thread(target=start_socket_server, daemon=True)
    t2 = threading.Thread(target=start_flask_server, daemon=True)
    t1.start()
    t2.start()
    try:
        rclpy.spin(cmd_vel_node)
    except KeyboardInterrupt:
        pass
    finally:
        cmd_vel_node.destroy_node()
        rclpy.shutdown()