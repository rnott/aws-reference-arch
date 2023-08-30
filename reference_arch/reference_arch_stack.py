'''
Copyright 2023 Randy Nott (rnott.org)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

'''
from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
'''
from aws_cdk import (
    Stack,
    Duration,
    aws_dynamodb as dynamodb,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_cloudwatch as cloudwatch,
    aws_logs)
from constructs import Construct

class ReferenceArchStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        # automatically creates public and private subnets per AZ
        #vpc = ec2.Vpc(self, "reference-vpc",
        vpc = ec2.Vpc(self, "trial-vpc",
                      ip_addresses = ec2.IpAddresses.cidr("10.0.0.0/16"),
                      create_internet_gateway = False,  # no egress
                      #enable_dns_hostnames = False,     # private instances do not get public DNS names
                      enable_dns_support = True,        # enable internal AWS DNS (169.254.169.253)
                      # flow_logs = True,
                      max_azs = 2,
                      subnet_configuration = [
                        ec2.SubnetConfiguration(  # public subnet group
                            name = 'ingress',
                            subnet_type = ec2.SubnetType.PUBLIC,
                            cidr_mask = 24
                        ),
                        ec2.SubnetConfiguration(  # public subnet group (no egress)
                            name = 'service',
                            subnet_type = ec2.SubnetType.PRIVATE_ISOLATED,
                            cidr_mask = 24
                        )
                      ]
                    )
        # add gateway endpoints so that we can customize subnets and policies
        # privae subnets only
        dynamo_db_endpoint = vpc.add_gateway_endpoint(
            'DynamoDbEndpoint',
            service = ec2.GatewayVpcEndpointAwsService.DYNAMODB,
            subnets = [
                ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)
            ]
        )
        s3_endpoint = vpc.add_gateway_endpoint(
            'S3Endpoint',
            service = ec2.GatewayVpcEndpointAwsService.S3
        )

        # interface endpoints: private subnets by default
        vpc.add_interface_endpoint(
            "EcrDockerEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER
        )
        vpc.add_interface_endpoint(
            "CloudTrailEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDTRAIL
        )
        vpc.add_interface_endpoint(
            "CloudWatchEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH
        )
        vpc.add_interface_endpoint(
            "KmsEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.KMS
        )
        vpc.add_interface_endpoint(
            "SecretsManagerEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER
        )

        # vpn_gateway

        # create dynamodb table - ping
        table = dynamodb.Table(self, "ping",
                                table_name='ping',
                                billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
                                point_in_time_recovery=False,
                                partition_key=dynamodb.Attribute(name='pid', type=dynamodb.AttributeType.STRING),
                                sort_key=dynamodb.Attribute(name='id', type=dynamodb.AttributeType.STRING)
                                )
        # raise an alarm if any requests are throttled
        metric = table.metric_throttled_requests_for_operations(
            operations=[dynamodb.Operation.PUT_ITEM],
            period=Duration.minutes(1)
        )
        cloudwatch.Alarm(self, "Alarm",
                        metric=metric,
                        evaluation_periods=1,
                        threshold=1
                    )

        # create container repository
        ecr_repository = ecr.Repository(self, "reference-repository",
                                        repository_name="reference-repository"
                                        )
