#! /bin/sh
path=$(dirname $(realpath $0))/

log_file=${path}streamer.log

level="-v fatal"
level=

channel=$1
provider="CT iVysilani"

request="https://api.ceskatelevize.cz/video/v1/playlist-live/v1/stream-data/channel/${channel}?canPlayDrm=false&streamType=dash"

json=$(wget -qO - ${request})
# echo json: ${json}
url=$(echo ${json} | jq -r '.streamUrls.main')
# echo url: ${url} >> ${log_file}
# wget -qO ${path}streamer.dat ${url}
ffmpeg -fflags +genpts ${level} -i "${url}" -f mpegts -c:v copy -c:a copy -metadata service_provider="${provider}" -metadata service_name="${channel}" pipe:1
