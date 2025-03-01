#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Parametry pro řešení příjmu iVysílání v Tvheadend
#
# Poznámka:
# Ve všech parametrech, kde je použit postfix _PLUS jde o parametry pro iVysílání extra kanály
# iVysílání extra kanály - většinou jde o kanály Sport Plus, případně kanály s dalším obsahem (vysílání ze Senátu Parlementu ČR atp.)

class CONFIG:

    # Cesta a jméno souboru pro xmltv
    GUIDE = 'xmltv.xml'
    PLAYLIST = 'playlistx.m3u8'

    # Zdroje dat EPG
    # Adresa serveru HbbTV včetně cesty k souboru json, z kterého se získává EPG pro extra kanály
    SOURCE_NAME_PLUS = 'HbbTV Česká televize'
    SOURCE_URL_PLUS = 'https://hbbtv.ceskatelevize.cz/online/services/data/online.json'
    # Parametry pro čtení dat se serveru zdroje dat
    SOURCE_REPEAT = 5
    SOURCE_DELAY = 2
  
    # Parametry Tvheadend serveru
    # - protokol, adresa a port jsou zatím default!
    # - ostatní parametry musí odpovídat parametrům Tvh a použitého playlistu - zatím se nekontroluje!
    #
    # Přihlašovací údaje
    USER_TVH = ''
    PASSWORD_TVH = ''
    # Název sítě, používá se jako channelTag a group title kanálů v playlistu
    NETWORK_TVH = 'iVysilani'
    NETWORK_TVH_PLUS = 'iVysilani+'
    # Tabulka mapování služeb ke kanálům (obsahuje relace <služba: kanál>
    MAPPING_SERVICES_PLUS = {
    "CH_25": "CT iVysilani+ 1",
    "CH_26": "CT iVysilani+ 2",
    "CH_27": "CT iVysilani+ 3",
    "CH_28": "CT iVysilani+ 4",
    "CH_29": "CT iVysilani+ 5",
    "CH_30": "CT iVysilani+ 6",
    "CH_31": "CT iVysilani+ 7",
    "CH_32": "CT iVysilani+ 8",
    "CH_MOB_01": "CT iVysilani+ 9",
    "CH_MP_01": "CT iVysilani+ 10",
    "CH_MP_02": "CT iVysilani+ 11",
    "CH_MP_03": "CT iVysilani+ 12",
    "CH_MP_04": "CT iVysilani+ 13",
    "CH_MP_05": "CT iVysilani+ 14",
    "CH_MP_06": "CT iVysilani+ 15",
    "CH_MP_07": "CT iVysilani+ 16",
    "CH_MP_08": "CT iVysilani+ 17"
    }
