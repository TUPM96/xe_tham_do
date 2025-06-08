# A. Build source
## 1. Chạy docker
``` bash
cd ~/Desktop/xe_tham_do
git pull
docker-compose build --no-cache
docker-compose up -d
docker exec -it ros2_humble_container bash
```
**Sau đó có thể chạy lệnh bên dưới**

# B. Chạy các phần tử
## 1. Chạy robot để test điều khiển động cơ từ bàn phím

* ### Chạy diffdrive_arduino
``` bash
rm -rf logs install build
rm -rf /root/ros2_ws/build/ackermann_msgs/ament_cmake_python/ackermann_msgs/ackermann_msgs
colcon build --symlink-install


docker exec -it ros2_humble_container bash
source /opt/ros/humble/install/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch diffdrive_arduino diffbot.launch.py
```

* ### Chạy robot với điều khiển từ bàn phím
``` bash
docker exec -it ros2_humble_container bash
source /opt/ros/humble/install/setup.bash
source /opt/ros/humble/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=diffbot_base_controller/cmd_vel_unstamped
```

# 2. Chạy robot thật

### Lấy port COM theo path

``` bash
docker exec -it ros2_humble_container bash
ls -l /dev/serial/by-path/
```


* ###  Chạy robot tổng
``` bash
docker exec -it ros2_humble_container bash
source ~/ros2_ws/install/setup.bash
ros2 launch xe_tham_do launch_robot.launch.py
```


* ### Chạy robot với điều khiển từ bàn phím
``` bash
docker exec -it ros2_humble_container bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

* ### Test lidar xem ở port nào
``` bash
docker exec -it ros2_humble_container bash
ros2 run rplidar_ros rplidar_composition --ros-args -p serial_port:=/dev/ttyUSB0 -p serial_baudrate:=115200
```

* ### Chạy lidar
``` bash
docker exec -it ros2_humble_container bash
source ~/ros2_ws/install/setup.bash
ros2 launch xe_tham_do rplidar.launch.py serial_port:=/dev/ttyUSB0
```

* ###  Chạy camera
``` bash
docker exec -it ros2_humble_container bash
sudo chmod 777 /dev/video*
source ~/ros2_ws/install/setup.bash
ros2 launch xe_tham_do camera.launch.py
```

* ### Chạy http video
``` bash
docker exec -it ros2_humble_container bash
cd ~/Desktop
cd xedieukhien
python3 video.py
```

* ###  Chạy slam toolbox
``` bash
docker exec -it ros2_humble_container bash
source ~/ros2_ws/install/setup.bash
ros2 launch xe_tham_do online_async_launch.py
```

* ### Mở rviz2 xem map
``` bash
docker exec -it ros2_humble_container bash
cd ~/ros2_ws
rviz2 -d src/xe_tham_do/config/map.rviz
```

* ### Mở rviz2 xem tổng quan
``` bash
docker exec -it ros2_humble_container bash
cd ~/ros2_ws
rviz2 -d src/xe_tham_do/config/main.rviz
```

* ### Lưu map
``` bash
docker exec -it ros2_humble_container bash
mkdir -p ~/maps
```

* ### Chạy localization từ map đã tạo
``` bash
docker exec -it ros2_humble_container bash
ros2 launch xe_tham_do localization_launch.py map:=/home/ubuntu/maps/my_map.yaml
```


* ### Chạy navigation
``` bash
docker exec -it ros2_humble_container bash
source ~/ros2_ws/install/setup.bash
ros2 launch xe_tham_do navigation_launch.py
```





