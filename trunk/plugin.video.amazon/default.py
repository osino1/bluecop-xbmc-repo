# -*- coding: utf_8 -*-

import xbmcplugin,xbmcgui
import urllib,urllib2,cookielib,re,os.path
import sys
import binascii
import md5
import base64
import operator
import cookielib
import time
from datetime import datetime
import demjson
from BeautifulSoup import BeautifulSoup
try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite    

pluginhandle = int(sys.argv[1])
COOKIEFILE = os.path.join(os.getcwd().replace(';', ''),'resources','cache','cookies.lwp')
moviesDB = os.path.join(os.getcwd().replace(';', ''),'resources','cache','movies.db')
tvDB = os.path.join(os.getcwd().replace(';', ''),'resources','cache','tv.db')
cj = cookielib.LWPCookieJar()
BASE_URL = 'http://www.amazon.com'
#MOVIE_URL = 'http://www.amazon.com/s/ref=sa_menu_piv_mov0/182-5606325-6863626?ie=UTF8&node=16386761&field-is_prime_benefit=1&sort=-releasedate'
MOVIE_URL = 'http://www.amazon.com/gp/search/ref=sr_st?qid=1314934213&rh=n%3A2625373011%2Cn%3A!2644981011%2Cn%3A!2644982011%2Cn%3A2858778011%2Cn%3A2858905011%2Cp_85%3A2470955011&sort=-releasedate'
#TV_URL = 'http://www.amazon.com/s/ref=sa_menu_piv_tv0/182-5606325-6863626?ie=UTF8&node=16262841&field-is_prime_benefit=1&sort=-releasedate'
TV_URL = 'http://www.amazon.com/gp/search/ref=sr_st?qid=1314982661&rh=n%3A2625373011%2Cn%3A!2644981011%2Cn%3A!2644982011%2Cn%3A2858778011%2Cn%3A2864549011%2Cp_85%3A2470955011&sort=-releasedate'

def getURL( url , host='www.amazon.com'):
    print 'getHTTP :: url = '+url
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.10 (maverick) Firefox/3.6.17'),
                         ('Host', host)]
    usock = opener.open(url)
    response = usock.read()
    usock.close()
    return response

def postURL( url, values, host='www.amazon.com'):    
    print 'postHTTP :: url = '+url
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.10 (maverick) Firefox/3.6.17'),
                         ('Host', host)]
    data = urllib.urlencode(values)
    usock = opener.open(url, data)
    response = usock.read()
    usock.close()
    return response

def login():
    if os.path.isfile(COOKIEFILE):
        os.remove(COOKIEFILE)
    data=getURL(BASE_URL)
    SIGNIN_URL = re.compile('<a href="(.+?)" rel="nofollow">Sign in</a>').findall(data)[0].replace('&amp;','&')
    data = getURL(SIGNIN_URL)
    form =  '<form name="signIn"' + re.compile('<form name="signIn"(.*?)</form>',re.DOTALL).findall(data)[0] + '</form>'
    tree = BeautifulSoup(form, convertEntities=BeautifulSoup.HTML_ENTITIES)
    action_url = tree.form['action']
    items = tree.findAll('input',attrs={'type' : 'hidden'})
    values = {}
    for item in items:
        values[item['name']] = item['value']
    values['create'] = '0'
    values['email'] =       xbmcplugin.getSetting(pluginhandle,"login_name")
    values['password'] =    xbmcplugin.getSetting(pluginhandle,"login_pass")
    postURL(action_url,values)
    cj.save(COOKIEFILE, ignore_discard=True, ignore_expires=True)

def GETTRAILERS(getstream):
    try:
        data = getURL(getstream,'atv-ps.amazon.com')
        print data
        rtmpdata = demjson.decode(data)
        print rtmpdata
        sessionId = rtmpdata['message']['body']['streamingURLInfoSet']['sessionId']
        cdn = rtmpdata['message']['body']['streamingURLInfoSet']['cdn']
        rtmpurls = rtmpdata['message']['body']['streamingURLInfoSet']['streamingURLInfo']
        return rtmpurls, sessionId, cdn
    except:
        return False, False, False

