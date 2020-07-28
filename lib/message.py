from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread
import smtplib


class Message(object):

    def __init__(self, server: str, login: str, password: str):
        self._msg = MIMEMultipart()
        self._server = server
        self._login = login
        self._password = password

    def create(self, email, subject, message):
        self._msg['From'] = self._login
        self._msg['To'] = email
        self._msg['Subject'] = subject
        self._msg.attach(MIMEText(message, 'plain'))

    def send(self):
        thread = SMTPThread(self._msg, self._server, self._login, self._password)
        thread.setDaemon(True)
        thread.start()


class SMTPThread(Thread):

    def __init__(self, msg, server, login, password):
        super().__init__()
        self._msg = msg
        self._server = server
        self._login = login
        self._password = password

    def run(self):
        try:
            sender = smtplib.SMTP(self._server)
            sender.starttls()
            sender.login(self._login, self._password)
            sender.sendmail(self._msg['From'], self._msg['To'], self._msg.as_string())
            sender.quit()
        except BaseException as err:
            print(err)
