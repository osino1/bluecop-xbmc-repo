#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, urllib2, cookielib
import string, os, re, time, datetime, math, time, unicodedata

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import demjson

import unicodedata

import facebook
from facebook import GraphAPIError, GraphWrapAuthError

import mechanize

pluginhandle = int(sys.argv[1])
xbmcplugin.setContent(pluginhandle, 'musicvideos')

addon = xbmcaddon.Addon('plugin.video.vevo')
pluginpath = addon.getAddonInfo('path')
datapath = xbmc.translatePath('special://profile/addon_data/plugin.video.vevo/')

BASE = 'http://www.vevo.com'
COOKIEFILE = os.path.join(pluginpath,'resources','vevo-cookies.lwp')
#USERFILE = os.path.join(pluginpath,'resources','userfile.js')
FAVFILE = os.path.join(datapath,'favs.json')

fanart = os.path.join(pluginpath,'fanart.jpg')
vicon = os.path.join(pluginpath,'icon.png')
maxperpage=(int(addon.getSetting('perpage'))+1)*25

# Root listing

def listCategories():
    if (addon.getSetting('latitude') == 'Lookup by IP') and (addon.getSetting('latitude') == 'Lookup by IP'):
        setLocation()
    #addDir('Featured',    'http://api.vevo.com/mobile/v2/featured/carousel.json?extended=true',   '')
    addDir('Premieres',   'http://api.vevo.com/mobile/v1/video/list.json?ispremiere=true',        'listVideos')
    if (addon.getSetting('latitude') <> '') or (addon.getSetting('latitude') <> ''):
        addDir('Trending',        '',                                                 'Trending')
    addDir('Videos by Genre',       'http://api.vevo.com/mobile/v1/video/list.json',                'rootVideos')
    addDir('Artists by Genre',            'http://api.vevo.com/mobile/v1/artist/list.json',         'rootArtists')
    if (addon.getSetting('latitude') <> '') or (addon.getSetting('latitude') <> ''):
        addDir('Artists Touring Nearby',          '',                                               'toursRightNow')
    cm = []
    u=sys.argv[0]+"?url="+urllib.quote_plus('')+"&mode="+urllib.quote_plus('rematchArtists')+'&page='+str(1)
    cm.append( ('Rematch Library Artists', "XBMC.RunPlugin(%s)" % u) )
    u=sys.argv[0]+"?url="+urllib.quote_plus('')+"&mode="+urllib.quote_plus('deletefavArtists')+'&page='+str(1)
    cm.append( ('Delete All Artists', "XBMC.RunPlugin(%s)" % u) )
    addDir('Favorite Artists',         '',                                                          'favArtists' , cm=cm)
    addDir('Playlists',        'http://api.vevo.com/mobile/v1/featured/staffpicks.json',            'rootPlaylists')
    addDir('Staff Picks',        '',                                                                'listStaffPicks')
    addDir('Shows',               'http://api.vevo.com/mobile/v1/show/list.json?',                  'rootShows')
    addDir('Search',             '',                                                                'searchArtists')
    #addDir('Search Videos',      '',                                                                'searchVideos')
    #addDir('Search Artists',     '',                                                                'searchArtists')
    xbmcplugin.endOfDirectory(pluginhandle)

def listStaffPicks():
    addDir('Video Picks',        'http://api.vevo.com/mobile/v1/featured/TopVideos.json?',          'listVideos')
    addDir('Playlist Picks',     'http://api.vevo.com/mobile/v3/featured/TopPlaylists.json?',       'listPlaylists')
    xbmcplugin.endOfDirectory(pluginhandle)

def Trending():
    addDir('Being Watched',        '',                                                 'watchingRightNowIn')
    addDir('Trending Now',         '',                                                 'TrendingRightNowIn')
    xbmcplugin.endOfDirectory(pluginhandle)
  


