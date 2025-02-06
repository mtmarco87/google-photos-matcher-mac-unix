# Convert vp9 mov to quicktime compatible h264 mp4

# Read original GPS Data
GPS_DATA="$(exiftool  "$1" -GPSCoordinates -s3 -n)"
echo "==> Original GPS Data: ${GPS_DATA}"

# Transcode video from VP9 to H264
echo "==> Transcoding..."
ffmpeg -i "$1" -map 0 -c:v libx264 -c:a copy -pix_fmt yuv420p "$2" # -map_metadata 0 -movflags use_metadata_tags

# Copy over all metadata/exif tags
echo "==> Copy metadata from original video..."
exiftool -TagsFromFile "$1" "-all:all>all:all" "$2" -overwrite_original

# Remove all wrong GPS tags
echo "==> Remove wrong GPS tags..."
exiftool "$2" -overwrite_original -QuickTime:Keys:GPSCoordinates=
exiftool "$2" -overwrite_original -QuickTime:ItemList:GPSCoordinates=
exiftool "$2" -overwrite_original -QuickTime:LocationInformation=

# Write down Android/iOS compatible GPS tags
echo "==> Reapply correct GPS tags..."
exiftool "$2" -overwrite_original -n -QuickTime:ItemList:GPSCoordinates="${GPS_DATA}"
exiftool "$2" -overwrite_original -n -QuickTime:Keys:GPSCoordinates="${GPS_DATA}"

# Reapply correct file creation/modification date
echo "==> Reapply correct file creation/modification date..."
touch -r "$1" "$2"

echo "Transcode completed."
