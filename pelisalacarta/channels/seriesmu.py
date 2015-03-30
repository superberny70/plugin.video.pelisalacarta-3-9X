# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para seriesmu
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os,sys

from core import logger
from core import config
from core import scrapertools
from core import jsontools
from core.item import Item
from servers import servertools

__channel__ = "seriesmu"
__category__ = "F,S,D"
__type__ = "generic"
__title__ = "SeriesMU"
__language__ = "ES"

DEBUG = config.get_setting("debug")
host = "http://series.mu/"
#Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0
#DEFAULT_HEADERS = []
#DEFAULT_HEADERS.append( ["User-Agent","User-Agent=Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; es-ES; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12"] )



def isGeneric():
    return True

def login():
    url = "http://series.mu/login/"
    post = "user="+config.get_setting("seriesmuuser")+"&pass="+config.get_setting("seriesmupassword")
    data = scrapertools.cache_page(url,post=post)



def mainlist(item):
    logger.info("pelisalacarta.seriesmu mainlist")
    itemlist = []
    title ="Habilita tu cuenta en la configuración..."
    title = title.replace(title,"[COLOR greenyellow]"+title+"[/COLOR]")
    if config.get_setting("seriesmuaccount")!="true":
        itemlist.append( Item( channel=__channel__ , title=title , action="openconfig" , url="" , fanart="http://s17.postimg.org/6d3kggvvj/smfanlog.jpg", thumbnail="http://s2.postimg.org/c678law6x/smloglog.jpg",  folder=False ) )
    else:
        login()
        title ="Mis Series"
        title = title.replace(title,"[COLOR aqua][B]"+title+"[/B][/COLOR]")
        
        itemlist.append( Item(channel=__channel__, title=title      , action="mis_series", url="http://series.mu/catalogo/mis-series/1/", fanart="http://s27.postimg.org/agsoe4jir/smumsfan.jpg", thumbnail= "https://cdn4.iconfinder.com/data/icons/sabre/snow_sabre_black/512/folder_black_library.png"))
        title ="Series"
        title = title.replace(title,"[COLOR aqua][B]"+title+"[/B][/COLOR]")
        
        itemlist.append( Item(channel=__channel__, title=title      , action="catalogo", url="http://series.mu/catalogo/series/1/", fanart="http://s12.postimg.org/eh5r2oefh/smsfan.jpg", thumbnail="https://lh3.googleusercontent.com/-eSiNj7X0wQU/AAAAAAAAAAI/AAAAAAAAAEM/iolph9ldX5w/photo.jpg"))
        title ="Peliculas"
        title = title.replace(title,"[COLOR aqua][B]"+title+"[/B][/COLOR]")
        
        itemlist.append( Item(channel=__channel__, title=title     , action="catalogo", url="http://series.mu/catalogo/pelis/1/", fanart="http://s7.postimg.org/ybxhxdc0r/smpfan.jpg", thumbnail="http://cdn.flaticon.com/png/256/24949.png"))
       
        title ="Buscar..."
        title = title.replace(title,"[COLOR aqua][B]"+title+"[/B][/COLOR]")
        
        itemlist.append( Item(channel=__channel__, title=title      , action="search", url="http://series.mu/search/", fanart="http://s7.postimg.org/9be35fm6z/smbfan.jpg", thumbnail="http://cdn.mysitemyway.com/etc-mysitemyway/icons/legacy-previews/icons/black-ink-grunge-stamps-textures-icons-people-things/060097-black-ink-grunge-stamp-textures-icon-people-things-eye6.png"))
    

    return itemlist

def openconfig(item):
    if "xbmc" in config.get_platform() or "boxee" in config.get_platform():
        config.open_settings( )
    return []


def search(item,texto):
    logger.info("pelisalacarta.seriesmu search")
    itemlist = []
    
    url = urlparse.urljoin(host, "/search/")
    post = 'post=yes' + '&q='+ texto[0:18]

    item.extra = post
    
    try:
        return buscador(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []



def buscador(item, ):
    itemlist = []
    logger.info("pelisalacarta.seriesmu buscador    ")
    # Descarga la página
    
    data = scrapertools.cache_page(item.url,post=item.extra)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    logger.info("data="+data)
    
    
    patron = '<a href="([^"]+)".*?'
    patron += 'src="([^"]+)".*?'
    patron += '<h2>(.*?)</h2>'
    
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    
    
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(host, scrapedurl)
        if "series" in scrapedurl:
            action= "temporadas"
            
        if "peli" in scrapedurl:
                action="peliculas"
    
        itemlist.append( Item(channel=__channel__, title =scrapedtitle , url=scrapedurl, action=action, thumbnail= scrapedthumbnail, fanart="http://s21.postimg.org/gmwquc5hz/smfan2.jpg", folder=True) )

    return itemlist

def mis_series(item):
    logger.info("pelisalacarta.seriesmu mis_series")
    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)

    patron = '<div.*?class="col-md-2.*?media".*?>.*?'
    patron += '<a href="([^"]+)".*?'
    patron += 'src="([^"]+)".*?'
    patron += '<h2>(.*?)</h2>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(host, scrapedurl)
        scrapedtitle = scrapedtitle.replace(scrapedtitle,"[COLOR sandybrown][B]"+scrapedtitle+"[/B][/COLOR]")
        
        itemlist.append( Item(channel=__channel__, title =scrapedtitle , url=scrapedurl, action="temporadas", thumbnail=scrapedthumbnail, fanart="http://s21.postimg.org/gmwquc5hz/smfan2.jpg", folder=True) )

    return itemlist