# Video listings
def rootVideos():
    videos_url = params['url']
    addGenres(videos_url, 'sortByVideo')
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def sortByVideo():
    url = params['url']
    addDir('Most Viewed',   url+'&order=MostViewed',      'sortWhenVideo')
    addDir('Most Liked',    url+'&order=MostFavorited',   'sortWhenVideo')
    addDir('Most Recent',   url+'&order=MostRecent',      'listVideos')
    addDir('Surprise Me',   url+'&order=Random',          'listVideos')
    xbmcplugin.endOfDirectory(pluginhandle)

def sortWhenVideo():
    url = params['url']
    if 'MostFavorited' in url:
        name = 'Most Liked'
    elif 'MostViewed' in url:
        name = 'Most Viewed'
    addDir(name+' Today',         url+'Today',      'listVideos')
    addDir(name+' This Week' ,    url+'ThisWeek',   'listVideos')
    addDir(name+' This Month',    url+'ThisMonth',  'listVideos')
    addDir(name+' All-Time',      url+'AllTime',    'listVideos')
    xbmcplugin.endOfDirectory(pluginhandle)
    
def listVideos(url = False,playlist=False,playall=False):
    #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_UNSORTED)
    #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_GENRE)
    #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_ALBUM)
    if not url:
        url = params['url']
    max = maxperpage
    page = int(params['page'])
    offset = (page-1)*max
    fetch_url=url+'&offset='+str(offset)+'&max='+str(max)+'&extended=true'
    data = getURL(fetch_url)
    if data:
        if playlist:
            videos = demjson.decode(data)['result']['videos']
        else:
            videos = demjson.decode(data)['result']
        total = len(videos)
        if playall:
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            playlist.clear()        
        elif playlist is False:
            total = len(videos)
            if total >= max:
                addDir('*Next Page*', url,    'listVideos', page=str(page+1))
            addDir('*Play All*', url, 'playAll',folder=False)
        for video in videos:
            cm=[]
            video_id = video['isrc']
            try:title = video['title'].encode('utf-8')
            except: title = ''
            video_image = video['image_url']
            duration = video['duration_in_seconds']
            try:year = int(video['video_year'])
            except:year = 0
            
            if video.has_key('credit'):
                credits = video['credit']
                genre = ''
                recordlabel = ''
                try:
                    for credit in credits:
                        if credit['Key'] == 'Genre':
                            genre = credit['Value']
                        #elif credit['Key'] == 'Producer':
                        #    pass
                        #elif credit['Key'] == 'Director':
                        #    pass
                        #elif credit['Key'] == 'Composer':
                        #    pass
                        elif credit['Key'] == 'Record Label':
                            recordlabel = credit['Value']
                except:
                      genre = credits['Genre']
                      recordlabel = credits['Record Label']
            else:
                genre = ''
                recordlabel = ''
    
            if len(video['artists_main']) > 0:
                artistdata = video['artists_main'][0]
                artist_id = artistdata['id']
                artist_name = artistdata['name'].encode('utf-8')
                artist_image = artistdata['image_url']
                artist_url = 'http://api.vevo.com/mobile/v1/artist/%s/videos.json?order=MostRecent' % artist_id
                u=sys.argv[0]+"?url="+urllib.quote_plus(artist_url)+"&mode="+urllib.quote_plus('listVideos')+'&page='+str(1)
                cm.append( ('More %s Videos' % artist_name, "Container.Update(%s)" % u) )
                artist_url = 'http://api.vevo.com/mobile/v1/artist/%s.json' % artist_id
                u=sys.argv[0]+"?url="+urllib.quote_plus(artist_url)+"&mode="+urllib.quote_plus('addfavArtists')+'&page='+str(1)
                cm.append( ('Add %s to Favorites' % artist_name, "XBMC.RunPlugin(%s)" % u) )
            else:
                artist_name = ''
                artist_image = ''
        
            if len(video['artists_featured']) > 0:
                feats=''
                for featuredartist in video['artists_featured']:
                    featuredartist_id = featuredartist['id']
                    #featuredartist_image = featuredartist['image_url']
                    featuredartist_name = featuredartist['name'].encode('utf-8')
                    feats= featuredartist_name+', '
                    artist_url = 'http://api.vevo.com/mobile/v1/artist/%s/videos.json?order=MostRecent' % featuredartist_id
                    u=sys.argv[0]+"?url="+urllib.quote_plus(artist_url)+"&mode="+urllib.quote_plus('listVideos')+'&page='+str(1)
                    cm.append( ('More %s Videos' % featuredartist_name, "Container.Update(%s)" % u) )
                    artist_url = 'http://api.vevo.com/mobile/v1/artist/%s.json' % featuredartist_id
                    u=sys.argv[0]+"?url="+urllib.quote_plus(artist_url)+"&mode="+urllib.quote_plus('addfavArtists')+'&page='+str(1)
                    cm.append( ('Add %s to Favorites' % featuredartist_name, "XBMC.RunPlugin(%s)" % u) )
                feats=feats[:-2]
                artist = artist_name+' feat. '+feats
            else:
                artist = artist_name
            u = sys.argv[0]
            u += '?url='+urllib.quote_plus(video_id)
            u += '&mode='+urllib.quote_plus('playVideo')
            displayname = artist+' - '+title
            item=xbmcgui.ListItem(displayname, iconImage=video_image, thumbnailImage=video_image)
            item.setInfo( type="Music", infoLabels={ "Title":title,
                                                     "Artist":artist,
                                                     "Duration":duration,
                                                     "Album":recordlabel,
                                                     "Studio":recordlabel,
                                                     "Genre":genre,
                                                     "Year":year})
            item.setProperty('fanart_image',artist_image)
            item.setProperty('IsPlayable', 'true')
            item.addContextMenuItems( cm )
            if playall:
                playlist.add(url=u, listitem=item)
            else:
                xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)#,totalItems=total)
        if playall:
            xbmc.Player().play(playlist)
        else:
            xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
            setView()

