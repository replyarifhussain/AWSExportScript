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
        ec2_client = boto3.client('ec2', region_name="us-east-1")
        regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
        print("*** Start Generating Report ***")
        # export_ec2(regions, filepath)
        # export_ec2(regions, filepath, launchedOver24hr=True)
        # export_alb(regions, filepath)
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
