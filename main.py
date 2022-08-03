import boto3
from aws_scripts.ec2_script import export_ec2
from aws_scripts.alb_scripts import export_alb
import os
from dotenv import load_dotenv
from helper.email_helper import EmailHelper
from pathlib import Path

if __name__ == '__main__':
    try:
        load_dotenv()
        cwd = os.getcwd()
        filepath = os.path.join(cwd, "exports")
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        filepath = os.path.join(filepath, "")
        AWS_SECRET_ID = os.getenv("AWS_SECRET_ID","")
        AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY","")
        if AWS_SECRET_KEY and AWS_SECRET_ID:
            session = boto3.Session(
                aws_access_key_id=AWS_SECRET_ID,
                aws_secret_access_key=AWS_SECRET_KEY)
        else:
            session = boto3.Session()

        aws_client = session.client('ec2', region_name="us-east-1")
        regions = [region['RegionName'] for region in aws_client.describe_regions()['Regions']]
        print("*** Start Generating Report ***")
        export_ec2(regions,AWS_SECRET_KEY,AWS_SECRET_ID, filepath)
        export_alb(regions,AWS_SECRET_KEY,AWS_SECRET_ID, filepath)
        print(f"Reports are located at {filepath}")
        print("*** Finish Generating Report ***")
    except Exception as e:
        print(f"Unsuccessful Exception at {e}")

    try:
        recipients = os.getenv("TO_EMAIL").split(',')
        SMTP_HOST = os.getenv("SMTP_HOST")
        SMTP_PORT = os.getenv("SMTP_PORT")
        EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT")
        EMAIL_BODY = os.getenv("EMAIL_BODY")

        email_helper = EmailHelper(SMTP_HOST, SMTP_PORT, os.getenv("SMPT_USER"), os.getenv("SMPT_PASSWORD"))
        files = list()
        for path in Path(filepath).glob("*.csv"):
            files.append(str(path))
        email_helper.send_mail(subject=EMAIL_SUBJECT, text=EMAIL_BODY, send_to=recipients, files=files)

    except Exception as e:
        print(f"Email Service failed to send email.{e}")
