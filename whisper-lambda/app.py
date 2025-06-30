import whisper
import boto3
import os
import json

s3 = boto3.client('s3')
MODEL_PATH = "/opt/ml/models"
model = whisper.load_model("base", download_root=MODEL_PATH)

def lambda_handler(event, context):
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
    
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
        return {
            "statusCode": 500,
            "body": json.dumps(f"Errore: {str(e)}")
        }

