import boto3
import csv
from urllib.parse import urlparse

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
    region = parts[3]
    service = parts[2]
    return region, service

def write_to_csv(resources, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['ResourceARN', 'Region', 'Service', 'Tags']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for resource in resources:
            region, service = parse_arn(resource['ResourceARN'])
            tags = "; ".join([f"{tag['Key']}={tag['Value']}" for tag in resource['Tags']])
            writer.writerow({
                'ResourceARN': resource['ResourceARN'],
                'Region': region,
                'Service': service,
                'Tags': tags
            })

if __name__ == "__main__":
    tag_key = 'housekeeping-cleanup'
    tag_value = 'Tagged for termination by MS Standardize and Enforce'
    output_file = 'tagged_resources.csv'

    resources = get_resources_by_tag(tag_key, tag_value)
    write_to_csv(resources, output_file)

    print(f"Output written to {output_file}")

