# pip install boto3 python-dotenv
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load config from .env file
load_dotenv()


aws_access_key = os.getenv("AWS_ACCESS_KEY_ID", "")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
s3_region = os.getenv("AWS_REGION_S3", "us-east-1")
s3_bucket = os.getenv("S3_BUCKET_NAME", "")
dynamodb_region = os.getenv("AWS_REGION_DYNAMODB", "us-east-2")
dynamodb_table = os.getenv("DYNAMODB_TABLE_NAME", "")

def get_s3_client():
    """Create and return an S3 client in the specified S3 region."""
    return boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=s3_region
    )

def get_dynamodb_client():
    """Create and return a DynamoDB client in the specified DynamoDB region."""
    return boto3.client(
        'dynamodb',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=dynamodb_region
    )

def setup_s3_bucket():
    """Checks if S3 bucket exists, creates it if not, and blocks all public access."""
    if not s3_bucket:
        print("Missing 'S3_BUCKET_NAME' in .env")
        return
        
    print(f"Checking S3 bucket: {s3_bucket} in {s3_region}...")
    s3 = get_s3_client()
    
    try:
        # head_bucket will succeed if bucket exists and we have permissions
        s3.head_bucket(Bucket=s3_bucket)
        print(f"  -> S3 bucket '{s3_bucket}' already exists and is accessible. Skipping creation.")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        # 404 indicates the bucket does not exist. We can safely create it.
        if error_code == '404':
            print(f"  -> S3 bucket does not exist. Creating '{s3_bucket}'...")
            try:
                # us-east-1 does NOT use LocationConstraint
                if s3_region == "us-east-1":
                    s3.create_bucket(Bucket=s3_bucket)
                else:
                    s3.create_bucket(
                        Bucket=s3_bucket,
                        CreateBucketConfiguration={'LocationConstraint': s3_region}
                    )
                print(f"  -> S3 bucket '{s3_bucket}' created successfully.")
                
                # Apply PublicAccessBlock (block ALL public access)
                s3.put_public_access_block(
                    Bucket=s3_bucket,
                    PublicAccessBlockConfiguration={
                        'BlockPublicAcls': True,
                        'IgnorePublicAcls': True,
                        'BlockPublicPolicy': True,
                        'RestrictPublicBuckets': True
                    }
                )
                print("  -> PublicAccessBlock policy applied successfully (all public access blocked).")
            except ClientError as create_error:
                print(f"  -> Error creating S3 bucket or blocking access: {create_error}")
        else:
            print(f"  -> Unexpected error checking S3 bucket: {e}")

def setup_dynamodb_table():
    """Checks if DynamoDB table exists, creates it if not."""
    if not dynamodb_table:
        print("Missing 'DYNAMODB_TABLE_NAME' in .env")
        return
        
    print(f"Checking DynamoDB table: {dynamodb_table} in {dynamodb_region}...")
    dynamodb = get_dynamodb_client()
    
    try:
        dynamodb.describe_table(TableName=dynamodb_table)
        print(f"  -> DynamoDB table '{dynamodb_table}' already exists. Skipping creation.")
    except ClientError as e:
        # ResourceNotFoundException indicates it doesn't exist
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"  -> DynamoDB table does not exist. Creating '{dynamodb_table}'...")
            try:
                dynamodb.create_table(
                    TableName=dynamodb_table,
                    KeySchema=[
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},       # Partition Key
                        {'AttributeName': 'chat_id', 'KeyType': 'RANGE'}       # Sort Key
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'user_id', 'AttributeType': 'S'},
                        {'AttributeName': 'chat_id', 'AttributeType': 'S'}
                    ],
                    BillingMode='PAY_PER_REQUEST' # On-demand billing
                )
                print(f"  -> DynamoDB table '{dynamodb_table}' creation requested. It may take a moment to become completely active.")
            except ClientError as create_error:
                print(f"  -> Error creating DynamoDB table: {create_error}")
        else:
            print(f"  -> Unexpected error checking DynamoDB table: {e}")

if __name__ == "__main__":
    print("=== AWS Resources Setup Start ===")
    setup_s3_bucket()
    setup_dynamodb_table()
    print("=== AWS Resources Setup Complete ===")
