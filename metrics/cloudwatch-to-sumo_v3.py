#!/usr/bin/env python

import datetime, json, urllib2, time
import boto3
from operator import itemgetter
from time import gmtime, strftime
from datetime import datetime, timedelta

### GLOBAL VARIABLES ###
AWS_ACCESS_KEY_ID = '<YOUR AWS ACCESS KEY'>'
AWS_SECRET_ACCESS_KEY = '<YOUR AWS SECRET'>'

#regions = ["us-east-1", "us-west-1", "us-west-2", "ap-northeast-1", "ap-southeast-1", "ap-southeast-2", "eu-west-1", "sa-east-1"]
regions = ["us-east-1"]

# The instances from which you want to collect metrics. Default is all
filters = []

# Which instance attributes do you want to include with instance metrics
attributes = ['tags', 'public_ip_address', 'private_ip_address', 'vpc_id', 'instance_id', 'private_dns_name', 'public_dns_name', 'security_groups', 'instance_type', 'key_name', 'subnet_id']

# Which EC2 metrics do you want to capture
ec2_metrics = [ 'CPUUtilization', 'NetworkIn', 'NetworkOut', 'DiskReadBytes', 'DiskReadOps', 'DiskWriteBytes', 'DiskWriteOps']

# Store results 
d = {}

# Only required when using write_to_file()
logfile = '/var/log/cloudwatch_metrics.log'

### CONSTANTS ###
# Start and end times for the Cloudwatch query
QUERY_END = datetime.utcnow()
QUERY_START = QUERY_END - timedelta(minutes=9)

### FUNCTIONS ###
def convert(input):
    """Covert from unicode to utf8"""
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def remove_underscore(attrib):
    """Remove underscores and camel case attribute names"""
    index = 0 
    while index < len(attrib):
        if attrib[index] is '_':
            attrib[index+1] = attrib[index+1].upper()
            del attrib[index]
            index = index+ 1
        else:
            index = index + 1 
            continue
    new_attrib = "".join(attrib)
    return new_attrib

def write_to_file(logdata):
    """Write log message to file."""
    fh = open(logfile, "a")
    fh.write(str(logdata) + '\n')
    fh.close()

def push_to_collector(logdata):
    """Sends log message to hosted collector"""
    logdata = logdata + '\n'
    print urllib2.urlopen(url, logdata).read()

def get_ec2_metrics(metric, instanceId):
    """Pull instance metrics from CloudWatch."""
    global d

    cw = boto3.client('cloudwatch', region_name=region, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    results = cw.get_metric_statistics(
                            Namespace='AWS/EC2',
                            MetricName=metric,
                            Dimensions=[{'Name': 'InstanceId', 'Value': instanceId}],
                            StartTime=QUERY_START,
                            EndTime=QUERY_END,
                            Period=300,
                            Statistics=['Average'])

    datapoints = convert(results['Datapoints'])

    if datapoints:
        datapoint = datapoints[0]
        del datapoint['Timestamp']

        l = [datapoint]
        d[metric] = l
    else:
        d[metric] = []

for region in regions:
    s = boto3.session.Session(region_name=region, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    ec2 = s.resource('ec2')

    for i in ec2.instances.filter(Filters=filters):

        d['timestamp'] = str(QUERY_START)
        d['region'] = region

        id = getattr(i,'id')

        instance = ec2.Instance(id)

        for a in range(len(attributes)):
            r = {}
            attrib = list(attributes[a])
            new_attrib = remove_underscore(attrib) 

            r[attributes[a]] = getattr(instance,attributes[a])
            d[new_attrib] = r[attributes[a]]

        for metric in ec2_metrics:
            get_ec2_metrics(metric, d['instanceId'])

        print d
        write_to_file(d)
