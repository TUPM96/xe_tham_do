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

# docker exec -it ros2_humble_container bash

# Chỉ chạy khi muốn build lại từ đầu
# colcon build --symlink-install        

```
**Sau đó có thể chạy lệnh bên dưới**

# B. Chạy robot test hoạt động
* ###  Chạy diffdrive_arduino
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source install/setup.bash

ros2 launch diffdrive_arduino diffbot.launch.py
```

* ###  Chạy điều khiển xe từ bàn phím
``` bash
docker exec -it ros2_humble_container bash
source /opt/ros/humble/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=diffbot_base_controller/cmd_vel_unstamped
```

# C. Chạy các phần tử
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

ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

* ### Chạy lidar A1M8
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source install/setup.bash

ros2 launch xe_tham_do rplidar.launch.py serial_port:=/dev/ttyUSB0
```

* ###  Chạy slam toolbox để tạo map
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

source install/setup.bash

ros2 launch xe_tham_do online_async_launch.py
```

* ### Mở rviz2 xem map đang được tạo
``` bash
docker exec -it ros2_humble_container bash

source /opt/ros/humble/install/setup.bash

cd ~/ros2_ws

rviz2 -d src/xe_tham_do/config/map.rviz
```




