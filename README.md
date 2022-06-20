# Cloud Computing: Group Project 1 - IAAS

### Group Members
#### Nithya Vardhan Reddy Veerati
#### Anuj Dharurkar
#### Kshitij Srivastava

### **Overview:**
In this project, a cloud application to perform image recognition was developed. It consists of a web-tier and app-tiers that are instantiated on the basis of the load of inputs. 
The web-tier determines the number of app-tier instances that need to be created to distribute the load and perform the classification.
When images are loaded into the application, they are dropped in an SQS reuqest queue that triggers that webtier to create the proportionate amount of app-tiers. 
Once an apptier is created, it polls for images in the queue and classifies them and send the data to S3 buckets and output message to SQS response queue that the webtier then sends to the user.

The language used if *Python* and the package used to create, process and destroy AWS cloud functionalities are is *boto3*. The classification function uses *torch* package for the recognition. The web-tier is hosted as a *Flask* application.
To run it, please use an environment which has these requirements installed.

### **AWS component details:**
```
Web-tier endpoint:           http://18.207.244.202:8000
AWS EC2 apptier image:       ami-0ccdd16d4988d0878
AWS SQS Request queue name:  RequestQueue
AWS SQS Request queue URL:   https://sqs.us-east-1.amazonaws.com/013922704123/RequestQueue
AWS SQS Response queue name: ResponseQueue
AWS SQS Response queue URL:  https://sqs.us-east-1.amazonaws.com/013922704123/ResponseQueue
AWS S3 input bucket:         new-input-bucket
AWS S3 outut bucket:         output-imagedataset-bucket
```
### **Execution Instructions:**
1. Setup the workload generating code.
2. Log into the web-tier
3. Run the flask app for the workload to hit:

```
python3 cloud_project1/web_tier/app.py
```
4. Run the scale out script to perform auto-scaling:
```
python3 cloud_project1/web_tier/scalingOut.py
```
5. Point the workload generating code to the web-tier endpoint and run the multithreaded workload generator code.