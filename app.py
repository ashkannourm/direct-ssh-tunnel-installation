import streamlit as st
import subprocess
import os
import base64

# تنظیمات صفحه
st.set_page_config(page_title="SSH Tunnel Manager", page_icon="🚀", layout="centered")

# تابع برای تبدیل فونت به Base64 جهت استفاده در CSS
def get_font_base64(font_path):
    with open(font_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# بارگذاری فونت و اعمال استایل‌های RTL
# بارگذاری فونت و اعمال استایل‌های RTL و فونت سراسری
font_base64 = get_font_base64("IRANSansX-Medium.woff")
st.markdown(f"""
    <style>
    @font-face {{
        font-family: 'IRANSansX';
        src: url(data:application/font-woff;base64,{font_base64}) format('woff');
    }}

    /* اعمال فونت به تمام المان‌های احتمالی Streamlit */
    html, body, [class*="css"], .stApp, .stMarkdown, .stTextInput, .stButton, p, div, h1, h2, h3, h4, h5, h6, span, label, input, button {{
        font-family: 'IRANSansX' !important;
        direction: rtl !important;
        text-align: right !important;
    }}
    
    /* اصلاح نمایش اعداد و متن در فیلدهای ورودی */
    .stTextInput > div > div > input {{
        direction: ltr !important;
        text-align: left !important;
        font-family: 'IRANSansX' !important; /* حتی در حالت LTR فونت حفظ شود */
    }}

    /* استایل دکمه برای ظاهر زیباتر */
    .stButton > button {{
        width: 100%;
        border-radius: 10px;
        background-color: #ff4b4b;
        color: white;
        transition: 0.3s;
    }}
    
    .stButton > button:hover {{
        background-color: #ff2b2b;
        border: none;
    }}

    /* راست‌چین کردن سایدبار */
    [data-testid="stSidebar"] {{
        direction: rtl !important;
        text-align: right !important;
    }}
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 مدیریت هوشمند تانل SSH (مستقیم)")
st.markdown("این ابزار به صورت خودکار کلید SSH ساخته و تانل مستقیم بین ایران و مقصد برقرار می‌کند.")

with st.form("tunnel_form"):
    st.subheader("تنظیمات سرور مقصد")
    target_ip = st.text_input("IP سرور مقصد (Final Server)", placeholder="مثلاً 91.186.217.145")
    target_pass = st.text_input("رمز عبور سرور مقصد (برای انتقال کلید)", type="password")
    port = st.text_input("پورت مورد نظر برای تانل", value="29283")
    
    submit = st.form_submit_button("نصب و راه‌اندازی تانل")

if submit:
    if not target_ip or not target_pass:
        st.error("لطفاً تمامی فیلدها را پر کنید.")
    else:
        try:
            # 1. تولید کلید SSH اگر وجود نداشته باشد
            if not os.path.exists("/root/.ssh/id_rsa"):
                st.info("در حال تولید کلید SSH...")
                subprocess.run("ssh-keygen -t rsa -N '' -f /root/.ssh/id_rsa", shell=True)

            # 2. انتقال مستقیم کلید به مقصد (بدون واسط)
            st.info("در حال انتقال کلید به سرور مقصد...")
            copy_cmd = f"sshpass -p '{target_pass}' ssh-copy-id -o StrictHostKeyChecking=no root@{target_ip}"
            result = subprocess.run(copy_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                st.error(f"خطا در انتقال کلید: {result.stderr}")
            else:
                # 3. ایجاد فایل سرویس برای تانل مستقیم
                st.info("در حال ساخت سرویس تانل...")
                service_content = f"""[Unit]
Description=Direct SSH Tunnel to {target_ip}
After=network.target

[Service]
User=root
ExecStart=/usr/bin/ssh -N -o "StrictHostKeyChecking=no" -o "ServerAliveInterval=30" -o "ExitOnForwardFailure=yes" -L 0.0.0.0:{port}:127.0.0.1:{port} root@{target_ip}
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
"""
                service_path = f"/etc/systemd/system/ssh-tunnel-{port}.service"
                with open("temp_service", "w") as f:
                    f.write(service_content)
                
                subprocess.run(f"sudo mv temp_service {service_path}", shell=True)
                subprocess.run("sudo systemctl daemon-reload", shell=True)
                subprocess.run(f"sudo systemctl enable ssh-tunnel-{port}", shell=True)
                subprocess.run(f"sudo systemctl start ssh-tunnel-{port}", shell=True)
                
                st.success(f"✅ تانل مستقیم روی پورت {port} با موفقیت فعال شد!")
                st.balloons()

        except Exception as e:
            st.error(f"خطای غیرمنتظره: {e}")

st.sidebar.markdown("---")
st.sidebar.info("سیستم مدیریت تانل - نسخه RTL")