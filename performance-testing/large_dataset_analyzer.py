#!/usr/bin/env python3
import boto3
import json
import statistics
from datetime import datetime, timedelta
import time

class LargeDatasetAnalyzer:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.cloudwatch = boto3.client('cloudwatch')
        self.bucket = 'whisper-audio-base-robertomagno1'
        
    def analyze_complete_dataset(self):
        print("🔍 LARGE DATASET PERFORMANCE ANALYSIS")
        print("=" * 60)
        print(f"👤 Student: robertomagno1")
        print(f"📅 Analysis: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        try:
            # Get all objects
            audio_objects = self._get_all_objects('audio/')
            transcript_objects = self._get_all_objects('transcripts/')
            
            print(f"\n📊 DATASET OVERVIEW:")
            print(f"Total audio files: {len(audio_objects):,}")
            print(f"Total transcripts: {len(transcript_objects):,}")
            
            if len(audio_objects) > 0:
                success_rate = len(transcript_objects) / len(audio_objects) * 100
                print(f"Success rate: {success_rate:.2f}%")
            
            # Size analysis
            self._analyze_file_sizes(audio_objects, transcript_objects)
            
            # Performance analysis
            self._analyze_performance(transcript_objects)
            
            # Cost analysis
            self._analyze_costs(audio_objects, transcript_objects)
            
            return {
                'audio_files': len(audio_objects),
                'transcript_files': len(transcript_objects),
                'success_rate': success_rate if len(audio_objects) > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ Analysis error: {str(e)}")
            return None
    
    def _get_all_objects(self, prefix):
        objects = []
        paginator = self.s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.bucket, Prefix=prefix)
        
        for page in pages:
            if 'Contents' in page:
                objects.extend(page['Contents'])
        
        return objects
    
    def _analyze_file_sizes(self, audio_objects, transcript_objects):
        print(f"\n📊 FILE SIZE ANALYSIS:")
        
        if audio_objects:
            audio_sizes = [obj['Size'] for obj in audio_objects]
            total_audio_mb = sum(audio_sizes) / (1024 * 1024)
            avg_audio_mb = statistics.mean(audio_sizes) / (1024 * 1024)
            
            print(f"Audio files:")
            print(f"  - Total size: {total_audio_mb:.2f} MB")
            print(f"  - Average size: {avg_audio_mb:.2f} MB")
            print(f"  - Size range: {min(audio_sizes):,} - {max(audio_sizes):,} bytes")
        
        if transcript_objects:
            transcript_sizes = [obj['Size'] for obj in transcript_objects]
            total_transcript_kb = sum(transcript_sizes) / 1024
            avg_transcript_bytes = statistics.mean(transcript_sizes)
            
            print(f"Transcript files:")
            print(f"  - Total size: {total_transcript_kb:.2f} KB")
            print(f"  - Average size: {avg_transcript_bytes:.0f} bytes")
            print(f"  - Size range: {min(transcript_sizes):,} - {max(transcript_sizes):,} bytes")
            
            if audio_objects and transcript_objects:
                compression = sum(transcript_sizes) / sum([obj['Size'] for obj in audio_objects])
                print(f"  - Compression ratio: {compression:.6f}")
                print(f"  - Space efficiency: {(1-compression)*100:.2f}% space saved")
    
    def _analyze_performance(self, transcript_objects):
        print(f"\n⚡ PERFORMANCE ANALYSIS:")
        
        if not transcript_objects:
            print("No transcript data for performance analysis")
            return
        
        # Analyze temporal patterns
        recent_1h = [obj for obj in transcript_objects 
                    if obj['LastModified'] > datetime.now(obj['LastModified'].tzinfo) - timedelta(hours=1)]
        recent_6h = [obj for obj in transcript_objects 
                    if obj['LastModified'] > datetime.now(obj['LastModified'].tzinfo) - timedelta(hours=6)]
        
        print(f"Processing rate:")
        print(f"  - Last 1 hour: {len(recent_1h)} files ({len(recent_1h):.1f} files/hour)")
        print(f"  - Last 6 hours: {len(recent_6h)} files ({len(recent_6h)/6:.1f} files/hour)")
        
        # Estimate completion time
        if len(recent_1h) > 0:
            estimated_rate = len(recent_1h)  # files per hour
            remaining_estimate = 1600 - len(transcript_objects)  # assuming 1600 total target
            if estimated_rate > 0:
                hours_remaining = remaining_estimate / estimated_rate
                print(f"  - Estimated completion: {hours_remaining:.1f} hours")
    
    def _analyze_costs(self, audio_objects, transcript_objects):
        print(f"\n💰 COST ANALYSIS:")
        
        # Lambda invocation costs (approximate)
        lambda_invocations = len(transcript_objects)
        lambda_cost = lambda_invocations * 0.000002  # $0.000002 per invocation
        
        # S3 storage costs (approximate)
        total_audio_gb = sum([obj['Size'] for obj in audio_objects]) / (1024**3) if audio_objects else 0
        total_transcript_gb = sum([obj['Size'] for obj in transcript_objects]) / (1024**3) if transcript_objects else 0
        s3_cost = (total_audio_gb + total_transcript_gb) * 0.023  # $0.023 per GB/month
        
        print(f"Lambda processing: ${lambda_cost:.6f} ({lambda_invocations:,} invocations)")
        print(f"S3 storage: ${s3_cost:.6f}/month ({total_audio_gb + total_transcript_gb:.3f} GB)")
        print(f"Total estimated cost: ${lambda_cost + s3_cost:.6f}")
        print(f"Cost per file: ${(lambda_cost + s3_cost)/max(len(transcript_objects), 1):.8f}")

if __name__ == "__main__":
    analyzer = LargeDatasetAnalyzer()
    results = analyzer.analyze_complete_dataset()
    
    if results:
        print(f"\n✅ ANALYSIS COMPLETED!")
        print(f"📊 Dataset processed: {results['audio_files']:,} → {results['transcript_files']:,}")
        print(f"🎯 Success rate: {results['success_rate']:.2f}%")