def PLAYTRAILER():
    pageurl = params['url']
    videoname = params['name']
    showpage = getURL(pageurl)
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
        print rtmpurls
        quality = [0,2500,1328,996,664,348]
        try: lbitrate = quality[int(xbmcplugin.getSetting(pluginhandle,"bitrate"))]
        except: lbitrate = 2500
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
        ident = getURL(identurl)
        ip = re.compile('<fcs><ip>(.+?)</ip></fcs>').findall(ident)[0]
        basertmp = 'rtmpe://'+ip+':1935/'+appName+'?_fcs_vhost='+hostname+'&ovpfv=2.1.4&'+auth
        finalUrl = basertmp
        finalUrl += " playpath=" + stream 
        finalUrl += " pageurl=" + pageurl
        finalUrl += " swfurl=" + swfUrl + " swfvfy=true"
        finalname = videoname+' Trailer'
        item = xbmcgui.ListItem(finalname,path=finalUrl)
        item.setInfo( type="Video", infoLabels={ "Title": finalname})
        item.setProperty('IsPlayable', 'true')
        xbmc.Player().play(finalUrl,item)
        
def GETSTREAMS(getstream):
    try:
        data = getURL(getstream,'atv-ps.amazon.com')
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
    pageurl = params['url']
    if os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE, ignore_discard=True, ignore_expires=True)
    showpage = getURL(pageurl)
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
        ident = getURL(identurl)
        ip = re.compile('<fcs><ip>(.+?)</ip></fcs>').findall(ident)[0]
        basertmp = 'rtmpe://'+ip+':1935/'+appName+'?_fcs_vhost='+hostname+'&ovpfv=2.1.4&'+auth
        finalUrl = basertmp
        finalUrl += " playpath=" + stream 
        finalUrl += " pageurl=" + pageurl
        finalUrl += " swfurl=" + swfUrl + " swfvfy=true"
        item = xbmcgui.ListItem(path=finalUrl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
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
        print getURL(USurl,'atv-ps.amazon.com')

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
        print getURL(surl,'atv-ps.amazon.com')

def addDir(name,url,mode,iconimage='',plot=''):
    u=sys.argv[0]
    u+="?url="+urllib.quote_plus(url)
    u+="&mode="+urllib.quote_plus(mode)
    u+="&name="+urllib.quote_plus(name)
    u+="&thumb="+urllib.quote_plus(iconimage)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot":plot})
    liz.setProperty('fanart_image',iconimage)
    ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=True)
    return ok

################################ Movie db

def loadMoviedb():
    #if os.path.exists(moviesDB):
    #    os.remove(moviesDB)
    if not os.path.exists(moviesDB):
        conn = sqlite.connect(moviesDB)
        conn.text_factory = str
        c = conn.cursor()
        c.execute('''create table movies
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, movietitle text, url text, poster text, plot text, director text, runtime text, year integer, premiered text, studio text, mpaa text, actors text, genres text, stars float, votes string)''')
        c.close()
        addMoviesdb()
    conn = sqlite.connect(moviesDB)
    c = conn.cursor()
    return c.execute('select * from movies order by movietitle')

def getMovieGenres():
    conn = sqlite.connect(moviesDB)
    c = conn.cursor()
    return c.execute('select distinct genres from movies')

def getMovieStudios():
    conn = sqlite.connect(moviesDB)
    c = conn.cursor()
    return c.execute('select distinct studio from movies')

def getMovieActors():
    conn = sqlite.connect(moviesDB)
    c = conn.cursor()
    return c.execute('select distinct actors from movies')

def getMovieDirectors():
    conn = sqlite.connect(moviesDB)
    c = conn.cursor()
    return c.execute('select distinct director from movies')

def getMovieYears():
    conn = sqlite.connect(moviesDB)
    c = conn.cursor()
    return c.execute('select distinct year from movies')

def getMovieMPAA():
    conn = sqlite.connect(moviesDB)
    c = conn.cursor()
    return c.execute('select distinct mpaa from movies')

