#!

PATTERN=${1}

# (1 second / 20 frames) * (100 ticks / second) = 5 ticks (delay)
#convert -delay 5 -coalesce -duplicate 1,-2-1 -layers Optimize -loop 0 ${PATTERN}/\*.jpg ${PATTERN}.gif
convert -delay 4 -coalesce                   -layers Optimize -loop 0 ${PATTERN}/\*.jpg ${PATTERN}.gif

