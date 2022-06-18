import boto3
import time

input_queue_url = "https://sqs.us-east-1.amazonaws.com/013922704123/RequestQueue"
def send_message(queue_url, sqs_client, name, body):
    print("Sending message to SQS queue")
    try:
        m_att = {
            'Name': {
                'DataType': 'String',
                'StringValue': name
            }
        }
        m_bod = (body)
        ret_pack = sqs_client.send_message(QueueUrl = queue_url, MessageAttributes = m_att, MessageBody = m_bod)
        print("Message "+name+" sent to SQS")
        print()
    except Exception as e:
        print("Unable to send message to SQS")
        print(e)

sqs_obj = boto3.client('sqs', region_name='us-east-1')
for i in range(5):
	send_message(input_queue_url,sqs_obj,"FRI message "+str(i),"The "+str(i)+" message")