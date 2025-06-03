# Sử dụng image NVIDIA đã có ROS 2 Humble, PyTorch, CUDA, ... trên Jetson
FROM dustynv/ros:humble-desktop-pytorch-l4t-r35.4.1

WORKDIR /root/ros2_ws

RUN rm -f /etc/apt/sources.list.d/ros2.list

# Sửa lỗi GPG key ROS2 (chuẩn mới 2024)
RUN apt-get update && apt-get install -y curl gnupg2 lsb-release && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=arm64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2.list

# Cài đặt các dependencies cần thiết, bao gồm thư viện "serial" và các gói GUI/X11
RUN apt-get update && apt-get install -y \
    python3-pip \
    build-essential \
    ros-humble-serial-driver \
    ros-humble-rviz2 \
    ros-humble-xacro \
    ros-humble-teleop-twist-keyboard \
    libqt5gui5 \
    libqt5widgets5 \
    libxkbcommon-x11-0 \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    x11-apps \
    && pip3 install pyserial \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt ROS 2 Control và các gói liên quan
RUN apt-get update && apt-get install -y \
    ros-humble-ros2-control \
    ros-humble-hardware-interface \
    ros-humble-controller-manager \
    ros-humble-joint-state-broadcaster \
    ros-humble-diff-drive-controller

# Không cần sudo trong container (user root rồi), chỉ cần khởi tạo rosdep nếu cần
RUN if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then \
      rosdep init; \
    fi && \
    rosdep fix-permissions && rosdep update

# Cài đặt dependencies cho ROS workspace
RUN rosdep install --from-paths /root/ros2_ws/src --ignore-src -r -y