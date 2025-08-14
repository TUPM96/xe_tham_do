import socket
import threading
import subprocess
import cv2
from flask import Flask, Response
import sys
import numpy as np
import time

# YOLOv8
from ultralytics import YOLO

# ROS2 import
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped
from nav_msgs.msg import Odometry, OccupancyGrid

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
        print(f"[Publish /cmd_vel] linear.x={twist.linear.x:.2f} angular.z={twist.angular.z:.2f}")
        self.publisher.publish(twist)

# ---------- ROS2 SUBSCRIBER: POSE & MAP ----------
latest_pose = {"x": 0.0, "y": 0.0, "from_amcl": False}
latest_map = None

class AmclPoseSubscriber(Node):
    def __init__(self):
        super().__init__('amcl_pose_subscriber')
        self.subscription = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.listener_callback,
            10)
        self.subscription

    def listener_callback(self, msg):
        global latest_pose
        latest_pose["x"] = msg.pose.pose.position.x
        latest_pose["y"] = msg.pose.pose.position.y
        latest_pose["from_amcl"] = True

class OdomSubscriber(Node):
    def __init__(self):
        super().__init__('odom_subscriber')
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.listener_callback,
            10)
        self.subscription

    def listener_callback(self, msg):
        global latest_pose
        # Chỉ update nếu không lấy từ amcl
        if latest_pose.get("from_amcl", False):
            return
        latest_pose["x"] = msg.pose.pose.position.x
        latest_pose["y"] = msg.pose.pose.position.y

class MapSubscriber(Node):
    def __init__(self):
        super().__init__('map_subscriber')
        self.subscription = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.listener_callback,
            10)
        self.subscription

    def listener_callback(self, msg):
        global latest_map
        latest_map = msg

# ---------- PHẦN 1: SOCKET ĐIỀU KHIỂN XE ----------

HOST = '0.0.0.0'
PORT = 3000

cmd_vel_node = None

def xu_ly_lenh_socket(command):
    global cmd_vel_node
    command = command.strip()
    if command.startswith("o"):
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

# ---------- PHẦN 2: FLASK STREAM WEBCAM + THERMAL + MAP ----------

app = Flask(__name__)

# ----------- WEBCAM/RTSP THREAD (YOLOv8) -----------
webcam_index = 0 # đổi thành URL RTSP nếu cần

latest_frame = None
frame_lock = threading.Lock()

def webcam_reader():
    global latest_frame
    cap = cv2.VideoCapture(webcam_index)
    if not cap.isOpened():
        print("Khong mo duoc camera!", file=sys.stderr)
        return
    while True:
        success, frame = cap.read()
        if not success:
            print("Khong doc duoc frame, dang thu lai sau 1s ...", file=sys.stderr)
            time.sleep(1)
            cap.release()
            cap = cv2.VideoCapture(webcam_index)
            continue
        with frame_lock:
            latest_frame = frame
        time.sleep(0.03)  # ~30fps

yolo_model = YOLO("yolov8n.pt")

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

@app.route('/video')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ----------- FLAME DETECTION TRÊN CAMERA NHIỆT (thermal) -----------

thermal_index = 1  # đổi thành đúng index hoặc URL của camera nhiệt

FIRE_TEMP_THRESHOLD = 200  # mặc định, bạn có thể đổi thành 180, 220... tùy camera

