import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv


def send_email(subject, body):
    # Load environment variables
    load_dotenv()
    PASSWORD = os.getenv("app_password")
    EMAIL = os.getenv("email")

    # Constants
    SENDER_EMAIL = EMAIL
    TO_EMAILS = [EMAIL]
    SMTP_SERVER = "smtp.gmail.com"
    PORT = 465  # SSL port
    """Send an email notification."""

    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = ", ".join(TO_EMAILS)

        

        with smtplib.SMTP_SSL(SMTP_SERVER, PORT) as server:
            server.login(SENDER_EMAIL, PASSWORD)
            server.sendmail(SENDER_EMAIL, TO_EMAILS, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
