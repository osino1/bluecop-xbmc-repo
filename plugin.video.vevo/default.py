#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, urllib2, cookielib
import string, os, re, time, datetime

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import demjson
import glob
import unicodedata 

pluginhandle = int(sys.argv[1])
xbmcplugin.setContent(pluginhandle, 'musicvideos')

addon = xbmcaddon.Addon('plugin.video.vevo')
pluginpath = addon.getAddonInfo('path')

BASE = 'http://www.vevo.com'
COOKIEFILE = os.path.join(pluginpath,'resources','vevo-cookies.lwp')
USERFILE = os.path.join(pluginpath,'resources','userfile.js')

# Root listing
def listCategories():
    logedin = login_cookie()
    addDir('Music Videos',  'http://www.vevo.com/videos',       'rootVideos')
    addDir('Search Videos', '',                                 'searchVideos')
    addDir('Artists',       'http://www.vevo.com/artists',      'rootArtists')
    addDir('Search Artists','',                                 'searchArtists')
    if logedin:
        addDir('My Playlists',  'http://www.vevo.com/user/profile/',             'myPlaylists')
    addDir('VEVO Playlists',     'http://www.vevo.com/playlists',    'rootPlaylists')
    addDir('Shows',         'http://www.vevo.com/shows',        'rootShows')
    addDir('Channels',      'http://www.vevo.com/channels',     'rootChannels')
    xbmcplugin.endOfDirectory(pluginhandle)

# Video listings
def rootVideos():
    videos_url = params['url']
    addGenres(videos_url, 'sortByVideo')
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def sortByVideo():
    url = params['url']
    if '?' in url:
        urlsplit = url.split('?')
        url = urlsplit[0]
        parameters = '?'+urlsplit[1]+'&'
    else:
        parameters = '?'
    addDir('Most Recent',   url+'/videosbrowse'+parameters+'order=MostRecent',      'listVideos')
    addDir('Most Liked',    url+'/videosbrowse'+parameters+'order=MostFavorited',   'sortWhenVideo')
    addDir('Most Viewed',   url+'/videosbrowse'+parameters+'order=MostViewed',      'sortWhenVideo')
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

def listVideos(url = False):
    if not url:
        url = params['url']
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    try:       
        nextitems = int(re.compile('javascript:Vevo\\.explore\\.show_more\\(.*?, (.*?)\\)').findall(data)[0])
        pagedisplay = ' ('+str(nextitems-59)+'-'+str(nextitems)+')'
        if '/videosbrowse' in url:
            addDir('*Next Page*'+pagedisplay,      url.replace('/videosbrowse?','/videos?page=2&'),    'listVideos')
        elif 'page=' in url:
            page = int(url.split('page=')[1].split('&')[0])
            nextpage = page + 1
            addDir('*Next Page*'+pagedisplay,      url.replace('page='+str(page),'page='+str(nextpage)),    'listVideos')
    except:
        pagedisplay = ''
    processVideos(tree)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def processVideos(tree,total=False):
    thumbs = tree.findAll(attrs={'class' : 'listThumb'})
    videos = tree.findAll(attrs={'class' : 'listContent'})
    if not total:
        total = len(videos)
    for video,thumb in zip(videos,thumbs):
        cm = []
        url = BASE+thumb.find(attrs={'class' : 'playOverlay video-link'})['href'].split('?')[0]
        thumbnail = thumb.img['src'].split('?')[0]
        tags = re.compile(r'<.*?>')
        spaces = re.compile(r'\s+')
        title = video.find('h4', attrs={'class' : 'ui-ellipsis'}).a.string.encode('utf-8')
        title = unicode(BeautifulSoup(title,convertEntities=BeautifulSoup.HTML_ENTITIES).contents[0]).encode( "utf-8" )
        artist = str(video.find('h5')).decode('utf-8').encode('utf-8')
        artist = tags.sub('', artist)
        artist = spaces.sub(' ', artist)
        artist = unicode(BeautifulSoup(artist,convertEntities=BeautifulSoup.HTML_ENTITIES).contents[0]).encode( "utf-8" )
        cm.append( ('Related Playlist', "XBMC.RunPlugin(%s?mode=relatedList&url=%s)" % ( sys.argv[0], urllib.quote_plus(url) ) ) )
        u = sys.argv[0]
        u += '?url='+urllib.quote_plus(url)
        u += '&mode='+urllib.quote_plus('playVideo')
        displayname = artist+' - '+title
        item=xbmcgui.ListItem(displayname, iconImage=thumbnail, thumbnailImage=thumbnail)
        item.setInfo( type="Music", infoLabels={ "Title":title,
                                                 "Artist":artist})
        item.addContextMenuItems( cm )
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False,totalItems=total)
    return total

