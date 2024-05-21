import boto3
import csv
from urllib.parse import urlparse


####### To Do ################

## modify script to output to stdout
## modify script to have friendlier output
## modify script to iterate through all regions of an environment (currently uses whatever is in aws configure)

###### To Do ###################


def get_resources_by_tag(tag_key, tag_value):
    client = boto3.client('resourcegroupstaggingapi')
    response = client.get_resources(
        TagFilters=[
            {
                'Key': tag_key,
                'Values': [tag_value]
            }
        ]
    )
    resources = response.get('ResourceTagMappingList', [])
    return resources

def parse_arn(arn):
    parsed = urlparse(arn)
    parts = parsed.path.split(':')
    service = parts[2]
    region = parts[3]
    account_id = parts[4]
    resource_id = parts[-1]
    return service, region, account_id, resource_id

def get_resource_name(service, resource_id):
    if service == 'ec2':
        ec2 = boto3.client('ec2')
        if 'instance' in resource_id:
            instance_id = resource_id.split('/')[-1]
            response = ec2.describe_instances(InstanceIds=[instance_id])
            instances = response.get('Reservations', [])
            if instances:
                return instances[0]['Instances'][0].get('Tags', [])
        elif 'eipalloc' in resource_id:
            eipalloc_id = resource_id.split('/')[-1]
            response = ec2.describe_addresses(AllocationIds=[eipalloc_id])
            addresses = response.get('Addresses', [])
            if addresses:
                return addresses[0].get('Tags', [])
    return []

def write_to_csv(resources, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['ResourceARN', 'Region', 'Service', 'AccountID', 'ResourceID', 'Tags', 'ResourceName']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for resource in resources:
            service, region, account_id, resource_id = parse_arn(resource['ResourceARN'])
            tags = "; ".join([f"{tag['Key']}={tag['Value']}" for tag in resource['Tags']])
            resource_tags = get_resource_name(service, resource_id)
            resource_name = "; ".join([f"{tag['Key']}={tag['Value']}" for tag in resource_tags])
            writer.writerow({
                'ResourceARN': resource['ResourceARN'],
                'Region': region,
                'Service': service,
                'AccountID': account_id,
                'ResourceID': resource_id,
                'Tags': tags,
                'ResourceName': resource_name
            })

if __name__ == "__main__":
    tag_key = 'housekeeping-cleanup'
    tag_value = 'Tagged for termination by MS Standardize and Enforce'
    output_file = 'tagged_resources.csv'

    resources = get_resources_by_tag(tag_key, tag_value)
    write_to_csv(resources, output_file)

    print(f"Output written to {output_file}")

