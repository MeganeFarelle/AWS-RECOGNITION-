import boto3
import json
import logging
from botocore.exceptions import ClientError

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize the AWS SNS client
sns_client = boto3.client('sns')

# Specify the ARN of your SNS topic
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:211125692741:sendMailTopic'

def check_vehicle_status(detected_texts, table):
    results = []
    for vehicle_id in detected_texts:
        try:
            response = table.get_item(Key={'VehicleID': vehicle_id})
            if 'Item' in response:
                vehicle_status = response['Item'].get('Status')
                if vehicle_status == 'blacklisted':
                    results.append({'vehicle_id': vehicle_id, 'status': 'blacklisted'})
                else:
                    results.append({'vehicle_id': vehicle_id, 'status': 'whitelisted'})
            else:
                results.append({'vehicle_id': vehicle_id, 'status': 'not found'})
        except Exception as e:
            results.append({'vehicle_id': vehicle_id, 'status': 'error', 'error_message': str(e)})
    return results

def send_email(topic_arn, subject, message):
    # Construct the message to be sent via SNS
    email_message = f"Subject: {subject}\n\n{message}"
    try:
        # Publish the message to the SNS topic
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=email_message
        )
    except ClientError as e:
        logger.error(f"An error occurred: {e.response['Error']['Message']}")
    else:
        logger.info(f"Email sent! Message ID: {response['MessageId']}")

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table_name = 'VehicleTable-s2110849'
    table = dynamodb.Table(table_name)

    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_image = record['dynamodb']['NewImage']
            image_name = new_image['ImageName']['S']
            detected_texts = json.loads(new_image['DetectedTexts']['S'])
            detected_labels = json.loads(new_image['DetectedLabels']['S'])

            results = check_vehicle_status(detected_texts, table)
            blacklisted = any(result['status'] == 'blacklisted' for result in results)
            blacklisted_vehicles = [result['vehicle_id'] for result in results if result['status'] == 'blacklisted']
            not_found_vehicles = [result['vehicle_id'] for result in results if result['status'] == 'not found']
            
            if blacklisted:
                email_subject = 'Security Alert: Action Required'
                email_body = (
                    f"A blacklisted vehicle has been detected in the image: {image_name}\n"
                    f"Blacklisted vehicles: {', '.join(blacklisted_vehicles)}"
                    f"\n\nDetected labels: {', '.join(label['Name'] for label in detected_labels)}"
                    f"\nDetected texts: {', '.join(detected_texts)}"
                    f"\n\nPlease take the necessary action."
                    f"\n\nThis is an automated message."
                    f"\n\nThank you."
                    f"\nSecurity Team"
                )
                send_email(SNS_TOPIC_ARN, email_subject, email_body)
                logger.info(f"Alert sent for image: {image_name}")
            elif not_found_vehicles:
                email_subject = 'Vehicle Not Found: Action Required'
                email_body = (
                    f"A vehicle detected in the image: {image_name} is not found in the record.\n"
                    f"Detected vehicles: {', '.join(not_found_vehicles)}"
                    f"\n\nDetected labels: {', '.join(label['Name'] for label in detected_labels)}"
                    f"\nDetected texts: {', '.join(detected_texts)}"
                    f"\n\nPlease take the necessary action to investigate."
                    f"\n\nThis is an automated message."
                    f"\n\nThank you."
                    f"\nSecurity Team"
                )
                send_email(SNS_TOPIC_ARN, email_subject, email_body)
                logger.info(f"Alert sent for vehicle not found in record: {image_name}")
            else:
                logger.info(f"No action required for image: {image_name}")
    
    return {'statusCode': 200, 'body': json.dumps('Email notification processing completed successfully.')}
