import requests
import json
import time
import os
import sys
from datetime import datetime

# ===== CONFIGURATION =====
API_BASE = 'https://op9f1otmg0.execute-api.us-east-1.amazonaws.com/dev'
AUDIO_FILE = 'audio_sample.wav'  # Change with the path to your file
MAX_RETRIES = 30
POLLING_DELAY = 30  # seconds

def log(message):
    """Print log messages with timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {message}")

def upload_file():
    """Start a transcription job and get a presigned upload URL"""
    if not os.path.exists(AUDIO_FILE):
        log(f"ERROR: Audio file not found: {AUDIO_FILE}")
        return None, None
        
    file_name = os.path.basename(AUDIO_FILE)
    
    url = f'{API_BASE}/upload'
    payload = {'fileName': file_name}
    headers = {'Content-Type': 'application/json'}
    
    log(f"SENDING REQUEST: POST {url}")
    log(f"Payload: {json.dumps(payload)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        log(f"Response code: {response.status_code}")
        
        if response.status_code != 200:
            log(f"Error: Invalid response ({response.status_code}): {response.text}")
            return None, None
        
        try:
            response_data = response.json()
            log(f"Response: {json.dumps(response_data)}")
            
            job_id = response_data.get('jobId')
            upload_url = response_data.get('uploadUrl')
            
            if not job_id or not upload_url:
                log("Error: Missing jobId or uploadUrl in response")
                return None, None
                
            log(f"Job created: {job_id}")
            return job_id, upload_url
            
        except json.JSONDecodeError as e:
            log(f"JSON parsing error: {str(e)}")
            log(f"Raw response: {response.text}")
            return None, None
            
    except requests.RequestException as e:
        log(f"Network error: {str(e)}")
        return None, None

def put_audio_file(upload_url):
    """Upload audio file to S3 using presigned URL"""
    log(f"UPLOADING FILE TO S3")
    log(f"URL: {upload_url}")
    
    try:
        # IMPORTANT: No Content-Type header for presigned S3 URLs
        with open(AUDIO_FILE, 'rb') as f:
            response = requests.put(upload_url, data=f)
        
        log(f"S3 response code: {response.status_code}")
        
        if response.status_code != 200:
            log(f"Upload error: {response.text}")
            return False
        
        log("File successfully uploaded to S3")
        return True
    except Exception as e:
        log(f"Exception during upload: {str(e)}")
        return False

def poll_status(job_id):
    """Check job status until completed or timed out"""
    url = f'{API_BASE}/status/{job_id}'
    log(f"STARTING POLLING: {url}")
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log(f"Attempt {attempt}/{MAX_RETRIES}")
            response = requests.get(url)
            
            log(f"Response code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                status = response_data.get('status')
                
                log(f"Job status: {status}")
                
                if status == 'COMPLETED':
                    download_url = response_data.get('downloadUrl')
                    log(f"TRANSCRIPTION COMPLETED!")
                    log(f"Download URL: {download_url}")
                    
                    if download_url:
                        download_transcription(download_url)
                    
                    return True
                elif status == 'FAILED':
                    log(f"TRANSCRIPTION FAILED: {response_data.get('error', 'Unknown error')}")
                    return False
                else:
                    log(f"Transcription in progress (status: {status})")
            elif response.status_code == 404:
                log("Job not found")
                return False
            else:
                log(f"Request error: {response.status_code} - {response.text}")
                
            if attempt < MAX_RETRIES:
                log(f"Waiting {POLLING_DELAY} seconds...")
                time.sleep(POLLING_DELAY)
            
        except Exception as e:
            log(f"Polling error: {str(e)}")
            if attempt < MAX_RETRIES:
                time.sleep(POLLING_DELAY)
    
    log(f"TIMEOUT: No result after {MAX_RETRIES} attempts")
    return False

def download_transcription(download_url):
    """Download and display the transcription file"""
    log("DOWNLOADING TRANSCRIPTION")
    
    try:
        response = requests.get(download_url)
        
        if response.status_code == 200:
            os.makedirs('downloads', exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = os.path.join('downloads', f'transcription_{timestamp}.txt')
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            log(f"Transcription saved to: {file_path}")
            
            text = response.text.strip()
            log("\n" + "=" * 50)
            log("TRANSCRIPTION CONTENT:")
            log("-" * 50)
            print(text)
            log("=" * 50)
            
            return True
        else:
            log(f"Download error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        log(f"Exception during download: {str(e)}")
        return False

def run_transcription():
    """Main function to run the full transcription process"""
    log("=" * 70)
    log("STARTING AUDIO TRANSCRIPTION PROCESS")
    log("=" * 70)
    
    log("\nSTEP 1: Creating transcription job...")
    job_id, upload_url = upload_file()
    
    if not job_id or not upload_url:
        log("Unable to create job. Exiting.")
        return
    
    log("\nSTEP 2: Uploading audio file...")
    if not put_audio_file(upload_url):
        log("File upload failed. Exiting.")
        return
    
    log("\nSTEP 3: Waiting for transcription processing...")
    success = poll_status(job_id)
    
    log("\n" + "=" * 70)
    if success:
        log("TRANSCRIPTION COMPLETED SUCCESSFULLY!")
    else:
        log("TRANSCRIPTION PROCESS FAILED")
    log("=" * 70)

def check_specific_job_status():
    """Check the status of a specific job"""
    job_id = input("Enter the job ID to check: ").strip()
    if job_id:
        log(f"Checking job status: {job_id}")
        poll_status(job_id)
    else:
        log("Invalid job ID")

if __name__ == '__main__':
    # Main menu
    print("\nWHISPER TRANSCRIPTION CLIENT")
    print("-----------------------------")
    print("1. Start a new transcription")
    print("2. Check status of an existing job")
    print("3. Exit")
    
    choice = input("\nChoose an option (1-3): ").strip()
    
    if choice == '1':
        if not os.path.exists(AUDIO_FILE):
            print(f"\nERROR: Audio file not found: {AUDIO_FILE}")
            print("Edit the AUDIO_FILE variable in the code with the correct path to your audio file.")
            sys.exit(1)
        
        run_transcription()
    elif choice == '2':
        check_specific_job_status()
    else:
        print("Exiting.")
