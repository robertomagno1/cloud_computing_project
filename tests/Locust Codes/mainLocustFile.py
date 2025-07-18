import random
import time
import os
import json
from locust import HttpUser, task, between
import requests
from datetime import datetime


class AudioTranscriptionUser(HttpUser):
    
    def adaptive_wait_time(self):
        """Adaptive wait time based on active jobs"""
        if self.active_jobs:
            # If we have active jobs, check more frequently
            return random.uniform(5, 15)
        else:
            # If no active jobs, simulate user uploading new files less frequently
            return random.uniform(60, 120)  # 1-2 minutes

    def wait_time(self):
        return self.adaptive_wait_time()  # Wait time between tasks

    def on_start(self):
        """Initialize user session"""
        self.api_base = "https://gbnq6sfqml.execute-api.us-east-1.amazonaws.com/dev"
        self.test_files = self.load_test_files()
        self.active_jobs = []

    def load_test_files(self):
        """Load available test files"""
        files = {
            'small': [],
            'medium': [],
            'large': []
        }
        for size in ['small', 'medium', 'large']:
            file_dir = f"/home/ec2-user/performance-testing/test-files/{size}"
            if os.path.exists(file_dir):
                files[size] = [f for f in os.listdir(file_dir) if f.endswith('.mp3')]
        return files

    def log_metric(self, operation, duration, success, file_size=None):
        """Log custom metrics"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'operation': operation,
            'duration': duration,
            'success': success,
            'file_size': file_size,
        }
        with open('/home/ec2-user/performance-testing/logs/metrics.log', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    @task(30)
    def upload_audio_file(self):
        """Upload audio file for transcription"""
        
        size_category = random.choices(
            ['small', 'medium', 'large'], 
            weights=[60, 30, 10]
        )[0]  # Assign different probabilities: small (60%), medium (30%), large (10%)

        if not self.test_files[size_category]:
            return
        filename = random.choice(self.test_files[size_category])
        file_path = f"/home/ec2-user/performance-testing/test-files/{size_category}/{filename}"
        if not os.path.exists(file_path):
            return

        start_time = time.time()
        try:
            with self.client.post(
                "/upload",
                json={"fileName": filename},
                headers={"Content-Type": "application/json"},
                catch_response=True
            ) as response:
                if response.status_code != 200:
                    duration = time.time() - start_time
                    self.log_metric('upload', duration, False, size_category)
                    response.failure(f"Upload request failed: {response.text}")
                    return

                try:
                    data = response.json()
                    job_id = data.get('jobId')
                    upload_url = data.get('uploadUrl')
                    if not job_id or not upload_url:
                        duration = time.time() - start_time
                        self.log_metric('upload', duration, False, size_category)
                        response.failure("Missing jobId or uploadUrl")
                        return
                except Exception as e:
                    duration = time.time() - start_time
                    self.log_metric('upload', duration, False, size_category)
                    response.failure(f"JSON parse error: {str(e)}")
                    return

                # Step 2: Upload file to S3 (outside Locust tracked request)
                try:
                    with open(file_path, 'rb') as f:
                        s3_response = requests.put(upload_url, data=f)
                    if s3_response.status_code != 200:
                        duration = time.time() - start_time
                        self.log_metric('upload', duration, False, size_category)
                        response.failure(f"S3 upload failed: {s3_response.status_code}")
                        return
                except Exception as e:
                    duration = time.time() - start_time
                    self.log_metric('upload', duration, False, size_category)
                    response.failure(f"Exception during S3 upload: {str(e)}")
                    return

                # Track job for status checking
                self.active_jobs.append({
                    'job_id': job_id,
                    'filename': filename,
                    'size_category': size_category,
                    'upload_time': time.time()
                })
                duration = time.time() - start_time
                self.log_metric('upload', duration, True, size_category)
                response.success()
        except Exception as e:
            duration = time.time() - start_time
            self.log_metric('upload', duration, False, size_category)


    @task(70)  
    def automatic_status_check(self):
        """Automatic status check that happens every 30 seconds in the real app"""
        if not self.active_jobs:
            return
        
        current_time = time.time()
        
        # Check jobs that haven't been checked in the last 30 seconds
        for job_info in self.active_jobs[:]:  # Use slice to avoid modification during iteration
            if current_time - job_info.get('last_check', 0) >= 30:
                job_id = job_info['job_id']
                start_time = time.time()
                
                try:
                    with self.client.get(
                        f"/status/{job_id}",
                        catch_response=True
                    ) as response:
                        if response.status_code == 200:
                            data = response.json()
                            status = data.get('status')
                            
                            if status == 'COMPLETED':
                                self.active_jobs.remove(job_info)
                                end_to_end_time = time.time() - job_info['upload_time']
                                self.log_metric('end_to_end', end_to_end_time, True, job_info['size_category'])
                                
                                # Automatically download since app does this
                                download_url = data.get('downloadUrl')
                                if download_url:
                                    self._auto_download(download_url, job_info['size_category'])
                                    
                            elif status == 'FAILED':
                                self.active_jobs.remove(job_info)
                                self.log_metric('end_to_end', time.time() - job_info['upload_time'], False, job_info['size_category'])
                            else:
                                # Update last check time for ongoing jobs
                                job_info['last_check'] = current_time
                                
                            duration = time.time() - start_time
                            self.log_metric('status_check', duration, True)
                            response.success()
                        else:
                            duration = time.time() - start_time
                            self.log_metric('status_check', duration, False)
                            response.failure(f"Status check failed: {response.status_code}")
                            
                except Exception as e:
                    duration = time.time() - start_time
                    self.log_metric('status_check', duration, False)

    def _auto_download(self, download_url, size_category):
        """Automatic download when transcription is completed"""
        start_time = time.time()
        try:
            response = requests.get(download_url)
            duration = time.time() - start_time
            if response.status_code == 200:
                self.log_metric('download', duration, True, size_category)
            else:
                self.log_metric('download', duration, False, size_category)
        except Exception as e:
            duration = time.time() - start_time
            self.log_metric('download', duration, False, size_category)
