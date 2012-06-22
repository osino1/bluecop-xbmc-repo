#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xbmcplugin
import xbmc
import xbmcgui
import os.path
import sys
import urllib
import resources.lib.common as common

pluginhandle = common.pluginhandle

# 501-POSTER WRAP 503-MLIST3 504=MLIST2 508-FANARTPOSTER 
confluence_views = [500,501,502,503,504,508]

###################### Television

def LIST_TV_ROOT():
    common.addDir('Favorited','listtv','LIST_TVSHOWS_FAVOR_FILTERED')
    common.addDir('All Shows','listtv','LIST_TVSHOWS')
    common.addDir('HDTV Shows','listtv','LIST_HDTVSHOWS')
    common.addDir('Genres','listtv','LIST_TVSHOWS_TYPES','GENRE' )
    common.addDir('Years','listtv','LIST_TVSHOWS_TYPES','YEARS' )
    common.addDir('Networks','listtv','LIST_TVSHOWS_TYPES','NETWORKS')
    common.addDir('TV Rating','listtv','LIST_TVSHOWS_TYPES','MPAA' )
    #common.addDir('Creators','listtv','LIST_TVSHOWS_TYPES','CREATORS')
    xbmcplugin.endOfDirectory(pluginhandle)
    
def LIST_TVSHOWS_TYPES(type=False):
    import tv as tvDB
    if not type:
        type = common.args.url
    if type=='GENRE':
        mode = 'LIST_TVSHOWS_GENRE_FILTERED'
        items = tvDB.getShowTypes('genres')
    elif type=='NETWORKS':
        mode =  'LIST_TVSHOWS_NETWORKS_FILTERED'
        items = tvDB.getShowTypes('network')  
    elif type=='YEARS':
        mode = 'LIST_TVSHOWS_YEARS_FILTERED'
        items = tvDB.getShowTypes('year')
    elif type=='MPAA':
        mode = 'LIST_TVSHOWS_MPAA_FILTERED'
        items = tvDB.getShowTypes('mpaa')
    elif type=='CREATORS':
        mode = 'LIST_TVSHOWS_CREATORS_FILTERED'
        items = tvDB.getShowTypes('creator')
    for item in items:
        common.addDir(item,'listtv',mode,item)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)          
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)   

def LIST_TVSHOWS_GENRE_FILTERED():
    LIST_TVSHOWS(genrefilter=common.args.url)

def LIST_TVSHOWS_NETWORKS_FILTERED():
    LIST_TVSHOWS(networkfilter=common.args.url)
    
def LIST_TVSHOWS_YEARS_FILTERED():
    LIST_TVSHOWS(yearfilter=common.args.url)

def LIST_TVSHOWS_MPAA_FILTERED():
    LIST_TVSHOWS(mpaafilter=common.args.url)

def LIST_TVSHOWS_CREATORS_FILTERED():
    LIST_TVSHOWS(creatorfilter=common.args.url)
  
def LIST_TVSHOWS_FAVOR_FILTERED():
    LIST_TVSHOWS(favorfilter=True)
    
def LIST_HDTVSHOWS():
    LIST_TVSHOWS(HDonly=True)

def LIST_TVSHOWS(HDonly=False,mpaafilter=False,genrefilter=False,creatorfilter=False,networkfilter=False,yearfilter=False,favorfilter=False):
    xbmcplugin.setContent(pluginhandle, 'tvshows')
    import tv as tvDB
    shows = tvDB.loadTVShowdb(HDonly=HDonly,mpaafilter=mpaafilter,genrefilter=genrefilter,creatorfilter=creatorfilter,networkfilter=networkfilter,yearfilter=yearfilter,favorfilter=favorfilter)
    for showdata in shows:
        ADD_SHOW_ITEM(showdata,HDonly=HDonly)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE)
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)
    viewenable=common.addon.getSetting("viewenable")
    if viewenable == 'true':
        view=int(common.addon.getSetting("showview"))
        xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")

