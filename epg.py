#!/usr/bin/python3
# -*- coding: utf-8 -*-

version = 'v0.1.0'

import requests
import json
import time
import os

from lib.xmltvhbb import generateXmltv
from lib.apitvh import ApiTvh

from config import CONFIG

sourceUrl = CONFIG.SOURCE_URL_PLUS
sourceName = CONFIG.SOURCE_NAME_PLUS
guide = CONFIG.GUIDE
repeat = CONFIG.SOURCE_REPEAT
delay = CONFIG.SOURCE_DELAY
userTvh = CONFIG.USER_TVH
passwordTvh = CONFIG.PASSWORD_TVH
networkTvh = CONFIG.NETWORK_TVH
networkTvhPlus = CONFIG.NETWORK_TVH_PLUS
mappingServices = CONFIG.MAPPING_SERVICES_PLUS

def getJson(url, repeat = 5, delay = 2):
    while repeat > 0:
        try:
            data = requests.get(url)
            return json.loads(data.text)
        except:
            repeat -= 1
            print('WARNING: Neúspěšné čtení dat, zbývá pokusů: {}/{}, prodleva před dalším pokusem: {} s'.format(repeat, REPEAT, delay))
            time.sleep(delay)
    return None

def getServicesAndChannels(programs, mapping):
    services = []
    channelsWithEpg = []
    channelsWithoutEpg = []
    for program in programs:
        service = program['encoder']
        if service not in services:
            services.append(service)
            channelsWithEpg.append(mapping[service])
    for service in mapping:
        channel = mapping[service]
        if channel not in channelsWithEpg:
            channelsWithoutEpg.append(channel)
    return services, channelsWithEpg, channelsWithoutEpg

def getPrograms(channels, items):
    programs = []
    for channel in channels:
        for item in items:
            if item['encoder'] == channel:
                programs.append(item)
                # print('channel: {} programTitle: {}'.format(item['encoder'], item['programTitle']))
    return programs

if __name__ == "__main__":
    print('Generace Xmltv - Start')
    path = os.path.dirname(os.path.realpath(__file__))
    apiTvh = ApiTvh(user = userTvh, password = passwordTvh)
    # Generace xmltv pro iVysilání+ kanály
    source = getJson(sourceUrl)
    # print('DEBUG sourceJson:\n{}'.format(str(source)))
    if source == None:
        print('ERROR: Chyba při načtení zdrojových json dat iVysílání+')
    else:
        services, channelsWithEpg, channelsWithoutEpg = getServicesAndChannels(source, mappingServices)
        programs = getPrograms(services, source)
        apiTvh.setChannelsTag(networkTvhPlus)
        if generateXmltv(sourceUrl, sourceName, path, guide, None, programs, mappingServices) == 0:
            apiTvh.enableChannelsName(channelsWithEpg)
            apiTvh.enableChannelsName(channelsWithoutEpg, setting = False)
        else:
            print('ERROR: Chyba při vytvoření xmltv iVysílání+')
    print('Generace Xmltv - End')
    # Workarround and test for O2TV Sport + (2-8) kanály - begin
    # print('Nastavení kanálů O2TV+ - Start')
    # apiTvh.setChannelsTag('O2TVsport+')
    # channels = apiTvh.getChannelsName()
    # apiTvh.enableChannelsName(channels)
    # channelsWithEpg = apiTvh.getChannelsNameWithEpg()
    # channelsWithoutEpg = []
    # for item in channels:
        # if item not in channelsWithEpg:
            # channelsWithoutEpg.append(item)
    # apiTvh.enableChannelsName(channelsWithoutEpg, setting = False)
    # print('Nastavení kanálů O2TV+ - End')
    # Workarround and test for O2TV Sport + (2-8) kanály - end
    del(apiTvh)
