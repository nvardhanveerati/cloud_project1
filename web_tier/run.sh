#!/bin/bash
cd /home/ec2-user/cloud_project1/app_tier
touch before.txt
python3 app_module.py > execution_logs.txt
touch after.txt