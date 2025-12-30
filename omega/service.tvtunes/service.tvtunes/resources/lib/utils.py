#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import xbmc
import xbmcvfs
if sys.version_info.major == 3:
    import urllib.request, urllib.parse, urllib.error
    import traceback
else:
    import urllib
    from traceback import format_exc

try:
    import simplejson as json
except Exception:
    import json

ADDON_ID = "service.tvtunes"
KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split(".")[0])
KODILANGUAGE = xbmc.getLanguage(xbmc.ISO_639_1)


def log_msg(msg, loglevel=xbmc.LOGDEBUG):
    '''log message to kodi log'''
    if sys.version_info.major < 3:
        if isinstance(msg, unicode):
            msg = msg.encode('utf-8')
    xbmc.log("[TV Tunes] %s" % msg, level=loglevel)