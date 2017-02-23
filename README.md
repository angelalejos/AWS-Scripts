#Various Amazon Web Services (AWS) Scripts#


* cloudwatch-to-sumo_lambda.py is an AWS Lambda function.

* cloudwatch-to-sumo_v3.py is written with the AWS SDK for Python Version 3 (https://github.com/boto/boto3)
* cloudwatch_to_sumo_v2.py is deprecated. It is written with AWS SDK for Python Version 2 (https://aws.amazon.com/sdk-for-python/)


#Environment Configuration (Mac OS)#
* Install pip
`pip install boto3`
* Install AWS CLI
`pip install awscli`
* Install Boto3

* Putting your AWS credentials directly into your scripts is dangerous as you can quite easily forget to remove them before pushing it to a github repo. See here for other options - http://boto3.readthedocs.io/en/latest/guide/configuration.html