def playAll():
    listVideos(params['url'],playall=True)
    
# common genre listing for artists and videos
def addGenres(url,mode):
    data = getURL('http://api.vevo.com/mobile/v1/genre/list.json?culture=en_US')
    genres = demjson.decode(data)['result']
    addDir('All Genres', url+'?', mode)
    for genre in genres:
        name = genre['Value']
        furl = url+'?genres='+genre['Key']
        addDir(name, furl, mode)

# Artist listings
def rootArtists():
    artist_url = params['url']
    addGenres(artist_url, 'sortByArtists')
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def sortByArtists():
    url = params['url']
    #addDir('Alphabetical',  url+'&order=Alphabetic',      'listAZ')
    addDir('Most Viewed',   url+'&order=MostViewed',      'sortWhenArtists')
    addDir('Most Liked',    url+'&order=MostFavorited',   'sortWhenArtists')
    addDir('Most Recent',   url+'&order=MostRecent',      'listArtists')
    addDir('Surprise Me',   url+'&order=Random',          'listArtists')
    xbmcplugin.endOfDirectory(pluginhandle)

def sortWhenArtists():
    url = params['url']
    if 'MostFavorited' in url:
        name = 'Most Liked'
    elif 'MostViewed' in url:
        name = 'Most Viewed'
    addDir(name+' Today',         url+'Today',      'listArtists')
    addDir(name+' This Week' ,    url+'ThisWeek',   'listArtists')
    addDir(name+' This Month',    url+'ThisMonth',  'listArtists')
    addDir(name+' All-Time',      url+'AllTime',    'listArtists')
    xbmcplugin.endOfDirectory(pluginhandle)

def listAZ():
    url = params['url']
    addDir('#', url+'&alpha='+urllib.quote_plus('#'), 'listVideos')
    alphabet=set(string.ascii_uppercase)
    for letter in alphabet:
        addDir(letter, url+'&alpha='+str(letter), 'listArtists')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle)

