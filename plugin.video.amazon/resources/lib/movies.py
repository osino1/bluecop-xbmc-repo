from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup
import os.path
import xbmcplugin
import xbmc
import xbmcgui
import resources.lib.common as common
try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite

NEW_MOVIE_URL = 'http://www.amazon.com/gp/search/ref=sr_nr_p_n_date_0?rh=n%3A2625373011%2Cn%3A!2644981011%2Cn%3A!2644982011%2Cn%3A2858778011%2Cn%3A2858905011%2Cp_85%3A2470955011%2Cp_n_date%3A2693527011&bbn=2858905011&ie=UTF8&qid=1315385409&rnid=2693522011'
MOVIE_URL = 'http://www.amazon.com/gp/search/ref=sr_st?qid=1314934213&rh=n%3A2625373011%2Cn%3A!2644981011%2Cn%3A!2644982011%2Cn%3A2858778011%2Cn%3A2858905011%2Cp_85%3A2470955011&sort=-releasedate'

################################ Movie db

def createMoviedb():
    c = MovieDB.cursor()
    c.execute('''create table movies
                (asin UNIQUE,movietitle PRIMARY KEY,url text,poster text,plot text,director text,writer text,runtime text,year integer,premiered text,studio text,mpaa text,actors text,genres text,stars float,votes string,TMDBbanner string,TMDBposter string,TMDBfanart string,isprime boolean,watched boolean,favor boolean)''')
    MovieDB.commit()
    c.close()

def loadMoviedb(genrefilter=False,actorfilter=False,directorfilter=False,studiofilter=False,yearfilter=False,mpaafilter=False,watchedfilter=False,favorfilter=False,isprime=True):
    c = MovieDB.cursor()
    if genrefilter:
        genrefilter = '%'+genrefilter+'%'
        return c.execute('select distinct * from movies where isprime = (?) and genres like (?)', (isprime,genrefilter))
    elif mpaafilter:
        mpaafilter = '%'+mpaafilter+'%'
        return c.execute('select distinct * from movies where isprime = (?) and mpaa like (?)', (isprime,mpaafilter))
    elif actorfilter:
        actorfilter = '%'+actorfilter+'%'
        return c.execute('select distinct * from movies where isprime = (?) and actors like (?)', (isprime,actorfilter))
    elif directorfilter:
        return c.execute('select distinct * from movies where isprime = (?) and director like (?)', (isprime,directorfilter))
    elif studiofilter:
        return c.execute('select distinct * from movies where isprime = (?) and studio = (?)', (isprime,studiofilter))
    elif yearfilter:    
        return c.execute('select distinct * from movies where isprime = (?) and year = (?)', (isprime,int(yearfilter)))
    elif watchedfilter:
        return c.execute('select distinct * from movies where isprime = (?) and watched = (?)', (isprime,watchedfilter))
    elif favorfilter:
        return c.execute('select distinct * from movies where isprime = (?) and favor = (?)', (isprime,favorfilter))        
    else:
        return c.execute('select distinct * from movies where isprime = (?)', (isprime,))

def getMovieTypes(col):
    c = MovieDB.cursor()
    items = c.execute('select distinct %s from movies' % col)
    list = []
    for data in items:
        data = data[0]
        if type(data) == type(str()):
            if 'Rated' in data:
                item = data.split('for')[0]
                if item not in list and item <> '' and item <> 0 and item <> 'Inc.' and item <> 'LLC.':
                    list.append(item)
            else:
                data = data.decode('utf-8').encode('utf-8').split(',')
                for item in data:
                    item = item.replace('& ','').strip()
                    if item not in list and item <> '' and item <> 0 and item <> 'Inc.' and item <> 'LLC.':
                        list.append(item)
        elif data <> 0:
            list.append(str(data))
    c.close()
    return list

def addNewMoviesdb():
    addMoviesdb(NEW_MOVIE_URL)

def addMoviesdb(url=MOVIE_URL):
    data = getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    atf = tree.find(attrs={'id':'atfResults'}).findAll('div',recursive=False)
    try:
        btf = tree.find(attrs={'id':'btfResults'}).findAll('div',recursive=False)
        atf.extend(btf)
        del btf
    except:
        print 'AMAZON: No btf found'
    nextpage = tree.find(attrs={'title':'Next page','id':'pagnNextLink','class':'pagnNext'})
    del tree
    del data  
    for movie in atf:
        asin = movie['name']
        movietitle = movie.find('a', attrs={'class':'title'}).string
        poster = movie.find(attrs={'class':'image'}).find('img')['src'].replace('._AA160_','')
        url = common.BASE_URL+'/gp/product/'+asin
        print getMovieInfo(asin,movietitle,url,poster,isPrime=True)
    del atf
    if nextpage:
        pagenext = common.BASE_URL + nextpage['href']
        del nextpage
        addMoviesdb(pagenext)

