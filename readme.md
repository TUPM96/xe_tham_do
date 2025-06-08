# . Kết nối tới jetson nano
```bash
ssh ubuntu@192.168.137.192
```


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

docker exec -it ros2_humble_container bash

# Chỉ chạy khi muốn build lại từ đầu
# colcon build --symlink-install        

```
**Sau đó có thể chạy lệnh bên dưới**

# B. Chạy các phần tử
## 1. Chạy robot để test điều khiển động cơ từ bàn phím

* ### Chạy diffdrive_arduino
``` bash

docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source /install/setup.bash

ros2 launch diffdrive_arduino diffbot.launch.py
```

* ### Chạy robot với điều khiển từ bàn phím
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source /install/setup.bash

ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=diffbot_base_controller/cmd_vel_unstamped
```

# 2. Chạy robot thật

### Lấy port COM theo path

``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source /install/setup.bash

ls -l /dev/serial/by-path/
```

* ###  Chạy robot tổng
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source /install/setup.bash

ros2 launch xe_tham_do launch_robot.launch.py
```

* ### Chạy robot với điều khiển từ bàn phím
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source /install/setup.bash

ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

* ### Test lidar xem ở port nào
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source /install/setup.bash

ros2 run rplidar_ros rplidar_composition --ros-args -p serial_port:=/dev/ttyUSB0 -p serial_baudrate:=115200
```

* ### Chạy lidar A1M8
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source /install/setup.bash

ros2 launch xe_tham_do rplidar.launch.py serial_port:=/dev/ttyUSB0
```

* ###  Chạy slam toolbox để tạo map
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source /install/setup.bash

ros2 launch xe_tham_do online_async_launch.py
```

* ### Mở rviz2 xem map đang được tạo
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

cd ~/ros2_ws

rviz2 -d src/xe_tham_do/config/map.rviz
```

* ### Mở rviz2 xem tổng quan xe
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

cd ~/ros2_ws

rviz2 -d src/xe_tham_do/config/main.rviz
```




