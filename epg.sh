#! /bin/sh
path=$(dirname $(realpath $0))

log_file=${path}/playlist.log
err_file=${path}/playlist.err

echo >> ${log_file}
echo $(date +"%Y-%m-%d %H:%M:%S.%N") Start >> ${log_file}
python ${path}/epg.py >> ${log_file}
cat ${path}/xmltv.xml | sudo socat - UNIX-CONNECT:/var/lib/tvheadend/epggrab/xmltv.sock >> ${log_file}
echo $(date +"%Y-%m-%d %H:%M:%S.%N") Konec >> ${log_file}

exit 0
