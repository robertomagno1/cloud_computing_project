# Verifica che tutto sia pronto
echo "🔍 VERIFICA SETUP FINALE"
echo "========================"

# Controlla file audio
if [ -f "../test-files/test_audio.wav" ]; then
    echo "✅ File audio: $(ls -lh ../test-files/test_audio.wav | awk '{print $5}')"
else
    echo "⚠️ File audio non ancora copiato, facciamolo ora..."
    mkdir -p ../test-files
    FIRST_AUDIO=$(find ~/Desktop/CC -name "Speaker_0000_*.wav" | head -1)
    cp "$FIRST_AUDIO" ../test-files/test_audio.wav
    echo "✅ File audio copiato: $(ls -lh ../test-files/test_audio.wav | awk '{print $5}')"
fi

# Test connessioni AWS
echo ""
echo "🔌 Test connessioni AWS:"
aws sts get-caller-identity --query 'Account' --output text
aws s3 ls s3://whisper-audio-base-robertomagno1/ >/dev/null 2>&1 && echo "✅ S3 bucket accessibile" || echo "❌ Problema accesso S3"

# Test Python
echo ""
echo "🐍 Test Python:"
python3 -c "import boto3; print('✅ boto3 OK')" 2>/dev/null || echo "❌ Problema boto3"

echo ""
echo "🎯 TUTTO PRONTO PER I TEST!"