def listArtists(url = False):
    if not url:
        url = params['url']
    max = maxperpage
    page = int(params['page'])
    offset = (page-1)*max
    fetch_url=url+'&offset='+str(offset)+'&max='+str(max)
    data = getURL(fetch_url)
    artists = demjson.decode(data)['result']
    total = len(artists)
    if total >= max:
        addDir('*Next Page*', url,    'listArtists', page=str(page+1))
    for artist in artists:
        artist_id = artist['id']
        artist_name = artist['name']
        artist_image = artist['image_url']
        video_count = artist['video_count']
        url = 'http://api.vevo.com/mobile/v1/artist/'+artist_id+'/videos.json?order=MostRecent'
        display_name=artist_name+' ('+str(video_count)+')'
        cm = []
        artist_url = 'http://api.vevo.com/mobile/v1/artist/%s.json' % artist_id
        u=sys.argv[0]+"?url="+urllib.quote_plus(artist_url)+"&mode="+urllib.quote_plus('addfavArtists')+'&page='+str(1)
        cm.append( ('Add %s to Favorites' % artist_name, "XBMC.RunPlugin(%s)" % u) )
        addDir(display_name, url, 'listVideos', iconimage=artist_image, total=total, cm=cm)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
    setView()

# Playlist listings
def rootPlaylists():
    addDir('Top Playlists',        'http://api.vevo.com/mobile/v1/featured/staffpicks.json',        'listPlaylists')
    if addon.getSetting('login_name') <> '' and addon.getSetting('login_pass') <> '':
        if addon.getSetting('getnewtoken') == 'true':
            if getFBAuth():
                getVEVOAccount()
                addon.setSetting(id='getnewtoken',value='false')
        if addon.getSetting('session_token'):
            addDir('My Playlists',         'http://api.vevo.com/mobile/v1/userplaylists.json?',             'userPlaylists')
            #friendPlaylists('http://api.vevo.com/mobile/v1/user/getfacebookfriends.json?')
            addDir('My Friends',           'http://api.vevo.com/mobile/v1/user/getfacebookfriends.json?',   'friendPlaylists')
    xbmcplugin.endOfDirectory(pluginhandle)

def userPlaylists():
    #url = 'http://api.vevo.com/mobile/v1/userplaylists/%s/list.json' %
    listPlaylists(VEVOToken=True)
    
def friendPlaylists(url = False):
    if not url:
        url = params['url']
    sendtoken = 'accessToken='+addon.getSetting(id='fbtoken')
    data = getURL(url, postdata=sendtoken, VEVOToken=True)
    print data
    friends = demjson.decode(data)['result']['friends_on_vevo']
    total = len(friends)
    for friend in friends:
        url = 'http://api.vevo.com/mobile/v1/userplaylists/%s/list.json' % friend['vevo_id']
        name = friend['name']
        addDir(name, url, 'listPlaylistsToken', total=total)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
    
def listPlaylistsToken():
    listPlaylists(VEVOToken=True)

def listPlaylists(url = False, VEVOToken=False):
    if not url:
        url = params['url']
    #max = maxperpage
    #page = int(params['page'])
    #offset = (page-1)*max1
    #fetch_url=url+'&offset='+str(offset)+'&max='+str(max)#+'&extended=true'
    #data = getURL(fetch_url)
    data = getURL(url,VEVOToken=VEVOToken)
    playlists = demjson.decode(data)['result']
    total = len(playlists)
    #if total >= max:
    #    addDir('*Next Page*', url,    'listPlaylists', page=str(page+1))
    for playlist in playlists:
        try:playlist_id = playlist['playlist_id']
        except:playlist_id = str(playlist['id'])
        playlist_name = playlist['title']
        playlist_image = playlist['image_url']
        video_count = playlist['videocount']
        display_name=playlist_name+' ('+str(video_count)+')'
        addDir(display_name, playlist_id, 'playlistRoot', iconimage=playlist_image, total=total)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def playlistRoot():
    playlist_id = params['url']
    if playlist_id.isdigit():
        url = 'http://api.vevo.com/mobile/v1/playlist/'+playlist_id+'.json?'
    else:
        url = 'http://api.vevo.com/mobile/v2/playlist/'+playlist_id+'.json?'
    addDir('*Play*', url, 'playPlaylist',folder=False)
    listVideos(url,playlist=True)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def playPlaylist():
    listVideos(params['url'],playlist=True,playall=True)

