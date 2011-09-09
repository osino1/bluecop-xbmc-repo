#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time
import urllib
import demjson
import xbmcplugin
import xbmc
import xbmcgui
import resources.lib.common as common

pluginhandle = common.pluginhandle

def GETTRAILERS(getstream):
    try:
        data = common.getURL(getstream,'atv-ps.amazon.com')
        print data
        rtmpdata = demjson.decode(data)
        print rtmpdata
        sessionId = rtmpdata['message']['body']['streamingURLInfoSet']['sessionId']
        cdn = rtmpdata['message']['body']['streamingURLInfoSet']['cdn']
        rtmpurls = rtmpdata['message']['body']['streamingURLInfoSet']['streamingURLInfo']
        return rtmpurls, sessionId, cdn
    except:
        return False, False, False

def PLAYTRAILER_RESOLVE():
    PLAYTRAILER(resolve=True)

def PLAYTRAILER(resolve=False):
    videoname = common.args.name
    swfUrl, values = GETFLASHVARS(common.args.url) 
    values['deviceID'] = values['customerID'] + str(int(time.time() * 1000)) + values['asin']
    getstream  = 'https://atv-ps.amazon.com/cdp/catalog/GetStreamingTrailerUrls'
    getstream += '?asin='+values['asin']
    getstream += '&deviceTypeID='+values['deviceTypeID']
    getstream += '&deviceID='+values['deviceID']
    getstream += '&firmware=LNX%2010,3,181,14%20PlugIn'
    getstream += '&format=json'
    getstream += '&version=1'
    rtmpurls, streamSessionID, cdn = GETTRAILERS(getstream)
    if rtmpurls == False:
        xbmcgui.Dialog().ok('Trailer Not Available',videoname)
    elif cdn == 'limelight':
        xbmcgui.Dialog().ok('Limelight CDN','Limelight uses swfverfiy2. Playback may fail.')
    else:
        PLAY(rtmpurls,swfUrl=swfUrl,Trailer=videoname,resolve=resolve)
        
def GETSTREAMS(getstream):
    try:
        data = common.getURL(getstream,'atv-ps.amazon.com',useCookie=True)
        print data
        rtmpdata = demjson.decode(data)
        print rtmpdata
        sessionId = rtmpdata['message']['body']['urlSets']['streamingURLInfoSet'][0]['sessionId']
        cdn = rtmpdata['message']['body']['urlSets']['streamingURLInfoSet'][0]['cdn']
        rtmpurls = rtmpdata['message']['body']['urlSets']['streamingURLInfoSet'][0]['streamingURLInfo']
        return rtmpurls, sessionId, cdn
    except:
        return False, False, False

def PLAYVIDEO():
    swfUrl, values = GETFLASHVARS(common.args.url)            
    values['deviceID'] = values['customerID'] + str(int(time.time() * 1000)) + values['asin']
    getstream  = 'https://atv-ps.amazon.com/cdp/catalog/GetStreamingUrlSets'
    getstream += '?asin='+values['asin']
    getstream += '&deviceTypeID='+values['deviceTypeID']
    getstream += '&firmware=LNX%2010,3,181,14%20PlugIn'
    getstream += '&customerID='+values['customerID']
    getstream += '&deviceID='+values['deviceID']
    getstream += '&token='+values['token']
    getstream += '&xws-fa-ov=true'
    getstream += '&format=json'
    getstream += '&version=1'
    rtmpurls, streamSessionID, cdn = GETSTREAMS(getstream)
    if cdn == 'limelight':
        xbmcgui.Dialog().ok('Limelight CDN','Limelight uses swfverfiy2. Playback may fail.')
    if rtmpurls <> False:
        basertmp, ip = PLAY(rtmpurls,swfUrl=swfUrl)
    if streamSessionID <> False:
        epoch = str(int(time.mktime(time.gmtime()))*1000)
        USurl =  'https://atv-ps.amazon.com/cdp/usage/UpdateStream'
        USurl += '?device_type_id='+values['deviceTypeID']
        USurl += '&deviceTypeID='+values['deviceTypeID']
        USurl += '&streaming_session_id='+streamSessionID
        USurl += '&operating_system=Linux%202.6.35-28-generic'
        USurl += '&timecode=45.003'
        USurl += '&flash_version=LNX%2010,3,181,14%20PlugIn'
        USurl += '&asin='+values['asin']
        USurl += '&token='+values['token']
        USurl += '&browser='+urllib.quote_plus(values['userAgent'])
        USurl += '&server_id='+ip
        USurl += '&client_version='+swfUrl.split('/')[-1]
        USurl += '&unique_browser_id='+values['UBID']
        USurl += '&device_id='+values['deviceID']
        USurl += '&format=json'
        USurl += '&version=1'
        USurl += '&page_type='+values['pageType']
        USurl += '&start_state=Video'
        USurl += '&amazon_session_id='+values['sessionID']
        USurl += '&event=STOP'
        USurl += '&firmware=LNX%2010,3,181,14%20PlugIn'
        USurl += '&customerID='+values['customerID']
        USurl += '&deviceID='+values['deviceID']
        USurl += '&source_system=http://www.amazon.com'
        USurl += '&http_referer=ecx.images-amazon.com'
        USurl += '&event_timestamp='+epoch
        USurl += '&encrypted_customer_id='+values['customerID']
        print common.getURL(USurl,'atv-ps.amazon.com',useCookie=True)

        epoch = str(int(time.mktime(time.gmtime()))*1000)
        surl =  'https://atv-ps.amazon.com/cdp/usage/ReportStopStreamEvent'
        surl += '?deviceID='+values['deviceID']
        surl += '&source_system=http://www.amazon.com'
        surl += '&format=json'
        surl += '&event_timestamp='+epoch
        surl += '&encrypted_customer_id='+values['customerID']
        surl += '&http_referer=ecx.images-amazon.com'
        surl += '&device_type_id='+values['deviceTypeID']
        surl += '&download_bandwidth=9926.295518207282'
        surl += '&device_id='+values['deviceTypeID']
        surl += '&from_mode=purchased'
        surl += '&operating_system=Linux%202.6.35-28-generic'
        surl += '&version=1'
        surl += '&flash_version=LNX%2010,3,181,14%20PlugIn'
        surl += '&url='+urllib.quote_plus(basertmp)
        surl += '&streaming_session_id='+streamSessionID
        surl += '&browser='+urllib.quote_plus(values['userAgent'])
        surl += '&server_id='+ip
        surl += '&client_version='+swfUrl.split('/')[-1]
        surl += '&unique_browser_id='+values['UBID']
        surl += '&amazon_session_id='+values['sessionID']
        surl += '&page_type='+values['pageType']
        surl += '&start_state=Video'
        surl += '&token='+values['token']
        surl += '&to_timecode=3883'
        surl += '&streaming_bit_rate=348'
        surl += '&new_streaming_bit_rate=2500'
        surl += '&asin='+values['asin']
        surl += '&deviceTypeID='+values['deviceTypeID']
        surl += '&firmware=LNX%2010,3,181,14%20PlugIn'
        surl += '&customerID='+values['customerID']
        print common.getURL(surl,'atv-ps.amazon.com',useCookie=True)
        if values['pageType'] == 'movie':
            import movies as moviesDB
            moviesDB.watchMoviedb(values['asin'])
        if values['pageType'] == 'tv':
            import tv as tvDB
            tvDB.watchEpisodedb(values['asin'])

