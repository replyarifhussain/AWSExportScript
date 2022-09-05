import smtplib
from email.mime.application import MIMEApplication
from os.path import basename
import boto3
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from botocore.exceptions import ClientError,EndpointConnectionError

class EmailHelper:
    def __init__(self,smtp_host,smtp_port,sender_email,sender_pass):
        self.smtp_host=smtp_host
        self.smtp_port=smtp_port
        self.smtp_email=sender_email
        self.smtp_password=sender_pass

    def send_mail(self,subject: str, text: str,
                  send_to, files=None):

        msg = MIMEMultipart()
        msg['From'] = self.smtp_email
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

        smtp = smtplib.SMTP(host=self.smtp_host,port=self.smtp_port)
        smtp.starttls()
        smtp.login(self.smtp_email, self.smtp_password)
        smtp.sendmail(self.smtp_email, send_to, msg.as_string())
        smtp.close()

    def verify_email_identity(self,client,email):
        try:
            ses_client = client
            response = ses_client.verify_email_identity(
                EmailAddress=email
            )
            return response['ResponseMetadata']['HTTPStatusCode']==200
        except Exception as e:
            return False;

    def send_email_ses(self,aws_session,from_email,sendTo_mail,subject: str, text: str,
                   files=None):
        email_ses_client = aws_session.client("ses", region_name="us-east-1")
        if not self.verify_email_identity(email_ses_client,from_email):
            raise Exception(f"{from_email} is not a verified SES Identity")
        email_body_text = text
        email_charset = "UTF-8"
        email_msg = MIMEMultipart('mixed')
        email_msg['Subject'] = subject
        email_msg['From'] = from_email
        email_msg['To'] = ', '.join(sendTo_mail)
        email_msg_body = MIMEMultipart('alternative')
        textpart = MIMEText(email_body_text.encode(email_charset), 'plain', email_charset)
        email_msg_body.attach(textpart)
        email_msg.attach(email_msg_body)
        if files:
            for file in files:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(open(file, 'rb').read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
                email_msg.attach(part)
        try:
            response = email_ses_client.send_raw_email(
                Source=from_email,
                Destinations=sendTo_mail,
                    RawMessage = {
                        'Data': email_msg.as_string(),
                    },
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        except EndpointConnectionError as exp:
            print(exp)
        except ConnectionError as exp:
            print(exp)
        except Exception as e:
            print("Unknown Exception(AWS SES) while sending Email")
        else:
            print(response)

