# test_email.py
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

smtp_server = os.getenv("EMAIL_HOST")
smtp_port = int(os.getenv("EMAIL_PORT"))
sender_email = os.getenv("EMAIL_USER")
sender_password = os.getenv("EMAIL_PASSWORD")

msg = MIMEText("Este es un correo de prueba.")
msg['Subject'] = "Prueba de Correo"
msg['From'] = sender_email
msg['To'] = "marcosanint8@gmail.com"  # Cambia esto por un correo real

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, msg['To'], msg.as_string())
print("Correo enviado con éxito!")