def addMoviesdb(url=MOVIE_URL):
    conn = sqlite.connect(moviesDB)
    conn.text_factory = str
    c = conn.cursor()
    data = getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    atf = tree.find(attrs={'id':'atfResults'}).findAll('div',recursive=False)
    btf = tree.find(attrs={'id':'btfResults'}).findAll('div',recursive=False)
    nextpage = tree.find(attrs={'title':'Next page','id':'pagnNextLink','class':'pagnNext'})
    #if not nextpage:
    #    print tree.prettify()
    del tree
    del data
    for movie in atf:
        link = movie.find('a', attrs={'class':'title'})
        name = link.string
        url = link['href']
        poster = movie.find(attrs={'class':'image'}).find('img')['src'].replace('_AA160_','_SX500_')
        plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes = getMovieInfo(url)
        moviedata = [None,name,url,poster,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes]
        c.execute('insert into movies values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', moviedata)
        conn.commit() 
    for movie in btf:
        link = movie.find('a', attrs={'class':'title'})
        name = link.string
        url = link['href']
        poster = movie.find(attrs={'class':'image'}).find('img')['src'].replace('_AA160_','_SX500_')
        plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes = getMovieInfo(url)
        moviedata = [None,name,url,poster,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes]
        c.execute('insert into movies values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', moviedata)
        conn.commit() 
    c.close()
    if nextpage:
        del atf
        del btf
        pagenext = BASE_URL + nextpage['href']
        del nextpage
        addMoviesdb(pagenext)

def getMovieInfo(url):
    tags = re.compile(r'<.*?>')
    scripts = re.compile(r'<script.*?script>',re.DOTALL)
    spaces = re.compile(r'\s+')
    data = getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    try:
        stardata = tree.find('span',attrs={'class':'crAvgStars'}).renderContents()
        stardata = scripts.sub('', stardata)
        stardata = tags.sub('', stardata)
        stardata = spaces.sub(' ', stardata).strip().split('out of ')
        stars = float(stardata[0])*2
        votes = stardata[1].split('customer reviews')[0].split('See all reviews')[1].replace('(','').strip()
    except:
        stars = 0.0
        votes = ''
    try:
        premieredpossible = tree.find('div', attrs={'class':'bucket','id':'stills'}).findAll('li')
        for item in premieredpossible:
            if item.contents[0].string == 'US Theatrical Release Date:':
                premiered = item.contents[1].strip()
                d = datetime.strptime(premiered, '%B %d, %Y')
                premiered = d.strftime('%Y-%m-%d')
        if not premiered:
            premiered = ''
    except:
        premiered = ''
    metadatas = tree.findAll('div', attrs={'style':'margin-top:7px;margin-bottom:7px;'})
    del tree, data
    metadict = {}
    for metadata in metadatas:
        mdata = metadata.renderContents()
        mdata = scripts.sub('', mdata)
        mdata = tags.sub('', mdata)
        mdata = spaces.sub(' ', mdata).strip().split(': ')
        metadict[mdata[0]] = mdata[1]
    try:plot = metadict['Synopsis']
    except: plot = ''
    try:director = metadict['Directed by']
    except:director = ''
    try:
        runtime = metadict['Runtime']
        if 'hours' in runtime:
            split = 'hours'
        elif 'hour' in runtime:
            split = 'hour'
        if 'minutes' in runtime:
            replace = 'minutes'
        elif 'minute' in runtime:
            replace = 'minute'
        if 'hour' not in runtime:
            runtime = runtime.replace(replace,'')
            minutes = int(runtime.strip())
        elif 'minute' not in runtime:
            runtime = runtime.replace(split,'')
            minutes = (int(runtime.strip())*60)     
        else:
            runtime = runtime.replace(replace,'').split(split)
            try:
                minutes = (int(runtime[0].strip())*60)+int(runtime[1].strip())
            except:
                minutes = (int(runtime[0].strip())*60)
        runtime = str(minutes)
    except: runtime = ''
    try: year = int(metadict['Release year'])
    except: year = 0
    try: studio = metadict['Studio']
    except: studio = ''
    try: mpaa = metadict['MPAA Rating']
    except: mpaa = ''
    try: actors = metadict['Starring']+', '+metadict['Supporting actors']
    except:
        try: actors = metadict['Starring']
        except: actors = ''      
    try: genres = metadict['Genre']
    except: genres = ''
    return plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes

