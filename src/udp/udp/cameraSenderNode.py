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

        # 상태
        self.running = False
        self.thread = None

        # 구독
        self.sub = self.create_subscription(
            String,
            "follow_event",
            self.callback,
            10
        )

        self.get_logger().info("CameraSenderNode Ready")

    def callback(self, msg):
        if msg.data == "start":
            self.start_stream()
        elif msg.data == "stop":
            self.stop_stream()

    def start_stream(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self.stream_loop)
        self.thread.start()

        self.get_logger().info("카메라 송신 시작")

    def stop_stream(self):
        self.running = False
        self.get_logger().info("카메라 송신 정지")

    def stream_loop(self):
        # YAML 로드
        with open("udpconfig.yaml", "r") as f:
            config = yaml.safe_load(f)

        udp_cfg = config["udp"]
        camera_cfg = config["camera"]

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        picam2 = Picamera2()
        video_config = picam2.create_video_configuration(
            main={"size": (camera_cfg["width"], camera_cfg["height"])},
            controls={"FrameRate": camera_cfg["fps"]}
        )
        picam2.configure(video_config)
        picam2.start()
        time.sleep(1)

        while self.running:
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
            data = jpeg.tobytes()

            if len(data) < 65507:
                sock.sendto(data, (udp_cfg["server_ip"], udp_cfg["server_port"]))

            time.sleep(1 / camera_cfg["fps"])

        picam2.stop()
        sock.close()


def main(args=None):
    rclpy.init(args=args)
    node = CameraSenderNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()