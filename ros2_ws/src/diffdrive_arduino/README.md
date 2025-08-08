# diffdrive_arduino

Gói `diffdrive_arduino` là một package hỗ trợ điều khiển robot sử dụng điều khiển vi sai (differential drive) thông qua Arduino. Gói này thường dùng trong các dự án robot di động, cho phép giao tiếp giữa máy tính chủ (host) và vi điều khiển Arduino để điều khiển động cơ và đọc dữ liệu encoder.

## Tính năng

- Giao tiếp với Arduino để điều khiển động cơ vi sai (2 bánh độc lập trái/phải)
- Nhận dữ liệu encoder từ Arduino để xác định vận tốc và vị trí robot
- Tích hợp dễ dàng vào các hệ thống robot dựa trên ROS (Robot Operating System)
- Tùy chỉnh các thông số PID, tốc độ, và cấu hình phần cứng qua file cấu hình

## Thư mục chính

- `firmware/`: Chứa mã nguồn Arduino để nạp vào vi điều khiển
- `src/`: Chứa mã nguồn ROS node dùng để giao tiếp với Arduino
- `launch/`: Chứa các file launch để khởi động node dễ dàng
- `config/`: Chứa file cấu hình (nếu có)

## Yêu cầu

- Arduino (Uno, Mega hoặc tương tự)
- Bộ điều khiển động cơ (motor driver)
- Encoder gắn trên động cơ
- ROS Noetic (hoặc phiên bản tương thích)
- Thư viện Arduino: `rosserial`, `Encoder`, `PID` (hoặc các thư viện do bạn tự chọn)

## Cài đặt

### 1. Nạp firmware cho Arduino

1. Mở file trong thư mục `firmware/` bằng Arduino IDE.
2. Chỉnh lại các thông số chân kết nối, PID… cho phù hợp với phần cứng của bạn.
3. Nạp chương trình vào Arduino.

### 2. Build package ROS

```bash
cd ~/catkin_ws/src
git clone https://github.com/TUPM96/xe_cat_co.git
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

### 3. Kết nối Arduino với máy tính

Kết nối Arduino qua cổng USB. Xác định port serial (thường là `/dev/ttyACM0` hoặc `/dev/ttyUSB0`).

### 4. Khởi động node

```bash
roslaunch diffdrive_arduino diffdrive.launch
```
Hoặc chỉnh sửa file launch/config cho phù hợp.

## Cấu hình

Bạn có thể chỉnh sửa các thông số trong file cấu hình như:

- `port`: Cổng serial kết nối với Arduino
- `baudrate`: Tốc độ truyền serial
- `wheel_radius`, `wheel_base`: Kích thước bánh xe và khoảng cách giữa 2 bánh
- Các thông số PID

## Sử dụng

Sau khi node hoạt động, bạn có thể gửi lệnh vận tốc đến topic `/cmd_vel` để điều khiển robot, hoặc đọc dữ liệu odometry từ `/odom`.
