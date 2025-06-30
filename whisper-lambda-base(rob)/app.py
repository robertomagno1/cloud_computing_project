import json
import boto3
import logging
from urllib.parse import unquote_plus

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    AWS Lambda handler for Whisper transcription
    """
    try:
        logger.info(f"=== LAMBDA START ===")
        logger.info(f"Request ID: {context.aws_request_id}")
        logger.info(f"Event received: {json.dumps(event)}")
        
        # Initialize S3 client
        s3_client = boto3.client('s3')
        
        # Validate event structure
        if 'Records' not in event:
            logger.error("No Records found in event")
            raise ValueError("Invalid event structure: missing Records")
        
        processed_files = []
        
        # Process each record in the event
        for i, record in enumerate(event['Records']):
            logger.info(f"Processing record {i+1}/{len(event['Records'])}")
            
            try:
                # Extract S3 information
                if 's3' not in record:
                    logger.warning(f"Record {i+1} missing s3 information, skipping")
                    continue
                
                bucket = record['s3']['bucket']['name']
                key = unquote_plus(record['s3']['object']['key'])
                
                logger.info(f"Processing: bucket={bucket}, key={key}")
                
                # Validate it's an audio file
                if not key.startswith('audio/'):
                    logger.info(f"Skipping {key} - not in audio/ prefix")
                    continue
                
                # Create transcript filename
                transcript_key = key.replace('audio/', 'transcripts/').replace('.wav', '.txt')
                
                # Create transcript content
                transcript_content = f"""=== WHISPER TRANSCRIPTION REPORT ===
Source File: {key}
Bucket: {bucket}
Request ID: {context.aws_request_id}
Processed: {context.get_remaining_time_in_millis()}ms remaining
Timestamp: 2025-06-29 19:30:00

=== TRANSCRIPT CONTENT ===
[This is a placeholder transcript]
Audio file successfully received and processed by AWS Lambda.
In a production environment, this would contain the actual 
Whisper AI transcription of the audio content.

=== PROCESSING STATUS ===
Status: SUCCESS
File Size: {record['s3']['object'].get('size', 'Unknown')} bytes
Processing Time: <1 second (placeholder)
Model: Whisper Base (placeholder)

=== END REPORT ===
"""
                
                # Upload transcript to S3
                logger.info(f"Uploading transcript to: {transcript_key}")
                
                s3_client.put_object(
                    Bucket=bucket,
                    Key=transcript_key,
                    Body=transcript_content.encode('utf-8'),
                    ContentType='text/plain',
                    Metadata={
                        'source-file': key,
                        'request-id': context.aws_request_id,
                        'processing-status': 'success'
                    }
                )
                
                processed_files.append({
                    'source': key,
                    'transcript': transcript_key,
                    'status': 'success'
                })
                
                logger.info(f"Successfully created transcript: {transcript_key}")
                
            except Exception as record_error:
                logger.error(f"Error processing record {i+1}: {str(record_error)}")
                processed_files.append({
                    'source': record.get('s3', {}).get('object', {}).get('key', 'unknown'),
                    'transcript': None,
                    'status': 'error',
                    'error': str(record_error)
                })
                # Continue processing other records instead of failing completely
                continue
        
        # Create success response
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Lambda execution completed',
                'request_id': context.aws_request_id,
                'processed_files': len(processed_files),
                'successful_files': len([f for f in processed_files if f['status'] == 'success']),
                'details': processed_files
            }, indent=2)
        }
        
        logger.info(f"=== LAMBDA SUCCESS ===")
        logger.info(f"Response: {json.dumps(response)}")
        
        return response
        
    except Exception as e:
        error_msg = f"Critical Lambda error: {str(e)}"
        logger.error(f"=== LAMBDA ERROR ===")
        logger.error(error_msg)
        logger.error(f"Error type: {type(e).__name__}")
        
        # Return error response instead of raising exception
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': error_msg,
                'request_id': context.aws_request_id,
                'error_type': type(e).__name__
            })
        }

# Test function for local development
if __name__ == "__main__":
    import sys
    
    # Mock event for testing
    test_event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "whisper-audio-base-robertomagno1"},
                    "object": {"key": "audio/test_local.wav", "size": 2621440}
                }
            }
        ]
    }
    
    # Mock context
    class MockContext:
        def __init__(self):
            self.aws_request_id = "test-local-123"
            
        def get_remaining_time_in_millis(self):
            return 890000
    
    # Test the handler
    try:
        result = lambda_handler(test_event, MockContext())
        print(f"✅ Local test SUCCESS:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Local test ERROR: {e}")
        sys.exit(1)
