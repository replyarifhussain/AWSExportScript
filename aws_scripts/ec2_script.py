import csv
import os
import boto3
from datetime import datetime, timedelta


def launched_in_last24hours(launch_time):
    return (datetime.utcnow().replace(tzinfo=launch_time.tzinfo) - launch_time) < timedelta(hours=24)


def export_ec2(regions, secret_key, secret_key_id, output_file_path):
    payload_outer = []
    payload_outer_launchecOver = []
    payload_inner = dict()
    for r in regions:
        if secret_key_id and secret_key:
            session = boto3.Session(
                aws_access_key_id=secret_key_id,
                aws_secret_access_key=secret_key,
                region_name=r)
        else:
            session = boto3.Session(region_name=r)

        ec2client = session.client('ec2')
        paginator = ec2client.get_paginator('describe_instances')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            for each_res in page['Reservations']:
                instance = each_res['Instances'][0]
                for instance in each_res['Instances']:
                    if instance['State']['Name'] == "running":
                        volumes = ec2client.describe_volumes(
                            Filters=[{'Name': 'attachment.instance-id', 'Values': [instance['InstanceId']]}]
                        )
                        volume_devices = volumes.get('Volumes', [])
                        root_device_name = instance.get("RootDeviceName")
                        root_device = {}
                        for vol in volume_devices:
                            is_root = [i.get("Device", '') for i in vol.get("Attachments", []) if
                                       i.get("Device", '') == root_device_name]
                            if is_root:
                                root_devide = vol
                        secondary_devices = [v for v in volume_devices if
                                             v.get("VolumeId") != root_devide.get("VolumeId") and v.get(
                                                 'State') == 'in-use']
                        secondary_device = secondary_devices[0] if secondary_devices else dict()
                        inst_names = [i['Value'] for i in instance['Tags'] if i['Key'] == 'Name']
                        payload_inner['Instance Name'] = inst_names[0] if inst_names else ''
                        payload_inner['Host'] = instance.get('PublicDnsName')
                        payload_inner['Ip Address'] = instance.get('PublicIpAddress')
                        payload_inner['Primary Ebs Size'] = root_devide.get("Size", "")
                        payload_inner['Primary Ebs Encryption Status'] = "Encrypted" if root_devide.get(
                            "Encrypted") else "UnEncrypted"
                        payload_inner['Secondary Ebs Size'] = secondary_device.get("Size", "")
                        payload_inner['Secondary Ebs Encryption Status'] = "Encrypted" if secondary_device.get(
                            "Encrypted") else "UnEncrypted"
                        payload_inner['Region'] = r
                        launchedOver24hr = launched_in_last24hours(instance.get('LaunchTime'))
                        if launchedOver24hr:
                            payload_outer_launchecOver.append(payload_inner.copy())
                        payload_outer.append(payload_inner.copy())

    field_names = ['Instance Name', 'Host', 'Ip Address', 'Primary Ebs Size', 'Primary Ebs Encryption Status',
                   'Secondary Ebs Size', 'Secondary Ebs Encryption Status'
        , 'Region']
    create_excel_file(output_file_path, "ec2_report.csv", field_names, payload_outer)
    create_excel_file(output_file_path, "ec2_launched_over24hrs_report.csv", field_names, payload_outer_launchecOver)


def create_excel_file(output_file_path,filename, field_names, data):
    with open(f'{output_file_path}{filename}', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, quoting=csv.QUOTE_ALL,
                                delimiter=',', dialect='excel', fieldnames=field_names)
        writer.writeheader()
        for i in data:
            writer.writerow(i)
    return
