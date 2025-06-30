#!/usr/bin/env python3
"""
Quick Performance Summary
Student: Roberto Magno
"""

import os
import json
import boto3
from datetime import datetime

def quick_analysis():
    print("🎯 QUICK PERFORMANCE SUMMARY")
    print("👤 Student: Roberto Magno")
    print("📅 Time:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 40)
    
    # Quick S3 check
    try:
        s3 = boto3.client('s3')
        bucket = "whisper-audio-base-robertomagno1"
        
        audio_resp = s3.list_objects_v2(Bucket=bucket, Prefix='audio/')
        transcript_resp = s3.list_objects_v2(Bucket=bucket, Prefix='transcripts/')
        
        audio_count = len(audio_resp.get('Contents', []))
        transcript_files = transcript_resp.get('Contents', [])
        transcript_count = len(transcript_files)
        
        empty_count = sum(1 for t in transcript_files if t['Size'] == 0)
        valid_count = transcript_count - empty_count
        
        success_rate = (valid_count / transcript_count * 100) if transcript_count > 0 else 0
        
        print(f"📁 S3 Status:")
        print(f"  Audio files: {audio_count}")
        print(f"  Transcript files: {transcript_count}")
        print(f"  Valid transcripts: {valid_count}")
        print(f"  Empty transcripts: {empty_count}")
        print(f"  Success rate: {success_rate:.1f}%")
        
    except Exception as e:
        print(f"❌ S3 Error: {e}")
    
    # Check results directory
    results_dir = "../results"
    if os.path.exists(results_dir):
        analysis_files = [f for f in os.listdir(results_dir) if f.endswith('_analysis.json')]
        print(f"\n📊 Analysis Results: {len(analysis_files)} tests completed")
        
        for file_name in sorted(analysis_files)[-3:]:  # Last 3 tests
            try:
                with open(os.path.join(results_dir, file_name), 'r') as f:
                    data = json.load(f)
                
                test_name = data['test_metadata']['test_name']
                summary = data['performance_summary']
                
                print(f"\n  🔍 {test_name}:")
                print(f"    Invocations: {summary['lambda_performance']['total_invocations']:.0f}")
                print(f"    Error Rate: {summary['lambda_performance']['error_rate_percent']:.1f}%")
                print(f"    S3 Success: {summary['s3_performance']['success_rate_percent']:.1f}%")
                
            except Exception as e:
                print(f"    ❌ Error reading {file_name}: {e}")
    else:
        print("\n📊 No analysis results found yet")
    
    print("\n🔧 Ready for testing!")

if __name__ == "__main__":
    quick_analysis()
