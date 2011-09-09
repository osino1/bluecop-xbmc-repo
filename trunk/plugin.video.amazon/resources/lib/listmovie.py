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

################################ Movie listing
def LIST_MOVIE_ROOT():
    common.addDir('Favorited','listmovie','LIST_MOVIES_FAVOR_FILTERED')
    common.addDir('All Movies','listmovie','LIST_MOVIES')
    common.addDir('Genres','listmovie','LIST_MOVIE_TYPES','GENRE')
    common.addDir('Years','listmovie','LIST_MOVIE_TYPES','YEARS')
    common.addDir('Studios','listmovie','LIST_MOVIE_TYPES','STUDIOS')
    common.addDir('MPAA Rating','listmovie','LIST_MOVIE_TYPES','MPAA')
    common.addDir('Directors','listmovie','LIST_MOVIE_TYPES','DIRECTORS')
    #common.addDir('Actors','listmovie','LIST_MOVIE_TYPES','ACTORS')
    common.addDir('Watched History','listmovie','LIST_MOVIES_WATCHED_FILTERED')
    xbmcplugin.endOfDirectory(pluginhandle)

def LIST_MOVIE_TYPES(type=False):
    import movies as moviesDB
    if not type:
        type = common.args.url
    if type=='GENRE':
        mode = 'LIST_MOVIES_GENRE_FILTERED'
        items = moviesDB.getMovieTypes('genres')
    elif type=='STUDIOS':
        mode =  'LIST_MOVIES_STUDIO_FILTERED'
        items = moviesDB.getMovieTypes('studio')
    elif type=='YEARS':
        mode = 'LIST_MOVIES_YEAR_FILTERED'
        items = moviesDB.getMovieTypes('year')
    elif type=='DIRECTORS':
        mode = 'LIST_MOVIES_DIRECTOR_FILTERED'
        items = moviesDB.getMovieTypes('director')
    elif type=='MPAA':
        mode = 'LIST_MOVIES_MPAA_FILTERED'
        items = moviesDB.getMovieTypes('mpaa')
    elif type=='ACTORS':        
        mode = 'LIST_MOVIES_ACTOR_FILTERED'
        items = moviesDB.getMovieTypes('actors')     
    for item in items:
        common.addDir(item,'listmovie',mode,item)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)          
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)   

def LIST_MOVIES_GENRE_FILTERED():
    LIST_MOVIES(genrefilter=common.args.url)

def LIST_MOVIES_YEAR_FILTERED():
    LIST_MOVIES(yearfilter=common.args.url)

def LIST_MOVIES_MPAA_FILTERED():
    LIST_MOVIES(mpaafilter=common.args.url)
    
def LIST_MOVIES_STUDIO_FILTERED():
    LIST_MOVIES(studiofilter=common.args.url)

def LIST_MOVIES_DIRECTOR_FILTERED():
    LIST_MOVIES(directorfilter=common.args.url)

def LIST_MOVIES_ACTOR_FILTERED():
    LIST_MOVIES(actorfilter=common.args.url)
    
def LIST_MOVIES_WATCHED_FILTERED():
    LIST_MOVIES(watchedfilter=True)
  
def LIST_MOVIES_FAVOR_FILTERED():
    LIST_MOVIES(favorfilter=True)

def LIST_MOVIES(genrefilter=False,actorfilter=False,directorfilter=False,studiofilter=False,yearfilter=False,mpaafilter=False,watchedfilter=False,favorfilter=False):
    xbmcplugin.setContent(pluginhandle, 'Movies')
    editenable=xbmcplugin.getSetting(pluginhandle,"editenable")
    import movies as moviesDB
    movies = moviesDB.loadMoviedb(genrefilter=genrefilter,actorfilter=actorfilter,directorfilter=directorfilter,studiofilter=studiofilter,yearfilter=yearfilter,mpaafilter=mpaafilter,watchedfilter=watchedfilter,favorfilter=favorfilter)
    for asin,movietitle,url,poster,plot,director,writer,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,TMDBbanner,TMDBposter,TMDBfanart,isprime,watched,favor in movies:
        actors = actors.split(',')
        fanart = poster.replace('.jpg','._BO354,0,0,0_CR177,354,708,500_.jpg')
        infoLabels={'Title':movietitle,'Plot':plot,'Year':year,'Premiered':premiered,
                    'Rating':stars,'Votes':votes,'Genre':genres,'Director':director,
                    'Studio':studio,'Duration':runtime,'mpaa':mpaa,'Cast':actors}
        cm = []
        if watched:
            infoLabels['overlay']=7
            cm.append( ('Unwatch', 'XBMC.RunPlugin(%s?mode="movies"&sitemode="unwatchMoviedb"&url="%s")' % ( sys.argv[0], urllib.quote_plus(asin) ) ) )
        else: cm.append( ('Mark Watched', 'XBMC.RunPlugin(%s?mode="movies"&sitemode="watchMoviedb"&url="%s")' % ( sys.argv[0], urllib.quote_plus(asin) ) ) )
        if favor: cm.append( ('Remove from Favorites', 'XBMC.RunPlugin(%s?mode="movies"&sitemode="unfavorMoviedb"&url="%s")' % ( sys.argv[0], urllib.quote_plus(asin) ) ) )
        else: cm.append( ('Add to Favorites', 'XBMC.RunPlugin(%s?mode="movies"&sitemode="favorMoviedb"&url="%s")' % ( sys.argv[0], urllib.quote_plus(asin) ) ) )
        if editenable == 'true':
            cm.append( ('Remove from Movies', 'XBMC.RunPlugin(%s?mode="movies"&sitemode="deleteMoviedb"&url="%s")' % ( sys.argv[0], urllib.quote_plus(asin) ) ) )
        common.addVideo(movietitle,url,poster,fanart,infoLabels=infoLabels,cm=cm)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_DURATION)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE)
    viewenable=xbmcplugin.getSetting(pluginhandle,"viewenable")
    if viewenable == 'true':
        view=int(xbmcplugin.getSetting(pluginhandle,"movieview"))
        xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)