def ADD_SHOW_ITEM(showdata,HDonly=False):
    artOptions = ['Poster','Banner','Amazon']
    tvart=int(common.addon.getSetting("tvart"))
    option = artOptions[tvart]
    asin,feed,seriestitle,poster,plot,network,mpaa,genres,actors,premiered,year,stars,votes,seasontotal,episodetotal,watched,unwatched,isHD,isprime,favor,TVDBbanner,TVDBposter,TVDBfanart,TVDBseriesid = showdata
    infoLabels={'Title': seriestitle,'TVShowTitle':seriestitle}
    if plot:
        infoLabels['Plot'] = plot
    if mpaa:
        infoLabels['MPAA'] = mpaa
    if actors:
        infoLabels['Cast'] = actors.split(',')
    if year:
        infoLabels['Year'] = year
    if premiered:
        infoLabels['Premiered'] = premiered
    if stars:
        infoLabels['Rating'] = stars           
    if votes:
        infoLabels['Votes'] = votes  
    if genres:
        infoLabels['Genre'] = genres 
    if episodetotal:
        infoLabels['Episode'] = episodetotal
    if network:
        infoLabels['Studio'] = network
    if HDonly==True: listmode = 'LIST_HDTV_SEASONS'
    else: listmode = 'LIST_TV_SEASONS'
    if poster is None:
        poster=''
    if TVDBposter and option == 'Poster':
        poster = TVDBposter
    elif TVDBbanner and option == 'Banner':
        poster = TVDBbanner
    if TVDBfanart:
        fanart = TVDBfanart
    else:
        fanart = poster
    cm = []
    if favor: cm.append( ('Remove from Favorites', 'XBMC.RunPlugin(%s?mode="tv"&sitemode="unfavorShowdb"&title="%s")' % ( sys.argv[0], urllib.quote_plus(seriestitle) ) ) )
    else: cm.append( ('Add to Favorites', 'XBMC.RunPlugin(%s?mode="tv"&sitemode="favorShowdb"&title="%s")' % ( sys.argv[0], urllib.quote_plus(seriestitle) ) ) )
    if common.addon.getSetting("editenable") == 'true':
        cm.append( ('Rename Show', 'XBMC.RunPlugin(%s?mode="tv"&sitemode="renameShowdb"&title="%s")' % ( sys.argv[0], urllib.quote_plus(seriestitle) ) ) )
        if TVDBseriesid:
            cm.append( ('Refresh TVDB Data', 'XBMC.RunPlugin(%s?mode="tv"&sitemode="refreshTVDBshow"&title="%s")' % ( sys.argv[0], urllib.quote_plus(seriestitle) ) ) )
        cm.append( ('Lookup Show in TVDB', 'XBMC.RunPlugin(%s?mode="tv"&sitemode="scanTVDBshow"&title="%s")' % ( sys.argv[0], urllib.quote_plus(seriestitle) ) ) )
        cm.append( ('Remove Show', 'XBMC.RunPlugin(%s?mode="tv"&sitemode="deleteShowdb"&title="%s")' % ( sys.argv[0], urllib.quote_plus(seriestitle) ) ) )
    common.addDir(seriestitle,'listtv',listmode,seriestitle,poster,fanart,infoLabels,cm=cm)

def LIST_HDTV_SEASONS():
    LIST_TV_SEASONS(HDonly=True)
   
def LIST_TV_SEASONS(HDonly=False):
    namefilter = common.args.url
    import tv as tvDB
    seasons = tvDB.loadTVSeasonsdb(showname=namefilter,HDonly=HDonly).fetchall()
    seasonTotal = len(seasons)
    #FLATTEN ONE SEASON
    #if seasonTotal == 1:
    #    if HDonly:
    #        LIST_HDEPISODES_DB(url=seriestitle+'<split>'+str(season))
    #    else:
    #        LIST_EPISODES_DB(url=seriestitle+'<split>'+str(season))
    #    return
    for seasondata in seasons:
        ADD_SEASON_ITEM(seasondata)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setContent(pluginhandle, 'tvshows')
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)
    viewenable=common.addon.getSetting("viewenable")
    if viewenable == 'true':
        view=int(common.addon.getSetting("seasonview"))
        xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")

