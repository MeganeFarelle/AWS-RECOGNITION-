import boto3

# Initialize the SNS client
sns_client = boto3.client('sns', region_name='us-east-1')

def create_topic(topic_name):
    """
    Creates an SNS topic with the given name.

    Args:
        topic_name (str): The name of the SNS topic to be created.
        
    Returns:
        str: The ARN of the created SNS topic.
    """
    try:
        response = sns_client.create_topic(Name=topic_name)
        topic_arn = response['TopicArn']
        print(f"SNS topic {topic_name} created with ARN: {topic_arn}")
        return topic_arn
    except Exception as e:
        print(f"Error creating SNS topic: {e}")
        return None

def subscribe_email_to_topic(topic_arn, email_address):
    """
    Subscribes an email address to the given SNS topic.

    Args:
        topic_arn (str): The ARN of the SNS topic.
        email_address (str): The email address to be subscribed.

    Returns:
        bool: True if the subscription is successful, False otherwise.
    """
    try:
        response = sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email_address
        )
        subscription_arn = response['SubscriptionArn']
        print(f"Subscribed {email_address} to topic {topic_arn} with subscription ARN: {subscription_arn}")
        return True
    except Exception as e:
        print(f"Error subscribing {email_address} to topic {topic_arn}: {e}")
        return False

def send_email_message(topic_arn, message):
    """
    Sends an email message to the subscribers of the given SNS topic.

    Args:
        topic_arn (str): The ARN of the SNS topic.
        message (str): The message to be sent.

    Returns:
        bool: True if the message is successfully published, False otherwise.
    """
    try:
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=message
        )
        print("Message sent successfully.")
        return True
    except Exception as e:
        print(f"Error sending message to topic {topic_arn}: {e}")
        return False

if __name__ == '__main__':
    # Define variables
    topic_name = 'sendMailTopic'
    email_address = 'm.demgne@alustudent.com'
    message = 'Test message from Amazon SNS via Boto3'

    # Create SNS topic
    topic_arn = create_topic(topic_name)
    if topic_arn:
        # Subscribe email address to topic
        if subscribe_email_to_topic(topic_arn, email_address):
            # Send email message
            send_email_message(topic_arn, message)