# Show listings
def rootShows(url = False):
    xbmcplugin.setContent(pluginhandle, 'shows')
    if not url:
        url = params['url']
    max = maxperpage
    page = int(params['page'])
    offset = (page-1)*max
    fetch_url=url+'&offset='+str(offset)+'&max='+str(max)
    data = getURL(fetch_url)
    shows = demjson.decode(data)['result']
    total = len(shows)
    if total >= max:
        addDir('*Next Page*', url,    'listArtists', page=str(page+1))
    for show in shows:
        show_id = show['id']
        show_name = show['name']
        show_image = show['image_url']
        video_count = show['total_videos_count']
        description = show['description']
        url = 'http://api.vevo.com/mobile/v1/show/'+str(show_id)+'/videos.json?order=MostRecent'
        display_name=show_name+' ('+str(video_count)+')'
        addDir(display_name, url, 'listVideos', plot=description, iconimage=show_image, total=total)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

# Search
def searchVideos():
    Search('Videos')

def searchArtists():
    Search('Artists')

def researchArtists():
    listArtists(params['url'])
    
def researchVideos():
    listVideos(params['url'])

def Search(mode):
    keyb = xbmc.Keyboard('', 'Search '+mode)
    keyb.doModal()
    if keyb.isConfirmed():
            search = urllib.quote_plus(keyb.getText())
            vurl = 'http://api.vevo.com/mobile/v1/search/videos.json?q='+search
            aurl = 'http://api.vevo.com/mobile/v1/search/artists.json?q='+search
            if mode == 'Videos':
                addDir('*Artist Results*',aurl,'researchArtists')
                listVideos(vurl)
            elif mode == 'Artists':
                addDir('*Video Results*',vurl,'researchVideos')
                listArtists(aurl)

def searchBox():
    latitude = float(addon.getSetting('latitude')) 
    longitude = float(addon.getSetting('longitude'))
    radius = (int(addon.getSetting('radius'))+1)*100
    lon_min = longitude - radius / abs(math.cos(math.radians(latitude)) * 69)
    lon_max = longitude + radius / abs(math.cos(math.radians(latitude)) * 69)
    lat_min = latitude - (radius / 69)
    lat_max = latitude + (radius / 69)
    parameters = '?s='+str(lat_min)
    parameters += '&w='+str(lon_min)
    parameters += '&n='+str(lat_max)
    parameters += '&e='+str(lon_max)
    return parameters

def TrendingRightNowIn():             
    url  = 'http://api.vevo.com/mobile/v1/video/TrendingRightNowIn.json'+searchBox()
    listVideos(url)

def watchingRightNowIn():             
    url  = 'http://api.vevo.com/mobile/v1/video/watchingRightNowIn.json'+searchBox()
    listVideos(url)  