def catalogo(item):
    logger.info("pelisalacarta.seriesmu peliculas")
    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    patronseries = 'Mis series</a></div>(.*?)</a></li></ul></div></div></div>'
    matchesseries = re.compile(patronseries,re.DOTALL).findall(data)
    
    for bloque_series in matchesseries:
        if (DEBUG): logger.info("bloque_series="+bloque_series)
        # Extrae las series
    
        patron = '<a href="([^"]+)".*?'
        patron += 'src="([^"]+)".*?'
        patron += '<h2>(.*?)</h2>.*?'
        patron += '<h3>([^<]+)</h3>'
    
    
        matches = re.compile(patron,re.DOTALL).findall(bloque_series)
        scrapertools.printMatches(matches)
    

        for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedinfo in matches:
            scrapedinfo = scrapedinfo.replace(scrapedinfo,"[COLOR gold]"+scrapedinfo+"[/COLOR]")
            scrapedtitle = scrapedtitle.replace(scrapedtitle,"[COLOR white]"+scrapedtitle+"[/COLOR]")
            title = scrapedtitle +  " (" + scrapedinfo + ")"
            scrapedurl = urlparse.urljoin(host, scrapedurl)
            if "series" in scrapedurl:
                action= "temporadas"
            
            if "peli" in scrapedurl:
                action="peliculas"
        
        
            itemlist.append( Item(channel=__channel__, title =title , url=scrapedurl, action=action, thumbnail=scrapedthumbnail, fanart="http://s21.postimg.org/gmwquc5hz/smfan2.jpg", folder=True) )
    ## Paginación
    try:
        next_page = scrapertools.get_match(data,'<a href="([^"]+)">Siguiente &rsaquo;</a></li></ul></div></div></div>')
        next_page = urlparse.urljoin(host, next_page)
        title= "[COLOR blue]>> Página siguiente[/COLOR]"
        itemlist.append( Item(channel=__channel__, title=title, url=next_page, action="catalogo" , fanart="http://s21.postimg.org/gmwquc5hz/smfan2.jpg", thumbnail="http://s21.postimg.org/pro3rcu6v/smarrow.jpg", folder=True) )
    except: pass
   

    return itemlist

def peliculas(item):
    logger.info("pelisalacarta.seriesmu temporadas")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)

    patron = '<div class="link-row">'
    patron += '<a href="([^"]+)".*?'
    patron += '<div class="host.*?([^<]+)"></div>.*?'
    patron += '<div class="lang audio">([^<]+)</div>.*?'
    patron += '<div class="quality">([^<]+)</div>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedhost, scrapedaudio, scrapedcalidad in matches:
        scrapedhost= scrapedhost.replace("net","")
        scrapedhost= scrapedhost.replace("eu","")
        scrapedhost= scrapedhost.replace("sx","")
        puntuacion = scrapertools.get_match(data,'<li><div class="num" id="val-score">(.*?)</div>')
        puntuacion = puntuacion.replace(puntuacion,"[COLOR yellow]"+puntuacion+"[/COLOR]")
        puntuacion_title = "Puntuación :"
        puntuacion_title = puntuacion_title.replace(puntuacion_title,"[COLOR pink]"+puntuacion_title+"[/COLOR]")
        puntuacion = puntuacion_title + " " + puntuacion + "[CR]"
        scrapedplot = scrapertools.get_match(data,'<h2>(.*?)<div class="card media-chapters">')
        plotformat = re.compile('<p>(.*?)</p>',re.DOTALL).findall(scrapedplot)
        scrapedplot = scrapedplot.replace(scrapedplot,"[COLOR white]"+scrapedplot+"[/COLOR]")
        for plot in plotformat:
            scrapedplot = scrapedplot.replace(plot,"[COLOR skyblue][B]"+plot+"[/B][/COLOR]")
            scrapedplot = scrapedplot.replace("</h2><p>","[CR]")
            scrapedplot = scrapedplot.replace("</p></div>","")
        scrapedplot = puntuacion + scrapedplot
        scrapedhost = scrapedhost.replace(scrapedhost,"[COLOR burlywood]"+scrapedhost+"[/COLOR]")
        scrapedaudio = scrapedaudio.replace(scrapedaudio,"[COLOR white]"+scrapedaudio+"[/COLOR]")
        scrapedcalidad = scrapedcalidad.replace(scrapedcalidad,"[COLOR olive]"+scrapedcalidad+"[/COLOR]")
        fanart = scrapertools.get_match(data,'<div class="media-cover" style="background-image: url\(http://series.mu([^"]+)\)')
        fanart = urlparse.urljoin(host, fanart)
        
        title = scrapedhost + "--" + scrapedaudio + "--" + scrapedcalidad
        itemlist.append( Item(channel=__channel__, action="play", title= title  , url=scrapedurl , thumbnail=item.thumbnail , plot=scrapedplot, fanart=fanart, folder=True) )


    return itemlist


