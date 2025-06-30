#!/usr/bin/env python3
"""
Whisper Lambda Performance Analysis
Student: Roberto Magno
Date: 2025-06-29
"""

import boto3
import json
import os
from datetime import datetime, timedelta
import logging

class WhisperPerformanceAnalyzer:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        self.logs = boto3.client('logs')
        self.s3 = boto3.client('s3')
        self.function_name = "whisperBaseTranscriber"
        self.bucket_name = "whisper-audio-base-robertomagno1"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def analyze_performance(self, test_name, duration_minutes=30):
        """Main analysis function"""
        print(f"🔍 Performance Analysis: {test_name}")
        print(f"👤 Student: Roberto Magno")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ Analysis Period: {duration_minutes} minutes")
        
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=duration_minutes)
        
        print(f"🕐 Time Range: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
        
        # Create results directory
        os.makedirs("../results", exist_ok=True)
        
        # Collect all metrics
        results = {
            'test_metadata': {
                'test_name': test_name,
                'student_name': 'Roberto Magno',
                'timestamp': datetime.now().isoformat(),
                'analysis_period_minutes': duration_minutes,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            },
            'lambda_metrics': self.get_lambda_metrics(start_time, end_time),
            's3_analysis': self.analyze_s3_bucket(),
            'error_analysis': self.analyze_error_patterns(start_time, end_time),
            'performance_summary': {}
        }
        
        # Calculate performance metrics
        results['performance_summary'] = self.calculate_performance_metrics(results)
        
        # Save results
        output_file = f"../results/{test_name}_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Generate report
        self.generate_markdown_report(results)
        
        # Print summary
        self.print_summary(results['performance_summary'])
        
        return results
    
    def get_lambda_metrics(self, start_time, end_time):
        """Collect Lambda CloudWatch metrics"""
        print("📊 Collecting Lambda metrics...")
        
        metrics = {}
        metric_names = ['Duration', 'Invocations', 'Errors', 'Throttles', 'ConcurrentExecutions']
        
        for metric_name in metric_names:
            try:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/Lambda',
                    MetricName=metric_name,
                    Dimensions=[{'Name': 'FunctionName', 'Value': self.function_name}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=300,  # 5 minute intervals
                    Statistics=['Sum', 'Average', 'Maximum', 'Minimum']
                )
                
                datapoints = response['Datapoints']
                metrics[metric_name] = {
                    'datapoints': datapoints,
                    'count': len(datapoints),
                    'total_sum': sum([dp.get('Sum', 0) for dp in datapoints]),
                    'avg_value': sum([dp.get('Average', 0) for dp in datapoints]) / len(datapoints) if datapoints else 0
                }
                
                print(f"  ✅ {metric_name}: {len(datapoints)} datapoints")
                
            except Exception as e:
                print(f"  ❌ Error collecting {metric_name}: {e}")
                metrics[metric_name] = {'error': str(e), 'datapoints': [], 'count': 0, 'total_sum': 0, 'avg_value': 0}
        
        return metrics
    
    def analyze_s3_bucket(self):
        """Analyze S3 bucket content and file sizes"""
        print("📁 Analyzing S3 bucket...")
        
        try:
            # Get audio files
            audio_response = self.s3.list_objects_v2(
                Bucket=self.bucket_name, 
                Prefix='audio/'
            )
            
            # Get transcript files
            transcript_response = self.s3.list_objects_v2(
                Bucket=self.bucket_name, 
                Prefix='transcripts/'
            )
            
            audio_files = audio_response.get('Contents', [])
            transcript_files = transcript_response.get('Contents', [])
            
            # Analyze transcript files
            empty_transcripts = 0
            valid_transcripts = 0
            total_transcript_size = 0
            
            transcript_details = []
            
            for transcript in transcript_files:
                size = transcript['Size']
                if size == 0:
                    empty_transcripts += 1
                else:
                    valid_transcripts += 1
                    total_transcript_size += size
                
                transcript_details.append({
                    'key': transcript['Key'],
                    'size': size,
                    'last_modified': transcript['LastModified'],
                    'is_empty': size == 0
                })
            
            # Calculate success rates
            total_transcripts = len(transcript_files)
            success_rate = (valid_transcripts / total_transcripts * 100) if total_transcripts > 0 else 0
            failure_rate = (empty_transcripts / total_transcripts * 100) if total_transcripts > 0 else 0
            
            analysis = {
                'audio_files': {
                    'count': len(audio_files),
                    'files': [{'key': f['Key'], 'size': f['Size'], 'last_modified': f['LastModified']} for f in audio_files[-10:]]  # Last 10 files
                },
                'transcript_files': {
                    'total_count': total_transcripts,
                    'empty_count': empty_transcripts,
                    'valid_count': valid_transcripts,
                    'total_size_bytes': total_transcript_size,
                    'avg_size_bytes': total_transcript_size / valid_transcripts if valid_transcripts > 0 else 0
                },
                'success_metrics': {
                    'success_rate_percent': success_rate,
                    'failure_rate_percent': failure_rate,
                    'processing_efficiency': valid_transcripts / len(audio_files) * 100 if audio_files else 0
                },
                'file_details': transcript_details[-10:]  # Last 10 transcript files
            }
            
            print(f"  📁 Audio files: {len(audio_files)}")
            print(f"  📄 Transcript files: {total_transcripts}")
            print(f"  ✅ Valid transcripts: {valid_transcripts}")
            print(f"  ❌ Empty transcripts: {empty_transcripts}")
            print(f"  🎯 Success rate: {success_rate:.1f}%")
            
            return analysis
            
        except Exception as e:
            print(f"  ❌ Error analyzing S3: {e}")
            return {'error': str(e)}
    
    def analyze_error_patterns(self, start_time, end_time):
        """Analyze Lambda error logs"""
        print("🔍 Analyzing error patterns...")
        
        try:
            log_group = f"/aws/lambda/{self.function_name}"
            
            # Define error patterns to look for
            error_patterns = {
                'Runtime.InvalidEntrypoint': 0,
                'exec format error': 0,
                'timeout': 0,
                'memory exceeded': 0,
                'permission denied': 0,
                'container startup': 0,
                'other_errors': 0
            }
            
            recent_errors = []
            total_log_events = 0
            
            try:
                # Get recent log events
                events_response = self.logs.filter_log_events(
                    logGroupName=log_group,
                    startTime=int(start_time.timestamp() * 1000),
                    endTime=int(end_time.timestamp() * 1000),
                    limit=200
                )
                
                events = events_response.get('events', [])
                total_log_events = len(events)
                
                # Analyze error patterns
                for event in events:
                    message = event.get('message', '').lower()
                    timestamp = event.get('timestamp', 0)
                    
                    error_found = False
                    for pattern in error_patterns.keys():
                        if pattern.lower() in message and 'error' in message:
                            error_patterns[pattern] += 1
                            error_found = True
                            
                            # Store recent error details
                            if len(recent_errors) < 10:
                                recent_errors.append({
                                    'timestamp': datetime.fromtimestamp(timestamp / 1000).isoformat(),
                                    'pattern': pattern,
                                    'message': event.get('message', '')[:200]  # First 200 chars
                                })
                            break
                    
                    if not error_found and 'error' in message:
                        error_patterns['other_errors'] += 1
                        if len(recent_errors) < 10:
                            recent_errors.append({
                                'timestamp': datetime.fromtimestamp(timestamp / 1000).isoformat(),
                                'pattern': 'other_errors',
                                'message': event.get('message', '')[:200]
                            })
                
                # Find most common error
                most_common_error = max(error_patterns.items(), key=lambda x: x[1])
                
                analysis = {
                    'total_log_events': total_log_events,
                    'error_patterns': error_patterns,
                    'most_common_error': {
                        'pattern': most_common_error[0],
                        'count': most_common_error[1]
                    },
                    'recent_errors': recent_errors,
                    'log_access_status': 'success'
                }
                
                print(f"  📄 Log events analyzed: {total_log_events}")
                print(f"  🔴 Most common error: {most_common_error[0]} ({most_common_error[1]} occurrences)")
                
                return analysis
                
            except Exception as log_error:
                print(f"  ⚠️ Limited log access: {log_error}")
                return {
                    'total_log_events': 0,
                    'error_patterns': error_patterns,
                    'most_common_error': {'pattern': 'unknown', 'count': 0},
                    'recent_errors': [],
                    'log_access_status': 'limited',
                    'log_error': str(log_error)
                }
                
        except Exception as e:
            print(f"  ❌ Error analyzing logs: {e}")
            return {'error': str(e)}
    
    def calculate_performance_metrics(self, results):
        """Calculate comprehensive performance metrics"""
        print("📈 Calculating performance metrics...")
        
        lambda_metrics = results['lambda_metrics']
        s3_analysis = results['s3_analysis']
        
        # Lambda metrics
        total_invocations = lambda_metrics.get('Invocations', {}).get('total_sum', 0)
        total_errors = lambda_metrics.get('Errors', {}).get('total_sum', 0)
        avg_duration = lambda_metrics.get('Duration', {}).get('avg_value', 0)
        total_throttles = lambda_metrics.get('Throttles', {}).get('total_sum', 0)
        
        # Calculate rates
        error_rate = (total_errors / total_invocations * 100) if total_invocations > 0 else 0
        throttle_rate = (total_throttles / total_invocations * 100) if total_invocations > 0 else 0
        
        # S3 metrics
        s3_success_rate = s3_analysis.get('success_metrics', {}).get('success_rate_percent', 0)
        processing_efficiency = s3_analysis.get('success_metrics', {}).get('processing_efficiency', 0)
        
        # System health
        system_availability = 100 - error_rate
        overall_health_score = (system_availability + s3_success_rate) / 2
        
        # Throughput calculation (files per hour)
        analysis_period_hours = results['test_metadata']['analysis_period_minutes'] / 60
        throughput_successful = s3_analysis.get('transcript_files', {}).get('valid_count', 0) / analysis_period_hours
        throughput_attempted = total_invocations / analysis_period_hours if analysis_period_hours > 0 else 0
        
        summary = {
            'lambda_performance': {
                'total_invocations': total_invocations,
                'total_errors': total_errors,
                'error_rate_percent': error_rate,
                'avg_duration_ms': avg_duration,
                'throttle_rate_percent': throttle_rate
            },
            's3_performance': {
                'success_rate_percent': s3_success_rate,
                'processing_efficiency_percent': processing_efficiency,
                'valid_files': s3_analysis.get('transcript_files', {}).get('valid_count', 0),
                'empty_files': s3_analysis.get('transcript_files', {}).get('empty_count', 0)
            },
            'system_health': {
                'availability_percent': system_availability,
                'overall_health_score': overall_health_score,
                'critical_issues': error_rate > 50 or s3_success_rate == 0
            },
            'performance_indicators': {
                'throughput_successful_files_per_hour': throughput_successful,
                'throughput_attempted_files_per_hour': throughput_attempted,
                'efficiency_ratio': (throughput_successful / throughput_attempted * 100) if throughput_attempted > 0 else 0
            }
        }
        
        return summary
    
    def generate_markdown_report(self, results):
        """Generate comprehensive markdown report"""
        metadata = results['test_metadata']
        summary = results['performance_summary']
        s3_analysis = results['s3_analysis']
        
        report_content = f"""# Whisper Lambda Performance Analysis Report

## Test Metadata
- **Test Name**: {metadata['test_name']}
- **Student**: {metadata['student_name']}
- **Analysis Date**: {metadata['timestamp'][:19]}
- **Analysis Period**: {metadata['analysis_period_minutes']} minutes
- **Time Range**: {metadata['start_time'][11:19]} - {metadata['end_time'][11:19]}

## Executive Summary

### System Performance Overview
- **Lambda Invocations**: {summary['lambda_performance']['total_invocations']:.0f}
- **Error Rate**: {summary['lambda_performance']['error_rate_percent']:.1f}%
- **S3 Success Rate**: {summary['s3_performance']['success_rate_percent']:.1f}%
- **System Availability**: {summary['system_health']['availability_percent']:.1f}%
- **Overall Health Score**: {summary['system_health']['overall_health_score']:.1f}%

### Key Performance Indicators
- **Successful Throughput**: {summary['performance_indicators']['throughput_successful_files_per_hour']:.1f} files/hour
- **Processing Efficiency**: {summary['performance_indicators']['efficiency_ratio']:.1f}%
- **Average Lambda Duration**: {summary['lambda_performance']['avg_duration_ms']:.0f}ms

## Detailed Analysis

### Lambda Function Performance
- **Total Invocations**: {summary['lambda_performance']['total_invocations']:.0f}
- **Total Errors**: {summary['lambda_performance']['total_errors']:.0f}
- **Error Rate**: {summary['lambda_performance']['error_rate_percent']:.1f}%
- **Throttle Rate**: {summary['lambda_performance']['throttle_rate_percent']:.1f}%
- **Average Duration**: {summary['lambda_performance']['avg_duration_ms']:.0f}ms

### S3 Storage Analysis
- **Audio Files Processed**: {s3_analysis.get('audio_files', {}).get('count', 0)}
- **Transcript Files Generated**: {s3_analysis.get('transcript_files', {}).get('total_count', 0)}
- **Valid Transcripts**: {s3_analysis.get('transcript_files', {}).get('valid_count', 0)}
- **Empty Transcripts**: {s3_analysis.get('transcript_files', {}).get('empty_count', 0)}
- **Success Rate**: {s3_analysis.get('success_metrics', {}).get('success_rate_percent', 0):.1f}%

### System Health Assessment
"""

        # Add health assessment
        if summary['system_health']['critical_issues']:
            report_content += """
**🔴 CRITICAL ISSUES DETECTED**
- System requires immediate attention
- High error rate or zero successful processing detected
"""
        elif summary['system_health']['overall_health_score'] > 80:
            report_content += """
**🟢 SYSTEM HEALTHY**
- System operating within acceptable parameters
- Minor optimizations may improve performance
"""
        else:
            report_content += """
**🟡 SYSTEM ISSUES**
- System functional but with performance concerns
- Investigation and optimization recommended
"""

        report_content += f"""
### Issues Identified
"""

        # Add specific issues based on metrics
        if summary['s3_performance']['empty_files'] > 0:
            report_content += f"- **Empty Transcript Files**: {summary['s3_performance']['empty_files']} files contain no content (configuration issue)\n"
        
        if summary['lambda_performance']['error_rate_percent'] > 10:
            report_content += f"- **High Lambda Error Rate**: {summary['lambda_performance']['error_rate_percent']:.1f}% error rate detected\n"
        
        if summary['lambda_performance']['total_invocations'] == 0:
            report_content += "- **No Lambda Invocations**: S3 triggers may not be properly configured\n"
        
        if summary['performance_indicators']['efficiency_ratio'] < 50:
            report_content += f"- **Low Processing Efficiency**: Only {summary['performance_indicators']['efficiency_ratio']:.1f}% of attempts successful\n"

        report_content += f"""
### Recommendations
1. **Immediate Actions**:
   - Investigate Docker container configuration for empty transcript issue
   - Review Lambda function logs for specific error patterns
   - Verify S3 bucket triggers and permissions

2. **Short-term Improvements**:
   - Implement error handling and retry mechanisms
   - Add comprehensive logging and monitoring
   - Optimize Lambda memory and timeout settings

3. **Long-term Optimizations**:
   - Implement automated scaling based on load
   - Add comprehensive alerting and dashboards
   - Consider alternative processing architectures for high-volume scenarios

## Technical Details
- **Analysis Tool**: Custom Python CloudWatch/S3 analyzer
- **Metrics Source**: AWS CloudWatch and S3 API
- **Student**: Roberto Magno
- **Project**: Whisper Lambda Performance Evaluation

---
*Report generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        # Save report
        report_file = f"../results/{metadata['test_name']}_report.md"
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        print(f"📄 Report saved: results/{metadata['test_name']}_report.md")
    
    def print_summary(self, summary):
        """Print formatted summary to console"""
        print(f"\n📊 PERFORMANCE ANALYSIS RESULTS")
        print("=" * 50)
        print(f"Lambda Invocations: {summary['lambda_performance']['total_invocations']:.0f}")
        print(f"Error Rate: {summary['lambda_performance']['error_rate_percent']:.1f}%")
        print(f"S3 Success Rate: {summary['s3_performance']['success_rate_percent']:.1f}%")
        print(f"System Availability: {summary['system_health']['availability_percent']:.1f}%")
        print(f"Processing Efficiency: {summary['performance_indicators']['efficiency_ratio']:.1f}%")
        print("=" * 50)

if __name__ == "__main__":
    import sys
    
    # Get test name from command line argument
    test_name = sys.argv[1] if len(sys.argv) > 1 else f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Initialize analyzer and run analysis
    analyzer = WhisperPerformanceAnalyzer()
    results = analyzer.analyze_performance(test_name, duration_minutes=30)
    
    print(f"\n✅ Analysis completed successfully!")
    print(f"📄 Results saved to: results/{test_name}_analysis.json")
    print(f"📄 Report saved to: results/{test_name}_report.md")
