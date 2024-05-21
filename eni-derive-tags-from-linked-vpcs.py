import boto3
import csv
import sys

#Will look at all enis in all regions for an environment (defined in aws config). For each eni, it will look at linked VPCs, and will get those tags for the eni. # This script needs polish, and takes a long time. 


def get_ec2_client(region):
    print(f"Creating EC2 client for region: {region}")
    return boto3.client('ec2', region_name=region)

def list_all_regions():
    client = boto3.client('ec2', region_name='us-east-1')
    regions = client.describe_regions()
    return [region['RegionName'] for region in regions['Regions']]

def get_vpc_tags(ec2_client, vpc_id):
    try:
        print(f"Retrieving tags for VPC: {vpc_id}")
        vpc = ec2_client.describe_vpcs(VpcIds=[vpc_id])
        return {tag['Key']: tag['Value'] for tag in vpc['Vpcs'][0].get('Tags', [])}
    except Exception as e:
        return {'Notes': str(e)}

def process_enis_in_region(ec2_client):
    enis = ec2_client.describe_network_interfaces()
    results = []
    for eni in enis['NetworkInterfaces']:
        eni_id = eni['NetworkInterfaceId']
        vpc_id = eni.get('VpcId', 'Unknown')
        tags = eni.get('TagSet', [])
        notes = 'Has pre-existing tags' if tags else 'No tags'
        vpc_tags = get_vpc_tags(ec2_client, vpc_id) if vpc_id != 'Unknown' else {}
        results.append({
            'ENI ID': eni_id,
            'VPC ID': vpc_id,
            **vpc_tags,
            'Notes': notes
        })
    return results

def write_to_csv(output_data, filepath):
    print(f"Writing results to {filepath}")
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
        region_eni_data = process_enis_in_region(ec2_client)
        all_eni_data.extend(region_eni_data)

    write_to_csv(all_eni_data, output_csv_path)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python test9.py <output_csv_path>")
        sys.exit(1)
    output_csv_path = sys.argv[1]
    main(output_csv_path)

