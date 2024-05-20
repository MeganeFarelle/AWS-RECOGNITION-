import boto3
import os
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the S3 client
s3_client = boto3.client('s3')

def create_bucket(bucket_name):
    """
    Creates an S3 bucket with the given name.

    Args:
        bucket_name (str): The name of the S3 bucket to be created.

    Returns:
        str: The name of the created S3 bucket.
    """
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        logger.info(f"S3 bucket {bucket_name} created.")
        return bucket_name
    except s3_client.exceptions.BucketAlreadyExists as e:
        logger.warning(f"S3 bucket {bucket_name} already exists.")
        return bucket_name
    except Exception as e:
        logger.error(f"Error creating S3 bucket: {e}")
        return None

def copy_zip_files_to_bucket(bucket_name, base_dir):
    """
    Copies zip files from the base directory to the specified S3 bucket.

    Args:
        bucket_name (str): The name of the destination S3 bucket.
        base_dir (str): The base directory where the zip files are located.

    Returns:
        bool: True if zip files are successfully copied, False otherwise.
    """
    try:
        zip_files = [
            "process-image-function\process-image-function-s2110849.zip",
            "send-alerte-function\send-alerte-function-s2110849.zip"
        ]
        for zip_file in zip_files:
            local_file_path = os.path.join(base_dir, zip_file)
            s3_key = os.path.basename(zip_file)
            s3_client.upload_file(local_file_path, bucket_name, s3_key)
            logger.info(f"Uploaded {local_file_path} to S3 bucket {bucket_name} with key {s3_key}")
        return True
    except Exception as e:
        logger.error(f"Error copying zip files to S3 bucket: {e}")
        return False

if __name__ == '__main__':
    # Define variables
    bucket_name = "zipstorefunctions-s2110849"
    base_dir = r"C:\Users\User\Downloads\coursework-megane-main\lambda"

    # Create S3 bucket
    created_bucket_name = create_bucket(bucket_name)
    if created_bucket_name:
        # Copy zip files to S3 bucket
        copy_zip_files_to_bucket(created_bucket_name, base_dir)
