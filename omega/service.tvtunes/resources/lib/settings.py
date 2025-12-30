# -*- coding: utf-8 -*-
import os
import unicodedata
import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui

#from settings import log
from resources.lib.utils import log_msg

ADDON = xbmcaddon.Addon(id='service.tvtunes')
ADDON_ID = ADDON.getAddonInfo('id')


# Common logging module
def log(txt, debug_logging_enabled=True, loglevel=xbmc.LOGDEBUG):
    if ((ADDON.getSetting("logEnabled") == "true") and debug_logging_enabled) or (loglevel != xbmc.LOGDEBUG):
        if isinstance(txt, str):
            txt = txt
        message = u'%s: %s' % (ADDON_ID, txt)
        log(message, loglevel)


def normalize_string(text):
    try:
        text = text.replace(":", "")
        text = text.replace("/", "-")
        text = text.replace("\\", "-")
        text = text.replace("<", "")
        text = text.replace(">", "")
        text = text.replace("*", "")
        text = text.replace("?", "")
        text = text.replace('|', "")
        text = text.strip()
        # Remove dots from the last character as windows can not have directories
        # with dots at the end
        text = text.rstrip('.')
        text = unicodedata.normalize('NFKD', unicode(text, 'utf-8')).encode('ascii', 'ignore')
    except:
        pass
    return text


# There has been problems with calling join with non ascii characters,
# so we have this method to try and do the conversion for us
def os_path_join(dir, file):
    # Check if it ends in a slash
    if dir.endswith("/") or dir.endswith("\\"):
        # Remove the slash character
        dir = dir[:-1]

    # Convert each argument - if an error, then it will use the default value
    # that was passed in
    try:
        dir = dir.decode("utf-8")
    except:
        pass
    try:
        file = file.decode("utf-8")
    except:
        pass
    return os.path.join(dir, file)


# There has been problems with calling isfile with non ascii characters,
# so we have this method to try and do the conversion for us
def os_path_isfile(workingPath):
    # Support special paths like smb:// means that we can not just call
    # os.path.isfile as it will return false even if it is a file
    # (A bit of a shame - but that's the way it is)
    if workingPath.startswith("smb://") or workingPath.startswith("nfs://") or workingPath.startswith("afp://"):
        # The test for the file existing will not work, so return true
        return True

    # Convert each argument - if an error, then it will use the default value
    # that was passed in
    try:
        workingPath = workingPath.decode("utf-8")
    except:
        pass
    try:
        return os.path.isfile(workingPath)
    except:
        return False


# Splits a path the same way as os.path.split but supports paths of a different
# OS than that being run on
def os_path_split(fullpath):
    # Check if it ends in a slash
    if fullpath.endswith("/") or fullpath.endswith("\\"):
        # Remove the slash character
        fullpath = fullpath[:-1]

    try:
        slash1 = fullpath.rindex("/")
    except:
        slash1 = -1

    try:
        slash2 = fullpath.rindex("\\")
    except:
        slash2 = -1

    # Parse based on the last type of slash in the string
    if slash1 > slash2:
        return fullpath.rsplit("/", 1)

    return fullpath.rsplit("\\", 1)


# Get the contents of the directory
def list_dir(dirpath):
    # There is a problem with the afp protocol that means if a directory not ending
    # in a / is given, an error happens as it just appends the filename to the end
    # without actually checking there is a directory end character
    #    http://forum.org/showthread.php?tid=192255&pid=1681373#pid1681373
    if dirpath.startswith('afp://') and (not dirpath.endswith('/')):
        dirpath = os_path_join(dirpath, '/')
    return xbmcvfs.listdir(dirpath)


# Checks if a directory exists (Do not use for files)
def dir_exists(dirpath):
    # There is an issue with password protected smb shares, in that they seem to
    # always return false for a directory exists call, so if we have a smb with
    # a password and user name, then we return true
    if Settings.isSmbEnabled() and ('@' in dirpath):
        return True

    directoryPath = dirpath
    # The xbmcvfs exists interface require that directories end in a slash
    # It used to be OK not to have the slash in Gotham, but it is now required
    if (not directoryPath.endswith("/")) and (not directoryPath.endswith("\\")):
        dirSep = "/"
        if "\\" in directoryPath:
            dirSep = "\\"
        directoryPath = "%s%s" % (directoryPath, dirSep)
    return xbmcvfs.exists(directoryPath)


