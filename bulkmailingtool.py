import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sqlite3
import time
import random


class BulkEmailTool:
    def __init__(self, smtp_server, port, sender_email, sender_password):
        """
        Initialize the bulk email tool with SMTP server details.
        """
        self.smtp_server = smtp_server
        self.port = port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.connection = None
        self.setup_database()

    def setup_database(self):
        """
        Setup SQLite database for logging email performance.
        """
        self.db = sqlite3.connect("email_performance.db")
        cursor = self.db.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT,
            subject TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.db.commit()

    def connect(self):
        """
        Connect to the SMTP server.
        """
        try:
            self.connection = smtplib.SMTP(self.smtp_server, self.port)
            self.connection.starttls()
            self.connection.login(self.sender_email, self.sender_password)
            print("Connected to SMTP server.")
        except Exception as e:
            print(f"Failed to connect to SMTP server: {e}")
            raise

    def send_email(self, recipient, subject, body):
        """
        Send an email to a single recipient and log the performance.
        """
        try:
            # Construct the email
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = recipient
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            # Send the email
            self.connection.sendmail(self.sender_email, recipient, message.as_string())
            print(f"Email sent to {recipient}")

            # Log success in the database
            self.log_email(recipient, subject, "Success")
        except Exception as e:
            print(f"Failed to send email to {recipient}: {e}")
            self.log_email(recipient, subject, "Failed")

    def log_email(self, recipient, subject, status):
        """
        Log the email performance in the SQLite database.
        """
        cursor = self.db.cursor()
        cursor.execute("""
        INSERT INTO email_logs (recipient, subject, status)
        VALUES (?, ?, ?)
        """, (recipient, subject, status))
        self.db.commit()

    def send_bulk_emails(self, recipients, subject, body, delay_range=(1, 5)):
        """
        Send emails in bulk with randomized delay to mimic human behavior.
        """
        for recipient in recipients:
            self.send_email(recipient, subject, body)
            delay = random.randint(*delay_range)
            print(f"Waiting for {delay} seconds before sending the next email...")
            time.sleep(delay)

    def close(self):
        """
        Close the SMTP connection and the database.
        """
        if self.connection:
            self.connection.quit()
        if self.db:
            self.db.close()


# Usage Example
if __name__ == "__main__":
    # SMTP configuration
    SMTP_SERVER = "smtp.gmail.com"
    PORT = 587
    SENDER_EMAIL = "your_email@gmail.com"
    SENDER_PASSWORD = "your_password"

    # Email details
    SUBJECT = "Welcome to Our Newsletter!"
    BODY = """
    Hi there,

    Thank you for subscribing to our newsletter. We are thrilled to have you on board!

    Best Regards,
    Your Company
    """
    RECIPIENTS = ["recipient1@example.com", "recipient2@example.com"]

    # Create and use the bulk email tool
    email_tool = BulkEmailTool(SMTP_SERVER, PORT, SENDER_EMAIL, SENDER_PASSWORD)

    try:
        email_tool.connect()
        email_tool.send_bulk_emails(RECIPIENTS, SUBJECT, BODY)
    finally:
        email_tool.close()
