#!/usr/bin/env bash
# Builds one short silent loop per coming-soon country from the Mixkit ids in video/sources.json.
# Each clip: 2.6 s from second 1, cropped to 960x540, joined with 0.5 s crossfades.
# Usage: scripts/build-videos.sh [key ...]   (default: all keys). Needs ffmpeg, jq, curl.
set -euo pipefail
cd "$(dirname "$0")/.."
SEG=2.6; XF=0.5; TMP=$(mktemp -d)
keys=("$@"); [ ${#keys[@]} -eq 0 ] && mapfile -t keys < <(jq -r 'keys[] | select(startswith("_")|not)' video/sources.json)
for k in "${keys[@]}"; do
  mapfile -t ids < <(jq -r --arg k "$k" '.[$k][]' video/sources.json)
  ins=(); n=0
  for id in "${ids[@]}"; do
    f="$TMP/$id.mp4"
    if [ -n "${LOCAL_CLIPS:-}" ]; then cp "$LOCAL_CLIPS/$id.mp4" "$f"
    else curl -fsSL --retry 3 -o "$f" "https://assets.mixkit.co/videos/$id/$id-720.mp4"; fi
    ins+=(-ss 1 -t "$SEG" -i "$f"); n=$((n+1))
  done
  fc=""; for ((i=0;i<n;i++)); do fc+="[$i:v]scale=960:540:force_original_aspect_ratio=increase,crop=960:540,fps=30,setsar=1,format=yuv420p[v$i];"; done
  prev="v0"; off=0
  for ((i=1;i<n;i++)); do off=$(echo "$off + $SEG - $XF" | bc); fc+="[$prev][v$i]xfade=transition=fade:duration=$XF:offset=$off[x$i];"; prev="x$i"; done
  ffmpeg -loglevel error -y "${ins[@]}" -filter_complex "${fc%;}" -map "[$prev]" -an -c:v libx264 -preset slow -crf 28 -profile:v high -pix_fmt yuv420p -movflags +faststart "video/$k.mp4"
  ffmpeg -loglevel error -y -ss 0.3 -i "video/$k.mp4" -frames:v 1 -q:v 5 "video/$k.jpg"
  echo "$k: $(du -h "video/$k.mp4" | cut -f1)"
done
rm -rf "$TMP"
