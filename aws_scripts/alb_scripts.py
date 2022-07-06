import csv
import os
import boto3
from datetime import datetime, timedelta


def export_alb(regions, output_file_path):
    payload_outer = []
    payload_inner = dict()
    for r in regions:
        ec2client = boto3.client('elbv2', region_name=r)
        paginator = ec2client.get_paginator('describe_load_balancers')
        page_iterator = paginator.paginate()

        for page in page_iterator:
            for alb in page['LoadBalancers']:
                if alb['Type'] == 'application':
                    payload_inner['Name'] = alb.get('LoadBalancerName', '')
                    payload_inner['DNSName'] = alb.get('DNSName', '')
                    payload_inner['Type'] = alb.get('Type', '')
                    payload_inner['Scheme'] = alb.get('Scheme', '')
                    payload_inner['State'] = alb.get("State", {}).get("Code", '')
                    payload_inner['Region'] = r
                    payload_outer.append(payload_inner.copy())

    field_names = ["Name", "DNSName", "Type", "Scheme", "State", "Region"]
    filename = "alb_report.csv"
    with open(f'{output_file_path}{filename}', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, quoting=csv.QUOTE_ALL,
                                delimiter=',', dialect='excel', fieldnames=field_names)
        writer.writeheader()
        for i in payload_outer:
            writer.writerow(i)
    return
