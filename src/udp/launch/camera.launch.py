# camera.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('udp'),
        'config',
        'udpconfig.yaml'
    )
    return LaunchDescription([
        Node(
            package='udp',
            executable='cameraSenderNode',
            name='camera_sender_node',
            parameters=[config]
        )
    ])