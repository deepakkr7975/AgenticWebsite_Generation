# pip install boto3 python-dotenv
import os
import json
from storage_handler import (
    upload_input_to_s3,
    generate_presigned_url,
    store_output_to_dynamodb,
    store_output_log_to_s3
)

def run_tests():
    print("=== Starting Storage Tests ===")
    
    # Beginner Note: We use dummy data starting with "test_user_DO_NOT_USE"
    # so anyone checking the bucket/database knows it's safe to clear out.
    test_user_id = "user123"
    test_chat_timestamp = "chat_001_2026-03-30"
    test_chat_id = "chat_001"
    test_query_id = 1
    
    print("\n--- Test 1: Upload dummy text file to S3 ---")
    mock_text_bytes = b"Hello, this is a test from the new med-bot student."
    text_s3_uri = upload_input_to_s3(
        file_bytes=mock_text_bytes,
        user_id=test_user_id,
        chat_id=test_chat_id,
        query_id=1,
        input_type="text",
        file_extension="txt"
    )
    
    print("\n--- Test 2: Generate presigned URL for text file ---")
    if text_s3_uri:
        presigned_text_url = generate_presigned_url(text_s3_uri, expiry_seconds=600)
    else:
        print("Skipping presigned URL test due to missing S3 URI.")
        

    print("\n--- Test 3: Upload dummy audio file to S3 ---")
    mock_audio_bytes = b"RIFFfake_audio_bytes_wav_format"
    audio_s3_uri = upload_input_to_s3(
        file_bytes=mock_audio_bytes,
        user_id=test_user_id,
        chat_id=test_chat_id,
        query_id=1,
        input_type="audio",
        file_extension="wav"
    )

    print("\n--- Test 4: Store dummy dictionary output to DynamoDB ---")
    # This precisely matches the object shape organization requested (V2 Format)
    dummy_record = {
      "user_id": test_user_id,
      "chat_id": test_chat_id,
      "query_num": [1],
      "language": "hinglish",
      "chats": {
        "query_1": {
          "input": {
            "query_text": "mere chest me dard hai, test mode",
            "audio": audio_s3_uri,
            "image": [
                f"s3://healthbot-input-storage/{test_user_id}/{test_chat_id}/chats/1/input/image_1.jpg"
            ]
          },
          "output": {
            "text": "consult immediately"
          }
        }
      },
      "severity": "high",
      "doctor_specialist": "cardiologist",
      "recommended_action": "consult immediately",
      "timestamp": "2026-03-30T10:20:00Z"
    }
    
    store_output_to_dynamodb(dummy_record)
    
    print("\n--- Test 5: Store output log to S3 ---")
    log_s3_uri = store_output_log_to_s3(dummy_record)
    
    print("\n=== All Tests Finished ===")

if __name__ == "__main__":
    run_tests()







