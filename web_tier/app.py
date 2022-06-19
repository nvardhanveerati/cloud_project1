from flask import Flask, request, session
from datetime import timedelta
import boto3
import uuid
import base64
import json
import os

app = Flask(__name__)
app.secret_key = "something unique"

sqs = boto3.client('sqs', region_name='us-east-1')
SQS_request = 'https://sqs.us-east-1.amazonaws.com/013922704123/RequestQueue'
SQS_response = 'https://sqs.us-east-1.amazonaws.com/013922704123/ResponseQueue'

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/', methods=['POST'])
def process():
    try:
        Img_file = request.files.get('myfile')
        print(Img_file)
        if Img_file.filename:
            converted_string = base64.b64encode(Img_file.read())
            struct_message = {
                'encoded_image': str(converted_string, 'utf-8'),
                'file_name': Img_file.filename
            }
            sqs.send_message(QueueUrl=SQS_request, MessageBody=json.dumps(struct_message))
            print("Message sent to request queue")

        while True:
            received_mess_1 = sqs.receive_message(QueueUrl=SQS_response, AttributeNames=['All'], MaxNumberOfMessages=10, WaitTimeSeconds=1)
            received_mess_list = received_mess_1.get('Messages', [])
            for r_mess in received_mess_list:
                body = r_mess.get('Body')
                contnt = json.loads(body)
                if(Img_file.filename==contnt['file_name']):  
                    sqs.delete_message(QueueUrl=SQS_response, ReceiptHandle=r_mess.get('ReceiptHandle'))
                    return contnt.get('classification')
                    #return Img_file.filename
    except Exception as e:
        print("Couldn't Process the images")
        print(e)
        return ""


if __name__ == '__main__':
    # from waitress import serve
    # serve(app, host='0.0.0.0', port=3000)
    app.run(host=os.getenv('LISTEN', '0.0.0.0'), port=int(os.getenv('PORT', '8000')))
