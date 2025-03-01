#!/usr/bin/python3
# -*- coding: utf-8 -*-

version = 'v0.2.0'

import os
import time
import re
import pytz

from datetime import datetime, timedelta

infoName = 'iVysilání+ Extra kanály - Version: {} - Author: JiRo'.format(version)
infoUrl = 'https://xbmc-kodi.cz/prispevek-ivysilani'

def parseDate(programId):
    timeStr = re.findall('.*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.000Z).*', programId)[0]
    timeUtc = datetime.strptime(timeStr, "%Y-%m-%dT%H:%M:%S.%fZ")
    return timeUtc.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Prague'))

def timeBuild(date, start, end):

    def minutes(time):
        parsed = time.split(':')
        return int(parsed[0])*60 + int(parsed[1])

    def build(date, minutes):
        return '{0}{1:02d}{2:02d}00'.format(date, minutes // 60, minutes % 60)
    
    dateStart = date.strftime('%Y%m%d')
    dateEnd = (date + timedelta(days=1)).strftime('%Y%m%d')
    if minutes(start) < minutes(end):
        dateEnd = dateStart
    return build(dateStart, minutes(start)), build(dateEnd, minutes(end))

def zoneBuild():
    shift = int(int(time.mktime(datetime.now().timetuple()) - time.mktime(datetime.utcnow().timetuple())) / 3600)
    if shift < 0:
        return ' -{0:02d}00'.format(abs(shift))
    elif shift > 0:
        return ' +{0:02d}00'.format(shift)
    else:
        return ''

def generateXmltv(sourceUrl, sourceName, path, guide, channels, programs, mappingServices):
    zone = zoneBuild()
    try:
        file = os.path.join(path, guide)
        with open(file, 'w') as xmltv:

            xmltv.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            xmltv.write('<tv generator-info-name="{}" generator-info-url="{}" source-info-name="{}" source-info-url="{}">\n'.format(infoName, infoUrl, sourceName, sourceUrl))

            channelsCount = 0
            for encoder in mappingServices:
                try:
                    channel = mappingServices[encoder]
                except:
                    print('WARNING: Chyba mapování kanálů pro: "{}"'.format(encoder))
                    continue
                channelsCount += 1

                xmltv.write('\t<channel id="{}">\n'.format(encoder))
                xmltv.write('\t\t<display-name lang="cs">{}</display-name>\n'.format(channel))
                xmltv.write('\t</channel>\n')

            programsCount = 0
            print('Pořady:')
            for program in programs:
                try:
                    channel = mappingServices[program['encoder']]
                except:
                    print('WARNING: Chyba mapování kanálů programu pro: "{}"'.format(program['encoder']))
                    continue               
                programsCount += 1
                programDate = parseDate(program['id'])
                start, end = timeBuild(programDate, program['time_str'], program['time_end_str'])
                
                print('{}. channel: {} encoder: {} type: {} start: {} end: {} date: {}\n\tprogramTitle: {}'\
                    .format(programsCount, channel, program['encoder'], program['assignmentType'], program['time_str'], program['time_end_str'], programDate, program['programTitle']))
                
                xmltv.write('\t<programme start="{0}{2}" stop="{1}{2}" channel="{3}">\n'\
                    .format(start, end, zone, program['encoder']))
                xmltv.write('\t\t<title lang="cs">{}</title>\n'\
                    .format(program['programTitle']))
                xmltv.write('\t\t<sub-title lang="cs">{}</sub-title>\n'\
                    .format('Pořad kanálu ČT Sport Plus' if program['assignmentType'] == 'ctsport' else ''))
                xmltv.write('\t\t<desc lang="cs">{0}{1}{2}</desc>\n'\
                    .format('Přímý přenos. ' if program['isLive'] == 1 else '', program['programTitle'] if program['assignmentType'] == 'ctsport' else program['notice'],'\n\n[COLOR grey]Zdroj: [/COLOR]iVysílání - kanál {}'.format(program['encoder'])))
                xmltv.write('\t\t<category lang="en">{}</category>\n'\
                    .format('Sports' if program['assignmentType'] == 'ctsport' else ''))
                xmltv.write('\t\t<icon src="{}" />\n'\
                    .format('file://{}/tvlogo/{}'.format(path, 'ctsportplus.png') if program['assignmentType'] == 'ctsport' else program['imageUrl']))
                xmltv.write('\t</programme>\n')
            
            xmltv.write('</tv>\n')
            xmltv.close()

            print('Generováno kanálů: {} a programů: {}'.format(channelsCount, programsCount))
            print('Vygenerované xmltv uloženo do souboru: {}/{}'.format(path, guide))
        return 0
    except:
        print('ERROR: Chyba při vytvoření xmltv')
        return 1
