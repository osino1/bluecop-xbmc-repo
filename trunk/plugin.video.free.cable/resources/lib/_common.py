import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import addoncompat

pluginhandle = int (sys.argv[1])
"""
    PARSE ARGV
"""

class _Info:
    def __init__( self, *args, **kwargs ):
        print "common.args"
        print kwargs
        self.__dict__.update( kwargs )

exec "args = _Info(%s)" % (urllib.unquote_plus(sys.argv[2][1:].replace("&", ", ").replace('"','\'')) , )



"""
    DEFINE
"""
site_dict = {'ABC': 'abc',
             'ABC Family':'abcfamily',
             'CBS': 'cbs',
             'NBC': 'nbc',
             'USA': 'usa',
             'SyFy': 'syfy',
             'FOX': 'fox',
             'The CW':'thecw',
             'FX': 'fx',
             'TNT': 'tnt',
             'TBS': 'tbs',
             'Spike':'spike',
             'TV Land':'tvland'
             }


"""
    GET SETTINGS
"""

settings={}
#settings general
quality = ['200', '400', '600', '800', '1000', '1200', '1400', '1600', '2000', '2500', '3000', '100000']
selectquality = int(addoncompat.get_setting('quality'))
settings['quality'] = quality[selectquality]
settings['enableproxy'] = addoncompat.get_setting('us_proxy_enable')


"""
    ADD DIRECTORY
"""

def addDirectory(name, mode='', sitemode='', url='', thumb=''):
    ok=True
    u  = sys.argv[0]
    u += '?url="'+urllib.quote_plus(url)+'"'
    u += '&mode="'+mode+'"'
    u += '&sitemode="'+sitemode+'"'
    u += '&name="'+urllib.quote_plus(name.replace("'",''))+'"'
    liz=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
    liz.setInfo( type="Video", infoLabels={ "Title":name })
    ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=True)
    return ok


def getURL( url , values = None ,proxy = False):
    try:
        if proxy == True:
            us_proxy = 'http://' + addoncompat.get_setting('us_proxy') + ':' + addoncompat.get_setting('us_proxy_port')
            print 'Using proxy: ' + us_proxy
            proxy_handler = urllib2.ProxyHandler({'http':us_proxy})
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)

        print 'FREE CABLE --> common :: getHTML :: url = '+url
        if values == None:
            req = urllib2.Request(url)
        else:
            data = urllib.urlencode(values)
            req = urllib2.Request(url,data)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
    except urllib2.URLError, e:
        print 'Error reason: ', e.reason
        return False
    else:
        return link
        
    