def temporadas(item):
    logger.info("pelisalacarta.seriesmu temporadas")
    itemlist = []
    
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    
    seguir = scrapertools.get_match(data,'<ul><li text="Siguiendo" color="green" class="([^"]+)"')
    abandonar = scrapertools.get_match(data,'<li text="Abandonada" color="red" class="([^"]+)">')
    fanart = scrapertools.get_match(data,'<div class="media-cover" style="background-image: url\(http://series.mu([^"]+)\)')
    fanart = urlparse.urljoin(host, fanart)
    seguir = urlparse.urljoin(host, seguir)
    abandonar = urlparse.urljoin(host, abandonar)
   
    if '<div class=""></div>' in data:
        action="seguir"
        title= "Seguir"
        title = title.replace(title,"[COLOR yellow]"+title+"[/COLOR]")
        thumbnail= "http://s14.postimg.org/ca5boj275/smseguir.png"


    else:
        action="siguiendo"
        title= "Siguiendo"
        title = title.replace(title,"[COLOR green]"+title+"[/COLOR]")
        thumbnail="http://s28.postimg.org/ugtnbj6z1/smsiguiendo2.png"
    
    itemlist.append( Item(channel=item.channel, title=title, url=seguir, fanart=fanart, thumbnail=thumbnail, action=action))

    if '<div class="green">' in data:
        
        action="abandono"
        title= "Abandonar"
        title = title.replace(title,"[COLOR red]"+title+"[/COLOR]")

        itemlist.append( Item(channel=item.channel, title=title, url=abandonar, fanart=fanart, thumbnail="http://s18.postimg.org/hh4l8hj1l/smabandonar2.png", action=action))




    patrontemporada = '<ul (temp[^<]+)>(.*?)>Marcar como vista</a>'
    matchestemporadas = re.compile(patrontemporada,re.DOTALL).findall(data)
    
    for nombre_temporada,bloque_episodios in matchestemporadas:
        if (DEBUG): logger.info("nombre_temporada="+nombre_temporada)
        if (DEBUG): logger.info("bloque_episodios="+bloque_episodios)
        # Extrae los episodios
        
    
        patron = '<span>(.*?)'
        patron += '</span>([^<]+).*?'
        patron += '<i class="(.*?)".*?'
        patron += '<i class="icon-play".*?'
        patron += 'href="([^"]+)"'
    
    
        matches = re.compile(patron,re.DOTALL).findall(bloque_episodios)
        scrapertools.printMatches(matches)
    
        for scrapednumber, scrapedtitle, scrapedeyes, scrapedurl in matches:
        
            if "open" in scrapedeyes:
               scrapedeyes = re.sub(r"eye-w icon-eye-open","[COLOR salmon]"+" [Visto]"+"[/COLOR]",scrapedeyes)
            if "close" in scrapedeyes:
               scrapedeyes = re.sub(r"eye-w icon-eye-close","[COLOR chartreuse]"+" [Pendiente]"+"[/COLOR]",scrapedeyes)
            scrapedtitle = nombre_temporada + "X" + scrapednumber + scrapedtitle + scrapedeyes
            scrapedtitle = scrapedtitle.replace("="," ")
            scrapedtitle = scrapedtitle.replace("temp","Temporada")
            scrapedtitle = scrapedtitle.replace(scrapedtitle,"[COLOR white]"+scrapedtitle+"[/COLOR]")
            puntuacion = scrapertools.get_match(data,'<li><div class="num" id="val-score">(.*?)</div>')
            puntuacion = puntuacion.replace(puntuacion,"[COLOR yellow]"+puntuacion+"[/COLOR]")
            puntuacion_title = "Puntuación :"
            puntuacion_title = puntuacion_title.replace(puntuacion_title,"[COLOR pink]"+puntuacion_title+"[/COLOR]")
            puntuacion = puntuacion_title + " " + puntuacion + "[CR]"
            scrapedplot = scrapertools.get_match(data,'<h2>(.*?)<div class="card media-chapters">')
            plotformat = re.compile('<p>(.*?)</p>',re.DOTALL).findall(scrapedplot)
            scrapedplot = scrapedplot.replace(scrapedplot,"[COLOR white]"+scrapedplot+"[/COLOR]")
            for plot in plotformat:
                scrapedplot = scrapedplot.replace(plot,"[COLOR skyblue][B]"+plot+"[/B][/COLOR]")
                scrapedplot = scrapedplot.replace("</h2><p>","[CR]")
                scrapedplot = scrapedplot.replace("</p></div>","")
            scrapedplot = puntuacion + scrapedplot
            fanart = scrapertools.get_match(data,'<div class="media-cover" style="background-image: url\(http://series.mu([^"]+)\)')
            fanart = urlparse.urljoin(host, fanart)
            scrapedurl = urlparse.urljoin(host, scrapedurl)
        
            itemlist.append( Item(channel=__channel__, title =scrapedtitle , url=scrapedurl, action="findvideos", thumbnail=item.thumbnail, plot=scrapedplot, fanart=fanart, folder=True) )
        



    
    

    
    return itemlist