################################ TV db

def loadTVdb():
    #if os.path.exists(tvDB):
    #   os.remove(tvDB)
    if not os.path.exists(tvDB):
        conn = sqlite.connect(tvDB)
        conn.text_factory = str
        c = conn.cursor()
        c.execute('''create table shows
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, seriestitle text, url text, poster text, season integer, episodes integer, plot text, creator text, runtime text, year integer, network text, actors text, genres text, stars float, votes string, HD boolean)''')
        c.close()
        addTVdb()
    conn = sqlite.connect(tvDB)
    c = conn.cursor()
    return c.execute('select * from shows order by seriestitle')

def getShowsdb():
    conn = sqlite.connect(tvDB)
    c = conn.cursor()
    return c.execute('select distinct seriestitle from shows')

def getShowGenres():
    conn = sqlite.connect(tvDB)
    c = conn.cursor()
    return c.execute('select distinct genres from shows')

def getShowNetworks():
    conn = sqlite.connect(tvDB)
    c = conn.cursor()
    return c.execute('select distinct network from shows')

def getShowCreators():
    conn = sqlite.connect(tvDB)
    c = conn.cursor()
    return c.execute('select distinct creator from shows')

def getShowYears():
    conn = sqlite.connect(tvDB)
    c = conn.cursor()
    return c.execute('select distinct year from shows')

def addTVdb(url=TV_URL):
    conn = sqlite.connect(tvDB)
    conn.text_factory = str
    c = conn.cursor()
    data = getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    atf = tree.find(attrs={'id':'atfResults'}).findAll('div',recursive=False)
    btf = tree.find(attrs={'id':'btfResults'}).findAll('div',recursive=False)
    nextpage = tree.find(attrs={'title':'Next page','id':'pagnNextLink','class':'pagnNext'})
    del tree
    del data
    for show in atf:
        link = show.find('a', attrs={'class':'title'})
        name = link.string
        if '[HD]' in name:
            isHD = True
        else:
            isHD = False
        name = name.split('Season ')[0].split('season ')[0].split('Volume ')[0].split('Series ')[0].split('Year ')[0].split(' The Complete')[0].replace('[HD]','').strip()
        if name.endswith('-') or name.endswith(',') or name.endswith(':'):
            name = name[:-1].strip()
        url = link['href']
        poster = show.find(attrs={'class':'image'}).find('img')['src'].replace('_AA160_','_SX500_')
        season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes = getShowInfo(url)
        strseason = str(season)
        if len(strseason)>2 and strseason in name:
            name = name.replace(strseason,'').strip()
        showdata = [None,name,url,poster,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,isHD]
        c.execute('insert into shows values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', showdata)
        conn.commit()
    for show in btf:
        link = show.find('a', attrs={'class':'title'})
        name = link.string
        if '[HD]' in name:
            isHD = True
        else:
            isHD = False
        name = name.split('Season ')[0].split('season ')[0].split('Volume ')[0].split('Series ')[0].split('Year ')[0].split(' The Complete')[0].replace('[HD]','').strip()
        if name.endswith('-') or name.endswith(',') or name.endswith(':'):
            name = name[:-1].strip()
        url = link['href']
        poster = show.find(attrs={'class':'image'}).find('img')['src'].replace('_AA160_','_SX500_')
        season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes = getShowInfo(url)
        strseason = str(season)
        if len(strseason)>2 and strseason in name:
            name = name.replace(strseason,'').strip()
        showdata = [None,name,url,poster,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,isHD]
        c.execute('insert into shows values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', showdata)
        conn.commit()
    c.close()
    if nextpage:
        del atf
        del btf
        pagenext = BASE_URL + nextpage['href']
        del nextpage
        addTVdb(pagenext)