def getMovieInfo(asin,movietitle,url,poster,isPrime=False):
    c = MovieDB.cursor()
    returndata = c.execute('select asin,movietitle,url,poster,plot,director,writer,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,TMDBbanner,TMDBposter,TMDBfanart,isprime,watched,favor from movies where asin = (?) or movietitle = (?)', (asin,movietitle)).fetchone()
    c.close()
    if returndata:
        print 'AMAZON: Returning Cached Meta for ASIN: '+asin
        return returndata
    else:
        plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes = scrapeMovieInfo(asin)
        moviedata = [asin,movietitle,url,poster,plot,director,'',runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,'','','',isPrime,False,False]
        addMoviedb(moviedata)
        print 'AMAZON: Cached Meta for ASIN: '+asin
        return moviedata

def addMoviedb(moviedata):
    c = MovieDB.cursor()
    c.execute('insert or ignore into movies values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', moviedata)
    MovieDB.commit()
    c.close()

def deleteMoviedb(asin=False):
    if not asin:
        asin = common.args.url
    c = MovieDB.cursor()
    shownamedata = c.execute('delete from movies where asin = (?)', (asin,))
    MovieDB.commit()
    c.close()

def watchMoviedb(asin=False):
    if not asin:
        asin = common.args.url
    c = MovieDB.cursor()
    c.execute("update movies set watched=? where asin=?", (True,asin))
    MovieDB.commit()
    c.close()
    
def unwatchMoviedb(asin=False):
    if not asin:
        asin = common.args.url
    c = MovieDB.cursor()
    c.execute("update movies set watched=? where asin=?", (False,asin))
    MovieDB.commit()
    c.close()

def favorMoviedb(asin=False):
    if not asin:
        asin = common.args.url
    c = MovieDB.cursor()
    c.execute("update movies set favor=? where asin=?", (True,asin))
    MovieDB.commit()
    c.close()
    
def unfavorMoviedb(asin=False):
    if not asin:
        asin = common.args.url
    c = MovieDB.cursor()
    c.execute("update movies set favor=? where asin=?", (False,asin))
    MovieDB.commit()
    c.close()

def scrapeMovieInfo(asin):
    url = common.BASE_URL+'/gp/product/'+asin
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
        stars = None
        votes = None
    try:
        premieredpossible = tree.find('div', attrs={'class':'bucket','id':'stills'}).findAll('li')
        for item in premieredpossible:
            if item.contents[0].string == 'US Theatrical Release Date:':
                premiered = item.contents[1].strip()
                d = datetime.strptime(premiered, '%B %d, %Y')
                premiered = d.strftime('%Y-%m-%d')
        if not premiered:
            premiered = None
    except:
        premiered = None
    metadatas = tree.findAll('div', attrs={'style':'margin-top:7px;margin-bottom:7px;'})
    del tree, data
    metadict = {}
    for metadata in metadatas:
        mdata = metadata.renderContents()
        mdata = scripts.sub('', mdata)
        mdata = tags.sub('', mdata)
        mdata = spaces.sub(' ', mdata).strip().split(':')
        fd = ''
        for md in mdata[1:]:
            fd += ' '+md
        metadict[mdata[0].strip()] = fd.strip()
    try:plot = metadict['Synopsis']
    except: plot = None
    try:director = metadict['Directed by']
    except:director = None
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
    except: runtime = None
    try: year = int(metadict['Release year'])
    except: year = None
    try: studio = metadict['Studio']
    except: studio = None
    try: mpaa = metadict['MPAA Rating']
    except: mpaa = None
    try: actors = metadict['Starring']+', '+metadict['Supporting actors']
    except:
        try: actors = metadict['Starring']
        except: actors = None     
    try: genres = metadict['Genre']
    except: genres = None
    return plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes

MovieDBfile = os.path.join(os.getcwd().replace(';', ''),'resources','cache','movies.db')
if not os.path.exists(MovieDBfile):
    MovieDB = sqlite.connect(MovieDBfile)
    MovieDB.text_factory = str
    createMoviedb()
else:
    MovieDB = sqlite.connect(MovieDBfile)
    MovieDB.text_factory = str