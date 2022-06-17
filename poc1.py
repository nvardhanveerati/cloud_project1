import boto3
import time
import os

input_queue_url = "https://sqs.us-east-1.amazonaws.com/383965277656/my_input_q"
output_queue_url = "https://sqs.us-east-1.amazonaws.com/383965277656/my_output_q"

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


def recieve_sqs_message(sqs_client):
    print("Receiving the most recent message")
    try:
        ret_pack = sqs_client.receive_message(QueueUrl = input_queue_url, AttributeNames = ['SentTimestamp'], MaxNumberOfMessages = 1, MessageAttributeNames = ['All'], VisibilityTimeout = 0, WaitTimeSeconds = 0)
        return ret_pack 
    except Exception as e:
        print("Unable to receive message from SQS")
        print(e)
        return None

def number_messages_in_queue(sqs_client, queue_url):
	att = sqs_client.get_queue_attributes(QueueUrl = queue_url, AttributeNames = ['All'])
	x = int(att['Attributes']['ApproximateNumberOfMessages'])
	print(str(x)+" MESSAGES PRESENT")
	return x

def delete_message(sqs_client, queue_url, receipt_handle):
	sqs_client.delete_message(QueueUrl = queue_url, ReceiptHandle = receipt_handle)

# poll for messages and recieve if present
# 

if __name__ == '__main__':
	try:
	    sqs_obj = boto3.client('sqs', region_name='us-east-1')
	except Exception as e:
		print(e)
	# Remove the following lines
	# for i in range(5):
	# 	send_message(input_queue_url,sqs_obj,"wed message "+str(i),"The "+str(i)+" message")
	# time.sleep(15)
	# Till here
	flag = True
	while flag:
		response = recieve_sqs_message(sqs_client = sqs_obj)
		if "Messages" not in response:
			print("No more messages")
			print("Polling for 30 secs")
			time.sleep(30)
			if(number_messages_in_queue(sqs_obj,input_queue_url)==0):
				flag = False
				break
			response = recieve_sqs_message(sqs_client = sqs_obj)
		rec_handle = response["Messages"][0]["ReceiptHandle"]
		print("Got the message: ")
		print(response)
		delete_message(sqs_client = sqs_obj, queue_url = input_queue_url, receipt_handle = rec_handle)
		# Decode the message and store the image on the ec2
		# Take the image, do classification and get result
		# Upload result and input image in respective S3, send result image to sqs queue.
		print()
		if(number_messages_in_queue(sqs_obj,input_queue_url)==0):
			print("Polling for 30 secs")
			time.sleep(30)
			if(number_messages_in_queue(sqs_obj,input_queue_url)==0):
				flag = False
				break
	print("Shuting down current ec2")
	# os.system('sudo shutdown -h now')