def getShowInfo(url):
    tags = re.compile(r'<.*?>')
    scripts = re.compile(r'<script.*?script>',re.DOTALL)
    spaces = re.compile(r'\s+')
    data = getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    try:
        season = int(tree.find('div',attrs={'class':'unbox_season_selected'}).string)
    except:
        try:
            season = int(tree.find('div',attrs={'style':'font-size: 120%;font-weight:bold; margin-top:15px;margin-bottom:10px;'}).contents[0].split('Season')[1].strip())
        except:
            season = 0
    try:
        episodebox = tree.find('div',attrs={'id':'avod-ep-list-rows'}).findAll('tr',attrs={'asin':True})
        episodes = len(episodebox)
        del episodebox
    except:
        episodes = 1 
    try:
        stardata = tree.find('span',attrs={'class':'crAvgStars'}).renderContents()
        stardata = scripts.sub('', stardata)
        stardata = tags.sub('', stardata)
        stardata = spaces.sub(' ', stardata).strip().split('out of ')
        stars = float(stardata[0])*2
        votes = stardata[1].split('customer reviews')[0].split('See all reviews')[1].replace('(','').strip()
    except:
        stars = 0.0
        votes = ''
    metadatas = tree.findAll('div', attrs={'style':'margin-top:7px;margin-bottom:7px;'})
    del tree, data
    metadict = {}
    for metadata in metadatas:
        mdata = metadata.renderContents()
        mdata = scripts.sub('', mdata)
        mdata = tags.sub('', mdata)
        mdata = spaces.sub(' ', mdata).strip().split(': ')
        metadict[mdata[0]] = mdata[1]
    try:plot = metadict['Synopsis']
    except: plot = ''
    try:creator = metadict['Creator']
    except:creator = ''
    try:
        runtime = metadict['Runtime']
        if 'hours' in runtime:
            split = 'hours'
        elif 'hour' in runtime:
            split = 'hour'
        if 'minutes' in runtime:
            replace = 'minutes'
        elif 'minute' in runtime:
            replace = 'minute'
        if 'hour' not in runtime:
            runtime = runtime.replace(replace,'')
            minutes = int(runtime.strip())
        elif 'minute' not in runtime:
            runtime = runtime.replace(split,'')
            minutes = (int(runtime.strip())*60)     
        else:
            runtime = runtime.replace(replace,'').split(split)
            try:
                minutes = (int(runtime[0].strip())*60)+int(runtime[1].strip())
            except:
                minutes = (int(runtime[0].strip())*60)
        runtime = str(minutes)
    except: runtime = ''
    try: year = int(metadict['Season year'])
    except: year = 0
    try: network = metadict['Network']
    except: network = ''
    try: actors = metadict['Starring']+', '+metadict['Supporting actors']
    except:
        try: actors = metadict['Starring']
        except: actors = ''      
    try: genres = metadict['Genre']
    except: genres = ''
    return season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes    

################################ Root listing
def ROOT():
    login()
    addDir('Movie'      ,''                  ,'LIST_MOVIE_ROOT')
    addDir('Television' ,''                  ,'LIST_TV_ROOT')
    xbmcplugin.endOfDirectory(pluginhandle)

################################ Movie listing   
def LIST_MOVIE_ROOT():
    addDir('All Movies' ,'' ,'LIST_MOVIES')
    addDir('Genres'     ,'' ,'LIST_MOVIE_GENRE')
    addDir('Years'      ,'' ,'LIST_MOVIE_YEARS')
    addDir('MPAA Rating','' ,'LIST_MOVIE_MPAA')
    addDir('Studios'    ,'' ,'LIST_MOVIE_STUDIOS')
    addDir('Directors'  ,'' ,'LIST_MOVIE_DIRECTORS')
    #addDir('Actors'     ,'' ,'LIST_MOVIE_ACTORS')
    xbmcplugin.endOfDirectory(pluginhandle)

def LIST_MOVIE_GENRE_FILTERED():
    genrefilter = params['url']
    LIST_MOVIES(genrefilter=genrefilter)

