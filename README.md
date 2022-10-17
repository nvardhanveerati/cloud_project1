### **Overview:**
In this project, a cloud application to perform image recognition was developed. It consists of a web-tier and app-tiers that are instantiated on the basis of the load of inputs. 
The web-tier determines the number of app-tier instances that need to be created to distribute the load and perform the classification.
When images are loaded into the application, they are dropped in an SQS reuqest queue that triggers that webtier to create the proportionate amount of app-tiers. 
Once an apptier is created, it polls for images in the queue and classifies them and send the data to S3 buckets and output message to SQS response queue that the webtier then sends to the user.

The language used if *Python* and the package used to create, process and destroy AWS cloud functionalities are is *boto3*. The classification function uses *torch* package for the recognition. The web-tier is hosted as a *Flask* application.
To run it, please use an environment which has these requirements installed.

### **AWS component details:**
```
Web-tier endpoint:           x
AWS EC2 apptier image:       x
AWS SQS Request queue name:  RequestQueue
AWS SQS Request queue URL:   x
AWS SQS Response queue name: ResponseQueue
AWS SQS Response queue URL:  x
AWS S3 input bucket:         x
AWS S3 outut bucket:         x
```
### **Execution Instructions:**
1. Log in to the web-tier instance.
2. Run the flask app for the workload to hit using the below command
```
python3 cloud_project1/web_tier/app.py
```
3. Run the scaling-out script to perform auto-scaling:
```
python3 cloud_project1/web_tier/scalingOut.py
```
4. Setup the multithread workload generator code to hit the web-tier’s endpoint.
5. Execute the generator with a specific number of images in the following format
```
python multithread_workload_generator.py --num_request <NUMBER_OF_IMAGES> --url '<WEB-TIER ENDPOINT>' --image_folder "<PATH_TO_IMAGES_FOLDER>"
```
