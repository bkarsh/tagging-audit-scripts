import boto3
import csv
import sys


# Script that searches enis for all regions in a given environment (defined by aws config) with the 'housekeeping-cleanup' tag. Used
# For verifying assets for removal


def get_ec2_client(region):
    print(f"Creating EC2 client for region: {region}")
    return boto3.client('ec2', region_name=region)

def list_all_regions():
    client = boto3.client('ec2', region_name='us-east-1')  # Central point for API calls
    regions = client.describe_regions()
    return [region['RegionName'] for region in regions['Regions']]

def process_enis_in_region(ec2_client, region):
    # Filter to fetch only ENIs with the specific tag
    filters = [{'Name': 'tag-key', 'Values': ['housekeeping-cleanup']}]
    enis = ec2_client.describe_network_interfaces(Filters=filters)
    results = []
    for eni in enis['NetworkInterfaces']:
        eni_id = eni['NetworkInterfaceId']
        status = eni['Status']
        vpc_id = eni.get('VpcId', 'Unknown')
        subnet_id = eni.get('SubnetId', 'Unknown')
        # Extract tags and include the ENI ID, region, and other details
        tags = {tag['Key']: tag['Value'] for tag in eni.get('TagSet', [])}
        tags.update({
            'ENI ID': eni_id,
            'Region': region,
            'Status': status,
            'VPC ID': vpc_id,
            'Subnet ID': subnet_id
        })
        results.append(tags)
    return results

def write_to_csv(output_data, filepath):
    print(f"Writing results to {filepath}")
    if not output_data:  # Check if output data is empty
        print("No ENIs found with the specified tag.")
        return
    fieldnames = set()
    for item in output_data:
        fieldnames.update(item.keys())
    fieldnames = sorted(fieldnames)

    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in output_data:
            writer.writerow(item)

def main(output_csv_path):
    regions = list_all_regions()
    all_eni_data = []
    for region in regions:
        ec2_client = get_ec2_client(region)
        region_eni_data = process_enis_in_region(ec2_client, region)
        all_eni_data.extend(region_eni_data)

    write_to_csv(all_eni_data, output_csv_path)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <output_csv_path>")
        sys.exit(1)
    output_csv_path = sys.argv[1]
    main(output_csv_path)

