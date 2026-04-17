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