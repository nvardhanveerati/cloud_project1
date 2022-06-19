import boto3

ec2_client = boto3.client('ec2', region_name='us-east-1')
security_grp = 'sg-0673f5c56597a0e62'
ami_id = 'ami-07b909b1b4747ac71'
key_name = 'project1'


def create_instance():
    user_data_script_content = '''
    #!/bin/bash
    cd /home/ubuntu/cloud_project1/app_tier
    python3 app_module.py > execution_logs.txt
    '''


    instances = ec2_client.run_instances(
        ImageId=ami_id,
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName=key_name,
        InstanceInitiatedShutdownBehavior='terminate',
        UserData=user_data_script_content,
        SecurityGroupIds=[security_grp]
        #IamInstanceProfile={'Arn': ROLE_ARN}
    )
    print('Creating instance:', instances['Instances'][0]['InstanceId'])


def get_running_instances():

    instance_list = list()
    reservations = ec2_client.describe_instances(Filters=[{
        'Name': 'instance-state-name',
        'Values': ['running', 'pending'],
    }]).get('Reservations')

    for reservation in reservations:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_list.append(instance_id)
    print('Running instances: ', instance_list)
    return instance_list
