#!/bin/bash

# Whisper Lambda Real-time Monitoring Script
# Student: Roberto Magno
# Date: 2025-06-29

BUCKET_NAME="whisper-audio-base-robertomagno1"
FUNCTION_NAME="whisperBaseTranscriber"

echo "🔍 WHISPER LAMBDA SYSTEM MONITOR"
echo "👤 Student: Roberto Magno"
echo "📅 Monitor started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================"

# Function to get S3 file counts
get_s3_counts() {
    AUDIO_COUNT=$(aws s3 ls s3://$BUCKET_NAME/audio/ 2>/dev/null | wc -l | tr -d ' ')
    TRANSCRIPT_COUNT=$(aws s3 ls s3://$BUCKET_NAME/transcripts/ 2>/dev/null | wc -l | tr -d ' ')
    EMPTY_COUNT=$(aws s3 ls s3://$BUCKET_NAME/transcripts/ --human-readable 2>/dev/null | awk '$3=="0" {count++} END {print count+0}')
    VALID_COUNT=$((TRANSCRIPT_COUNT - EMPTY_COUNT))
}

# Function to get Lambda metrics
get_lambda_status() {
    # Get recent log stream
    RECENT_STREAM=$(aws logs describe-log-streams \
        --log-group-name /aws/lambda/$FUNCTION_NAME \
        --order-by LastEventTime \
        --descending \
        --max-items 1 \
        --query 'logStreams[0].logStreamName' \
        --output text 2>/dev/null)
    
    if [ "$RECENT_STREAM" != "None" ] && [ -n "$RECENT_STREAM" ]; then
        LAST_EVENT_TIME=$(aws logs describe-log-streams \
            --log-group-name /aws/lambda/$FUNCTION_NAME \
            --order-by LastEventTime \
            --descending \
            --max-items 1 \
            --query 'logStreams[0].lastEventTime' \
            --output text 2>/dev/null)
        
        # Convert timestamp to human readable
        if [ "$LAST_EVENT_TIME" != "None" ] && [ -n "$LAST_EVENT_TIME" ]; then
            LAST_ACTIVITY=$(date -d "@$((LAST_EVENT_TIME / 1000))" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo "Unknown")
        else
            LAST_ACTIVITY="No recent activity"
        fi
    else
        LAST_ACTIVITY="No log streams found"
    fi
}

# Display current status
display_status() {
    clear
    echo "🔍 WHISPER LAMBDA SYSTEM MONITOR"
    echo "👤 Student: Roberto Magno"
    echo "📅 Last updated: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "================================"
    echo ""
    
    echo "📁 S3 BUCKET STATUS"
    echo "-------------------"
    echo "  Audio files: $AUDIO_COUNT"
    echo "  Transcript files: $TRANSCRIPT_COUNT"
    echo "  Empty transcripts: $EMPTY_COUNT"
    echo "  Valid transcripts: $VALID_COUNT"
    
    if [ $TRANSCRIPT_COUNT -gt 0 ]; then
        SUCCESS_RATE=$(echo "scale=1; $VALID_COUNT * 100 / $TRANSCRIPT_COUNT" | bc 2>/dev/null || echo "0.0")
        echo "  Success rate: ${SUCCESS_RATE}%"
    else
        echo "  Success rate: 0.0%"
    fi
    
    echo ""
    echo "⚡ LAMBDA FUNCTION STATUS"
    echo "------------------------"
    echo "  Function: $FUNCTION_NAME"
    echo "  Last activity: $LAST_ACTIVITY"
    
    echo ""
    echo "📄 RECENT TRANSCRIPT FILES"
    echo "-------------------------"
    if [ $TRANSCRIPT_COUNT -gt 0 ]; then
        aws s3 ls s3://$BUCKET_NAM#!/bin/bash

# Whisper Lambda Real-time Monitoring Script
# Student: Roberto Magno
# Date: 2025-06-29

BUCKET_NAME="whisper-audio-base-robertomagno1"
FUNCTION_NAME="whisperBaseTranscriber"

echo "🔍 WHISPER LAMBDA SYSTEM MONITOR"
echo "👤 Student: Roberto Magno"
echo "📅 Monitor started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================"

# Function to get S3 file counts
get_s3_counts() {
    AUDIO_COUNT=$(aws s3 ls s3://$BUCKET_NAME/audio/ 2>/dev/null | wc -l | tr -d ' ')
    TRANSCRIPT_COUNT=$(aws s3 ls s3://$BUCKET_NAME/transcripts/ 2>/dev/null | wc -l | tr -d ' ')
    EMPTY_COUNT=$(aws s3 ls s3://$BUCKET_NAME/transcripts/ --human-readable 2>/dev/null | awk '$3=="0" {count++} END {print count+0}')
    VALID_COUNT=$((TRANSCRIPT_COUNT - EMPTY_COUNT))
}

# Function to get Lambda metrics
get_lambda_status() {
    # Get recent log stream
    RECENT_STREAM=$(aws logs describe-log-streams \
        --log-group-name /aws/lambda/$FUNCTION_NAME \
        --order-by LastEventTime \
        --descending \
        --max-items 1 \
        --query 'logStreams[0].logStreamName' \
        --output text 2>/dev/null)
    
    if [ "$RECENT_STREAM" != "None" ] && [ -n "$RECENT_STREAM" ]; then
        LAST_EVENT_TIME=$(aws logs describe-log-streams \
            --log-group-name /aws/lambda/$FUNCTION_NAME \
            --order-by LastEventTime \
            --descending \
            --max-items 1 \
            --query 'logStreams[0].lastEventTime' \
            --output text 2>/dev/null)
        
        # Convert timestamp to human readable
        if [ "$LAST_EVENT_TIME" != "None" ] && [ -n "$LAST_EVENT_TIME" ]; then
            LAST_ACTIVITY=$(date -d "@$((LAST_EVENT_TIME / 1000))" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo "Unknown")
        else
            LAST_ACTIVITY="No recent activity"
        fi
    else
        LAST_ACTIVITY="No log streams found"
    fi
}

# Display current status
display_status() {
    clear
    echo "🔍 WHISPER LAMBDA SYSTEM MONITOR"
    echo "👤 Student: Roberto Magno"
    echo "📅 Last updated: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "================================"
    echo ""
    
    echo "📁 S3 BUCKET STATUS"
    echo "-------------------"
    echo "  Audio files: $AUDIO_COUNT"
    echo "  Transcript files: $TRANSCRIPT_COUNT"
    echo "  Empty transcripts: $EMPTY_COUNT"
    echo "  Valid transcripts: $VALID_COUNT"
    
    if [ $TRANSCRIPT_COUNT -gt 0 ]; then
        SUCCESS_RATE=$(echo "scale=1; $VALID_COUNT * 100 / $TRANSCRIPT_COUNT" | bc 2>/dev/null || echo "0.0")
        echo "  Success rate: ${SUCCESS_RATE}%"
    else
        echo "  Success rate: 0.0%"
    fi
    
    echo ""
    echo "⚡ LAMBDA FUNCTION STATUS"
    echo "------------------------"
    echo "  Function: $FUNCTION_NAME"
    echo "  Last activity: $LAST_ACTIVITY"
    
    echo ""
    echo "📄 RECENT TRANSCRIPT FILES"
    echo "-------------------------"
    if [ $TRANSCRIPT_COUNT -gt 0 ]; then
        aws s3 ls s3://$BUCKET_NAMEE
