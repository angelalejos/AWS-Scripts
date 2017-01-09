##################################################################################
##                      EC2 Info to SumoLogic                                  ##
## URL HERE  ##
##################################################################################

import boto3
import datetime 
import json
import urllib2

### GLOBAL VARIABLES ###
# Doc for creating Sumo Endpoint http://help.sumologic.com/Send_Data/Sources/02Sources_for_Hosted_Collectors/HTTP_Source
SUMO_ENDPOINT = 'YOUR SUMO ENDPOINT' 

# AWS Access Key ID and Access Key are not required. Instead setup a role with AmazonEC2ReadOnlyAccess

regions = ["us-east-1", "us-west-1", "us-west-2", "ap-northeast-1", "ap-southeast-1", "ap-southeast-2", "eu-west-1", "sa-east-1"]

### FUNCTIONS ###
def send_to_sumo(data):
    '''Sends data to hosted collector'''
    data = json.dumps(data)
    print(urllib2.urlopen(SUMO_ENDPOINT, data).read())

def lambda_handler(event, context):

    for region in regions:
        ec2 = boto3.resource('ec2', region_name=region)
    
        for instance in ec2.instances.filter():
    
            ec2Info = {'eventType': 'instanceInfo', 'region': region}
    
            for tag in instance.tags:
                if 'Name' in tag['Key']:
                    ec2Info['instanceName'] = tag['Value']
    
            ec2Info['instanceId'] = instance.id.strip('[]')
    
            interfaces = instance.network_interfaces
    
            for i in range(len(instance.network_interfaces_attribute)):
                n = {
                        'vpcId': instance.network_interfaces_attribute[i]['VpcId'],
                        'eni': instance.network_interfaces_attribute[i]['NetworkInterfaceId']
                }
    
                if 'Association' in instance.network_interfaces_attribute[i]:
                    n['publicIp'] = instance.network_interfaces_attribute[i]['Association']['PublicIp']
                if 'PrivateIpAddress' in instance.network_interfaces_attribute[i]:
                    n['privateIpAddress'] = instance.network_interfaces_attribute[i]['PrivateIpAddress']
    
                ec2Info['networkInterface'] = n
                
                send_to_sumo(ec2Info)