def seguir(item):
    logger.info("pelisalacarta.seriesmu seguir")
    
    itemlist = []
    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    if "status" in item.url:
        title= "Siguiendo!!"
        title = title.replace(title,"[COLOR green]"+title+"[/COLOR]")
        itemlist.append( Item(channel=__channel__, title= title,  fanart=item.fanart, thumbnail="http://s9.postimg.org/vc0l27qgf/smyasigue.png", folder=False) )

    return itemlist

def siguiendo(item):
    logger.info("pelisalacarta.seriesmu siguiendo")
    
    itemlist = []
    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    if "status" in item.url:
        title= "Ya sigues esta serie..."
        title = title.replace(title,"[COLOR red]"+title+"[/COLOR]")
        itemlist.append( Item(channel=__channel__, title= title, fanart=item.fanart, thumbnail="http://s12.postimg.org/ms7q9hj4d/smnotallowed.png", folder=False) )
    
    return itemlist

def abandono(item):
    logger.info("pelisalacarta.seriesmu siguiendo")
    
    itemlist = []
    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    if "status" in item.url:
        title= "Abandonada..."
        title = title.replace(title,"[COLOR red]"+title+"[/COLOR]")
        itemlist.append( Item(channel=__channel__, title= title, fanart=item.fanart, thumbnail="http://www.clker.com/cliparts/2/l/m/p/B/b/error-hi.png", folder=False) )
    
    return itemlist






def findvideos(item):
    logger.info("pelisalacarta.seriesmu findvideos")
    
    itemlist = []
    # Descarga la pagina
   
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    
    patronlinks = '<div class="sections episode-links online shown">(.*?)<div class="sections episode-comments">'
    matcheslinks = re.compile(patronlinks,re.DOTALL).findall(data)
    
    for bloque_links in matcheslinks:
        if (DEBUG): logger.info("bloque_links="+bloque_links)
        # Extrae los episodios
        
        patron = '<li><div class="link-row">'
        patron += '<a href="([^"]+)".*?'
        patron += '<div class="host.*?([^<]+)"></div>.*?'
        patron += '<div class="lang audio">([^<]+)</div>.*?'
        patron += '<div class="quality">([^<]+)</div></a></div></li>'
    
    
        matches = re.compile(patron,re.DOTALL).findall(data)
        scrapertools.printMatches(matches)

        for scrapedurl, scrapedhost, scrapedaudio, scrapedcalidad in matches:
            scrapedhost= scrapedhost.replace("net","")
            scrapedhost= scrapedhost.replace("eu","")
            scrapedhost= scrapedhost.replace("sx","")
            scrapedhost = scrapedhost.replace(scrapedhost,"[COLOR burlywood]"+scrapedhost+"[/COLOR]")
            scrapedaudio = scrapedaudio.replace(scrapedaudio,"[COLOR white]"+scrapedaudio+"[/COLOR]")
            scrapedcalidad = scrapedcalidad.replace(scrapedcalidad,"[COLOR olive]"+scrapedcalidad+"[/COLOR]")
            scrapedurl = urlparse.urljoin(host, scrapedurl)
            
            title = scrapedhost + "--" + scrapedaudio + "--" + scrapedcalidad
            
            

            itemlist.append( Item(channel=__channel__, action="play", title= title  , url=scrapedurl , thumbnail=item.thumbnail , fanart=item.fanart, folder=True) )



   



    return itemlist

def play(item):
    logger.info("pelisalacarta.seriesmu play")

    media_url = scrapertools.get_header_from_response(item.url,header_to_get="location")
    itemlist = servertools.find_video_items(data=media_url)

    if len(itemlist) == 0:
        itemlist = servertools.find_video_items(data=item.url)

    return itemlist




