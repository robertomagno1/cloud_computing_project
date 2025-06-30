#!/bin/bash

BUCKET="whisper-audio-base-robertomagno1"
SOURCE_DIR="$HOME/desktop/cc/Progetto_CC/audio-samples/audio"
LOG_DIR="industrial_processing_logs"
BATCH_SIZE=5
MAX_PARALLEL=2
UPLOAD_DELAY=1

echo "🏭 INDUSTRIAL AUDIO UPLOADER"
echo "============================"
echo "👤 Student: robertomagno1"
echo "📅 Started: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "🎯 Target: All Speaker directories"

# Setup logging
mkdir -p $LOG_DIR
MAIN_LOG="$LOG_DIR/industrial_upload_$(date +%Y%m%d_%H%M%S).log"
echo "📋 Main log: $MAIN_LOG"

echo "📂 Source directory: $SOURCE_DIR" | tee -a $MAIN_LOG

# Function to upload speaker directory
upload_speaker_batch() {
    local speaker_dir=$1
    local batch_id=$2
    local speaker_log="$LOG_DIR/speaker_${batch_id}_$(date +%s).log"
    
    echo "📤 Processing $speaker_dir (Batch $batch_id)" | tee -a $MAIN_LOG
    
    local uploaded=0
    local failed=0
    
    # Process all WAV files in directory
    for wav_file in "$SOURCE_DIR/$speaker_dir"/*.wav; do
        if [ -f "$wav_file" ]; then
            basename_file=$(basename "$wav_file")
            # Create unique S3 key with speaker info
            s3_key="audio/industrial_${speaker_dir}_$(date +%s)_${basename_file}"
            
            echo "📤 Uploading: $basename_file → $s3_key" >> $speaker_log
            
            if aws s3 cp "$wav_file" s3://$BUCKET/$s3_key >> $speaker_log 2>&1; then
                echo "✅ Success: $s3_key" >> $speaker_log
                ((uploaded++))
            else
                echo "❌ Failed: $s3_key" >> $speaker_log
                ((failed++))
            fi
            
            # Delay to prevent throttling
            sleep $UPLOAD_DELAY
        fi
    done
    
    echo "📊 $speaker_dir completed: $uploaded uploaded, $failed failed" | tee -a $MAIN_LOG
}

# Get all speaker directories
cd "$SOURCE_DIR"
mapfile -t SPEAKER_DIRS < <(ls -d Speaker* 2>/dev/null | grep -v "__MACOSX")
TOTAL_SPEAKERS=${#SPEAKER_DIRS[@]}

echo "🔢 Found $TOTAL_SPEAKERS speaker directories" | tee -a $MAIN_LOG

# Process speakers in parallel batches
batch_counter=1

for speaker_dir in "${SPEAKER_DIRS[@]}"; do
    echo "🚀 Starting batch $batch_counter: $speaker_dir" | tee -a $MAIN_LOG
    
    # Upload speaker batch in background
    upload_speaker_batch "$speaker_dir" $batch_counter &
    
    # Limit parallel processes
    if [ $((batch_counter % MAX_PARALLEL)) -eq 0 ]; then
        echo "⏸️ Waiting for parallel batches to complete..." | tee -a $MAIN_LOG
        wait
    fi
    
    ((batch_counter++))
done

# Wait for all remaining processes
echo "⏳ Waiting for final batches..." | tee -a $MAIN_LOG
wait

echo "✅ INDUSTRIAL UPLOAD COMPLETED" | tee -a $MAIN_LOG
echo "📊 Processed $TOTAL_SPEAKERS speaker directories" | tee -a $MAIN_LOG
echo "📅 Completed: $(date -u '+%Y-%m-%d %H:%M:%S UTC')" | tee -a $MAIN_LOG

# Final verification
echo ""
echo "📊 UPLOAD VERIFICATION:"
audio_count=$(aws s3 ls s3://$BUCKET/audio/ | wc -l | tr -d ' ')
echo "Files in S3: $audio_count" | tee -a $MAIN_LOG