def LIST_MOVIE_GENRE():
    genres = []
    genreUnsplit = getMovieGenres()
    for split in genreUnsplit:
        split = split[0].split(',')
        for genre in split:
            genre = genre.strip()
            if genre not in genres and genre <> '':
                genres.append(genre)
    for genre in genres:
        addDir(genre,genre,'LIST_MOVIE_GENRE_FILTERED')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)          
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

def LIST_MOVIE_ACTORS_FILTERED():
    actorfilter = params['url']
    LIST_MOVIES(actorfilter=actorfilter)

def LIST_MOVIE_ACTORS():
    actors = []
    actorsUnsplit = getMovieActors()
    for split in actorsUnsplit:
        split = split[0].split(',')
        for actor in split:
            actor = actor.strip().encode('utf-8')
            if actor not in actors and actor <> '':
                actors.append(actor)
    for actor in actors:
        addDir(actor,actor,'LIST_MOVIE_ACTORS_FILTERED')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)          
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

def LIST_MOVIE_DIRECTORS_FILTERED():
    directorfilter = params['url']
    LIST_MOVIES(directorfilter=directorfilter)
    
def LIST_MOVIE_DIRECTORS():
    directors = getMovieDirectors()
    list = []
    for director in directors:
        director = director[0].encode('utf-8')
        if director not in list and director <> '':
            list.append(director)
    for director in list:
        addDir(director,director,'LIST_MOVIE_DIRECTORS_FILTERED')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)          
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

def LIST_MOVIE_STUDIOS_FILTERED():
    studiofilter = params['url']
    LIST_MOVIES(studiofilter=studiofilter)
    
def LIST_MOVIE_STUDIOS():
    studios = getMovieStudios()
    list = []
    for studio in studios:
        studio = studio[0].encode('utf-8')
        if studio not in list and studio <> '':
            list.append(studio)
    for studio in list:
        addDir(studio,studio,'LIST_MOVIE_STUDIOS_FILTERED')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)          
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)
    
def LIST_MOVIE_YEARS_FILTERED():
    yearfilter = params['url']
    LIST_MOVIES(yearfilter=yearfilter)
    
def LIST_MOVIE_YEARS():
    years = getMovieYears()
    list = []
    for year in years:
        year = year[0]
        if year not in list and year <> 0:
            list.append(year)
    for year in list:
        addDir(str(year),str(year),'LIST_MOVIE_YEARS_FILTERED')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)          
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

def LIST_MOVIE_MPAA_FILTERED():
    mpaafilter = params['url']
    LIST_MOVIES(mpaafilter=mpaafilter)
    
def LIST_MOVIE_MPAA():
    mpaas = getMovieMPAA()
    list = []
    for mpaa in mpaas:
        mpaa = mpaa[0].split('for')[0].strip()
        if mpaa not in list and mpaa <> '':
            list.append(mpaa)
    for mpaa in list:
        addDir(mpaa,mpaa,'LIST_MOVIE_MPAA_FILTERED')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)          
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

def LIST_MOVIES(genrefilter=False,actorfilter=False,directorfilter=False,studiofilter=False,yearfilter=False,mpaafilter=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
    movies = loadMoviedb()
    for id,name,url,poster,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes in movies:
        if genrefilter:
            if genrefilter not in genres:
                continue
        elif actorfilter:
            if actorfilter not in actors:
                continue
        elif directorfilter:
            if directorfilter not in director:
                continue
        elif studiofilter:
            if studiofilter not in studio:
                continue
        elif yearfilter:
            if yearfilter <> str(year):
                continue
        elif mpaafilter:
            if mpaafilter not in mpaa:
                continue      
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode=PLAYVIDEO&name="+urllib.quote_plus(name)
        liz=xbmcgui.ListItem(name,iconImage=poster, thumbnailImage=poster)
        utrailer=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode=PLAYTRAILER&name="+urllib.quote_plus(name)
        actors = actors.split(',')
        liz.setInfo( type="Video", infoLabels={'Title':name,
                                               'Plot':plot,
                                               'Year':year,
                                               'premiered':premiered,
                                               'rating':stars,
                                               'votes':votes,
                                               'Genre':genres,
                                               'director':director,
                                               'studio':studio,
                                               'duration':runtime,
                                               'mpaa':mpaa,
                                               'cast':actors,
                                               'Trailer': utrailer})
        liz.setProperty('fanart_image',poster.replace('_SX500_','_BO354,0,0,0_CR177,354,708,500_'))
        liz.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_DURATION)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE)
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

