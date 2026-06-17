import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import socket
import cv2
import time
import yaml
from picamera2 import Picamera2
import threading


class CameraSenderNode(Node):
    def __init__(self):
        super().__init__('camera_sender_node')

        # 파라미터 선언
        self.declare_parameter("robot_name", "pinky1")
        self.declare_parameter("server_ip", "192.168.4.2")
        self.declare_parameter("server_port", 9999)
        self.declare_parameter("fps", 10)
        self.declare_parameter("width", 640)
        self.declare_parameter("height", 480)

        #파라미터 읽기
        self.robot_name = self.get_parameter("robot_name").value
        self.server_ip = self.get_parameter("server_ip").value
        self.server_port = self.get_parameter("server_port").value
        self.fps = self.get_parameter("fps").value
        self.width = self.get_parameter("width").value
        self.height = self.get_parameter("height").value

        # 상태
        self.running = False
        self.thread = None

        self.start_stream()
        self.get_logger().info("CameraSenderNode Ready")

    def start_stream(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self.stream_loop, daemon=True)
        self.thread.start()

        self.get_logger().info("카메라 송신 시작")

    def stop_stream(self):
        if not self.running:
            return

        self.running = False

        if self.thread is not None:
            self.thread.join()   
            self.thread = None

        self.get_logger().info("카메라 송신 정지")

    def stream_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        picam2 = Picamera2()
        video_config = picam2.create_video_configuration(
            main={"size": (self.width, self.height)},
            controls={"FrameRate": self.fps}
        )
        picam2.configure(video_config)
        picam2.start()
        time.sleep(1)

        while self.running:
            try:
                frame = picam2.capture_array()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.rotate(frame, cv2.ROTATE_180)

                _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
                data = jpeg.tobytes()
               
                header = f"{self.robot_name}|".encode()
                packet = header + data

                if len(packet) < 65507:
                    sock.sendto(packet, (self.server_ip, self.server_port))
                    self.get_logger().info(f"SEND! {self.server_ip}")

                time.sleep(1 / max(self.fps, 1))

            except Exception as e:
                self.get_logger().error(f"Stream error: {e}")

        picam2.stop()
        sock.close()


def main(args=None):
    rclpy.init(args=args)
    node = CameraSenderNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()