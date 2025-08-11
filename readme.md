# @. Kết nối tới jetson nano

# 1. Kết nối dây LAN từ máy tính tới jetson nano
# 2. SSH tới jetson nano
```bash
ssh ubuntu@ubuntu-desktop
```
# 3. Lấy danh sách wifi gần đây
```bash
sudo nmcli device wifi list
```

# 4. Kết nối tới wifi mới
```bash
sudo nmcli device wifi connect "admin23" password "12345678"
```
# 5. Lấy địa chỉ IP của jetson nano
```bash
ip a
```

# 6. Kết nối tới jetson nano từ IP mới
```bash
ssh ubuntu@192.168.137.128
```
Sau đó làm việc với jetson nano như bình thường.

# A. Build source
## 1. Chạy docker
``` bash
cd ~/Desktop/xe_tham_do

# Chỉ chạy khi muốn build lại từ đầu
# git pull                              

# Chỉ chạy khi muốn build lại source từ đầu
# docker-compose build --no-cache       

docker-compose up -d


# Chỉ chạy khi muốn build lại từ đầu
# rm -rf logs install build    

# Chỉ chạy khi muốn build lại từ đầu         
# rm -rf /build/ackermann_msgs/ament_cmake_python/ackermann_msgs/ackermann_msgs 

# docker exec -it ros2_humble_container bash

# Chỉ chạy khi muốn build lại từ đầu
# colcon build --symlink-install        
# colcon build --packages-select xe_tham_do
```
**Sau đó có thể chạy lệnh bên dưới**

# B. Chạy các phần tử

# 1. Chạy robot thật

* ###  Chạy robot tổng
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source install/setup.bash

ros2 launch xe_tham_do launch_robot.launch.py
```

* ### Chạy robot với điều khiển từ bàn phím
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source install/setup.bash

ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/cmd_vel_raw
```

* ### Chạy né vật cản khi điều khiển bằng tay
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source install/setup.bash

cd ~/python

python safety_teleop.py
```


* ### Chạy lidar A1M8
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source install/setup.bash

ros2 launch xe_tham_do rplidar.launch.py serial_port:=/dev/serial/by-path/platform-70090000.xusb-usb-0:2.4:1.0-port0 scan_mode:=Sensitivity

```

* ###  Chạy slam toolbox để tạo map
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source install/setup.bash

sudo apt update

sudo apt install libceres-dev

ros2 launch xe_tham_do online_async_launch.py
```

* ### Mở rviz2 xem map đang được tạo
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

cd ~/ros2_ws

rviz2 -d src/xe_tham_do/config/map.rviz
```

* #### Lưu map
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source install/setup.bash

mkdir -p ~/maps

apt install libgraphicsmagick++-dev

ros2 run nav2_map_server map_saver_cli -f ~/maps/my_map
```


* ### Chạy điều khiển từ xa bằng app điện thoại
```bash
docker exec -it ros2_humble_container bash

cd ~/python

pip install --ignore-installed blinker

pip install flask

source /opt/ros/humble/install/setup.bash

pip install --ignore-installed sympy

pip install ultralytics

pip install "numpy<2"

python xe_tham_do.py
```

Tắt rviz2 và slam_toolbox khi đã lưu map

* ###  Chạy location
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source install/setup.bash

sudo apt update

sudo apt install libgraphicsmagick++-dev

ros2 launch xe_tham_do localization_launch.py map:=/root/maps/my_map.yaml params_file:=/root/ros2_ws/src/xe_tham_do/config/nav2_params.yaml

```


* ### Chạy navigation
```bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source install/setup.bash

ros2 launch nav2_bringup bringup_launch.py  params_file:=/root/ros2_ws/src/xe_tham_do/config/nav2_params.yaml map:=/root/maps/my_map.yaml


```




