# pip install boto3 python-dotenv
import os
import json
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv


load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
S3_REGION = os.getenv("AWS_REGION_S3", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "")
DYNAMODB_REGION = os.getenv("AWS_REGION_DYNAMODB", "us-east-2")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE_NAME", "")

def _get_s3_client():
    """Helper function to create an S3 client securely."""
    return boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=S3_REGION
    )

def _get_dynamodb_resource():
    """Helper function to create a DynamoDB resource securely."""
    # We use boto3.resource here as it's often easier to interact with Items
    return boto3.resource(
        'dynamodb',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=DYNAMODB_REGION
    )

def upload_input_to_s3(
    file_bytes: bytes,
    user_id: str,
    chat_id: str,
    query_id: int,
    input_type: str,
    file_extension: str
) -> str:
    """
    Uploads user input (text, audio, or images) to the S3 bucket.
    Folder structure: {user_id}/{chat_id}/chats/{query_id}/input/{filename}
    """
    s3 = _get_s3_client()
    
    # Construct exact S3 Key path as agreed
    if input_type == "images":
        file_name = f"image_1.{file_extension}"
    elif input_type == "audio":
        file_name = f"audio.{file_extension}"
    else:
        file_name = f"query_text.{file_extension}"
        
    object_key = f"{user_id}/{chat_id}/chats/{query_id}/input/{file_name}"
    s3_uri = f"s3://{S3_BUCKET}/{object_key}"
    
    print(f"Uploading file to S3 at: {object_key}")
    try:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=object_key,
            Body=file_bytes
        )
        print(f"  -> Upload successful: {s3_uri}")
        return s3_uri
    except ClientError as e:
        print(f"  -> Error uploading to S3: {e}")
        return ""

def generate_presigned_url(s3_uri: str, expiry_seconds: int = 3600) -> str:
    """
    Generates a pre-signed HTTPS URL for a given S3 URI.
    Allows the model endpoint to securely read the file for 'expiry_seconds'.
    """
    # Parse the s3:// bucket and key from the URI string
    if not s3_uri.startswith(f"s3://{S3_BUCKET}/"):
        print(f"Invalid S3 URI or not matching our bucket: {s3_uri}")
        return ""
        
    object_key = s3_uri.replace(f"s3://{S3_BUCKET}/", "")
    s3 = _get_s3_client()
    
    try:
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': S3_BUCKET,
                'Key': object_key
            },
            ExpiresIn=expiry_seconds
        )
        print(f"Generated presigned URL (expires in {expiry_seconds}s) for {object_key}")
        return url
    except ClientError as e:
        print(f"  -> Error generating presigned URL: {e}")
        return ""

def _sync_query_num(record: dict) -> None:
    """Helper to proactively synchronize the query_num field with the chats dictionary."""
    if "chats" in record and isinstance(record["chats"], dict):
        nums = []
        for k in record["chats"].keys():
            if k.startswith("query_"):
                try:
                    nums.append(int(k.split("_")[1]))
                except ValueError:
                    pass
        if nums:
            record["query_num"] = sorted(nums)

def store_output_to_dynamodb(record: dict) -> None:
    """
    Stores the full LLM output JSON to DynamoDB.
    Expected Keys: user_id (PK), chat_id (SK)
    """
    dynamodb = _get_dynamodb_resource()
    table = dynamodb.Table(DYNAMODB_TABLE)
    
    # Auto-synchronize the query_num list to prevent user errors and mismatches
    _sync_query_num(record)
    
    print(f"Storing record to DynamoDB. PartitionKey={record.get('user_id')}, SortKey={record.get('chat_id')}")
    try:
        # The put_item operation completely replaces any existing item with same PK and SK.
        table.put_item(Item=record)
        print("  -> Record successfully stored to DynamoDB.")
    except ClientError as e:
        print(f"  -> Error storing to DynamoDB: {e}")

import copy

def store_output_log_to_s3(record: dict) -> str:
    """
    Stores LLM output JSON to S3 based on the S3 folder structure:
    {user_id}/{chat_id}/output/chat.json
    Also converts the 'chats' dictionary to a list configuration required by S3 pipeline.
    Returns the resulting S3 URI.
    """
    user_id = record.get("user_id", "unknown_user")
    chat_id = record.get("chat_id", "unknown_chat")

    object_key = f"{user_id}/{chat_id}/output/chat.json"
    s3_uri = f"s3://{S3_BUCKET}/{object_key}"
    
    s3 = _get_s3_client()
    try:
        # Pre-format to ensure consistency before cloning and uploading
        _sync_query_num(record)

        # Deepcopy to avoid mutating the original DynamoDB designed dictionary
        s3_record = copy.deepcopy(record)
        
        # S3 expects the 'chats' field to be an array list instead of dictionary of queries
        if "chats" in s3_record and isinstance(s3_record["chats"], dict):
            s3_record["chats"] = list(s3_record["chats"].values())
            
        # Convert the dictionary to a JSON formatted string and encode to bytes
        json_bytes = json.dumps(s3_record, indent=2).encode('utf-8')
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=object_key,
            Body=json_bytes
        )
        print(f"  -> Output log successfully stored to S3: {s3_uri}")
        return s3_uri
    except ClientError as e:
        print(f"  -> Error storing output log to S3: {e}")
        return ""