def toursRightNow():    
    url = 'http://api.vevo.com/mobile/v1/geo/toursrightnow.json'+searchBox()
    max = maxperpage
    page = int(params['page'])
    offset = (page-1)*max
    fetch_url=url+'&offset='+str(offset)+'&max='+str(max)#+'&extended=true'
    data = getURL(fetch_url)
    artists = demjson.decode(data)['result']
    total = len(artists)
    #if total >= max:
    #    addDir('*Next Page*', url,    'toursRightNow', page=str(page+1))
    for artist in artists:
        artist_id = artist['artistid']
        url = 'http://api.vevo.com/mobile/v1/artist/'+artist_id+'/videos.json?order=MostRecent'
        artist_name = artist['artist']['name'].encode('utf-8')
        artist_image = artist['artist']['image_url']
        city = artist['city'].encode('utf-8')
        venuename = artist['venuename'].encode('utf-8')
        startdate = artist['startdate']
        event_name = artist['eventname'].encode('utf-8')
        print event_name
        try:date = event_name.split('(')[1].strip(')')
        except:date = event_name.split(' ')[-1]
        final_name = date+' : '+city+' - '+artist_name+' @ '+venuename
        addDir(final_name, url, 'listVideos', iconimage=artist_image, total=total)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
    xbmc.executebuiltin("Container.SetViewMode(51)")


def favArtists():
    if not os.path.isfile(FAVFILE):
        SaveFile( FAVFILE, demjson.encode( matchedArtists() ) )
    if os.path.isfile(FAVFILE):
        artists = demjson.decode(OpenFile(FAVFILE))
        total = len(artists)
        for artist in artists:
            artist_id = artist['id']
            artist_name = artist['name']
            artist_image = artist['image_url']
            video_count = artist['video_count']
            url = 'http://api.vevo.com/mobile/v1/artist/'+artist_id+'/videos.json?order=MostRecent'
            display_name=artist_name+' ('+str(video_count)+')'
            cm = []
            u=sys.argv[0]+"?url="+urllib.quote_plus(artist_id)+"&mode="+urllib.quote_plus('removefavArtists')+'&page='+str(1)
            cm.append( ('Remove %s from Favorites' % artist_name, "XBMC.RunPlugin(%s)" % u) )
            addDir(display_name, url, 'listVideos', iconimage=artist_image, total=total, cm=cm)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)
        setView()
        
def addfavArtists():
    artists = demjson.decode(OpenFile(FAVFILE))
    add = demjson.decode(getURL(params['url']))['result']
    for artist in artists:
        if artist['id'] == add['id']:
            return xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Duplicate', 'Duplicate Artist', 5000) )
    artists.append(add)
    SaveFile( FAVFILE, demjson.encode( artists ) )
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Success', 'Added Artist', 5000) )

def removefavArtists():
    artists = demjson.decode(OpenFile(FAVFILE))
    for artist in artists:
        if params['url'] == artist['id']:
            artists.pop(artists.index(artist))
            SaveFile( FAVFILE, demjson.encode( artists ) )
            xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Success', 'Deleted Artist', 5000) )
            xbmc.executebuiltin("Container.Refresh()")
    
def deletefavArtists():
    os.remove(FAVFILE)
    # FORCE BLANK FAV
    #artists = []
    #SaveFile( FAVFILE, demjson.encode( artists ) )
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Success', 'Deleted Favorite Artists', 10000) )
    
def rematchArtists():
    if os.path.isfile(FAVFILE):
        artists = demjson.decode(OpenFile(FAVFILE))
    else:
        artists = []
    aids = []
    for artist in artists:
        aids.append(artist['id']) 
    for martist in matchedArtists():
        if martist['id'] not in aids:
            artists.append(martist)
    SaveFile( FAVFILE, demjson.encode( artists ) )
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( 'Success', 'Library Artists Added', 10000) )

def matchedArtists():
    url = 'http://api.vevo.com/mobile/v1/search/artistmatch.json'
    json_query = {}
    json_list = []
    for artist in getLibraryArtists():
        artistjson = {'songCount':1,
                      'query':artist}
        json_list.append(artistjson)
    json_query['query']=json_list 
    json_query['last_batch']='true'
    json_query = demjson.encode(json_query)
    data = getURL( url , postdata=json_query, extendTimeout=60)
    artists = demjson.decode(data)['result']
    total = len(artists)
    returns = []
    for artist in artists:
        returns.append(artist['artist'])
    return returns
      