################################################################
# Class to make it easier to see which screen is being displayed
################################################################
class WindowShowing():
    @staticmethod
    def isHome():
        return xbmc.getCondVisibility("Window.IsVisible(home)")

    @staticmethod
    def isVideoLibrary():
        # Removed check for videolibrary (before v17)...only checking videos (v17 onwards)
        return xbmc.getCondVisibility("Window.IsVisible(videos)") or WindowShowing.isTvTunesOverrideTvShows() or WindowShowing.isTvTunesOverrideMovie() or WindowShowing.isTvTunesOverrideContinuePlaying()

    @staticmethod
    def isMovieInformation():
        return xbmc.getCondVisibility("Window.IsVisible(movieinformation)") or WindowShowing.isTvTunesOverrideMovie()

    @staticmethod
    def isTvShows():
        return xbmc.getCondVisibility("Container.Content(tvshows)") or (xbmc.getInfoLabel("ListItem.dbtype") == 'tvshow') or WindowShowing.isTvTunesOverrideTvShows()

    @staticmethod
    def isSeasons():
        return xbmc.getCondVisibility("Container.Content(Seasons)") or (xbmc.getInfoLabel("ListItem.dbtype") == 'season') or WindowShowing.isTvTunesOverrideTvShows()

    @staticmethod
    def isEpisodes():
        return xbmc.getCondVisibility("Container.Content(Episodes)") or (xbmc.getInfoLabel("ListItem.dbtype") == 'episode') or WindowShowing.isTvTunesOverrideTvShows()

    @staticmethod
    def isMovies():
        return xbmc.getCondVisibility("Container.Content(movies)") or (xbmc.getInfoLabel("ListItem.dbtype") == 'movie') or WindowShowing.isTvTunesOverrideMovie()

    @staticmethod
    def isScreensaver():
        return xbmc.getCondVisibility("System.ScreenSaverActive")

    @staticmethod
    def isShutdownMenu():
        return xbmc.getCondVisibility("Window.IsVisible(shutdownmenu)")

    @staticmethod
    def isMusicSection():
        inMusicSection = False
        # Only record being in the music section if we have it enabled in the settings
        if Settings.isPlayMusicList():
            if xbmc.getCondVisibility("Container.Content(albums)"):
                inMusicSection = True
            elif xbmc.getCondVisibility("Container.Content(artists)"):
                inMusicSection = True
        return inMusicSection

    @staticmethod
    def isTvTunesOverrideTvShows():
        isOverride = False
        try:
            # If there is a problem with a skin where there is no current window Id, avoid the exception
            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            if win.getProperty("TvTunesSupported").lower() == "tvshows":
                isOverride = True
        except:
            isOverride = False

        return isOverride

    @staticmethod
    def isTvTunesOverrideMovie():
        isOverride = False
        try:
            # If there is a problem with a skin where there is no current window Id, avoid the exception
            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            if win.getProperty("TvTunesSupported").lower() == "movies":
                isOverride = True
        except:
            isOverride = False

        return isOverride

    @staticmethod
    def isTvTunesOverrideContinuePlaying():
        # Check the home screen for the forced continue playing flag
        if xbmcgui.Window(12000).getProperty("TvTunesContinuePlaying").lower() == "true":
            # Never allow continues playing on the Home Screen
            if WindowShowing.isHome():
                # An addon may have forgotten to undet the flag, or crashed
                # force the unsetting of the flag
                log_msg("WindowShowing: Removing TvTunesContinuePlaying property when on Home screen")
                xbmcgui.Window(12000).clearProperty("TvTunesContinuePlaying")
                return False

            # Only pay attention to the forced playing if there is actually media playing
            if Player().isPlaying():
                return True
        return False

    # Works out if the custom window option to play the TV Theme is set
    # and we have just opened a dialog over that
    @staticmethod
    def isTvTunesOverrideContinuePrevious():
        # Check the master override that forces the existing playing theme
        if WindowShowing.isTvTunesOverrideContinuePlaying():
            return True

        if WindowShowing.isTvTunesOverrideTvShows() or WindowShowing.isTvTunesOverrideMovie():
            # Check if this is a dialog, in which case we just continue playing
            try:
                dialogid = xbmcgui.getCurrentWindowDialogId()
            except:
                dialogid = 9999
            if dialogid != 9999:
                # Is a dialog so return True
                return True
        return False

    @staticmethod
    def isRecentEpisodesAdded():
        return xbmc.getInfoLabel("container.folderpath") == "videodb://recentlyaddedepisodes/"

    @staticmethod
    def isTvShowTitles():
        showingTvShowTitles = (xbmc.getInfoLabel("container.folderpath") == "videodb://tvshows/titles/")
        # There is a case where the user may have created a smart playlist that then
        # groups together all the TV Shows, if they also have the option to play themes
        # while browsing TV Shows enabled, then we need to return True for this case
        if not showingTvShowTitles:
            # Check if we are viewing a video playlist
            if 'special://profile/playlists/video/' in xbmc.getInfoLabel("container.folderpath"):
                # Check if what is being showed is actually TV Shows
                showingTvShowTitles = WindowShowing.isTvShows()
            elif (xbmc.getInfoLabel("ListItem.dbtype") == 'tvshow'):
                showingTvShowTitles = True
        return showingTvShowTitles

    @staticmethod
    def isMusicVideoTitles():
        return xbmc.getInfoLabel("container.folderpath") == "videodb://musicvideos/"

    @staticmethod
    def isPluginPath():
        currentPath = xbmc.getInfoLabel("ListItem.Path")
        if "plugin://" in currentPath:
            # There is a special case for Emby.Kodi that supports TvTunes
            # https://github.com/MediaBrowser/Emby.Kodi
            # So we pretend that isn't a plugin as long as Custom Path is set
            if ("plugin.video.emby" in currentPath) and Settings.isCustomPathEnabled():
                return False
            return True
        return False

    @staticmethod
    def isMovieSet():
        #folderPathId = "videodb://movies/sets/"
        return xbmc.getCondVisibility("!IsEmpty(ListItem.DBID) + ListItem.IsCollection")


