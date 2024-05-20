import boto3
import json
import logging
from botocore.exceptions import ClientError

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
BUCKET_NAME = 'store-device-images-s2110849'
IMAGE_ID = 'ami-0c101f26f147fa7fd'
INSTANCE_TYPE = 't2.micro'
KEY_NAME = 'vockey'
INSTANCE_NAME = 'Instance-s2110849'
IAM_INSTANCE_PROFILE = 'LabInstanceProfile'
CONFIG_FILE_PATH = r'C:\Users\User\Downloads\coursework-megane-main\ec2-s3\s3-notification-configuration.json'

# AWS Clients
s3_client = boto3.client('s3')
ec2_resource = boto3.resource('ec2')

def check_bucket_exists(bucket_name):
    """Check if an S3 bucket exists and handle potential errors."""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            logging.info(f"Bucket {bucket_name} does not exist.")
        else:
            logging.error(f"Error checking bucket: {e}")
        return False

def create_bucket(bucket_name):
    """Create an S3 bucket if it does not already exist."""
    if not check_bucket_exists(bucket_name):
        try:
            s3_client.create_bucket(Bucket=bucket_name)
            logging.info(f"Bucket {bucket_name} successfully created.")
            set_bucket_notification(bucket_name, CONFIG_FILE_PATH)
            return True
        except ClientError as e:
            logging.error(f"Failed to create bucket {bucket_name}: {e}")
            return False
    else:
        logging.info(f"Bucket {bucket_name} already exists.")
        return True

def set_bucket_notification(bucket_name, notification_config_path):
    """Set the bucket notification configuration."""
    try:
        with open(notification_config_path, 'r') as file:
            notification_configuration = json.load(file)
        
        response = s3_client.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration=notification_configuration
        )
        logging.info("Notification configuration set successfully.")
        return response
    except Exception as e:
        logging.error(f"Error setting bucket notification: {e}")
        return None

def check_instance_exists(instance_name):
    """Check if an EC2 instance with the given name exists."""
    instances = ec2_resource.instances.filter(
        Filters=[{'Name': 'tag:Name', 'Values': [instance_name]}]
    )
    return any(instance.state['Name'] == 'running' for instance in instances)

def create_ec2_instance(image_id, instance_type, key_name, instance_name, iam_instance_profile):
    """Create an EC2 instance with an IAM role."""
    if not check_instance_exists(instance_name):
        try:
            instance = ec2_resource.create_instances(
                ImageId=image_id,
                InstanceType=instance_type,
                KeyName=key_name,
                MinCount=1,
                MaxCount=1,
                UserData=get_user_data_script(),
                TagSpecifications=[{
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': instance_name}]
                }],
                IamInstanceProfile={'Name': iam_instance_profile}
            )[0]
            logging.info(f"EC2 Instance {instance.id} with name {instance_name} and IAM role {iam_instance_profile} created.")
            return instance.id
        except ClientError as e:
            logging.error(f"Error creating EC2 instance: {e}")
            return None
    else:
        logging.info(f"EC2 instance {instance_name} already exists.")
        return None

def get_user_data_script():
    """Provides the user data script for EC2 initialization."""
    return '''#!/bin/bash
    yum update -y
    yum install -y git unzip python3-pip
    pip3 install boto3
    git clone https://github.com/MeganeFarelle/device-coursework /home/ec2-user/device-coursework
    cd /home/ec2-user/device-coursework
    unzip Images.zip
    python3 device.py /home/ec2-user/device-coursework/Images/
    '''

if __name__ == '__main__':
    logging.info("Starting the AWS configuration process...")
    if create_bucket(BUCKET_NAME):
        instance_id = create_ec2_instance(IMAGE_ID, INSTANCE_TYPE, KEY_NAME, INSTANCE_NAME, IAM_INSTANCE_PROFILE)
        if instance_id:
            logging.info(f"Instance {instance_id} setup complete.")

