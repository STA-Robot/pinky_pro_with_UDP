# UDP Camera Streamer
이 프로젝트는 Raspberry Pi의 Picamera2를 사용하여 영상을 캡처하고, UDP 프로토콜을 통해 실시간으로 서버에 전송하는 ROS 2 노드입니다.


## build
```
cd ~/pinky_pro
colcon build
```
# 사용 매뉴얼

## 환경
- ubuntu 24.04
- ros2 jazzy

## 실행
```
ros2 launch udp camera.launch.py
```

## 설정 방법 
```
-config/udpconfig.yaml 파일을 수정하여 설정을 변경할 수 있습니다.

-노드를 실행할 때 터미널에서 즉시 파라미터를 변경할 수 있는 방법
    ros2 launch udp camera.launch.py server_ip:="192.168.4.5" server_port:=8888

```
## 주요 설정 파라미터 상세
```
robot_name :서버에서 다수의 로봇을 구분하기 위한 고유 식별자입니다. 패킷 헤더에 포함됩니다.
server_ip : 영상 데이터를 수신할 서버(수신기)의 IPv4 주소입니다.
server_port : 영상 데이터가 전송될 UDP 포트 번호입니다. 서버에서 해당 포트를 열어두어야 합니다.
```

## 주요 기능 
```
ROS 2 파라미터 지원: IP, 포트, FPS, 해상도 등을 별도의 YAML 파일로 설정 가능.

커스텀 헤더: 각 패킷에 robot_name 식별자를 포함하여 다수의 로봇 데이터를 구분 가능.

간편한 실행: ROS 2 Launch 시스템을 지원하여 시스템 부팅 시 자동 실행 연동이 용이함.
```
## 주의사항 
```
UDP 패킷 크기: UDP 패킷은 MTU 제한(일반적으로 1500바이트)이 있습니다. 현재 코드에서는 65507바이트 체크를 수행하지만, 고해상도 이미지 전송 시에는 데이터가 유실될 수 있으므로 적절한 JPEG 압축 품질(Quality) 조절이 필요합니다.

네트워크: 서버와 클라이언트가 동일한 네트워크 대역에 있는지 확인하십시오.
```
