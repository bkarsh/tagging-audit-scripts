import boto3
from datetime import datetime, timedelta
import pandas as pd

# Define the number of days of inactivity
DAYS_INACTIVE = 90
# Calculate the date 90 days ago
cutoff_date = datetime.utcnow() - timedelta(days=DAYS_INACTIVE)

def get_unused_ebs_volumes():
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    
    unused_volumes = []

    for region in regions:
        ec2 = boto3.client('ec2', region_name=region)
        volumes = ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])
        
        for volume in volumes['Volumes']:
            if volume['CreateTime'] < cutoff_date:
                volume_id = volume['VolumeId']
                tags = volume.get('Tags', [])
                size = volume['Size']
                volume_type = volume['VolumeType']
                iops = volume.get('Iops', 'N/A')
                account = boto3.client('sts').get_caller_identity().get('Account')
                
                unused_volumes.append({
                    'Account': account,
                    'Region': region,
                    'EBS Volume ID': volume_id,
                    'EBS Creation Date': volume['CreateTime'],
                    'Size in GB': size,
                    'EBS Type': volume_type,
                    'IOPS (if any)': iops,
                    'Tags': tags,
                    'Monthly cost': f"${size * 0.08:.2f}",  # Example cost calculation
                    'Yearly cost': f"${size * 0.08 * 12:.2f}"
                })
    
    return unused_volumes

def main():
    unused_volumes = get_unused_ebs_volumes()
    
    if unused_volumes:
        df = pd.DataFrame(unused_volumes)
        output_file = "/mnt/data/unused_ebs_volumes.csv"
        df.to_csv(output_file, index=False)
        print(f"Report generated: {output_file}")
    else:
        print("No unused volumes found.")

if __name__ == "__main__":
    main()

