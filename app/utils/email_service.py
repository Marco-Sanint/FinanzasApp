# utils/email_service.py
import smtplib
from email.mime.text import MIMEText
from typing import Optional

class EmailService:
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        """Inicializa el servicio de correo con las credenciales del servidor SMTP."""
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_verification_code(self, recipient_email: str, code: str) -> bool:
        """Envía un código de verificación al correo del destinatario."""
        subject = "Código de Verificación - Gestor de Finanzas Personales"
        body = f"Tu código de verificación es: {code}\nEste código expira en 15 minutos."
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = recipient_email

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Habilitar TLS
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, msg.as_string())
            return True
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
            return False