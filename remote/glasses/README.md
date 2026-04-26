[Unit]
Description=Assistive Glasses Main Program
After=network.target

[Service]
ExecStartPre=/bin/systemctl stop getty@ttyS0.service
ExecStartPre=/bin/systemctl stop serial-getty@ttyS0.service
ExecStartPre=/bin/stty -F /dev/ttyS0 9600 cs8 -cstopb -parenb
ExecStart=/usr/bin/python3 /home/admin/Desktop/glasses/main.py
WorkingDirectory=/home/admin/Desktop/glasses
Environment=DISPLAY=:0
Environment=XDG_RUNTIME_DIR=/run/user/1000
Restart=always
RestartSec=5
User=admin
Group=audio

[Install]
WantedBy=multi-user.target

currecny 
https://universe.roboflow.com/project-mccsh/currency-detection-cgpjn



python3 -c "
import os
os.environ['GEMINI_API_KEY'] = 'YOUR_KEY'
from google import genai
client = genai.Client()
response = client.models.generate_content(
    model='gemini-3-flash-preview',
    contents='Say hello'
)
print(response.text)
"


wget https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/voc/MobileNetSSD_deploy.prototxt

wget https://drive.google.com/uc?id=0B3gersZ2cHIxRm5PMWRoTkdHdHc -O MobileNetSSD_deploy.caffemodel

wget "https://github.com/djmv/MobilNet_SSD_opencv/raw/master/MobileNetSSD_deploy.caffemodel" -O MobileNetSSD_deploy.caffemodel