import boto3
import time
import os
import base64
import json
import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from urllib.request import urlopen
from PIL import Image
import numpy as np
import json
import sys
import time


input_queue_url = "https://sqs.us-east-1.amazonaws.com/013922704123/RequestQueue"
output_queue_url = "https://sqs.us-east-1.amazonaws.com/013922704123/ResponseQueue"
INPUT_BUCKET = "new-input-bucket"
OUTPUT_BUCKET = "output-imagedataset-bucket"


def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read())
    return b64_string


def decode_image_and_write(file_path, image_string):
    with open(file_path, 'wb') as fh:
        fh.write(base64.b64decode(image_string))


def classify_image(image_path):
    url = str(image_path)
    #img = Image.open(urlopen(url))
    img = Image.open(url)

    model = models.resnet18(pretrained=True)

    model.eval()
    img_tensor = transforms.ToTensor()(img).unsqueeze_(0)
    outputs = model(img_tensor)
    _, predicted = torch.max(outputs.data, 1)

    with open('./imagenet-labels.json') as f:
        labels = json.load(f)
    result = labels[np.array(predicted)[0]]
    img_name = url.split("/")[-1]
    #save_name = f"({img_name}, {result})"
    save_name = f"{img_name},{result}"
    print(f"{save_name}")

    return result


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
        ret_pack = sqs_client.receive_message(QueueUrl = input_queue_url, AttributeNames = ['SentTimestamp'], MaxNumberOfMessages = 1, MessageAttributeNames = ['All'], VisibilityTimeout = 15, WaitTimeSeconds = 0)
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
	try:
		sqs_client.delete_message(QueueUrl = queue_url, ReceiptHandle = receipt_handle)
	except Exception as e:
		print("Unable to delete message")
		print(e)
		print()


if __name__ == '__main__':
	try:
	    sqs_obj = boto3.client('sqs', region_name='us-east-1')
	except Exception as e:
		print(e)

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
		loaded_response = json.loads(response["Messages"][0]["Body"])

		encoded_img = bytes(loaded_response["encoded_image"], 'utf-8')
		image_name = loaded_response["file_name"]
		print("Recieved the Image: ", image_name)
		image_path = image_name
		decode_image_and_write(image_path, encoded_img)
		classified_label = classify_image(image_path)
		s3_client = boto3.resource('s3', region_name='us-east-1')

		s3_client.Bucket(INPUT_BUCKET).upload_file(image_path, image_name)
		print('Image uploaded to S3')

		s3_client.Object(OUTPUT_BUCKET, str( image_name.split(".")[0] ) ).put(Body=classified_label)
		print('Classification txt file uploaded to s3')

		sqs_message_body = {
                'classification': classified_label,
                'file_name': image_name
        }

		sqs_obj.send_message(QueueUrl=output_queue_url, MessageBody=json.dumps(sqs_message_body))
		print("Classification result sent to response queue")

		delete_message(sqs_client = sqs_obj, queue_url = input_queue_url, receipt_handle = rec_handle)
		# print("sleeping for 15 secs")
		# time.sleep(15)
		# print()
		if(number_messages_in_queue(sqs_obj,input_queue_url)==0):
			print("Polling for 30 secs")
			time.sleep(30)
			if(number_messages_in_queue(sqs_obj,input_queue_url)==0):
				flag = False
				break
	print("Shuting down current ec2")
	os.system('sudo shutdown -h now')

