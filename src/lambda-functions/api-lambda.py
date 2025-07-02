import boto3
import json
import uuid
import time

s3 = boto3.client('s3')
ddb = boto3.client('dynamodb')

BUCKET = 'whisper-audio-transcription-bucket'
TABLE = 'TranscriptionJobs'

def lambda_handler(event, context):
    print("[DEBUG] Event:", json.dumps(event))

    # Only handle API Gateway requests
    if 'resource' not in event or 'httpMethod' not in event:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'This function only accepts API Gateway requests'})
        }
    
    resource = event.get('resource', '')
    http_method = event.get('httpMethod', '')
    
    print(f"[DEBUG] API Gateway request - Resource: {resource}, Method: {http_method}")
    
    if resource == '/upload' and http_method == 'POST':
        # Extract body from API Gateway event
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        return handle_upload(body)
    elif '/status/' in resource and http_method == 'GET':
        job_id = event.get('pathParameters', {}).get('jobId')
        return check_status(job_id)
    else:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Not Found'})
        }

def handle_upload(data):
    try:
        print(f"[DEBUG] Upload data: {json.dumps(data)}")
        file_name = data.get('fileName')
        
        if not file_name:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing fileName parameter'})
            }
            
        job_id = str(uuid.uuid4())
        ttl = int(time.time()) + 3600 # 1 hours from now

        print(f"[DEBUG] Creating job {job_id} for file {file_name}")
        
        ddb.put_item(
            TableName=TABLE,
            Item={
                'jobId': {'S': job_id},
                'fileName': {'S': file_name},
                'status': {'S': 'UPLOADING'},
                'ttl': {'N': str(ttl)}
            }
        )

        url = s3.generate_presigned_url('put_object',
            Params={'Bucket': BUCKET, 'Key': f'audio/{file_name}',
            'Tagging': 'jobId={}'.format(job_id)},
            ExpiresIn=3600)

        response_body = {
            'jobId': job_id,
            'uploadUrl': url
        }
        
        print(f"[DEBUG] Successful response: {json.dumps(response_body)}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_body)
        }
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Upload handler error: {error_msg}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': error_msg})
        }

def check_status(job_id):
    if not job_id:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Missing jobId'})
        }
        
    try:
        job = ddb.get_item(TableName=TABLE, Key={'jobId': {'S': job_id}})
        if 'Item' not in job:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Job not found'})
            }

        status = job['Item']['status']['S']
        result = {'status': status}

        if status == 'COMPLETED':
            # Check if the url is already generated in the job item
            if 'downloadUrl' in job['Item']:
                result['downloadUrl'] = job['Item']['downloadUrl']['S']
            else:
                file_name = job['Item']['fileName']['S']
                url = s3.generate_presigned_url('get_object',
                    Params={'Bucket': BUCKET, 'Key': f'transcripts/{file_name}.txt'},
                    ExpiresIn=3600)
        
                # Update the job item with the download URL
                ddb.update_item(
                    TableName=TABLE,
                    Key={'jobId': {'S': job_id}},
                    UpdateExpression='SET downloadUrl = :url',
                    ExpressionAttributeValues={':url': {'S': url}}
                )

                result['downloadUrl'] = url

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
    
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Status check error: {error_msg}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': error_msg})
        }