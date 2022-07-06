import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from os.path import basename

class EmailHelper:
    def __init__(self,sender_email,sender_pass):
        self.sender_email=sender_email
        self.sender_pass=sender_pass

    def send_mail(self,subject: str, text: str,
                  send_to: list, files=None):

        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = ', '.join(send_to)
        msg['Subject'] = subject

        msg.attach(MIMEText(text))

        for f in files or []:
            with open(f, "rb") as fil:
                ext = f.split('.')[-1:]
                attachedfile = MIMEApplication(fil.read(), _subtype=ext)
                attachedfile.add_header(
                    'content-disposition', 'attachment', filename=basename(f))
            msg.attach(attachedfile)

        smtp = smtplib.SMTP(host="smtp.cloudslogics.com")
        smtp.starttls()
        smtp.login(self.sender_email, self.sender_pass)
        smtp.sendmail(self.sender_email, send_to, msg.as_string())
        smtp.close()