In Sumo, configure a [Hosted Collector] (http://help.sumologic.com/Send_Data/Hosted_Collectors/Configure_a_Hosted_Collector) and a [HTTP Source] (http://help.sumologic.com/Send_Data/Sources/02Sources_for_Hosted_Collectors/HTTP_Source)

Install Lambda Function with the following configuration
- Runtime: Python 2.7
- Handler: lambda_function.lambda_handler
- Create Role with the AmazonEC2ReadOnlyAccess policy

Configure CloudWatch Event
- Create an event to run as often as necessary

Edit Function
- Update SUMO_ENDPOINT with your Sumo HTTP Endpoint

Create Sumo parser
- This query will parse and save the data into a lookup file.
- Save it as a [Scheduled Search] (http://help.sumologic.com/Dashboards_and_Alerts/Alerts/02_Schedule_a_Search)
- Because this runs against indexed data there is a delay, so make sure there is an overlap with when the Lambda function runs.
- For example, if your Lambda function runs every 15 minutes, run your query every 25 min.

```_sourceCategory="aws/ec2info"
| json "instanceName", "region", "networkInterface", "instanceId"
| json field=networkInterface "vpcId", "eni", "publicIp", "privateIpAddress" nodrop
| count by instanceName, instanceId,region, eni,vpcId, publicIp, privateIpAddress
| fields - _count
| save /shared/ec2info```
