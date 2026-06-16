import socket
import cv2
import time
import threading
import argparse
from picamera2 import Picamera2

class CameraSender:
    def __init__(self, robot_name, robot_ip, robot_port, fps, width, height):
        self.robot_name = robot_name
        self.robot_ip = robot_ip
        self.robot_port = robot_port
        self.fps = fps
        self.width = width
        self.height = height

        self.running = False
        self.thread = None

    def start_stream(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.stream_loop, daemon=True)
        self.thread.start()
        print(f"카메라 송신 시작: {self.robot_ip}:{self.robot_port}")

    def stop_stream(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None
        print("카메라 송신 정지")

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
                    sock.sendto(packet, (self.robot_ip, self.robot_port))
                
                time.sleep(1 / max(self.fps, 1))
            except Exception as e:
                print(f"Stream error: {e}")
                break

        picam2.stop()
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--robot_name", default="pinky2")
    parser.add_argument("--robot_ip", default="192.168.4.2")
    parser.add_argument("--robot_port", type=int, default=9998)
    parser.add_argument("--fps", type=int, default=10)
    args = parser.parse_args()

    sender = CameraSender(args.robot_name, args.robot_ip, args.robot_port, args.fps, 640, 480)
    
    try:
        sender.start_stream()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sender.stop_stream()