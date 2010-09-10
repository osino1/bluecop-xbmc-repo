import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,datetime
from BeautifulSoup import BeautifulStoneSoup
pluginhandle = int(sys.argv[1])


################################ Common
def getURL( url ):
    try:
        print 'TNT--> getURL :: url = '+url
        txdata = None
        txheaders = {
                    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US;rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)'	
                    }
        req = urllib2.Request(url, txdata, txheaders)
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
    except urllib2.URLError, e:
        error = 'Error code: '+ str(e.code)
        xbmcgui.Dialog().ok(error,error)
        print 'Error code: ', e.code
        return False
    else:
        return link

def addLink(name,url,mode,iconimage='',plot=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot":plot})
        liz.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage='',plot=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot":plot})
        ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=True)
        return ok

################################ Root listing
def ROOT():
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        url = 'http://www.tnt.tv/processors/services/getCollections.do?id=62028'
        html=getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        collections = tree.findAll('collection')
        for collection in collections:
                cid = collection['id']
                name = collection.find('name').string
                if name == 'Featured':
                        continue
                mode = 1 #SHOWS() Mode
                addDir(name,cid,mode)
        xbmcplugin.endOfDirectory(pluginhandle)

def SHOWS(name, cid):
        xbmcplugin.setContent(pluginhandle, 'shows')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        if name == 'Full Episodes' or name == 'Web Exclusives':
            mode = 3 #EPISODE() Mode
        else:
            mode = 2 #SHOW() Mode
        url = 'http://www.tnt.tv/processors/services/getCollections.do?id=62028'
        html=getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        collections = tree.findAll('collection')
        for collection in collections:
                if collection['id'] == cid:
                        subcollections = collection.findAll('subcollection')
                        for subcollection in subcollections:
                                scid = subcollection['id']
                                name = subcollection.find('name').string
                                addDir(name,scid,mode)
        xbmcplugin.endOfDirectory(pluginhandle)  

def SHOW(scid):
        xbmcplugin.setContent(pluginhandle, 'shows')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_NONE)
        url = 'http://www.tnt.tv/processors/services/getCollections.do?id=62028'
        html=getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        collections = tree.findAll('collection')
        for collection in collections:
                subcollections = collection.findAll('subcollection')
                for subcollection in subcollections:
                        if subcollection['id'] == scid:
                                subsubcollections = subcollection.findAll('subsubcollection')
                                for subsubcollection in subsubcollections:
                                        sscid = subsubcollection['id']
                                        name = subsubcollection.find('name').string
                                        mode = 3 #EPISODE() Mode
                                        addDir(name,sscid,mode)
        xbmcplugin.endOfDirectory(pluginhandle)
        
def EPISODE(cid):
        xbmcplugin.setContent(pluginhandle, 'episodes')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_NONE)
        url = 'http://www.tnt.tv/processors/services/getCollectionByContentId.do?offset=0&sort=&limit=200&id='+cid
        html=getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        episodes = tree.findAll('episode')
        for episode in episodes:
                episodeId = episode['id']
                name = episode.find('title').string
                thumbnail = episode.find('thumbnailurl').string
                plot = episode.find('description').string
                segments = episode.findAll('segment')
                if len(segments) == 0:
                    url = episodeId
                    mode = 4
                    addLink(name,url,mode,thumbnail,plot)
                else:
                    for segment in segments:
                            url = segment['id']
                            segname = segment.find('title').string
                            fname = name +' '+segname
                            mode = 4 #PLAY
                            addLink(fname,url,mode,thumbnail,plot)

        xbmcplugin.endOfDirectory(pluginhandle)

def getAUTH(aifp,window,tokentype,vid,filename):
        authUrl = 'http://www.tnt.tv/processors/video_cvp/token.jsp'
        parameters = {'aifp' : aifp,
                      'window' : window,
                      'authTokenType' : tokentype,
                      'videoId' : vid,
                      'profile' : 'tnt',
                      'path' : filename
                      }
        data = urllib.urlencode(parameters) # Use urllib to encode the parameters
        request = urllib2.Request(authUrl, data)
        response = urllib2.urlopen(request) # This request is sent in HTTP POST
        link = response.read(200000)
        response.close()
        return re.compile('<token>(.+?)</token>').findall(link)[0]

def PLAY(vid):
        url = 'http://www.tnt.tv/video_cvp/cvp/videoData/?id='+vid
        html=getURL(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        files = tree.findAll('file')
        #stream details
        filename = files[0].string
        if 'http://' in filename:
            item = xbmcgui.ListItem(path=filename)
            return xbmcplugin.setResolvedUrl(pluginhandle, True, item)
        else:
            filename = filename[1:len(filename)-4]
        serverDetails = tree.find('akamai')
        server = serverDetails.find('src').string.split('://')[1]
        #get auth
        tokentype = serverDetails.find('authtokentype').string
        window = serverDetails.find('window').string
        aifp = serverDetails.find('aifp').string
        auth=getAUTH(aifp,window,tokentype,vid,filename)
        
        swfUrl = 'http://www.tnt.tv/dramavision/tnt_video.swf'
        rtmp = 'rtmpe://'+server+'?'+auth+" swfurl="+swfUrl+" swfvfy=true"+' playpath='+filename
        item = xbmcgui.ListItem(path=rtmp)
        return xbmcplugin.setResolvedUrl(pluginhandle, True, item)


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
                                param[splitparams[0]]=splitparams[1]
                                
        return param

              
params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:
        thumbnail=urllib.unquote_plus(params["thumbnail"])
except:
        thumbnail=''

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)


if mode==None or url==None or len(url)<1:
        ROOT()
elif mode==1:
        SHOWS(name,url)
elif mode==2:
        SHOW(url)
elif mode==3:
        EPISODE(url)
elif mode==4:
        PLAY(url)
