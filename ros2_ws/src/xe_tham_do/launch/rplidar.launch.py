import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def resolve_serial_port(port_path):
    # Nếu là symlink by-path thì chuyển sang ttyUSBx
    if os.path.exists(port_path) and os.path.islink(port_path):
        return os.path.realpath(port_path)
    return port_path

def generate_launch_description():

    serial_port_arg = DeclareLaunchArgument('serial_port', default_value='/dev/ttyUSB0',
                                            description='Serial port to which the RPLIDAR is connected')

    serial_port = LaunchConfiguration('serial_port')

    return LaunchDescription([
        serial_port_arg,
        Node(
            package='rplidar_ros',
            executable='rplidar_composition',
            output='screen',
            parameters=[
                {'serial_port': serial_port, 'serial_baudrate': 115200, 'frame_id': 'laser_frame',
                 'angle_compensate': True, 'scan_mode': 'Standard'}
            ]
        )
    ])