def detect_fire(frame, fire_threshold=None):
    if fire_threshold is None:
        fire_threshold = FIRE_TEMP_THRESHOLD
    if len(frame.shape) == 3:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    else:
        gray = frame

    # Tìm pixel có nhiệt độ cao nhất
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(gray)
    # Vẽ khung vùng max nhiệt độ, hiển thị lên hình
    x, y = maxLoc
    # Nếu muốn khoanh vùng 20x20 quanh điểm nóng nhất:
    box_size = 20
    x1 = max(0, x - box_size // 2)
    y1 = max(0, y - box_size // 2)
    x2 = min(gray.shape[1] - 1, x + box_size // 2)
    y2 = min(gray.shape[0] - 1, y + box_size // 2)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,255), 2)
    cv2.putText(frame, f"MAX TEMP: {int(maxVal)}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

    # Phát hiện vùng vượt ngưỡng nhiệt (đám cháy)
    thresh = cv2.threshold(gray, fire_threshold, 255, cv2.THRESH_BINARY)[1]
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    has_fire = False
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100:
            has_fire = True
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,0,255), 2)
            cv2.putText(frame, f"FIRE {fire_threshold}", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
    return frame, has_fire

def gen_thermal_frames():
    global FIRE_TEMP_THRESHOLD
    cap = cv2.VideoCapture(thermal_index)
    if not cap.isOpened():
        print("Khong mo duoc camera nhiet!", file=sys.stderr)
        return
    try:
        while True:
            success, frame = cap.read()
            if not success:
                break
            frame, has_fire = detect_fire(frame, fire_threshold=FIRE_TEMP_THRESHOLD)
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        cap.release()

@app.route('/video1')
def video1_feed():
    return Response(gen_thermal_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# --- Thêm API chỉnh nhiệt độ phát hiện đám cháy ---
from flask import request, redirect

@app.route('/set_temp', methods=['GET', 'POST'])
def set_temp():
    global FIRE_TEMP_THRESHOLD
    if request.method == 'POST':
        try:
            val = int(request.form.get('fire_temp', FIRE_TEMP_THRESHOLD))
            FIRE_TEMP_THRESHOLD = val
        except Exception:
            pass
        return redirect('/')
    else:
        return f'''
        <form method="POST">
            <label>Ngưỡng nhiệt độ phát hiện FIRE (0-255): </label>
            <input name="fire_temp" type="number" min="0" max="255" value="{FIRE_TEMP_THRESHOLD}">
            <input type="submit" value="Cập nhật">
        </form>
        <p>Giá trị hiện tại: <b>{FIRE_TEMP_THRESHOLD}</b></p>
        <a href="/">Quay lại trang chủ</a>
        '''

# --- Sửa trang index để có link chỉnh nhiệt độ ---
@app.route('/')
def index():
    return f"""
    <h1>Webcam YOLOv8 nhận diện <a href='/video'>/video</a></h1>
    <h1>Camera nhiệt nhận diện đám cháy <a href='/video1'>/video1</a></h1>
    <h1>Bản đồ vị trí xe (OccupancyGrid) <a href='/video3'>/video3</a></h1>
    <hr>
    <a href='/set_temp'>Chỉnh ngưỡng nhiệt độ phát hiện đám cháy (FIRE)</a>
    <br>
    <b>Ngưỡng hiện tại: {FIRE_TEMP_THRESHOLD}</b>
    """

# ----------- OCCUPANCY GRID MAP TO VIDEO STREAM -----------
def occupancy_grid_to_img(msg):
    data = np.array(msg.data, dtype=np.int8).reshape((msg.info.height, msg.info.width))
    img = np.zeros((msg.info.height, msg.info.width, 3), dtype=np.uint8)
    img[data == -1] = [128, 128, 128]    # unknown = gray
    img[data == 0] = [255, 255, 255]     # free = white
    img[data == 100] = [0, 0, 0]         # occupied = black
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
    return img

def gen_map_frames():
    global latest_map
    while True:
        if latest_map is not None:
            img = occupancy_grid_to_img(latest_map)
            try:
                x = latest_pose["x"]
                y = latest_pose["y"]
                mx = int((x - latest_map.info.origin.position.x) / latest_map.info.resolution)
                my = int((y - latest_map.info.origin.position.y) / latest_map.info.resolution)
                my = latest_map.info.height - my
                mx = mx * 2
                my = my * 2
                cv2.circle(img, (mx, my), 6, (0,0,255), -1)
            except Exception:
                pass
            ret, buffer = cv2.imencode('.jpg', img)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            time.sleep(0.1)

@app.route('/video3')
def video3_feed():
    return Response(gen_map_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_flask_server():
    print("[KHOI DONG] Flask webcam stream tren http://0.0.0.0:5000/video")
    app.run(host='0.0.0.0', port=5000, threaded=True)

# ---------- MAIN: CHẠY SONG SONG 3 SERVER + ROS2 ----------
if __name__ == '__main__':
    rclpy.init()
    cmd_vel_node = CmdVelPublisher()
    map_node = MapSubscriber()
    amcl_pose_node = AmclPoseSubscriber()
    odom_node = OdomSubscriber()
    t1 = threading.Thread(target=start_socket_server, daemon=True)
    t2 = threading.Thread(target=start_flask_server, daemon=True)
    t_cam = threading.Thread(target=webcam_reader, daemon=True)
    t1.start()
    t2.start()
    t_cam.start()
    try:
        executor = rclpy.executors.MultiThreadedExecutor()
        executor.add_node(cmd_vel_node)
        executor.add_node(map_node)
        executor.add_node(amcl_pose_node)
        executor.add_node(odom_node)
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        cmd_vel_node.destroy_node()
        map_node.destroy_node()
        amcl_pose_node.destroy_node()
        odom_node.destroy_node()
        rclpy.shutdown()