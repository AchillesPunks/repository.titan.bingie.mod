# -*- coding: utf-8 -*-
import os
import sys
import xbmc
import xbmcaddon
import xbmcvfs

if sys.version_info >= (2, 7):
    import json
else:
    import simplejson as json

# Import the common settings
from resources.lib.settings import log
from resources.lib.settings import Settings
from resources.lib.backend import TunesBackend

ADDON = xbmcaddon.Addon(id='service.tvtunes')
CWD = ADDON.getAddonInfo('path')
LIB_DIR = xbmcvfs.translatePath(os.path.join(CWD, 'resources', 'lib'))


# Class to detect when something in the system has changed
class TvTunesMonitor(xbmc.Monitor):
    def onSettingsChanged(self):
        log("TvTunesMonitor: Notification of settings change received")
        Settings.reloadSettings()


##################################
# Main of the TvTunes Service
##################################
if __name__ == '__main__':
    log("Starting TvTunes Service %s" % ADDON.getAddonInfo('version'))

    # Check if the settings mean we want to reset the volume on startup
    startupVol = Settings.getStartupVolume()

    if startupVol < 0:
        log("TvTunesService: No Volume Change Required")
    else:
        log("TvTunesService: Setting volume to %s" % startupVol)
        xbmc.executebuiltin('SetVolume(%d)' % startupVol, True)

    # Make sure the user wants to play themes
    if Settings.isThemePlayingEnabled():
        log("TvTunesService: Theme playing enabled")

        # Create a monitor so we can reload the settings if they change
        systemMonitor = TvTunesMonitor()

        # Start looping to perform the TvTune theme operations
        main = TunesBackend()

        # Start the themes running
        main.runAsAService()

        del main
        del systemMonitor
    else:
        log("TvTunesService: Theme playing disabled")