def getLibraryArtists():
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetArtists", "id": 1}')
    json_response = demjson.decode(json_query)
    artistlist = []
    if json_response['result']:
        for item in json_response['result']['artists']:
            artistname = cleanartists(item['label'])
            artistlist.append(artistname)
    return artistlist
    
# Play Video
def playVideo():
    playlistVideo()

def playlistVideo():
    if addon.getSetting('defaultyoutube') == 'true':
        try:YouTube()
        except:HTTPDynamic()
    else:  
        try:HTTPDynamic()
        except:YouTube()

def HTTPDynamic():
    item = xbmcgui.ListItem(path=getVideo(params['url']))
    xbmcplugin.setResolvedUrl(pluginhandle, True, item) 
    if addon.getSetting('unpause') == 'true':
        sleeptime = int(addon.getSetting('unpausetime'))+1
        time.sleep(sleeptime)
        xbmc.Player().pause()


def getLyrics(vevoID):
    url = 'http://www.vevo.com/data/VideoLyrics/'+vevoID
    data = getURL(url)
    json = demjson.decode(data)
    lyrics = json['Text'].replace('\r','').split('\n')
    for lyric in lyrics:
        print lyric.strip()

def YouTube():
    vevoID = params['url'].split('/')[-1]
    url = 'http://videoplayer.vevo.com/VideoService/AuthenticateVideo?isrc=%s' % vevoID
    data = getURL(url)
    youtubeID = demjson.decode(data)['video']['videoVersions'][0]['id']
    youtubeurl = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % youtubeID
    item = xbmcgui.ListItem(path=youtubeurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
     
def getVideo(pageurl):
    quality = [564000, 864000, 1328000, 1728000, 2528000, 3328000, 4392000, 5392000]
    select = int(addon.getSetting('bitrate'))
    maxbitrate = quality[select]
    vevoID = pageurl.split('/')[-1]
    url = 'http://smilstream.vevo.com/HDFlash/v1/smil/%s/%s.smil' % (vevoID,vevoID.lower())
    data = getURL(url)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    videobase = tree.find(attrs={'name':'httpBase'})['content']
    videos = tree.findAll('video')
    filenames = ''
    number = len(videos) - 1
    if number < select:
        select = number
    if '_' in videos[number]:
        for video in videos:
            filepath = video['src']
            path = filepath.split('_')[0]
            filename = filepath.replace(path,'').replace('.mp4','')
            filenames += filename+','
    else:
        for video in videos:
            filepath = video['src']
            filename = filepath.split('/')[-1]
            path = filepath.replace(filename,'')
            filenames += filename.replace('.mp4','')+','              
    finalUrl = videobase+path+','+filenames+'.mp4.csmil/bitrate='+str(select)+'?seek=0'
    return finalUrl

# Common
def addDir(name, url, mode, plot='', iconimage=vicon ,folder=True,total=0,page=1,cm=False):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)+'&page='+str(page)
    item=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    if iconimage <> vicon:
        item.setProperty('fanart_image',iconimage)
    else:
        item.setProperty('fanart_image',fanart)
    item.setInfo( type="Video", infoLabels={ "Title":name,
                                             "plot":plot
                                           })
    if cm:
        item.addContextMenuItems( cm )
    return xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=folder,totalItems=total)

def setView():
    confluence_views = [50,500,511]
    if addon.getSetting('viewenable') == 'true':
        view=int(addon.getSetting('defaultview'))
        xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")

def setLocation():
    try:
        url = 'http://www.geobytes.com/IpLocator.htm?GetLocation&template=json.txt'
        data = getURL(url)
        locationdata = demjson.decode(data)['geobytes']
        addon.setSetting(id='latitude',value=str(locationdata['latitude']))
        addon.setSetting(id='longitude',value=str(locationdata['longitude']))
    except:
        addon.setSetting(id='latitude',value='')
        addon.setSetting(id='longitude',value='')

def newGraph(email,password,uid=None,token=None,new_token_callback=None):
    graph = facebook.GraphWrap(token,new_token_callback=new_token_callback)
    graph.setAppData('184548202936',scope='email,user_birthday,user_likes,user_interests,publish_actions')
    graph.setLogin(email,password,uid)
    return graph

