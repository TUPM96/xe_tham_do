# find_grass

Gói **find_grass** dùng để phát hiện và theo dõi vùng cỏ trong ảnh sử dụng ROS 2 và OpenCV. Gói này được phát triển dựa trên mã nguồn của Tiziano Fiorenzani, đã được chỉnh sửa và bổ sung cho phù hợp với nhu cầu thực tế.

---

## Mô tả

- Phát hiện vùng cỏ dựa trên ngưỡng màu HSV và các tham số hình học.
- Có thể điều chỉnh tham số nhận diện qua file cấu hình YAML.
- Hỗ trợ ROS 2, dễ dàng tích hợp với các hệ thống robot di động.

---

## Cài đặt

1. **Clone repository về workspace ROS 2 của bạn:**
   ```bash
   git clone <link_repo> src/find_grass
   ```

2. **Cài đặt các phụ thuộc cần thiết:**
   ```bash
   sudo apt install ros-<distro>-cv-bridge ros-<distro>-image-transport python3-opencv
   ```

3. **Build workspace:**
   ```bash
   colcon build --packages-select find_grass
   source install/setup.bash
   ```

---

## Cách chạy

- Chỉnh sửa file cấu hình tham số HSV cho phù hợp với màu cỏ thực tế trong `find_grass_params_example.yaml`.
- Chạy node phát hiện cỏ bằng lệnh:
  ```bash
  ros2 launch find_grass find_grass.launch.py params_file:=<đường_dẫn_đến_file_yaml>
  ```
- Xem kết quả qua topic hình ảnh hoặc RViz.

---

## Tham số cấu hình

- `h_min`, `h_max`, `s_min`, `s_max`, `v_min`, `v_max`: Ngưỡng màu HSV cho cỏ.
- `x_min`, `x_max`, `y_min`, `y_max`: Vùng tìm kiếm trong ảnh (theo phần trăm).
- `sz_min`, `sz_max`: Kích thước blob tối thiểu/tối đa.

---

## Ghi chú

- Có thể cần tinh chỉnh các tham số HSV để phù hợp với điều kiện ánh sáng và loại cỏ thực tế.
- Nếu muốn chuyển sang nhận diện đối tượng khác, chỉ cần thay đổi tham số màu trong file YAML, không cần sửa code.

---