def ADD_SEASON_ITEM(seasondata,mode='listtv',submode='LIST_EPISODES_DB',seriesTitle=False,inWatchlist=False):
   #asin,episodeFeed,poster,season,seriestitle,plot,actors,studio,mpaa,genres,premiered,year,stars,votes,episodetotal,watched,unwatched,isHD,isprime
    asin,episodeFeed,poster,season,seriestitle,plot,actors,network,mpaa,genres,premiered,year,stars,votes,episodetotal,watched,unwatched,isHD,isprime = seasondata
    infoLabels={'Title': seriestitle,'TVShowTitle':seriestitle}
    if plot:
        infoLabels['Plot'] = plot
    if mpaa:
        infoLabels['MPAA'] = mpaa
    if actors:
        infoLabels['Cast'] = actors.split(',')
    if year:
        infoLabels['Year'] = year
    if premiered:
        infoLabels['Premiered'] = premiered
    if stars:
        infoLabels['Rating'] = stars           
    if votes:
        infoLabels['Votes'] = votes  
    if genres:
        infoLabels['Genre'] = genres 
    if episodetotal:
        infoLabels['Episode'] = episodetotal
    if season:
        infoLabels['Season'] = season
    if network:
        infoLabels['Studio'] = network
    if mode == 'listtv':
        url = seriestitle+'<split>'+str(season)
        if isHD:
            submode = 'LIST_HDEPISODES_DB'
    else:
        url = asin
    if seriesTitle:
        displayname=seriestitle+' '
    else:
        displayname=''
    if season <> 0 and len(str(season)) < 3: displayname += 'Season '+str(season)
    elif len(str(season)) > 2: displayname += 'Year '+str(season)
    else: displayname += 'Specials'
    if isHD: displayname += ' [HD]'
    cm = []
    if inWatchlist:
        cm.append( ('Remove from Watchlist', 'XBMC.RunPlugin(%s?mode="common"&sitemode="removeTVWatchlist"&asin="%s")' % ( sys.argv[0], urllib.quote_plus(asin) ) ) )
    else:
        cm.append( ('Add to Watchlist', 'XBMC.RunPlugin(%s?mode="common"&sitemode="addTVWatchlist"&asin="%s")' % ( sys.argv[0], urllib.quote_plus(asin) ) ) )
    if common.addon.getSetting("editenable") == 'true':
        cm.append( ('Rename Season', 'XBMC.RunPlugin(%s?mode="tv"&sitemode="renameSeasondb"&title="%s"&season="%s")' % ( sys.argv[0], urllib.quote_plus(seriestitle), str(season) ) ) )
        cm.append( ('Remove Season', 'XBMC.RunPlugin(%s?mode="tv"&sitemode="deleteSeasondb"&title="%s"&season="%s")' % ( sys.argv[0], urllib.quote_plus(seriestitle), str(season) ) ) )
    try:fanart = common.args.fanart
    except:fanart = poster
    common.addDir(displayname,mode,submode,url,poster,fanart,infoLabels,cm=cm)


def LIST_HDEPISODES_DB(url=False):
    LIST_EPISODES_DB(HDonly=True,url=url)

def LIST_EPISODES_DB(HDonly=False,owned=False,url=False):
    if not url:
        url = common.args.url
    split = url.split('<split>')
    seriestitle = split[0]
    try:
        season = int(split[1])
    except:
        season = 0
    import tv as tvDB
    episodes = tvDB.loadTVEpisodesdb(seriestitle,season,HDonly)
    for episodedata in episodes:
        ADD_EPISODE_ITEM(episodedata)
    #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setContent(pluginhandle, 'Episodes')
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)
    viewenable=common.addon.getSetting("viewenable")
    if viewenable == 'true':
        view=int(common.addon.getSetting("episodeview"))
        xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")  
        
def ADD_EPISODE_ITEM(episodedata):
   #asin,seriestitle,season,episode,poster,mpaa,actors,genres,episodetitle,studio,stars,votes,url,plot,airdate,year,runtime,isHD,isprime,watched
    asin,seriestitle,season,episode,poster,mpaa,actors,genres,episodetitle,network,stars,votes,url,plot,airdate,year,runtime,isHD,isprime,watched = episodedata
    infoLabels={'Title': episodetitle,'TVShowTitle':seriestitle,
                'Episode': episode,'Season':season}
    if plot:
        infoLabels['Plot'] = plot
    if airdate:
        infoLabels['Premiered'] = airdate 
    if year:
        infoLabels['Year'] = year
    if runtime:
        infoLabels['Duration'] = runtime
    if mpaa:
        infoLabels['MPAA'] = mpaa
    if actors:
        infoLabels['Cast'] = actors.split(',')
    if stars:
        infoLabels['Rating'] = stars           
    if votes:
        infoLabels['Votes'] = votes  
    if genres:
        infoLabels['Genre'] = genres 
    if network:
        infoLabels['Studio'] = network

    if season == 0: displayname =  str(episode)+'. '+episodetitle
    else: displayname =  str(season)+'x'+str(episode)+' - '+episodetitle
    if isHD: displayname += ' [HD]'
    displayname = displayname.replace('"','')
    try:
        if common.args.thumb and poster == None: poster = common.args.thumb
        if common.args.fanart and common.args.fanart <>'': fanart = common.args.fanart
        else: fanart=poster
    except: fanart=poster

    cm = []
    if watched:
        infoLabels['overlay']=7
        cm.append( ('Unwatch', 'XBMC.RunPlugin(%s?mode="tv"&sitemode="unwatchEpisodedb"&url="%s")' % ( sys.argv[0], urllib.quote_plus(asin) ) ) )
    else: cm.append( ('Mark Watched', 'XBMC.RunPlugin(%s?mode="tv"&sitemode="watchEpisodedb"&url="%s")' % ( sys.argv[0], urllib.quote_plus(asin) ) ) )
    common.addVideo(displayname,url,poster,fanart,infoLabels=infoLabels,cm=cm)
