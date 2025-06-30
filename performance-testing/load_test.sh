#!/bin/bash

# Whisper Lambda Load Testing Script
# Student: Roberto Magno
# Date: 2025-06-29

set -e  # Exit on any error

# Configuration
BUCKET_NAME="whisper-audio-base-robertomagno1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PERFORMANCE_DIR="$(dirname "$SCRIPT_DIR")"

# Function to display usage
show_usage() {
    echo "🧪 WHISPER LAMBDA LOAD TEST"
    echo "Student: Roberto Magno"
    echo ""
    echo "Usage: $0 <test_name> <concurrent_uploads> <total_files> [audio_file]"
    echo ""
    echo "Parameters:"
    echo "  test_name:        Name for this test run"
    echo "  concurrent_uploads: Number of simultaneous uploads"
    echo "  total_files:      Total number of files to upload"
    echo "  audio_file:       Optional path to audio file (default: ../test-files/test_audio.wav)"
    echo ""
    echo "Examples:"
    echo "  $0 light_load 2 4"
    echo "  $0 medium_load 3 9"
    echo "  $0 heavy_load 5 15"
    echo ""
    exit 1
}

# Validate parameters
if [ $# -lt 3 ]; then
    show_usage
fi

TEST_NAME=$1
CONCURRENT_UPLOADS=$2
TOTAL_FILES=$3
AUDIO_FILE=${4:-"$PERFORMANCE_DIR/test-files/test_audio.wav"}

# Validate inputs
if ! [[ "$CONCURRENT_UPLOADS" =~ ^[0-9]+$ ]] || [ "$CONCURRENT_UPLOADS" -lt 1 ]; then
    echo "❌ Error: concurrent_uploads must be a positive integer"
    exit 1
fi

if ! [[ "$TOTAL_FILES" =~ ^[0-9]+$ ]] || [ "$TOTAL_FILES" -lt 1 ]; then
    echo "❌ Error: total_files must be a positive integer"
    exit 1
fi

if [ "$CONCURRENT_UPLOADS" -gt "$TOTAL_FILES" ]; then
    echo "❌ Error: concurrent_uploads cannot be greater than total_files"
    exit 1
fi

# Display test information
echo "🧪 WHISPER LAMBDA LOAD TEST"
echo "👤 Student: Roberto Magno"
echo "📅 Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "🏷️ Test Name: $TEST_NAME"
echo "📊 Configuration:"
echo "  - Concurrent uploads: $CONCURRENT_UPLOADS"
echo "  - Total files: $TOTAL_FILES"
echo "  - Audio file: $AUDIO_FILE"
echo "  - S3 Bucket: $BUCKET_NAME"
echo ""

# Verify audio file exists
if [ ! -f "$AUDIO_FILE" ]; then
    echo "❌ Audio file not found: $AUDIO_FILE"
    echo ""
    echo "🔍 Looking for alternative audio files..."
    
    # Try to find alternative audio files
    ALTERNATIVE_FILES=(
        "$PERFORMANCE_DIR/test-files/Speaker_0000_00002copy.wav"
        "$PERFORMANCE_DIR/../test-files/Speaker_0000_00002copy.wav"
        "$PERFORMANCE_DIR/../audio/audio_concatenator.py"  # Check if we can find audio directory
    )
    
    for alt_file in "${ALTERNATIVE_FILES[@]}"; do
        if [ -f "$alt_file" ]; then
            echo "✅ Found alternative: $alt_file"
            echo "📋 Copying to test file location..."
            
            # Create test-files directory if it doesn't exist
            mkdir -p "$PERFORMANCE_DIR/test-files"
            
            # Copy the file
            cp "$alt_file" "$AUDIO_FILE"
            echo "✅ Audio file prepared at: $AUDIO_FILE"
            break
        fi
    done
    
    # Final check
    if [ ! -f "$AUDIO_FILE" ]; then
        echo "❌ No suitable audio file found. Please ensure you have an audio file at:"
        echo "   $AUDIO_FILE"
        echo ""
        echo "💡 You can copy any .wav file to that location or specify a different file as the 4th parameter"
        exit 1
    fi
fi

# Get audio file info
AUDIO_SIZE=$(ls -lh "$AUDIO_FILE" | awk '{print $5}')
echo "📄 Audio file info:"
echo "  - Size: $AUDIO_SIZE"
echo "  - Path: $AUDIO_FILE"
echo ""

# Create results directory
RESULTS_DIR="$PERFORMANCE_DIR/results/$TEST_NAME"
mkdir -p "$RESULTS_DIR"

# Initialize log file
LOG_FILE="$RESULTS_DIR/load_test.log"
echo "timestamp,batch,file_id,upload_status,file_size,upload_duration" > "$LOG_FILE"

echo "📁 Results will be saved to: $RESULTS_DIR"
echo ""

# Cleanup previous transcripts
echo "🧹 Cleaning previous transcripts..."
aws s3 rm "s3://$BUCKET_NAME/transcripts/" --recursive --quiet 2>/dev/null || echo "  (No previous transcripts to clean)"

# Wait a moment for cleanup
sleep 2

echo "🚀 Starting load test at $(date)"
echo ""

# Record start time
START_TIME=$(date +%s)
START_TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Calculate batches
BATCHES=$(( (TOTAL_FILES + CONCURRENT_UPLOADS - 1) / CONCURRENT_UPLOADS ))
echo "📦 Upload plan: $BATCHES batches of up to $CONCURRENT_UPLOADS files each"
echo ""

# Upload files in batches
uploaded_count=0
successful_uploads=0
failed_uploads=0

for batch in $(seq 1 $BATCHES); do
    echo "📦 Batch $batch/$BATCHES - $(date '+%H:%M:%S')"
    
    batch_pids=()
    batch_start_time=$(date +%s)
    
    # Upload files in this batch
    for i in $(seq 1 $CONCURRENT_UPLOADS); do
        if [ $uploaded_count -lt $TOTAL_FILES ]; then
            uploaded_count=$((uploaded_count + 1))
            file_id="${batch}_${i}"
            
            # Background upload process
            (
                upload_start=$(date +%s.%3N)
                remote_name="audio/loadtest_${TEST_NAME}_${file_id}_$(date +%s%3N).wav"
                
                if aws s3 cp "$AUDIO_FILE" "s3://$BUCKET_NAME/$remote_name" >/dev/null 2>&1; then
                    upload_end=$(date +%s.%3N)
                    upload_duration=$(echo "$upload_end - $upload_start" | bc)
                    echo "$(date +%s.%3N),$batch,$file_id,success,$AUDIO_SIZE,$upload_duration" >> "$LOG_FILE"
                    echo "  ✅ File $uploaded_count/$TOTAL_FILES uploaded successfully (${upload_duration}s)"
                    exit 0
                else
                    upload_end=$(date +%s.%3N)
                    upload_duration=$(echo "$upload_end - $upload_start" | bc)
                    echo "$(date +%s.%3N),$batch,$file_id,failed,$AUDIO_SIZE,$upload_duration" >> "$LOG_FILE"
                    echo "  ❌ File $uploaded_count/$TOTAL_FILES upload failed"
                    exit 1
                fi
            ) &
            
            batch_pids+=($!)
        fi
    done
    
    # Wait for this batch to complete
    batch_successful=0
    batch_failed=0
    
    for pid in "${batch_pids[@]}"; do
        if wait $pid; then
            batch_successful=$((batch_successful + 1))
            successful_uploads=$((successful_uploads + 1))
        else
            batch_failed=$((batch_failed + 1))
            failed_uploads=$((failed_uploads + 1))
        fi
    done
    
    batch_end_time=$(date +%s)
    batch_duration=$((batch_end_time - batch_start_time))
    
    echo "  📊 Batch $batch complete: ${batch_successful} successful, ${batch_failed} failed (${batch_duration}s)"
    echo "  📈 Overall progress: $uploaded_count/$TOTAL_FILES files processed"
    echo ""
    
    # Brief pause between batches
    if [ $batch -lt $BATCHES ]; then
        echo "  ⏸️ Waiting 3 seconds before next batch..."
        sleep 3
    fi
done

# Calculate upload statistics
END_TIME=$(date +%s)
TOTAL_DURATION=$((END_TIME - START_TIME))
END_TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "📊 UPLOAD PHASE COMPLETED"
echo "========================="
echo "Start time: $START_TIMESTAMP"
echo "End time: $END_TIMESTAMP"
echo "Total duration: ${TOTAL_DURATION}s"
echo "Files uploaded: $successful_uploads/$TOTAL_FILES"
echo "Upload success rate: $(echo "scale=1; $successful_uploads * 100 / $TOTAL_FILES" | bc 2>/dev/null || echo "0")%"
echo "Average upload rate: $(echo "scale=2; $successful_uploads / $TOTAL_DURATION" | bc 2>/dev/null || echo "0") files/second"
echo ""

# Save upload summary
cat > "$RESULTS_DIR/upload_summary.json" << EOF
{
  "test_metadata": {
    "test_name": "$TEST_NAME",
    "student_name": "Roberto Magno",
    "start_time": "$START_TIMESTAMP",
    "end_time": "$END_TIMESTAMP",
    "total_duration_seconds": $TOTAL_DURATION
  },
  "configuration": {
    "concurrent_uploads": $CONCURRENT_UPLOADS,
    "total_files": $TOTAL_FILES,
    "audio_file": "$AUDIO_FILE",
    "audio_file_size": "$AUDIO_SIZE",
    "bucket_name": "$BUCKET_NAME"
  },
  "upload_results": {
    "successful_uploads": $successful_uploads,
    "failed_uploads": $failed_uploads,
    "success_rate_percent": $(echo "scale=1; $successful_uploads * 100 / $TOTAL_FILES" | bc 2>/dev/null || echo "0"),
    "avg_upload_rate_files_per_second": $(echo "scale=2; $successful_uploads / $TOTAL_DURATION" | bc 2>/dev/null || echo "0")
  }
}
EOF

# Wait for Lambda processing
PROCESSING_WAIT_TIME=120
echo "⏳ Waiting ${PROCESSING_WAIT_TIME} seconds for Lambda processing..."
echo "   (Lambda functions need time to process uploaded files)"
echo ""

# Show a progress bar for waiting
for i in $(seq 1 $PROCESSING_WAIT_TIME); do
    if [ $((i % 10)) -eq 0 ]; then
        echo "   ⏱️ ${i}/${PROCESSING_WAIT_TIME}s elapsed..."
    fi
    sleep 1
done

echo ""
echo "📈 Starting performance analysis..."
echo ""

# Run performance analysis
cd "$SCRIPT_DIR"
if python3 error_analysis.py "$TEST_NAME" 2>/dev/null; then
    echo ""
    echo "✅ Performance analysis completed successfully!"
else
    echo ""
    echo "⚠️ Performance analysis completed with some warnings"
    echo "   (This is normal if CloudWatch logs have limited access)"
fi

echo ""
echo "🎯 LOAD TEST SUMMARY"
echo "===================="
echo "Test name: $TEST_NAME"
echo "Files uploaded: $successful_uploads/$TOTAL_FILES"
echo "Upload duration: ${TOTAL_DURATION}s"
echo "Processing wait: ${PROCESSING_WAIT_TIME}s"
echo "Results location: $RESULTS_DIR"
echo ""
echo "📄 Generated files:"
echo "  - $LOG_FILE"
echo "  - $RESULTS_DIR/upload_summary.json"
echo "  - ../results/${TEST_NAME}_analysis.json"
echo "  - ../results/${TEST_NAME}_report.md"
echo ""
echo "✅ Load test '$TEST_NAME' completed successfully!"
echo "👤 Test executed by: Roberto Magno"
echo "📅 Completed at: $(date '+%Y-%m-%d %H:%M:%S')"
