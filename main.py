import boto3
from aws_scripts.ec2_script import export_ec2
from aws_scripts.alb_scripts import export_alb
import os

if __name__ == '__main__':
    ec2_client = boto3.client('ec2',region_name="us-east-1")
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    cwd = os.getcwd()
    path=os.path.join(cwd, "")
    export_ec2(regions,path)
    export_ec2(regions,path,launchedOver24hr=True)
    export_alb(regions,path)
