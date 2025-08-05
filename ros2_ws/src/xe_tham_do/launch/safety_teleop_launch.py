import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class SafetyTeleop(Node):
    def __init__(self):
        super().__init__('safety_teleop')
        # Tham số khoảng cách an toàn cho từng hướng (m)
        self.declare_parameter('min_distance_front', 0.5)
        self.declare_parameter('min_distance_back', 0.3)
        self.declare_parameter('min_distance_left', 0.3)
        self.declare_parameter('min_distance_right', 0.3)
        # Tham số góc mỗi vùng (độ)
        self.declare_parameter('sector_angle_front', 60.0)
        self.declare_parameter('sector_angle_back', 60.0)
        self.declare_parameter('sector_angle_left', 60.0)
        self.declare_parameter('sector_angle_right', 60.0)

        self.min_distance_front = self.get_parameter('min_distance_front').get_parameter_value().double_value
        self.min_distance_back = self.get_parameter('min_distance_back').get_parameter_value().double_value
        self.min_distance_left = self.get_parameter('min_distance_left').get_parameter_value().double_value
        self.min_distance_right = self.get_parameter('min_distance_right').get_parameter_value().double_value

        self.sector_angle_front = self.get_parameter('sector_angle_front').get_parameter_value().double_value
        self.sector_angle_back = self.get_parameter('sector_angle_back').get_parameter_value().double_value
        self.sector_angle_left = self.get_parameter('sector_angle_left').get_parameter_value().double_value
        self.sector_angle_right = self.get_parameter('sector_angle_right').get_parameter_value().double_value

        self.cmd_sub = self.create_subscription(
            Twist, '/cmd_vel_raw', self.cmd_callback, 10)
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        self.cmd_pub = self.create_publisher(
            Twist, '/cmd_vel', 10)

        self.last_scan = None

    def scan_callback(self, msg):
        self.last_scan = msg

    def get_sector_min(self, scan, center_deg, width_deg):
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
        if self.last_scan is None:
            self.cmd_pub.publish(msg)
            return

        scan = self.last_scan

        # Các hướng (theo chuẩn ROS: 0 rad là trước, pi là sau, pi/2 là trái, -pi/2 là phải)
        min_front = self.get_sector_min(scan, 0, self.sector_angle_front)
        min_back  = self.get_sector_min(scan, 180, self.sector_angle_back)
        min_left  = self.get_sector_min(scan, 90, self.sector_angle_left)
        min_right = self.get_sector_min(scan, -90, self.sector_angle_right)

        blocked = False
        output = Twist()

        # Chặn tiến nếu phía trước có vật cản gần
        if msg.linear.x > 0 and min_front < self.min_distance_front:
            output.linear.x = 0.0
            output.angular.z = 0.0
            blocked = True
            self.get_logger().warn(f"Obstacle ahead ({min_front:.2f}m)! Cannot move forward.")

        # Chặn lùi nếu phía sau có vật cản gần
        elif msg.linear.x < 0 and min_back < self.min_distance_back:
            output.linear.x = 0.0
            output.angular.z = 0.0
            blocked = True
            self.get_logger().warn(f"Obstacle behind ({min_back:.2f}m)! Cannot move backward.")

        # Chặn rẽ trái nếu bên trái có vật cản gần và đang rẽ mạnh (tùy chọn)
        elif msg.angular.z > 0.2 and min_left < self.min_distance_left:
            output.linear.x = msg.linear.x
            output.angular.z = 0.0
            blocked = True
            self.get_logger().warn(f"Obstacle left ({min_left:.2f}m)! Cannot turn left.")

        # Chặn rẽ phải nếu bên phải có vật cản gần và đang rẽ mạnh (tùy chọn)
        elif msg.angular.z < -0.2 and min_right < self.min_distance_right:
            output.linear.x = msg.linear.x
            output.angular.z = 0.0
            blocked = True
            self.get_logger().warn(f"Obstacle right ({min_right:.2f}m)! Cannot turn right.")

        if not blocked:
            output = msg

        self.cmd_pub.publish(output)

def main(args=None):
    rclpy.init(args=args)
    node = SafetyTeleop()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()