###################### Television

def LIST_TV_ROOT():
    addDir('All Shows'  ,'LISTSHOWS'        ,'LIST_TVSHOWS')
    addDir('HDTV Shows' ,'LISTSHOWS'        ,'LIST_HDTVSHOWS')
    addDir('Genres'     ,'LISTSHOWS'        ,'LIST_TVSHOWS_GENRE')
    addDir('Networks'   ,'LISTSHOWS'        ,'LIST_TVSHOWS_NETWORKS')
    addDir('Years   '   ,'LISTSHOWS'        ,'LIST_TVSHOWS_YEARS')
    #addDir('Creators'   ,'LISTSHOWS'        ,'LIST_TVSHOWS_CREATORS')
    xbmcplugin.endOfDirectory(pluginhandle)
  
def LIST_TVSHOWS_GENRE_FILTERED():
    genrefilter = params['url']
    LIST_TVSHOWS(showmode='LISTSHOWS',genrefilter=genrefilter)

def LIST_TVSHOWS_GENRE():
    genres = []
    genreUnsplit = getShowGenres()
    for split in genreUnsplit:
        split = split[0].split(',')
        for genre in split:
            genre = genre.strip()
            if genre not in genres and genre <> '':
                genres.append(genre)
    for genre in genres:
        addDir(genre,genre,'LIST_TVSHOWS_GENRE_FILTERED')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)          
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

def LIST_TVSHOWS_CREATORS_FILTERED():
    creatorfilter = params['url']
    LIST_TVSHOWS(showmode='LISTSHOWS',creatorfilter=creatorfilter)

def LIST_TVSHOWS_CREATORS():
    creators = getShowCreators()
    list = []
    for creator in creators:
        creator = creator[0].encode('utf-8')
        if creator not in list and creator <> '':
            list.append(creator)
    for creator in list:
        addDir(creator,creator,'LIST_TVSHOWS_CREATORS_FILTERED')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)          
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

def LIST_TVSHOWS_NETWORKS_FILTERED():
    networkfilter = params['url']
    LIST_TVSHOWS(showmode='LISTSHOWS',networkfilter=networkfilter)
    
def LIST_TVSHOWS_NETWORKS():
    networks = getShowNetworks()
    list = []
    for network in networks:
        network = network[0].encode('utf-8')
        if network not in list and network <> '':
            list.append(network)
    for network in list:
        addDir(network,network,'LIST_TVSHOWS_NETWORKS_FILTERED')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)          
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)
    
def LIST_TVSHOWS_YEARS_FILTERED():
    yearfilter = params['url']
    LIST_TVSHOWS(showmode='LISTSHOWS',yearfilter=yearfilter)
    
def LIST_TVSHOWS_YEARS():
    years = getShowYears()
    list = []
    for year in years:
        year = year[0]
        if year not in list and year <> 0:
            list.append(year)
    for year in list:
        addDir(str(year),str(year),'LIST_TVSHOWS_YEARS_FILTERED')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)          
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

def LIST_HDTVSHOWS():
    LIST_TVSHOWS(HDonly=True)