def getFBAuth():
    email = addon.getSetting("login_name")
    password = addon.getSetting("login_pass")
    cj = cookielib.LWPCookieJar()
    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.set_cookiejar(cj)
    user = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0'
    #user = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Mobile/9A405'
    br.addheaders = [('User-agent', user)]
    #redirect = urllib.quote('fbconnect://success')
    redirect = urllib.quote('https://www.vevo.com')
    scope = urllib.quote('email,user_birthday,user_likes,user_interests,publish_actions')
    url = 'https://graph.facebook.com/oauth/authorize?client_id=184548202936&local_client_id=vevo&redirect_uri=%s&type=user_agent&scope=%s&sdk=ios&display=touch' % (redirect,scope)
    print url
    br.open(url)
    response = br.response()
    headers = response.info()
    headers["Content-type"] = "text/html; charset=utf-8"
    response.set_data(response.get_data().replace('<?xml version="1.0" encoding="utf-8"?>',''))
    br.set_response(response)
    br.select_form(nr=0)  
    br["email"] = email
    br["pass"] = password
    logged_in = br.submit()
    url = logged_in.geturl()
    print logged_in.read()
    print url
    graph = newGraph(email, password)
    token = graph.extractTokenFromURL(url)
    print token
    if graph.tokenIsValid(token):
        addon.setSetting(id='fbtoken',value=token)
        return True
    else:
        return False
        
def getVEVOAccount():
    url = 'http://api.vevo.com/mobile/v1/user/facebookauth.json'
    sendtoken = {}
    sendtoken['accessToken'] = addon.getSetting(id='fbtoken')
    data = getURL( url , postdata=demjson.encode(sendtoken), VEVOKey=True)
    json = demjson.decode(data)
    addon.setSetting(id='vevo_user_id',value=json['user_id'])
    addon.setSetting(id='session_token',value=json['session_token'])

def getURL( url , postdata=False, extendTimeout=False, VEVOToken=False, VEVOKey=False):
    try:
        print 'VEVO --> common :: getURL :: url = '+url
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'VEVO 1.5 rv:5529 (iPad; iPhone OS 5.0.1; en_US)')]
        if VEVOToken:
            opener.addheaders = [('X-VEVO-Session-Token', addon.getSetting('session_token') )]
        if VEVOKey:
            opener.addheaders = [('X-VEVO-Private-Key', 'G05bmz9x--_6-J-qpR4_' )]
        if postdata:
            if extendTimeout <> False:
                try:usock=opener.open(url,postdata,extendTimeout)
                except:usock=opener.open(url,postdata)
            else:
                usock=opener.open(url,postdata)
        else:
            usock=opener.open(url)
        response=usock.read()
        usock.close()
        return response
    except urllib2.URLError, e:
        print 'Error reason: ', e
        heading = 'Error'
        message = e
        duration = 10000
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )
        return False

def _unicode( text, encoding='utf-8' ):
    try: text = unicode( text, encoding )
    except: pass
    return text

def cleanartists(name):    
    try: name = unicodedata.normalize( 'NFKD', _unicode( name ) ).encode( 'ascii', 'ignore' )
    except: pass
    return name.replace('"','').replace("'",'').replace('<','').replace('>','').replace('(','').replace(')','').replace('\n',' ').replace('-',' ')

def SaveFile(path, data):
    file = open(path,'w')
    file.write(data)
    file.close()

def OpenFile(path):
    file = open(path, 'r')
    contents=file.read()
    file.close()
    return contents

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=urllib.unquote_plus(splitparams[1])                                        
    return param

params=get_params()
try:
    mode=params["mode"]
except:
    mode=None
print "Mode: "+str(mode)
print "Parameters: "+str(params)

if mode==None:
    listCategories()
else:
    exec '%s()' % mode