##############################
# Stores Various Settings
##############################
class Settings():
    @staticmethod
    def reloadSettings():
        # Force the reload of the settings to pick up any new values
        global ADDON
        ADDON = xbmcaddon.Addon(id='service.tvtunes')

    # Checks if the given file is names as a video file
    @staticmethod
    def isVideoFile(filename):
        if filename in [None, ""]:
            return False
        if filename.lower().endswith('.mp4'):
            return True
        if filename.lower().endswith('.mkv'):
            return True
        if filename.lower().endswith('.avi'):
            return True
        if filename.lower().endswith('.mov'):
            return True
        if filename.lower().endswith('.m2ts'):
            return True
        if filename.lower().endswith('.webm'):
            return True
        return False

    @staticmethod
    def isThemePlayingEnabled():
        return ADDON.getSetting("enableThemePlaying") == 'true'

    @staticmethod
    def isCustomPathEnabled():
        return ADDON.getSetting("custom_path_enable") == 'true'

    @staticmethod
    def getCustomPath():
        return ADDON.getSetting("custom_path")

    @staticmethod
    def getThemeVolume():
        return int(float(ADDON.getSetting("volume")))

    @staticmethod
    def isLoop():
        return ADDON.getSetting("loop") == 'true'

    @staticmethod
    def isFadeOut():
        return ADDON.getSetting("fadeOut") == 'true'

    @staticmethod
    def isFadeIn():
        return ADDON.getSetting("fadeIn") == 'true'

    @staticmethod
    def isSmbEnabled():
        return ADDON.getSetting("smb_share") == 'true'

    @staticmethod
    def getSmbUser():
        if ADDON.getSetting("smb_login"):
            return ADDON.getSetting("smb_login")
        else:
            return "guest"

    @staticmethod
    def getSmbPassword():
        if ADDON.getSetting("smb_psw"):
            return ADDON.getSetting("smb_psw")
        else:
            return "guest"

    # Calculates the regular expression to use to search for theme files
    @staticmethod
    def getThemeFileRegEx(searchDir=None, extensionOnly=False, audioOnly=False, videoOnly=False):
        fileTypes = ""
        if not videoOnly:
            fileTypes = "mp3"  # mp3 is the default that is always supported
            if(ADDON.getSetting("wma") == 'true'):
                fileTypes = fileTypes + "|wma"
            if(ADDON.getSetting("flac") == 'true'):
                fileTypes = fileTypes + "|flac"
            if(ADDON.getSetting("m4a") == 'true'):
                fileTypes = fileTypes + "|m4a"
            if(ADDON.getSetting("wav") == 'true'):
                fileTypes = fileTypes + "|wav"
            if(ADDON.getSetting("wav") == 'true'):
                fileTypes = fileTypes + "|wav"
        if not audioOnly:
            videoFileTypes = Settings.getVideoThemeFileExtensions()
            if videoFileTypes not in [None, ""]:
                if len(fileTypes) > 0:
                    fileTypes = fileTypes + '|'
                fileTypes = fileTypes + videoFileTypes
        themeRegEx = '(theme[ _A-Za-z0-9.-]*.(' + fileTypes + ')$)'
        # If using the directory method then remove the requirement to have "theme" in the name
        if (searchDir is not None) and Settings.isThemeDirEnabled():
            # Make sure this is checking the theme directory, not it's parent
            if searchDir.endswith(Settings.getThemeDirectory()):
                extensionOnly = True
        # See if we do not want the theme keyword
        if extensionOnly:
            themeRegEx = '(.(' + fileTypes + ')$)'
        return themeRegEx

    # Calculates the regular expression to use to search for trailer video files
    @staticmethod
    def getTrailerFileRegEx():
        fileTypes = ""
        videoFileTypes = Settings.getVideoThemeFileExtensions()
        if videoFileTypes not in [None, ""]:
            if len(fileTypes) > 0:
                fileTypes = fileTypes + '|'
            fileTypes = fileTypes + videoFileTypes
        return '(-trailer[ _A-Za-z0-9.-]*.(' + fileTypes + ')$)'

    @staticmethod
    def getVideoThemeFileExtensions():
        fileTypes = []
        if(ADDON.getSetting("mp4") == 'true'):
            fileTypes.append("mp4")
        if(ADDON.getSetting("mkv") == 'true'):
            fileTypes.append("mkv")
        if(ADDON.getSetting("avi") == 'true'):
            fileTypes.append("avi")
        if(ADDON.getSetting("mov") == 'true'):
            fileTypes.append("mov")
        if(ADDON.getSetting("m2ts") == 'true'):
            fileTypes.append("m2ts")
        if(ADDON.getSetting("webm") == 'true'):
            fileTypes.append("webm")
        return '|'.join(fileTypes)

    @staticmethod
    def isShuffleThemes():
        return ADDON.getSetting("shuffle") == 'true'

    @staticmethod
    def isRandomStart():
        return ADDON.getSetting("random") == 'true'

    @staticmethod
    def getRandomFixedOffset(filename):
        if not Settings.isRandomStart() or (filename in [None, ""]):
            return -1
        fixedOffsetSetting = "randomFixedAudioOffset"
        if Settings.isVideoFile(filename):
            fixedOffsetSetting = "randomFixedVideoOffset"
        return int(float(ADDON.getSetting(fixedOffsetSetting)))

    @staticmethod
    def isPlayMovieList():
        return ADDON.getSetting("movielist") == 'true'

    @staticmethod
    def isPlaySetsList():
        return ADDON.getSetting("setslist") == 'true'

    @staticmethod
    def isPlayTvShowList():
        return ADDON.getSetting("tvlist") == 'true'

    @staticmethod
    def isPlayMusicVideoList():
        return ADDON.getSetting("musicvideolist") == 'true'

    @staticmethod
    def isPlayVideoInformation():
        return ADDON.getSetting("videoInformation") == 'true'

    @staticmethod
    def isPlayTvShowSeasons():
        return ADDON.getSetting("tvShowSeasons") == 'true'

    @staticmethod
    def isPlayTvShowEpisodes():
        return ADDON.getSetting("tvShowEpisodes") == 'true'

    @staticmethod
    def isPlayMusicList():
        return ADDON.getSetting("musiclist") == 'true'

    @staticmethod
    def getPlayDurationLimit():
        return int(float(ADDON.getSetting("endafter")))

    @staticmethod
    def getTrackLengthLimit():
        return int(float(ADDON.getSetting("trackLengthLimit")))

    # Check if the video info button should be hidden
    @staticmethod
    def hideVideoInfoButton():
        return ADDON.getSetting("showVideoInfoButton") != 'true'

    # Check the delay start value
    @staticmethod
    def getStartDelaySeconds(themeFile=None):
        # check if this is a video file as the delay may be different
        if Settings.isVideoFile(themeFile):
            return int(float(ADDON.getSetting("delayVideoStart")))
        return int(float(ADDON.getSetting("delayStart")))

    @staticmethod
    def isThemeDirEnabled():
        # Theme sub directory only supported when not using a custom path
        if Settings.isCustomPathEnabled():
            return False
        return ADDON.getSetting("searchSubDir") == 'true'

    @staticmethod
    def getThemeDirectory():
        # Load the information about storing themes in sub-directories
        # Only use the Theme dir if custom path is not used
        return ADDON.getSetting("subDirName")

    @staticmethod
    def getStartupVolume():
        # Check to see if the volume needs to be changed when the system starts
        if ADDON.getSetting("resetVolumeOnStartup") == 'true':
            return int(float(ADDON.getSetting("resetStartupVolumeValue")))
        return -1

    @staticmethod
    def isVideoThemesOnlyIfOneExists():
        index = int(ADDON.getSetting("playVideoThemeRules"))
        if index == 2:
            return True
        return False

    @staticmethod
    def isVideoThemesFirst():
        index = int(ADDON.getSetting("playVideoThemeRules"))
        if index == 1:
            return True
        return False

    @staticmethod
    def useTrailers():
        return ADDON.getSetting("useTrailers") == "true"

    @staticmethod
    def onlyPlaySingleTheme():
        return ADDON.getSetting("singleThemeOnly") == 'true'

    @staticmethod
    def isRepeatSingleAudioAfterVideo():
        if ADDON.getSetting("repeatSingleAudioAfterVideo") == 'true':
            if Settings.isVideoThemesFirst():
                return True
        return False

    @staticmethod
    def showOnContextMenu():
        return ADDON.getSetting("showOnContextMenu") == "true"

    @staticmethod
    def blockRefreshRateChange():
        return ADDON.getSetting("blockChangeInRefreshRate") == "true"
