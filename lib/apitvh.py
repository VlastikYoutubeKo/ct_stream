#!/usr/bin/python3

import requests
import json
import time

REPEAT = 5
DELAY = 2

class URL:
    LOCAL = 'http://127.0.0.1:9981'

class ENDPOINT:
    API = '/api'
    CHANNELTAG = API + '/channeltag/list?all=1'
    CHANNELGRID = API + '/channel/grid?all=1&limit=10000'
    CHANNELGRID_SORTBYNUMBER = API + '/channel/grid?all=1&limit=10000&sort=number'
    IDNODE = API + '/idnode/save'
    EPG_EVENTS_GRID = API + '/epg/events/grid'

class HEADERS:
    IDNODE = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}

class DATA:
    IDNODE_ENABLE = 'node={{"enabled": {}, "uuid": {}}}'
    EPG_EVENTS_GRID = '{{"dir": "ASC", "sort": "start", "start": "0", "limit": "100000", "channelTag": {}}}'

class ApiTvh:
    def __init__(self, user = None, password = None, protocol = 'http', address = '127.0.0.1', port = 9981):
        self.channelsTagName = ''
        self.channelsTagUuid = ''
        self.channelsNameToUuid = []
        self.channelsUuidToName = []
        if user == None or password == None:
            self.url = '{}://{}:{}'.format(protocol, address, port)
        else:
            self.url = '{}://{}:{}@{}:{}'.format(protocol, user, password, address, port)

    def getJson(self, url, repeat = REPEAT, delay = DELAY):
        while repeat > 0:
            try:
                data = requests.get(url)
                return data.json()
                # return json.loads(data.text)
            except:
                repeat -= 1
                print('WARNING: Neúspěšné čtení dat, zbývá pokusů: {}/{}, prodleva před dalším pokusem: {} s'.format(repeat, REPEAT, delay))
                time.sleep(delay)
        return None

    def postNode(self, url, node, headers = HEADERS.IDNODE):
        status = requests.post(url, node, headers = headers)
        return status

    def postJson(self, url, json):
        data = requests.post(url, data = json)
        # print('data: {}'.format(data))
        return data.json()
   
    def getStatus(self):
        return 0

    def getChannelsTagUuid(self, tagName):
        url = self.url + ENDPOINT.CHANNELTAG
        data = self.getJson(url)
        tagUuid = ''
        for item in data['entries']:
            if item['val'] == tagName:
                tagUuid = item['key']
                break
        if tagUuid == "":
            print('WARNING getChannelTag: tagName {} neexistuje'.format(tagName))
        # print('DEBUG getChannelTag: tagName: {} tagUuid: {}'.format(tagName, tagUuid))
        return tagUuid

    def setChannelsTag(self, tagName):
        self.channelsTagName = tagName
        self.channelsTagUuid = self.getChannelsTagUuid(tagName)
        self.channelsNameToUuid, self.channelsUuidToName = self.getChannelsDictionaries()

    def selectTag(self, name, uuid):
        tag = self.channelsTagUuid
        if name != None:
            tag = self.getChannelsTagUuid(name)
        if uuid != None:
            tag = uuid
        return tag

    def getChannelsDictionaries(self, name = None, uuid = None):
        tag = self.selectTag(name, uuid)
        url = self.url + ENDPOINT.CHANNELGRID_SORTBYNUMBER
        data = self.getJson(url)
        dictionaryNameToUuid = {}
        dictionaryUuidToName = {}
        for item in data['entries']:
            if tag == '' or tag in item['tags']:
                dictionaryNameToUuid.update({item['name']: item['uuid']})
                dictionaryUuidToName.update({item['uuid']: item['name']})
        return dictionaryNameToUuid, dictionaryUuidToName

    def getChannelsName(self, name = None, uuid = None):
        # tag = self.channelsTagUuid
        # if name != None:
            # tag = self.getChannelsTagUuid(name)
        # if uuid != None:
            # tag = uuid
        tag = self.selectTag(name, uuid)
        url = self.url + ENDPOINT.CHANNELGRID_SORTBYNUMBER
        data = self.getJson(url)
        channels = []
        for item in data['entries']:
            if tag == '' or tag in item['tags']:
                channels.append(item['name'])
        return channels
      
    def getChannelsUuid(self, name = None, uuid = None):
        tag = self.channelsTagUuid
        if name != None:
            tag = self.getChannelsTagUuid(name)
        if uuid != None:
            tag = uuid
        url = self.url + ENDPOINT.CHANNELGRID_SORTBYNUMBER
        data = self.getJson(url)
        channels = []
        for item in data['entries']:
            if tag == '' or tag in item['tags']:
                channels.append(item['uuid'])
        return channels
      
    def getChannelsNameWithEpg(self, name = None, uuid = None):
        # tag = self.channelTagUuid
        # if name != None:
            # tag = self.getChannelsTagUuid(name)
        # if uuid != None:
            # tag = uuid
        tag = self.selectTag(name, uuid)
        url = self.url + '/api/epg/events/grid'
        data = {"dir": "ASC", "sort": "start", "start": "0", "limit": "100000", "channelTag": tag}
        # print('tag: {}'.format(tag))
        # print('url: {}'.format(url))
        # print('data: {}'.format(data))
        epg = self.postJson(url, json = data)
        channels = []
        for item in epg['entries']:
            if item['channelName'] not in channels:
                channels.append(item['channelName'])
        return channels

    def enableChannels(self, channels, setting):
        # print('DUMP enableChannels: channels: {}\nsettings: {}'.format(channels, setting))
        url = self.url + ENDPOINT.IDNODE
        # headers = HEADERS.IDNODE
        data = DATA.IDNODE_ENABLE.format('true' if setting else 'false', json.dumps(channels))
        # print('DUMP enableChannels: url: {}\nheaders: {}\ndata: {}'.format(url, headers, data))
        self.postNode(url, node = data)

    def enableChannelsName(self, channels, setting = True):
        channels = self.translate(channels)
        # print('channels: {}'.format(channels))
        self.enableChannels(channels, setting)

    def enableChannelsUuid(self, channels, setting = True):
        self.enableChannels(channels, setting)

    def translate(self, original, dictionary = None):
        if dictionary == None:
            dictionary = self.channelsNameToUuid
        translated = []
        for key in original:
            try:
                translated.append(dictionary[key])
            except:
                continue
        return translated
