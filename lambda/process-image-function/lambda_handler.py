import boto3
import json

s3_client = boto3.client('s3')
rekognition_client = boto3.client('rekognition')
dynamodb_client = boto3.client('dynamodb')

DYNAMODB_TABLE_NAME = 'EntryTable-s2110849'

def lambda_handler(event, context):
    for record in event.get('Records', []):
        try:
            record_body = json.loads(record['body'])
            s3_records = record_body.get('Records', [])

            # Check if there are any S3 records; continue only if non-empty
            if not s3_records:
                print("No S3 records found in the event.")
                continue  # Skip to the next record in the event

            s3_record = s3_records[0].get('s3', {})
            bucket_name = s3_record.get('bucket', {}).get('name', 'Unknown Bucket')
            object_key = s3_record.get('object', {}).get('key', 'Unknown Key')

            # Log the received S3 object information
            print(f"Received event for S3 bucket: {bucket_name}, object: {object_key}")
            
            # Call Rekognition to detect labels and text in the image
            label_response = rekognition_client.detect_labels(
                Image={'S3Object': {'Bucket': bucket_name, 'Name': object_key}},
                MaxLabels=10,
                MinConfidence=70
            )
            
            text_response = rekognition_client.detect_text(
                Image={'S3Object': {'Bucket': bucket_name, 'Name': object_key}}
            )
            
            # Extract the relevant data from the Rekognition response
            detected_labels = [{'Name': label['Name'], 'Confidence': label['Confidence']} for label in label_response['Labels']]
            detected_texts = [text['DetectedText'] for text in text_response['TextDetections'] if text['Type'] == 'LINE']
            
            # Store the detected labels and texts in DynamoDB
            dynamodb_client.put_item(
                TableName=DYNAMODB_TABLE_NAME,
                Item={
                    'ImageName': {'S': object_key},
                    'DetectedLabels': {'S': json.dumps(detected_labels)},
                    'DetectedTexts': {'S': json.dumps(detected_texts)}
                }
            )
            #print detected labels and texts
            print(f"Detected labels: {detected_labels}")
            print(f"Detected texts: {detected_texts}")
            
            # Log the stored data confirmation
            print(f"Stored detected labels and texts for image {object_key} in DynamoDB.")
        except Exception as e:
            # Log any exceptions that occur during processing
            print(f"Error processing record: {e}")

    # Return a success response
    return {'statusCode': 200, 'body': json.dumps('Processing completed successfully.')}
