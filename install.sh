#!/bin/bash

# بروزرسانی سیستم
sudo apt update && sudo apt install -y python3-pip python3-venv sshpass git

# ساخت پوشه برنامه
mkdir -p /opt/ssh-tunnel-manager
cd /opt/ssh-tunnel-manager

# دانلود فایل‌ها از گیت‌هاب شما (آدرس را بعدا اصلاح کنید)
# git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git .

# ساخت محیط مجازی و نصب استریم‌لیت
python3 -m venv venv
source venv/bin/activate
pip install streamlit

# ساخت سرویس برای خودِ پنل گرافیکی (پورت 2552)
cat <<EOF | sudo tee /etc/systemd/system/ssh-panel.service
[Unit]
Description=SSH Tunnel GUI Panel
After=network.target

[Service]
User=root
WorkingDirectory=/opt/ssh-tunnel-manager
ExecStart=/opt/ssh-tunnel-manager/venv/bin/streamlit run app.py --server.port 2552 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# فعال‌سازی سرویس پنل
sudo systemctl daemon-reload
sudo systemctl enable ssh-panel
sudo systemctl start ssh-panel

echo "-------------------------------------------------------"
echo "✅ نصب با موفقیت انجام شد!"
echo "🌐 آدرس پنل: http://YOUR_SERVER_IP:2552"
echo "-------------------------------------------------------"