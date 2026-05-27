import socket
import cv2
import time
import yaml
from picamera2 import Picamera2

# ===================== YAML 설정 로드 =====================
with open("udpconfig.yaml", "r") as f:
    config = yaml.safe_load(f)

udp_cfg    = config["udp"]
camera_cfg = config["camera"]

RECEIVER_IP   = udp_cfg["server_ip"]
RECEIVER_PORT = udp_cfg["server_port"]

CAM_FPS    = camera_cfg["fps"]
CAM_WIDTH  = camera_cfg["width"]
CAM_HEIGHT = camera_cfg["height"]

JPEG_QUALITY = 60
# ==========================================================

# 카메라 초기화
picam2 = Picamera2()
video_config = picam2.create_video_configuration(
    main={"size": (CAM_WIDTH, CAM_HEIGHT)},
    controls={"FrameRate": CAM_FPS}
)
picam2.configure(video_config)
picam2.start()
time.sleep(1)

# UDP 소켓
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"[송신 시작] → {RECEIVER_IP}:{RECEIVER_PORT}")

while True:
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.rotate(frame, cv2.ROTATE_180)

    _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    data = jpeg.tobytes()
    size = len(data)

    if size > 65507:
        print(f"[경고] 패킷 너무 큼: {size}B → JPEG_QUALITY 낮추세요")
        continue

    sock.sendto(data, (RECEIVER_IP, RECEIVER_PORT))
    print(f"[v_02송신] size={size}B")

    time.sleep(1 / CAM_FPS)  # fps 기반 딜레이