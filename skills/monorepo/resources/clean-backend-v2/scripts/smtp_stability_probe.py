


import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

to_email: str = "823042332@qq.com"
subject: str = "PostPin注册"
code = "123444"
body = f"您的重置密码验证码是：{code}\n10 分钟内有效，请勿泄露给他人。"


sender = "3322583078@qq.com"
password = "dvwkysmecwiichaj"

msg = MIMEMultipart()
msg["From"] = sender
msg["To"] = to_email
msg["Subject"] = subject
msg.attach(MIMEText(body, "plain", "utf-8"))

try:
    with smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=12) as server:
        server.login(sender, password)
        server.send_message(msg)

    print("pass")   
except Exception as e:
    print("nopass")