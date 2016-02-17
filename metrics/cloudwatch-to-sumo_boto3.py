#!/usr/bin/env python

import datetime, json, urllib2, time
import boto3
from operator import itemgetter
from time import gmtime, strftime
from datetime import datetime, timedelta

### GLOBAL VARIABLES ###
#regions = ["us-east-1", "us-west-1", "us-west-2", "ap-northeast-1", "ap-southeast-1", "ap-southeast-2", "eu-west-1", "sa-east-1"]
regions = ["us-east-1"]

attributes = ['public_ip_address', 'private_ip_address', 'vpc_id', 'instance_id', 'private_dns_name', 'public_dns_name', 'security_groups', 'instance_type', 'key_name', 'subnet_id']

ec2_metrics = [ 'CPUUtilization', 'NetworkIn', 'NetworkOut', 'DiskReadBytes', 'DiskReadOps', 'DiskWriteBytes', 'DiskWriteOps']
linux_metrics = [ 'DiskSpaceUtilization', 'MemoryUtilization', 'SwapUtilization' ]

#configure logging - http://boto3.readthedocs.org/en/latest/reference/core/boto3.html

d = {}

logfile = '/var/log/cloudwatch_metrics.log'

### CONSTANTS ###
# Start and end times for the Cloudwatch query
query_end = datetime.utcnow()
query_start = query_end - timedelta(minutes=9)

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
    """Writes a given log message to file."""
    fh = open(logfile, "a")
    fh.write(str(logdata) + '\n')
    fh.close()

def push_to_sumo(logdata):
    """Sends given log message to Hosted Collector"""
    logdata = str(logdata) + '\n'
    print urllib2.urlopen(url, logdata).read()

def get_ec2_metrics(metric, instanceId):
    """Pull instance metrics from CloudWatch."""
    global d

    cw = boto3.client('cloudwatch', region_name=region)

    results = cw.get_metric_statistics(
                            Namespace='AWS/EC2',
                            MetricName=metric,
                            Dimensions=[{'Name': 'InstanceId', 'Value': instanceId}],
                            StartTime=query_start,
                            EndTime=query_end,
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
    s = boto3.session.Session(region_name=region)
    ec2 = s.resource('ec2')

    for i in ec2.instances.all():
        d['timestamp'] = str(query_start)
        d['region'] = region
        for a in range(len(attributes)):
            r = {}
            attrib = list(attributes[a])
            new_attrib = remove_underscore(attrib)
            r[attributes[a]] = getattr(i,attributes[a])
            d[new_attrib] = r[attributes[a]]

        for metric in ec2_metrics:
          get_ec2_metrics(metric, d['instanceId'])

        write_to_file(d)
        #push_to_sumo(d)