# common genre listing for artists and videos
def addGenres(url,mode):
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    genres = tree.find('ul', attrs={'class':'left-navigation-genres'}).findAll('li',recursive=False)
    for genre in genres:
        gclass = genre['class']
        if 'view_more_genres' not in gclass:
            subgenres = genre.findAll('a')
            for subgenre in subgenres:
                url = BASE + subgenre['href']
                name = subgenre.string
                if 'Video Premieres' in name:
                    url = 'http://www.vevo.com/videos/videosbrowse/is-premiere?order=MostRecent'
                    addDir(name, url, 'listVideos')
                    continue
                if 'subgenre' in url:
                    name = ' - '+name
                addDir(name, url, mode)

# Artist listings
def rootArtists():
    artist_url = params['url']
    addGenres(artist_url, 'sortByArtists')
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def sortByArtists():
    url = params['url']
    if '?' in url:
        urlsplit = url.split('?')
        url = urlsplit[0]
        parameters = '?'+urlsplit[1]+'&'
    else:
        parameters = '?'
    addDir('Alphabetical',  url+'/artistsbrowse'+parameters+'order=Alphabetic&viewmode=list',      'listAZ')
    addDir('Most Recent',   url+'/artistsbrowse'+parameters+'order=MostRecent&viewmode=list',      'listArtists')
    addDir('Most Liked',    url+'/artistsbrowse'+parameters+'order=MostFavorited',   'sortWhenArtists')
    addDir('Most Viewed',   url+'/artistsbrowse'+parameters+'order=MostViewed',      'sortWhenArtists')
    xbmcplugin.endOfDirectory(pluginhandle)

def sortWhenArtists():
    url = params['url']
    if 'MostFavorited' in url:
        name = 'Most Liked'
    elif 'MostViewed' in url:
        name = 'Most Viewed'
    addDir(name+' Today',         url+'Today&viewmode=list',      'listArtists')
    addDir(name+' This Week' ,    url+'ThisWeek&viewmode=list',   'listArtists')
    addDir(name+' This Month',    url+'ThisMonth&viewmode=list',  'listArtists')
    addDir(name+' All-Time',      url+'AllTime&viewmode=list',    'listArtists')
    xbmcplugin.endOfDirectory(pluginhandle)

def listAZ():
    url = params['url']
    #addDir('#', url+'&alpha='+urllib.quote_plus('#'), 'listVideos')
    alphabet=set(string.ascii_uppercase)
    for letter in alphabet:
        addDir(letter, url+'&alpha='+str(letter), 'listArtists')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle)

def listArtists(url = False):
    if not url:
        url = params['url']
    data = getURL(url)
    try:
        nextitems = int(re.compile('javascript:Vevo\\.explore\\.show_more\\(.*?, (.*?)\\)').findall(data)[0])
        pagedisplay = ' ('+str(nextitems-100)+'-'+str(nextitems)+')'
    except:
        pagedisplay = ''
    if '&alpha=' in url:
        try:total = int(re.compile('<span class="itotal-items">(.*?)</span>').findall(data)[0].replace(',',''))
        except: total = 1
        processArtists(data,total)
        pages = (total/100)
        for i in range(pages):
            data = getURL(url.replace('/artistsbrowse?','/artists?page='+str(i+2)+'&'))
            processArtists(data,total)
    else:
        if '/artistsbrowse' in url:
            addDir('*Next Page*'+pagedisplay,      url.replace('/artistsbrowse?','/artists?page=2&'),    'listArtists')
        elif 'page=' in url:
            page = int(url.split('page=')[1].split('&')[0])
            nextpage = page + 1
            addDir('*Next Page*'+pagedisplay,      url.replace('page='+str(page),'page='+str(nextpage)),    'listArtists')
        processArtists(data)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def processArtists(data,total=False):
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    artists = tree.findAll(attrs={'class' : 'playOverlay'})
    if not total:
        total = len(artists)
    for artist in artists:
        url = BASE+artist['href']
        thumbnail = artist.find('img')['src'].split('?')[0]
        try:title = artist.find('img')['title'].encode('utf-8')
        except:title = artist.find('img')['alt'].encode('utf-8')
        addDir(title, url, 'listArtistsVideos', iconimage=thumbnail, total=total)

def listArtistsVideos(url = False,total=False):
    if not url:
        url = params['url']
    data = getURL(url)
    artistid = re.compile("Vevo.pageData = { pageType: 'artistProfile', artistID: '(.*?)' };").findall(data)[0]
    page1 = 'http://www.vevo.com/videos/artist/'+artistid
    listArtistsVideos2(page1,artistid)
    
def listArtistsVideos2(url,artistid,pagenumber=False):
    data = getURL(url) 
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    total = processVideos(tree)
    if 'Show More Videos' in data:
        if pagenumber:
            pagenumber += 1
        else:
            pagenumber = 2
        nextpage = 'http://www.vevo.com/videos/artistvideos/'+artistid+'?page='+str(pagenumber)
        listArtistsVideos2(nextpage,artistid,pagenumber)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

