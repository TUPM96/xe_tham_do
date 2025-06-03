# Bộ Điều Khiển Động Cơ Arduino cho Robot vi sai

Repository này cung cấp firmware biến Arduino thành một bộ điều khiển động cơ vi sai (dạng differential drive) có phản hồi encoder, phù hợp cho robot di chuyển sử dụng ROS hoặc các hệ thống điều khiển tốc độ qua giao tiếp Serial.

---

## Giới thiệu

- Firmware này giao tiếp với máy tính cấp cao qua Serial (USB), nhận lệnh điều khiển tốc độ động cơ và phản hồi giá trị encoder.
- Mục tiêu là giúp bạn dễ dàng điều khiển 2 động cơ DC có encoder, phù hợp cho các dự án robot tự chế, xe tự hành, v.v.
- Đây là bản fork từ [serial_motor_demo](https://github.com/joshnewans/serial_motor_demo), đã loại bỏ các node ROS và bổ sung tùy chỉnh phù hợp với nhu cầu cá nhân.

---

## Phần cứng đề xuất

- **Vi điều khiển:** Arduino Uno/Nano hoặc tương đương
- **Driver động cơ:** L298N (đã kiểm tra hoạt động tốt), có thể thử với H-Bridge khác
- **Động cơ DC**: Có encoder (bắt buộc nếu muốn phản hồi tốc độ)
- **Kết nối máy tính:** USB (Serial)
- **Nguồn:** Theo yêu cầu động cơ và Arduino

---

## Sơ đồ kết nối cơ bản

| Tín hiệu Arduino | Nối tới driver L298N |
|------------------|---------------------|
| D12              | ENA                 |
| D5               | IN1                 |
| D9               | IN2                 |
| D6               | IN3                 |
| D10              | IN4                 |
| D13              | ENB                 |
| D2/D3            | Encoder A/B Motor 1 |
| A4/A5            | Encoder A/B Motor 2 |

> **Lưu ý:** Mỗi setup phần cứng có thể khác, hãy kiểm tra lại pin mapping cụ thể trong mã nguồn.

---

## Hướng dẫn sử dụng

### 1. Cài đặt

1. **Kết nối phần cứng:** Đấu dây như sơ đồ trên, cấp nguồn cho Arduino và driver động cơ.
2. **Nạp chương trình:** Mở Arduino IDE, nạp firmware trong thư mục này lên board Arduino.
3. **Kết nối serial:** Dùng cáp USB nối Arduino với máy tính. Đảm bảo user thuộc nhóm `dialout` (Linux).

### 2. Giao tiếp Serial

- **Baudrate mặc định:** `57600`
- **Yêu cầu:** Mỗi lệnh cần kết thúc bằng ký tự xuống dòng (CR hoặc CRLF).

### 3. Các lệnh hỗ trợ

| Lệnh                         | Chức năng                                                                                         |
|------------------------------|---------------------------------------------------------------------------------------------------|
| `e`                          | Đọc số đếm encoder hiện tại của từng động cơ (trả về 2 giá trị)                                    |
| `r`                          | Đặt lại giá trị encoder về 0                                                                      |
| `o <PWM1> <PWM2>`            | Đặt tốc độ PWM thô cho mỗi động cơ (giá trị -255 đến 255)                                         |
| `m <Spd1> <Spd2>`            | Điều khiển tốc độ động cơ theo feedback encoder (đơn vị: số đếm mỗi vòng lặp, mặc định 30Hz)      |
| `p <Kp> <Kd> <Ki> <Ko>`      | Cập nhật hệ số PID (thứ tự: Kp, Kd, Ki, Ko)                                                      |

> **Lưu ý:**
> - Để động cơ không tự tắt, cần gửi lệnh liên tục (timeout mặc định 2 giây).
> - PID mặc định chỉ dùng cho closed-loop.
> - Khi đổi thông số PID, lệnh sẽ có hiệu lực ngay.

---

## Một số lưu ý khi sử dụng

- **Timeout:** Nếu không nhận lệnh trong 2 giây, động cơ sẽ tự dừng vì lý do an toàn.
- **Thứ tự thông số PID:** Được truyền vào theo thứ tự P, D, I, O (xem kỹ mã nguồn).
- **Tốc độ động cơ:** Được điều khiển theo số đếm encoder mỗi vòng lặp. Nếu muốn ra tốc độ (vòng/phút, m/s ...) cần tự quy đổi.
- **Truy cập Serial:** Đảm bảo user đã được cấp quyền truy cập cổng serial (Linux: `sudo usermod -a -G dialout $USER`).
- **Các chức năng khác:** Mã gốc còn hỗ trợ đọc/ghi chân digital/analog, điều khiển servo... nhưng chưa kiểm thử đầy đủ ở repo này.

---

## TODO (dự định phát triển)

- [ ] Tài liệu hóa chi tiết cách chỉnh PID và lý thuyết điều khiển
- [ ] Đổi đầu vào tốc độ động cơ sang dạng số đếm mỗi giây hoặc đơn vị vật lý
- [ ] Thêm/kiểm tra hỗ trợ các loại driver khác ngoài L298N
- [ ] Hoàn thiện mục ví dụ sử dụng (Python/ROS)
- [ ] Bổ sung sơ đồ mạch chi tiết (vẽ hình minh họa)

---

## Đóng góp & Phản hồi

- Vui lòng tạo issue hoặc pull request nếu bạn gặp lỗi hoặc muốn đề xuất tính năng mới.
- Repo này được duy trì cá nhân, phản hồi có thể chậm. Rất hoan nghênh mọi đóng góp!

---