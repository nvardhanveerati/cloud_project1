import boto3

try:
    ec2_client = boto3.client('ec2', region_name='us-east-1')
except Exception as e:
    print("Could not create EC2 client")
    print(e)
    print()

security_grp = 'sg-0673f5c56597a0e62'
ami_id = 'ami-0ccdd16d4988d0878'
key_name = 'project1'

def create_ec2_instance():
    content_script = '''#!/bin/bash
    cd /home/ubuntu/cloud_project1/
    sudo chmod -R 777 .
    cd /home/ubuntu/cloud_project1/app_tier
    touch new_file.txt
    echo 'new text here' >> new_file.txt
    su ubuntu -c 'python3 app_module.py > execution_logs.txt'
    touch after_run.txt'''

    # content_script = '''
    # #!/bin/bash
    # cd /home/ec2-user/cloud_project1/app_tier
    # touch before.txt
    # python3 app_module.py > execution_logs.txt
    # touch after.txt
    # '''

    instances = ec2_client.run_instances(
        ImageId = ami_id,
        MinCount = 1,
        MaxCount = 1,
        InstanceType = 't2.micro',
        KeyName = key_name,
        InstanceInitiatedShutdownBehavior = 'terminate',
        UserData = content_script,
        SecurityGroupIds = [security_grp],
        TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'App_Tier_'
                },
            ]
        },
    ],
    )
    ec2_inst_id = instances['Instances'][0]['InstanceId']
    print('Creating instance:', ec2_inst_id)


def list_running_ec2():
    list_running_insts = []
    insts = ec2_client.describe_instances(Filters=[{'Name': 'instance-state-name','Values': ['pending','running'],}]).get('Reservations')
    for inst in insts:
        for instance in inst['Instances']:
            list_running_insts.append(instance['InstanceId'])
    return list_running_insts
