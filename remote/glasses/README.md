[Unit]
Description=Assistive Glasses Main Program
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/admin/Desktop/glasses/main.py
WorkingDirectory=/home/admin/Desktop/glasses
Restart=always
RestartSec=5
User=admin

[Install]
WantedBy=multi-user.target