def GETFLASHVARS(pageurl):
    showpage = common.getURL(pageurl,useCookie=True)
    flashVars = re.compile("'flashVars', '(.*?)' \+ new Date\(\)\.getTime\(\)\+ '(.*?)'",re.DOTALL).findall(showpage)
    flashVars =(flashVars[0][0] + flashVars[0][1]).split('&')
    swfUrl = re.compile("avodSwfUrl = '(.*?)'\;").findall(showpage)[0]
    values={'token'          :'',
            'deviceTypeID'   :'A13Q6A55DBZB7M',
            'version'        :'1',
            'firmware'       :'1',       
            'customerID'     :'',
            'format'         :'json',
            'deviceID'       :'',
            'asin'           :''      
            }
    for item in flashVars:
        item = item.split('=')
        if item[0]      == 'token':
            values[item[0]]         = item[1]
        elif item[0]    == 'customer':
            values['customerID']    = item[1]
        elif item[0]    == 'ASIN':
            values['asin']          = item[1]
        elif item[0]    == 'pageType':
            values['pageType']      = item[1]        
        elif item[0]    == 'UBID':
            values['UBID']          = item[1]
        elif item[0]    == 'sessionID':
            values['sessionID']     = item[1]
        elif item[0]    == 'userAgent':
            values['userAgent']     = item[1]
    return swfUrl, values
        
def PLAY(rtmpurls,swfUrl,Trailer=False,resolve=True):
    print rtmpurls
    quality = [0,2500,1328,996,664,348]
    lbitrate = quality[int(xbmcplugin.getSetting(pluginhandle,"bitrate"))]
    mbitrate = 0
    streams = []
    for data in rtmpurls:
        url = data['url']
        bitrate = int(data['bitrate'])
        if lbitrate == 0:
            streams.append([bitrate,url])
        elif bitrate >= mbitrate and bitrate <= lbitrate:
            mbitrate = bitrate
            rtmpurl = url
    if lbitrate == 0:        
        quality=xbmcgui.Dialog().select('Please select a quality level:', [str(stream[0])+'kbps' for stream in streams])
        print quality
        if quality!=-1:
            rtmpurl = streams[quality][1]
    protocolSplit = rtmpurl.split("://")
    pathSplit   = protocolSplit[1].split("/")
    hostname    = pathSplit[0]
    appName     = protocolSplit[1].split(hostname + "/")[1].split('/')[0]    
    streamAuth  = rtmpurl.split(appName+'/')[1].split('?')
    stream      = streamAuth[0].replace('.mp4','')
    auth        = streamAuth[1]
    identurl = 'http://'+hostname+'/fcs/ident'
    ident = common.getURL(identurl)
    ip = re.compile('<fcs><ip>(.+?)</ip></fcs>').findall(ident)[0]
    basertmp = 'rtmpe://'+ip+':1935/'+appName+'?_fcs_vhost='+hostname+'&ovpfv=2.1.4&'+auth
    finalUrl = basertmp
    finalUrl += " playpath=" + stream 
    finalUrl += " pageurl=" + common.args.url
    finalUrl += " swfurl=" + swfUrl + " swfvfy=true"
    if Trailer and not resolve:
        finalname = Trailer+' Trailer'
        item = xbmcgui.ListItem(finalname,path=finalUrl)
        item.setInfo( type="Video", infoLabels={ "Title": finalname})
        item.setProperty('IsPlayable', 'true')
        xbmc.Player().play(finalUrl,item)
    else:
        item = xbmcgui.ListItem(path=finalUrl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
    return basertmp, ip