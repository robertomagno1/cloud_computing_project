#!/bin/bash
FFMPEG_URL="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"

mkdir -p ffmpeg-tmp && cd ffmpeg-tmp
curl -LO "$FFMPEG_URL"
tar -xf ffmpeg-release-amd64-static.tar.xz
cp ffmpeg-*-static/ffmpeg ../ffmpeg

cd ..
rm -rf ffmpeg-tmp

echo "ffmpeg scaricato e pronto in $(pwd)/ffmpeg"