def LIST_TVSHOWS(showmode=False,HDonly=False,genrefilter=False,creatorfilter=False,networkfilter=False,yearfilter=False,):
    if not showmode:
        showmode = params['url']
    shows = loadTVdb()
    shownamedata = getShowsdb()
    shownames = []
    for item in shownamedata:
        shownames.append(item[0])
    del shownamedata
    for id,name,url,poster,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,isHD in shows:
        if HDonly==True:
            if not isHD:
                continue
        elif genrefilter:
            if genrefilter not in genres:
                continue
        elif creatorfilter:
            if creatorfilter not in creator:
                continue
        elif networkfilter:
            if networkfilter not in network:
                continue
        elif yearfilter:
            if yearfilter <> str(year):
                continue
        if showmode == 'LISTSEASONS':
            xbmcplugin.setContent(int(sys.argv[1]), 'seasons')
            if params['name'] <> name:
                continue
            if season <> 0 and len(str(season)) < 3:
                displayname = 'Season '+str(season)
            else:
                displayname = name
            if isHD:
                displayname += ' [HD]'
            listmode = 'LIST_EPISODES'
        elif showmode == 'LISTSHOWS':
            xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
            if name in shownames:
                shownames.remove(name)
            else:
                continue
            displayname = name
            url = 'LISTSEASONS'
            if HDonly==True:
                listmode = 'LIST_HDTVSHOWS'
            else:
                listmode = 'LIST_TVSHOWS'

        actors = actors.split(',')
        infoLabels={'Title': name,
                       'Plot':plot,
                       'year':year,
                       #'premiered':str(year),
                       'rating':stars,
                       'votes':votes,
                       'Genre':genres,
                       'Season':season,
                       'episode':episodes,
                       'studio':network,
                       'duration':runtime,
                       'cast':actors,
                       'TVShowTitle':name,
                       'credits':creator}
        if year <> 0:
            infoLabels['premiered'] = str(year)
        u=sys.argv[0]              
        u+="?url="+urllib.quote_plus(url)
        u+="&mode="+urllib.quote_plus(listmode)
        u+="&name="+urllib.quote_plus(name)
        u+="&thumb="+urllib.quote_plus(poster)
        liz=xbmcgui.ListItem(displayname, iconImage="DefaultFolder.png", thumbnailImage=poster)
        liz.setInfo( type="Video", infoLabels=infoLabels)
        liz.setProperty('fanart_image',poster)
        xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=True)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE)
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

def LIST_EPISODES():
    episode_url = params['url']
    showname = params['name']
    thumbnail = params['thumb']
    xbmcplugin.setContent(int(sys.argv[1]), 'Episodes')   
    data = getURL(episode_url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    episodebox = tree.find('div',attrs={'id':'avod-ep-list-rows'})
    episodes = episodebox.findAll('tr',attrs={'asin':True})
    try:
        season = int(tree.find('div',attrs={'class':'unbox_season_selected'}).string)
    except:
        try:
            season = int(tree.find('div',attrs={'style':'font-size: 120%;font-weight:bold; margin-top:15px;margin-bottom:10px;'}).contents[0].split('Season')[1].strip())
        except:
            season = 0
    del tree
    del episodebox
    #Season and Episode info
    episodeNum = 0
    for episode in episodes:
        asin = episode['asin']
        name = episode.find(attrs={'title':True})['title'].encode('utf-8')
        airDate = episode.find(attrs={'style':'width: 150px; overflow: hidden'}).string.strip()
        try: plot =  episode.findAll('div')[1].string.strip()
        except: plot = ''
        episodeNum += 1
        if season == 0:
            displayname =  str(episodeNum)+'. '+name
        else:
            displayname =  str(season)+'x'+str(episodeNum)+' - '+name
        url = BASE_URL+'/gp/product/'+asin
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode=PLAYVIDEO&name="+urllib.quote_plus(name)
        liz=xbmcgui.ListItem(displayname, thumbnailImage=thumbnail)
        utrailer=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode=PLAYTRAILER&name="+urllib.quote_plus(name)
        liz.setProperty('IsPlayable', 'true')
        liz.setInfo( type="Video", infoLabels={'Title': name.replace('[HD]',''),
                                               'Plot':plot,
                                               'premiered':airDate,
                                               'Season':season,
                                               'Episode':episodeNum,
                                               'TVShowTitle':showname,
                                               'Trailer': utrailer})
        liz.setProperty('fanart_image',thumbnail)
        liz.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz)      
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)

############ SET PARAMETERS AND INIT
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
    ROOT()
else:
    exec '%s()' % mode
