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
            # identifier = str(uuid.uuid4())
            converted_string = base64.b64encode(Img_file.read())
            sqs_message_body = {
                'encoded_image': str(converted_string, 'utf-8'),
                # 'unique_id': identifier,
                'file_name': Img_file.filename
            }
            # Send message to SQS queue.
            sqs.send_message(
                QueueUrl=SQS_request,
                MessageBody=json.dumps(sqs_message_body)
            )
        print('Uploaded file to the request queue!')

        while True:
            sqs_output = sqs.receive_message(
                QueueUrl=SQS_response,
                AttributeNames=['All'],
                MaxNumberOfMessages=10,
                WaitTimeSeconds=1
            )
            msg = sqs_output.get('Messages', [])
            for item in msg:
                msg_body = json.loads(item.get('Body'))
                if msg_body['file_name'] == Img_file.filename:  # Check the id of the image
                    sqs.delete_message(
                        QueueUrl=SQS_response,
                        ReceiptHandle=item.get('ReceiptHandle')
                    )
                    return msg_body.get('classification')
                    #return Img_file.filename
    except Exception as e:
        print('Error occurred: {}'.format(e))
        return ''


if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=3000)
    # app.run(host=os.getenv('LISTEN', '0.0.0.0'),
    #         port=int(os.getenv('PORT', '3000')))
