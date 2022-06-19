import time
import boto3
import ec2Service_handler

client = boto3.client('sqs', region_name='us-east-1')
SQS_request = 'https://sqs.us-east-1.amazonaws.com/013922704123/RequestQueue'
web_tier_instanceID = 'i-045b26529675b8375'


def scaling_out():
    totalMsgs = int(client.get_queue_attributes(
        QueueUrl=SQS_request,
        AttributeNames=['ApproximateNumberOfMessages']
    ).get('Attributes').get('ApproximateNumberOfMessages'))

    print("Messages in Input Queue: ", totalMsgs)

    running_instances = ec2Service_handler.get_running_instances()
    running_instances.remove(web_tier_instanceID)
    num_of_running_instances = len(running_instances)
    print("Total app-instances: ", num_of_running_instances)

    if totalMsgs == 0:
        return

    # for x in range(2):
    #     ec2Service_handler.create_instance()

    if 0 < totalMsgs < 20:
        if num_of_running_instances < totalMsgs:
            totalMsgs -= num_of_running_instances
            for x in range(totalMsgs):
                ec2Service_handler.create_instance()

    else:
        if num_of_running_instances < 19:
            needed_instances = 19 - num_of_running_instances
            for x in range(needed_instances):
                ec2Service_handler.create_instance()
        else:
            print("REDUCE NUMBER OF INSTANCES!")


if __name__ == '__main__':
    # scaling_out()

    while True:
        print('Start Scaling Out')
        scaling_out()
        time.sleep(5)
