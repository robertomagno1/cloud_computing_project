import whisper
import boto3
import os
import json

s3 = boto3.client('s3')
ddb = boto3.client('dynamodb')

TABLE = 'TranscriptionJobs'


# Carica il modello dalla directory pre-configurata nell'immagine
MODEL_PATH = "/opt/ml/models"
model = whisper.load_model("base", download_root=MODEL_PATH)

def update_status(job_id, status):
    ddb.update_item(
        TableName=TABLE,
        Key={'jobId': {'S': job_id}},
        UpdateExpression='SET #s = :val',
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={':val': {'S': status}}
    )
        
def lambda_handler(event, context):
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        # Prendi i tag dell’oggetto
        tagging = s3.get_object_tagging(Bucket=bucket, Key=key)
        tags = {tag['Key']: tag['Value'] for tag in tagging['TagSet']}

        job_id = tags.get('jobId')
        if not job_id:
            raise Exception("jobId tag mancante")

        update_status(job_id, 'PROCESSING')

        filename = os.path.basename(key)
        local_path = f"/tmp/{filename}"
        s3.download_file(bucket, key, local_path)

        result = model.transcribe(local_path, fp16=False)
        text = result['text']

        output_key = f"transcripts/{filename}.txt"
        s3.put_object(
            Body=text.encode('utf-8'),
            Bucket=bucket,
            Key=output_key,
            ContentType='text/plain'
        )

        update_status(job_id, 'COMPLETED')

        if os.path.exists(local_path):
            os.remove(local_path)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Transcription finished successfully",
                "output_file": output_key,
                "text_preview": text[:200] + "..." if len(text) > 200 else text
            })
        }
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        if 'job_id' in locals():
            update_status(job_id, 'FAILED')
        return {
            "statusCode": 500,
            "body": json.dumps(f"Errore: {str(e)}")
        }
