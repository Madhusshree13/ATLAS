import imaplib
import smtplib
import email
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()


class GmailClient:
    def __init__(self):
        self.address = os.getenv("GMAIL_ADDRESS")
        self.password = os.getenv("GMAIL_APP_PASSWORD")
        self.imap_host = "imap.gmail.com"
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587

    def _decode_header(self, value):
        decoded, enc = decode_header(value)[0]
        if isinstance(decoded, bytes):
            return decoded.decode(enc or "utf-8", errors="ignore")
        return decoded or ""

    def _extract_email_address(self, field):
        match = re.search(r'[\w\.\+\-]+@[\w\.\-]+', field)
        return match.group(0) if match else field

    def _get_body(self, msg):
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                ct = part.get_content_type()
                cd = str(part.get("Content-Disposition", ""))
                if ct == "text/plain" and "attachment" not in cd:
                    try:
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
                    except Exception:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
            except Exception:
                pass
        return body[:800]

    def fetch_today_emails(self, max_count=10):
        emails = []
        if not self.address or not self.password:
            print("[Gmail] GMAIL_ADDRESS or GMAIL_APP_PASSWORD not set in .env")
            return emails
        try:
            mail = imaplib.IMAP4_SSL(self.imap_host, timeout=30)
            mail.login(self.address, self.password)
            mail.select("INBOX")

            today = date.today().strftime("%d-%b-%Y")
            status, data = mail.search(None, f'ON {today}')
            if status != "OK":
                mail.logout()
                return emails

            ids = data[0].split()
            for msg_id in list(reversed(ids))[:max_count]:
                _, msg_data = mail.fetch(msg_id, "(RFC822)")
                if not msg_data or not msg_data[0]:
                    continue
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)

                sender = msg.get("From", "Unknown")
                subject = self._decode_header(msg.get("Subject", "No Subject"))
                body = self._get_body(msg)

                emails.append({
                    "id": msg_id.decode(),
                    "sender": sender,
                    "subject": subject,
                    "body": body,
                    "reply_to": msg.get("Reply-To") or sender
                })

            mail.logout()
        except imaplib.IMAP4.error as e:
            print(f"[Gmail] IMAP auth error: {e} — check GMAIL_APP_PASSWORD in .env")
        except Exception as e:
            print(f"[Gmail] fetch error: {e}")
        return emails

    def send_email(self, to, subject, body):
        if not self.address or not self.password:
            print("[Gmail] GMAIL_ADDRESS or GMAIL_APP_PASSWORD not set in .env")
            return False
        to = to.strip()
        try:
            msg = MIMEMultipart()
            msg["From"] = self.address
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()  # Re-identify after STARTTLS (required by some servers)
                server.login(self.address, self.password)
                server.sendmail(self.address, [to], msg.as_string())
            print(f"[Gmail] Email sent to {to}")
            return True
        except smtplib.SMTPAuthenticationError:
            print("[Gmail] SMTP auth failed — check GMAIL_APP_PASSWORD in .env. "
                  "Make sure 2-Step Verification is enabled and you're using an App Password.")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            print(f"[Gmail] Recipient refused: {e}")
            return False
        except Exception as e:
            print(f"[Gmail] send error: {e}")
            return False

    def reply_to_email(self, original_email, body):
        to = self._extract_email_address(original_email.get("reply_to", original_email.get("sender", "")))
        subject = original_email.get("subject", "")
        if not subject.startswith("Re:"):
            subject = f"Re: {subject}"
        return self.send_email(to, subject, body)
