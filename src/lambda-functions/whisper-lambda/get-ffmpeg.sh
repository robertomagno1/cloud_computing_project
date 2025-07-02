#!/bin/bash

# Scarica l'ultima build statica di ffmpeg per Linux x86_64
FFMPEG_URL="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"

# Crea una directory temporanea
mkdir -p ffmpeg-tmp && cd ffmpeg-tmp

# Scarica e decomprimi
curl -LO "$FFMPEG_URL"
tar -xf ffmpeg-release-amd64-static.tar.xz

# Copia solo il binario ffmpeg nella directory superiore
cp ffmpeg-*-static/ffmpeg ../ffmpeg

# Pulisci
cd ..
rm -rf ffmpeg-tmp

echo "ffmpeg scaricato e pronto in $(pwd)/ffmpeg"
