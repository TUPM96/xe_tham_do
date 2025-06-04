# Sử dụng image NVIDIA đã có ROS 2 Humble, PyTorch, CUDA, ... trên Jetson
FROM dustynv/ros:humble-desktop-l4t-r36.2.0

WORKDIR /root/ros2_ws

RUN rm -f /etc/apt/sources.list.d/ros2.list

# Sửa lỗi GPG key ROS2 (chuẩn mới 2024)
RUN apt-get update && apt-get install -y curl gnupg2 lsb-release && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=arm64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2.list

# Cài đặt dependencies cần thiết, bao gồm build tools, GUI libs và pip packages
RUN apt-get update && apt-get install -y \
    python3-pip \
    build-essential \
    libqt5gui5 \
    libqt5widgets5 \
    libxkbcommon-x11-0 \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    x11-apps \
    git \
    cmake \
    && pip3 install pyserial \
    && rm -rf /var/lib/apt/lists/*

# Gỡ bất kỳ libbenchmark cũ nào (nếu có, tránh LTO mismatch)
RUN apt-get purge -y libbenchmark-dev libbenchmark1 || true

# Build lại Google Benchmark từ source với GCC hiện tại (11.4)
RUN git clone --depth 1 --branch v1.8.3 https://github.com/google/benchmark.git /tmp/benchmark && \
    cd /tmp/benchmark && \
    mkdir build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j$(nproc) && \
    make install && \
    cd / && rm -rf /tmp/benchmark

# Khởi tạo rosdep nếu cần
RUN if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then \
      rosdep init; \
    fi && \
    rosdep fix-permissions && rosdep update