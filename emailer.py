import smtplib
from email.mime.text import MIMEText

class Emailer(object):
	def __init__(self, givenHost, givenUsername, givenPassword):
		self.username = givenUsername
		self.password = givenPassword
		self.host = givenHost

	def send_email(self, to, subject, body):
		server = smtplib.SMTP(self.host, 587)
		server.ehlo()
		server.starttls()
		server.ehlo()
		server.login(self.username, self.password)
		msg = MIMEText(body)
		msg['Subject'] = subject
		msg['From'] = self.username
		msg['To'] = to
		print()
		print(msg)
		server.send_message(msg)
		server.quit()
