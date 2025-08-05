import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

# ========== NODE CODE ==========
class SafetyTeleop(Node):
    def __init__(self):
        print("Bat dau __init__ cua SafetyTeleop")
        super().__init__('safety_teleop')
        self.get_logger().info("Khoi tao node safety_teleop")

        # Tham so khoang cach an toan cho tung huong (m)
        self.declare_parameter('min_distance_front', 0.5)
        self.declare_parameter('min_distance_back', 0.3)
        self.declare_parameter('min_distance_left', 0.3)
        self.declare_parameter('min_distance_right', 0.3)
        # Tham so goc moi vung (do)
        self.declare_parameter('sector_angle_front', 60.0)
        self.declare_parameter('sector_angle_back', 60.0)
        self.declare_parameter('sector_angle_left', 60.0)
        self.declare_parameter('sector_angle_right', 60.0)

        print("Lay tham so tu ROS2 parameter server")
        self.min_distance_front = self.get_parameter('min_distance_front').get_parameter_value().double_value
        self.min_distance_back = self.get_parameter('min_distance_back').get_parameter_value().double_value
        self.min_distance_left = self.get_parameter('min_distance_left').get_parameter_value().double_value
        self.min_distance_right = self.get_parameter('min_distance_right').get_parameter_value().double_value

        self.sector_angle_front = self.get_parameter('sector_angle_front').get_parameter_value().double_value
        self.sector_angle_back = self.get_parameter('sector_angle_back').get_parameter_value().double_value
        self.sector_angle_left = self.get_parameter('sector_angle_left').get_parameter_value().double_value
        self.sector_angle_right = self.get_parameter('sector_angle_right').get_parameter_value().double_value

        print("Khoi tao subscription va publisher")
        self.cmd_sub = self.create_subscription(
            Twist, '/cmd_vel_raw', self.cmd_callback, 10)
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        self.cmd_pub = self.create_publisher(
            Twist, '/cmd_vel', 10)

        self.last_scan = None
        print("Ket thuc __init__")

    def scan_callback(self, msg):
        print("scan_callback: Nhan duoc LaserScan")
        self.last_scan = msg

    def get_sector_min(self, scan, center_deg, width_deg):
        print(f"get_sector_min: center={center_deg}, width={width_deg}")
        angle_min = scan.angle_min
        angle_inc = scan.angle_increment
        ranges = scan.ranges

        center_rad = center_deg * 3.1415926535 / 180.0
        width_rad = width_deg * 3.1415926535 / 180.0

        min_angle = center_rad - width_rad/2.0
        max_angle = center_rad + width_rad/2.0
        min_idx = int((min_angle - angle_min) / angle_inc)
        max_idx = int((max_angle - angle_min) / angle_inc)
        min_idx = max(0, min_idx)
        max_idx = min(len(ranges) - 1, max_idx)

        sector_ranges = [r for r in ranges[min_idx:max_idx+1] if r > 0.01]
        return min(sector_ranges) if sector_ranges else float('inf')

    def cmd_callback(self, msg):
        print("cmd_callback: Nhan duoc Twist")
        if self.last_scan is None:
            print("cmd_callback: last_scan chua co du lieu, publish raw cmd")
            self.cmd_pub.publish(msg)
            return

        scan = self.last_scan

        # Cac huong (theo chuan ROS: 0 rad la truoc, pi la sau, pi/2 la trai, -pi/2 la phai)
        min_front = self.get_sector_min(scan, 0, self.sector_angle_front)
        min_back  = self.get_sector_min(scan, 180, self.sector_angle_back)
        min_left  = self.get_sector_min(scan, 90, self.sector_angle_left)
        min_right = self.get_sector_min(scan, -90, self.sector_angle_right)

        print(f"Khoang cach min: front={min_front:.2f}, back={min_back:.2f}, left={min_left:.2f}, right={min_right:.2f}")

        blocked = False
        output = Twist()

        # Chan tien neu phia truoc co vat can gan
        if msg.linear.x > 0 and min_front < self.min_distance_front:
            output.linear.x = 0.0
            output.angular.z = 0.0
            blocked = True
            self.get_logger().warn(f"Vat can truoc mat ({min_front:.2f}m)! Khong the di tien.")

        # Chan lui neu phia sau co vat can gan
        elif msg.linear.x < 0 and min_back < self.min_distance_back:
            output.linear.x = 0.0
            output.angular.z = 0.0
            blocked = True
            self.get_logger().warn(f"Vat can phia sau ({min_back:.2f}m)! Khong the di lui.")

        # Chan re trai neu ben trai co vat can gan va dang re manh
        elif msg.angular.z > 0.2 and min_left < self.min_distance_left:
            output.linear.x = msg.linear.x
            output.angular.z = 0.0
            blocked = True
            self.get_logger().warn(f"Vat can ben trai ({min_left:.2f}m)! Khong the re trai.")

        # Chan re phai neu ben phai co vat can gan va dang re manh
        elif msg.angular.z < -0.2 and min_right < self.min_distance_right:
            output.linear.x = msg.linear.x
            output.angular.z = 0.0
            blocked = True
            self.get_logger().warn(f"Vat can ben phai ({min_right:.2f}m)! Khong the re phai.")

        if not blocked:
            print("cmd_callback: Khong bi chan, publish lenh goc")
            output = msg

        self.cmd_pub.publish(output)

# ========== LAUNCH CODE ==========
def main(args=None):
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--launch':
        # Chay nhu mot launch file
        from launch import LaunchDescription
        from launch_ros.actions import Node as LaunchNode

        def generate_launch_description():
            print("generate_launch_description: Goi launch file")
            return LaunchDescription([
                LaunchNode(
                    package='xe_tham_do',
                    executable='safety_teleop_with_launch.py',
                    name='safety_teleop',
                    output='screen',
                    parameters=[
                        {'min_distance_front': 0.5},
                        {'min_distance_back': 0.3},
                        {'min_distance_left': 0.3},
                        {'min_distance_right': 0.3},
                        {'sector_angle_front': 60.0},
                        {'sector_angle_back': 60.0},
                        {'sector_angle_left': 60.0},
                        {'sector_angle_right': 60.0},
                    ]
                ),
            ])
        globals()['generate_launch_description'] = generate_launch_description
    else:
        print("main: Khoi dong node thong thuong")
        rclpy.init(args=args)
        node = SafetyTeleop()
        print("main: Node khoi tao xong, bat dau spin ...")
        rclpy.spin(node)
        print("main: Spin ket thuc, huy node")
        node.destroy_node()
        rclpy.shutdown()
        print("main: Da shutdown rclpy")

if __name__ == '__main__':
    main()