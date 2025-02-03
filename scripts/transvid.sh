# Create a .mp4 from a .mov with params to work well with nexed and reduce size
transvid() {
    local inputfile="$1"
    local outputfile="$2"
    ffmpeg -i "$inputfile" -vf "scale=1280:-2" -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k "$outputfile"
}
