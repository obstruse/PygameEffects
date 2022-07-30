#!

PATTERN=${1}
ffmpeg  -framerate 20 -pattern_type glob -i ${PATTERN}/\*.jpg ${PATTERN}.mp4