# Playlist listings
def rootPlaylists():
    url = params['url']
    addGenres(url, 'listPlaylists')
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True) 
    
def myPlaylists():
    url = params['url']
    userfile = open(USERFILE, "r")
    userdata = userfile.read()
    userfile.close()
    userid = demjson.decode(userdata)['userId']
    url += str(userid)
    listPlaylists(url)
    
def listPlaylists(url = False):
    if not url:
        url = params['url'].replace('/playlists','/playlists/playlistsbrowse')
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    playlists = tree.findAll(attrs={'class' : 'listThumb'})
    for playlist in playlists:
        url = BASE+playlist.a['href']
        thumbnail = playlist.find('img')['src'].split('?')[0]
        title = playlist.find('img')['alt']
        addDir(title, url, 'playPlaylist', iconimage=thumbnail,folder=False)
    if 'Show More Playlists' in data:
        url2 = params['url'].replace('/playlists','/playlists/playlists')+'?page=2' 
        listPlaylists(url2)
    else:
        xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True) 

def playPlaylist():
    url = params['url']
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.findAll('meta',attrs={'property' : 'og:song','content':True})
    vids = ''
    for video in videos:
        vids += video['content'].split('/')[-1]+','
    vids = vids[:-1]
    infourl = 'http://www.vevo.com/Proxy/Video/GetData.ashx?isrc='+urllib.quote_plus(vids)
    data = getURL(infourl)
    playlistvideos = demjson.decode(data)
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    for video in videos:
        video = playlistvideos[video['content'].split('/')[-1]]
        artist = video['byline_text']
        title = video['video_name']
        thumbnail = video['image']
        url = BASE+video['video_url']
        u = sys.argv[0]
        u += '?url='+urllib.quote_plus(url)
        u += '&mode='+urllib.quote_plus('playlistVideo')
        displayname = artist+' - '+title
        item=xbmcgui.ListItem(displayname, iconImage=thumbnail, thumbnailImage=thumbnail)
        item.setInfo( type="Video", infoLabels={ "Title":displayname
                                                 #"Artist":artist
                                                 })
        item.setProperty('IsPlayable', 'true')
        playlist.add(url=u, listitem=item)
    xbmc.Player().play(playlist)

# Channel listings
def rootChannels(url = False,playlist=True):
    if not url:
        url = params['url']
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows = tree.findAll(attrs={'class' : 'listThumb'})
    for show in shows:
        url = BASE+show.a['href']
        thumbnail = show.find('img')['src'].split('?')[0]
        title = show.find('img')['title']
        if playlist:
            addDir(title, url, 'Channel', iconimage=thumbnail)
        else:
            addDir(title, url, 'listArtistsVideos', iconimage=thumbnail)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def Channel():
    url = params['url']
    addDir('Videos', url, 'listChannelVideos')
    addDir('Playlists', url+'/Playlists', 'ChannelPlaylists')
    xbmcplugin.endOfDirectory(pluginhandle)

def listChannelVideos(url = False,total=False):
    if not url:
        url = params['url']
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    processVideos(tree,total)
    try:
        nexturl = BASE+tree.find('a',attrs={'title' : 'Go to Next Page'})['href']
        del tree
        del data
        if not total:
            total = 60
        listChannelVideos(nexturl,total+60)
    except:
        xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def ChannelPlaylists():
    url = params['url']
    listPlaylists(url)
    
# Show listings
def rootShows():
    url = params['url']
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows = tree.findAll(attrs={'class' : 'listThumb'})
    for show in shows:
        url = BASE+show.a['href'].replace('/show/','/show/detailcontentlist/')
        thumbnail = show.find('img')['src'].split('?')[0]
        title = show.find('img')['title']
        addDir(title, url, 'listShowVideos', iconimage=thumbnail)
    xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

def listShowVideos(url = False,total=10):
    if not url:
        url = params['url']
    data = getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    processVideos(tree,total)
    more = tree.find('li',attrs={'class' : 'show-more'})
    if more <> None:
        if '?page=' in url:
            nextpage = int(url.split('?page=')[1])+1
            nexturl = url.split('?page=')[0]+'?page='+str(nextpage)
        else:
            nexturl  = url+'?page=2'
        del tree
        del data
        listShowVideos(nexturl,total+10)
    else:
        xbmcplugin.endOfDirectory(pluginhandle,cacheToDisc=True)

# Search
def searchVideos():
    Search('Videos')

def searchArtists():
    Search('Artists')    
    
