#!/bin/bash

echo "🔍 RICERCA INTELLIGENTE FILE AUDIO"
echo "👤 Student: Roberto Magno"
echo "📅 $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================"

# Crea directory test-files se non esiste
mkdir -p ../test-files

echo "🔍 Ricerca file .wav nel progetto..."

# Array per memorizzare i file trovati
declare -a AUDIO_FILES

# Cerca ricorsivamente file .wav
echo "📂 Scansione ricorsiva dalla directory home..."

# Trova file .wav
while IFS= read -r -d '' file; do
    AUDIO_FILES+=("$file")
    echo "  ✅ Trovato: $(basename "$file") ($(ls -lh "$file" | awk '{print $5}'))"
done < <(find ~/Desktop/CC -name "*.wav" -type f -print0 2>/dev/null)

echo ""
echo "📊 RISULTATI: Trovati ${#AUDIO_FILES[@]} file audio"

if [ ${#AUDIO_FILES[@]} -eq 0 ]; then
    echo "❌ Nessun file .wav trovato"
    echo ""
    echo "🔍 Cerco altri formati audio..."
    find ~/Desktop/CC -name "*.mp3" -o -name "*.m4a" -o -name "*.flac" 2>/dev/null | head -5
    echo ""
    echo "💡 Copia manualmente un file audio:"
    echo "cp /path/to/your/audio.wav ../test-files/test_audio.wav"
else
    # Scegli il primo file trovato
    SELECTED_FILE="${AUDIO_FILES[0]}"
    echo "🎯 File selezionato: $(basename "$SELECTED_FILE")"
    
    # Copia il file
    if cp "$SELECTED_FILE" ../test-files/test_audio.wav; then
        echo "✅ File audio copiato con successo!"
        echo "📄 Pronto in: ../test-files/test_audio.wav"
        
        # Verifica
        COPIED_SIZE=$(ls -lh ../test-files/test_audio.wav | awk '{print $5}')
        echo "🔍 Dimensione: $COPIED_SIZE"
        echo ""
        echo "🚀 PRONTO PER I TEST!"
    else
        echo "❌ Errore nella copia"
        echo "🔧 Comando manuale:"
        echo "cp \"$SELECTED_FILE\" ../test-files/test_audio.wav"
    fi
fi
