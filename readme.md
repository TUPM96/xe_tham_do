# Source bao gồm các thư viện ROS2 cần thiết để chạy robot
# Cây thư mục: 
# - articubot_one
Source code chính của chạy robot
# - diffdrive_arduino
Source code cho điều khiển động cơ
# - serial
Source code cho giao tiếp qua serial




# 1. Chạy robot để test điều khiển động cơ từ bàn phím

* ### Chạy diffdrive_arduino
`
cd ~/ros2_ws
colcon build --symlink-install
source ~/ros2_ws/install/setup.bash
ros2 launch diffdrive_arduino diffbot.launch.py
`

* ### Chạy robot với điều khiển từ bàn phím
`
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=diffbot_base_controller/cmd_vel_unstamped
`

# 2. Chạy robot thật

### Lấy port COM theo path

`
ls -l /dev/serial/by-path/
`
* ### Chạy robot với điều khiển từ bàn phím
`
ros2 run teleop_twist_keyboard teleop_twist_keyboard
`

* ### Test lidar xem ở port nào
`
ros2 run rplidar_ros rplidar_composition --ros-args -p serial_port:=/dev/ttyUSB0 -p serial_baudrate:=115200
`

* ### Chạy lidar
`
source ~/ros2_ws/install/setup.bash
ros2 launch articubot_one rplidar.launch.py serial_port:=/dev/ttyUSB0
`





* ### Chạy http video
`
cd ~/Desktop
cd xedieukhien
python3 video.py
`

* ###  Chạy slam toolbox
`
source ~/ros2_ws/install/setup.bash
ros2 launch articubot_one online_async_launch.py
`

* ### Mở rviz2 xem map
`
cd ~/ros2_ws
rviz2 -d src/articubot_one/config/map.rviz
`

* ### Mở rviz2 xem tổng quan
`
cd ~/ros2_ws
rviz2 -d src/articubot_one/config/main.rviz
`

* ### Lưu map
`
mkdir -p ~/maps
ros2 run nav2_map_server map_saver_cli -f ~/maps/my_map
`

* ### Chạy localization từ map đã tạo
`
ros2 launch articubot_one localization_launch.py map:=/home/ubuntu/maps/my_map.yaml
`


* ### Chạy navigation
`
source ~/ros2_ws/install/setup.bash
ros2 launch articubot_one navigation_launch.py
`

* ### Chạy tìm cỏ
`
source ~/ros2_ws/install/setup.bash
ros2 launch articubot_one find_grass.launch.py
`







Hôm nay chạy 26/05/2025

* ### Chạy thủ công
`
cd ~/Desktop
cd xedieukhien
python3 xecatco.py
`

* ###  Chạy camera
`
sudo chmod 777 /dev/video*
source ~/ros2_ws/install/setup.bash
ros2 launch articubot_one camera.launch.py
`

* ###  Chạy robot tổng
`
source ~/ros2_ws/install/setup.bash
ros2 launch articubot_one launch_robot.launch.py
`


--------------------------

* ### Chạy tìm cỏ theo tay
`
cd ~/Desktop
cd xedieukhien
python3 grass.py
`