def Search(mode):
        keyb = xbmc.Keyboard('', 'Search '+mode)
        keyb.doModal()
        if (keyb.isConfirmed()):
                search = urllib.quote_plus(keyb.getText())
                url = 'http://www.vevo.com/search?q='+search+'&content='+mode+'&page=1'
                if mode == 'Videos':
                    listVideos(url)
                elif mode == 'Artists':
                    rootChannels(url=url,playlist=False)
    
# Play Video
def playVideo():
    playlistVideo()
    if addon.getSetting('continousplay') == 'true':
        relatedList()

def relatedList():
    rmodes = ['a','b']
    index = int(addon.getSetting('relatedmode'))
    relatedmode = rmodes[index]
    url = 'http://www.vevo.com/related/video/'+params['url'].split('/')[-1]+'?source=watch&max=30&mode='+relatedmode
    data = getURL(url)
    relatedvideos = demjson.decode(data)
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    for video in relatedvideos:
        artist = video['byline_text']
        title = video['title']
        thumbnail = video['img']
        url = BASE+video['url'].split('?')[0]
        u = sys.argv[0]
        u += '?url='+urllib.quote_plus(url)
        u += '&mode='+urllib.quote_plus('playlistVideo')
        displayname = artist+' - '+title
        item=xbmcgui.ListItem(displayname, iconImage=thumbnail, thumbnailImage=thumbnail)
        item.setInfo( type="Video", infoLabels={ "Title":displayname
                                                 #"Artist":artist
                                                 })
        item.setProperty('IsPlayable', 'true')
        playlist.add(url=u, listitem=item)

def playlistVideo():
    try:
        item = xbmcgui.ListItem(path=getVideo(params['url']))
        xbmcplugin.setResolvedUrl(pluginhandle, True, item) 
        if addon.getSetting('unpause') == 'true':
            import time
            sleeptime = int(addon.getSetting('unpausetime'))+1
            time.sleep(sleeptime)
            xbmc.Player().pause()
    except:
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
def addDir(name, url, mode, plot='', iconimage='DefaultFolder.png' ,folder=True,total=0):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)
    item=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    return xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=folder,totalItems=total)

def getURL( url , extraheader=True):
    print 'VEVO --> common :: getURL :: url = '+url
    cj = cookielib.LWPCookieJar()
    if os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE, ignore_discard=True)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('Referer', 'http://www.vevo.com'),
                         ('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2;)')]
    if extraheader:
        opener.addheaders = [('X-Requested-With', 'XMLHttpRequest')]
    usock=opener.open(url)
    response=usock.read()
    usock.close()
    if os.path.isfile(COOKIEFILE):
        cj.save(COOKIEFILE, ignore_discard=True)
    return response

def UserPost( url ):
    print 'VEVO --> common :: UserPost :: url = '+url
    cj = cookielib.LWPCookieJar()
    if os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE, ignore_discard=True)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('Referer', 'http://www.vevo.com'),
                         ('X-Requested-With', 'XMLHttpRequest'),
                         ('Accept', 'application/json, text/javascript, */*; q=0.01'),
                         ('Pragma', 'no-cache'),
                         ('Cache-Control', 'no-cache'),
                         ('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2;)')]
    data = ''
    usock=opener.open(url,data)
    response=usock.read()
    usock.close()
    if os.path.isfile(COOKIEFILE):
        cj.save(COOKIEFILE, ignore_discard=True)
    return response

def login_cookie():
    #don't do anything if they don't have a password or username entered
    if addon.getSetting('login_name')=='' or addon.getSetting('login_pass')=='':
        print "VEVO --> WARNING: Could not login.  Please enter a username and password in settings"
        return False
    cj = cookielib.LWPCookieJar()
    cj.save(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    data = getURL('http://www.vevo.com/loginmodal')
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    token = tree.find(attrs={'name':'__RequestVerificationToken'})['value']
    cj.load(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('Referer', 'http://www.vevo.com/'),
                         ('Content-Type', 'application/x-www-form-urlencoded'),
                         ('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2;)'),
                         ('Connection', 'keep-alive')]
    data =urllib.urlencode({"email":addon.getSetting('login_name'),
                            "password":addon.getSetting('login_pass'),
                            "__RequestVerificationToken":token,
                            "btnLogin":"Login"})
    login_url = 'http://www.vevo.com/login?returnUrl=http%3A%2F%2Fwww.vevo.com%2F'
    usock = opener.open(login_url, data)
    response = usock.read()
    usock.close()
    print 'VEVO -- > These are the cookies we have received:'
    for index, cookie in enumerate(cj):
        print 'VEVO--> '+str(index)+': '+str(cookie)
    cj.save(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    usercontext = 'http://www.vevo.com/Proxy/User/GetUserContext.ashx'
    data = UserPost( usercontext )
    file = open(USERFILE, 'w')
    file.write(data)
    file.close()
    cj.save(COOKIEFILE, ignore_expires=True)
    return True

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
