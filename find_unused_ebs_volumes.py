import boto3
from datetime import datetime, timedelta
import pandas as pd

# Define the number of days of inactivity
DAYS_INACTIVE = 90
# Calculate the date 90 days ago
cutoff_date = datetime.utcnow().replace(tzinfo=None) - timedelta(days=DAYS_INACTIVE)

def extract_tag_value(tags, key):
    """Extract value from tags given a key."""
    for tag in tags:
        if tag['Key'] == key:
            return tag['Value']
    return "N/A"

def get_unused_ebs_volumes():
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    
    unused_volumes = []

    print(f"Checking EBS volumes in {len(regions)} regions...")
    for region in regions:
        print(f"Checking region: {region}")
        ec2 = boto3.client('ec2', region_name=region)
        volumes = ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])
        
        for volume in volumes['Volumes']:
            create_time = volume['CreateTime'].replace(tzinfo=None)
            if create_time < cutoff_date:
                volume_id = volume['VolumeId']
                tags = volume.get('Tags', [])
                size = volume['Size']
                volume_type = volume['VolumeType']
                iops = volume.get('Iops', 'N/A')
                account = boto3.client('sts').get_caller_identity().get('Account')
                
                pvc_namespace = extract_tag_value(tags, 'kubernetes.io/created-for/pvc/namespace')
                pvc_name = extract_tag_value(tags, 'kubernetes.io/created-for/pvc/name')

                unused_volumes.append({
                    'Account': account,
                    'Region': region,
                    'PVC Namespace': pvc_namespace,
                    'PVC Name': pvc_name,
                    'EBS Volume ID': volume_id,
                    'EBS Creation Date': volume['CreateTime'],
                    'Size in GB': size,
                    'EBS Type': volume_type,
                    'IOPS (if any)': iops,
                    'Tags': tags,
                    'Monthly cost': f"${size * 0.08:.2f}",  # Example cost calculation
                    'Yearly cost': f"${size * 0.08 * 12:.2f}"
                })
                print(f"Found unused volume: {volume_id} in region {region}")
    
    print("Finished checking all regions.")
    return unused_volumes

def main():
    print("Starting the unused EBS volumes check...")
    unused_volumes = get_unused_ebs_volumes()
    
    if unused_volumes:
        df = pd.DataFrame(unused_volumes)
        output_file = "unused_ebs_volumes.csv"
        df.to_csv(output_file, index=False)
        print(f"Report generated: {output_file}")
        print(df.to_string(index=False))  # Print DataFrame to stdout
    else:
        print("No unused volumes found.")

if __name__ == "__main__":
    main()

