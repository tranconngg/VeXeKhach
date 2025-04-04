import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL")

        self.base_url = os.getenv("BASE_URL", "http://localhost:8000")

    async def send_verification_email(self, to_email: str, verification_token: str) -> bool:
        try:
            msg = MIMEMultipart()
            msg['From'] = f"VeXeKhach <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = "Verify Your VeXeKhach Account"

            # Create email content using base_url
            verification_url = f"{self.base_url}/users/verify-email?token={verification_token}"
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                <p>Hello {to_email.split('@')[0]},</p>
                
                <p>Thank you for signing up for VeXeKhach. To complete your registration, please verify your email address by clicking the button below:</p>
                
                <p style="text-align: center;">
                    <a href="{verification_url}" style="display: inline-block; padding: 10px 20px; font-size: 16px; color: #fff; background-color: #007bff; text-decoration: none; border-radius: 5px;">
                        Verify Email
                    </a>
                </p>

                <p>Or copy and paste the following link into your browser:</p>
                <p><a href="{verification_url}">{verification_url}</a></p>
                
                <p>This link will expire in 24 hours.</p>
                
                <p>If you did not request this, please ignore this email.</p>
                
                <p>Best regards,</p>
                <p><strong>VeXeKhach Team</strong></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))

            # Connect and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Verification email successfully sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False


# Khởi tạo service
email_service = EmailService() 