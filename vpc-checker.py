import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


# This script looks at all regions for an environment defined in aws config. It returns vpcs in three ways:
# verbose mode will return all vpcs and its resources and tags
# orphan mode will return vpcs that have subnets but not other resources, returning its tags
# marked-for-cleanup will return vpcs that are already tagged with housekeeping-cleanup tag. 



def get_regions():
    """Retrieve all AWS regions."""
    ec2 = boto3.client('ec2', region_name='us-east-1')
    return [region['RegionName'] for region in ec2.describe_regions()['Regions']]

def get_vpc_tags(ec2, vpc_id):
    """Retrieve tags for a VPC."""
    response = ec2.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [vpc_id]}])
    return {tag['Key']: tag['Value'] for tag in response['Tags']}

def check_ec2_instances(ec2, vpc_id):
    instances = ec2.describe_instances(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    return [i['InstanceId'] for r in instances['Reservations'] for i in r['Instances']]

def check_subnets(ec2, vpc_id):
    subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    return [subnet['SubnetId'] for subnet in subnets['Subnets']]

def check_rds(vpc_id):
    rds = boto3.client('rds')
    dbs = rds.describe_db_instances()
    return [db['DBInstanceIdentifier'] for db in dbs['DBInstances'] if db['DBSubnetGroup']['VPCId'] == vpc_id]

def check_elb(vpc_id):
    elb = boto3.client('elb')
    elbv2 = boto3.client('elbv2')
    classic_elbs = elb.describe_load_balancers()['LoadBalancerDescriptions']
    linked_classic_elbs = [elb['LoadBalancerName'] for elb in classic_elbs if elb['VPCId'] == vpc_id]
    app_elbs = elbv2.describe_load_balancers()['LoadBalancers']
    linked_app_elbs = [elb['LoadBalancerName'] for elb in app_elbs if elb['VpcId'] == vpc_id]
    return linked_classic_elbs + linked_app_elbs

def check_lambda(vpc_id):
    lambda_client = boto3.client('lambda')
    functions = lambda_client.list_functions()['Functions']
    return [func['FunctionName'] for func in functions if 'VpcConfig' in func and func['VpcConfig']['VpcId'] == vpc_id]

def check_vpc_endpoints(ec2, vpc_id):
    endpoints = ec2.describe_vpc_endpoints(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    return [ep['VpcEndpointId'] for ep in endpoints['VpcEndpoints']]

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['verbose', 'orphan', 'marked-for-cleanup']:
        print("Usage: python vpc-checker.py <mode>")
        print("Modes: verbose, orphan, marked-for-cleanup")
        return

    mode = sys.argv[1]
    regions = get_regions()
    for region in regions:
        print(f"==================== Checking Region: {region} ====================")
        ec2 = boto3.client('ec2', region_name=region)
        vpcs = ec2.describe_vpcs()['Vpcs']
        for vpc in vpcs:
            vpc_id = vpc['VpcId']
            tags = get_vpc_tags(ec2, vpc_id)
            if mode == 'marked-for-cleanup' and 'housekeeping-cleanup' not in tags:
                continue  # Corrected logic to ensure it only processes VPCs with the specific tag
            resources = {
                'Subnets': check_subnets(ec2, vpc_id),
                'EC2 Instances': check_ec2_instances(ec2, vpc_id),
                'RDS Instances': check_rds(vpc_id),
                'ELBs': check_elb(vpc_id),
                'Lambda Functions': check_lambda(vpc_id),
                'VPC Endpoints': check_vpc_endpoints(ec2, vpc_id)
            }
            # Output details for the VPC if it matches the criteria
            if mode == 'verbose' or (mode == 'orphan' and resources['Subnets'] and all(not resources[res_type] for res_type in resources if res_type != 'Subnets')) or (mode == 'marked-for-cleanup'):
                print(f"-------- Checking VPC: {vpc_id} in Region: {region} --------")
                print(f"Tags: {tags}")
                for resource_type, instances in resources.items():
                    print(f"{resource_type}: {instances}")
                print("----------------------------------------------------------------\n")

if __name__ == "__main__":
    main()

