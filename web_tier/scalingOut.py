import time
import boto3
import ec2Service_handler as ec2_utils

client = boto3.client('sqs', region_name='us-east-1')
SQS_request = 'https://sqs.us-east-1.amazonaws.com/<Resource6>'
web_tier_instanceID = '<Resource7>'


def scaling_out():
    total_msgs = int(client.get_queue_attributes(QueueUrl=SQS_request, AttributeNames=['ApproximateNumberOfMessages']).get('Attributes').get('ApproximateNumberOfMessages'))
    print("Messages in Input Queue: ", str(total_msgs))
    curr_runn = ec2_utils.list_running_ec2()
    curr_runn.remove(web_tier_instanceID)
    len_curr_runn = len(curr_runn)
    print("Total app-instances: ", len_curr_runn)

    if total_msgs == 0:
        return

    # for x in range(2):
    #     ec2Service_handler.create_ec2_instance()

    if(0<total_msgs<20):
        if(len_curr_runn < total_msgs):
            for x in range(total_msgs - len_curr_runn):
                ec2_utils.create_ec2_instance()
    else:
        if(len_curr_runn<19):
            for x in range(19 - len_curr_runn):
                ec2_utils.create_ec2_instance()
        else:
            print("REDUCE NUMBER OF INSTANCES!")


if __name__ == '__main__':
    # scaling_out()

    while True:
        scaling_out()
        time.sleep(3)
