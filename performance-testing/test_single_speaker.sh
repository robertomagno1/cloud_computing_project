#!/bin/bash

BUCKET="whisper-audio-base-robertomagno1"
SOURCE_DIR="$HOME/desktop/cc/Progetto_CC/audio-samples/audio"

echo "🧪 TEST SINGLE SPEAKER UPLOAD"
echo "============================="

# Test con primo speaker
FIRST_SPEAKER=$(ls -d "$SOURCE_DIR"/Speaker* | head -1 | xargs basename)
echo "Testing with: $FIRST_SPEAKER"

# Upload primi 3 file del primo speaker
counter=1
for wav_file in "$SOURCE_DIR/$FIRST_SPEAKER"/*.wav; do
    if [ -f "$wav_file" ] && [ $counter -le 3 ]; then
        basename_file=$(basename "$wav_file")
        s3_key="audio/test_${FIRST_SPEAKER}_$(date +%s)_${basename_file}"
        
        echo "📤 Test upload $counter: $basename_file"
        
        if aws s3 cp "$wav_file" s3://$BUCKET/$s3_key; then
            echo "✅ Success: $s3_key"
        else
            echo "❌ Failed: $s3_key"
        fi
        
        ((counter++))
    fi
done

echo ""
echo "📊 S3 Status after test:"
aws s3 ls s3://$BUCKET/audio/ | tail -5
