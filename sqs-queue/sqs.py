import boto3
import json
import os

# Initialize the SQS client
sqs_client = boto3.client('sqs', region_name='us-east-1')

def set_queue_policy(queue_url, policy_file):
    """
    Sets the policy of an SQS queue.

    Args:
        queue_url (str): The URL of the SQS queue.
        policy_file (str): The path to the JSON file containing the policy.

    Returns:
        bool: True if the policy is successfully set, False otherwise.
    """
    try:
        # Check if policy file exists
        if not os.path.exists(policy_file):
            print(f"Policy file '{policy_file}' not found.")
            return False

        # Load policy from JSON file
        with open(policy_file, 'r') as f:
            policy_data = f.read()

        # Check if policy data is empty
        if not policy_data:
            print(f"Policy file '{policy_file}' is empty.")
            return False

        # Parse policy data as JSON
        policy = json.loads(policy_data)

        # Check if 'Policy' key exists in the loaded JSON
        if 'Policy' not in policy:
            print(f"Policy key not found in '{policy_file}'.")
            return False

        # Set the queue policy
        response = sqs_client.set_queue_attributes(
            QueueUrl=queue_url,
            Attributes={'Policy': policy['Policy']}
        )
        print("Queue policy set successfully.")
        return True
    except Exception as e:
        print(f"Error setting queue policy: {e}")
        return False

if __name__ == '__main__':
    # Define variables
    account_id = boto3.client('sts').get_caller_identity()['Account']
    queue_name = "queue-s2110849"
    region = "us-east-1"
    base_dir = r"C:\Users\User\Downloads\coursework-megane-main\sqs-queue"
    queue_url = f"https://sqs.{region}.amazonaws.com/{account_id}/{queue_name}"
    policy_file = os.path.join(base_dir, "sqs-policy.json")

    # Set the queue policy
    set_queue_policy(queue_url, policy_file)
