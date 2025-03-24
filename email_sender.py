from datetime import date
import smtplib
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

class EmailSender:
    def __init__(self, log_file: str = "/var/log/email.log"):
        """
        Initialize the EmailSender by loading SMTP details from the .env file.
        """
        load_dotenv()  # Load environment variables from .env file
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))  # Default to 587
        self.sender_email = os.getenv("EMAIL_SENDER")
        self.sender_password = os.getenv("EMAIL_PASSWORD")

        # Setup logging
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logging.info("✅ EmailSender initialized.")

    def read_file(self, file_path: str) -> str:
        """
        Read a file and return its content as a string.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            logging.error(f"❌ Error: File {file_path} not found.")
            return ""

    def send_email(self, recipient_email: str, subject: str, html_file: str, css_file: str):
        """
        Send an email with the provided HTML and CSS files.
        """
        # Read HTML and CSS content
        html_content = self.read_file(html_file)
        css_content = self.read_file(css_file)

        if not html_content:
            logging.error("❌ Error: HTML content is missing. Email not sent.")
            return

        # Embed CSS into HTML
        final_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                {css_content}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        # Create Email
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(final_html, "html"))

        # Send Email
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, recipient_email, msg.as_string())
            server.quit()
            logging.info(f"✅ Email sent successfully to {recipient_email}!")
        except Exception as e:
            logging.error(f"❌ Error: {e}")

if __name__=="__main__":
    #send email
    print('sending email..')
    # Create EmailSender instance (logs to email.log)
    email_sender = EmailSender()

    # Send an email
    today = date.today()
    formatted_date = today.strftime("%d/%m/%Y")  # Change the format as needed
    email_sender.send_email(
        recipient_email="receiver_email@gmail.com",
        subject=f"From Ofek Dinisman Code Jobs Outputs {formatted_date}",
        html_file="jobs_output.html",
        css_file="styles.css"
    )
    print('email sent!')  
