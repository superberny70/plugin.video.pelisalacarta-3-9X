# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para guaridavalencianista
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os
import sys

from core import scrapertools
from core import config
from core import logger
from core.item import Item
from servers import servertools
#from pelisalacarta import buscador

__channel__ = "guaridavalencianista"
__category__ = "D"
__type__ = "generic"
__adult__ = "false"
__title__ = "La guarida Valencianista"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[guaridavalencianista.py] mainlist")
    itemlist=[]
    
    itemlist.append( Item(channel=__channel__, title="Novedades"  , action="listvideos" , url="http://guaridavalencia.blogspot.com.es"))
    #itemlist.append( Item(channel=__channel__, title="Documentales - Series Disponibles"  , action="DocuSeries" , url="http://guaridavalencia.blogspot.com/"))
    itemlist.append( Item(channel=__channel__, title="Categorias"  , action="DocuTag" , url="http://guaridavalencia.blogspot.com.es"))
    itemlist.append( Item(channel=__channel__, title="Partidos de liga (Temporada 2014/2015)"  , action="listvideos" , url="http://guaridavalencia.blogspot.com.es/search/label/PARTIDOS%20DEL%20VCF%20%28TEMPORADA%202014-15%29"))

    return itemlist

def search(item):
    logger.info("[guaridavalencianista.py] search")

    keyboard = xbmc.Keyboard('')
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        tecleado = keyboard.getText()
        if len(tecleado)>0:
            #convert to HTML
            tecleado = tecleado.replace(" ", "+")
            searchUrl = "http://guaridavalencia.blogspot.com/index.php?s="+tecleado
            SearchResult(params,searchUrl,category)
            
def SearchResult(item):
    logger.info("[guaridavalencianista.py] SearchResult")
    
    # Descarga la página
    data = scrapertools.cachePage(url)

    # Extrae las entradas (carpetas)
    patronvideos  = '<p class="entry-title"><[^>]+>[^<]+</span><a href="([^"]+)"[^>]+>([^<]+)</a></p>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        # Atributos
        scrapedurl = match[0]
        
        scrapedtitle =match[1]
        scrapedtitle = scrapedtitle.replace("&#8211;","-")
        scrapedtitle = scrapedtitle.replace("&nbsp;"," ")
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        xbmctools.addnewfolder( __channel__ , "detail" , category , scrapedtitle , scrapedurl , scrapedthumbnail, scrapedplot )

    # Propiedades
    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=category )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )
        

def performsearch(texto):
    logger.info("[guaridavalencianista.py] performsearch")
    url = "http://guaridavalencia.blogspot.com/index.php?s="+texto

    # Descarga la página
    data = scrapertools.cachePage(url)

    # Extrae las entradas (carpetas)
    patronvideos  = '<p class="entry-title"><[^>]+>[^<]+</span><a href="([^"]+)"[^>]+>([^<]+)</a></p>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    resultados = []

    for match in matches:
        scrapedtitle = match[1]
        scrapedtitle = scrapedtitle.replace("&#8211;","-")
        scrapedtitle = scrapedtitle.replace("&nbsp;"," ")
        scrapedurl = match[0]
        scrapedthumbnail = ""
        scrapedplot = ""

        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        resultados.append( [__channel__ , "detail" , "buscador" , scrapedtitle , scrapedurl , scrapedthumbnail, scrapedplot ] )
        
    return resultados

def DocuSeries(item):
    logger.info("[guaridavalencianista.py] DocuSeries")
    itemlist=[]
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patronvideos  = '<li><b><a href="([^"]+)" target="_blank">([^<]+)</a></b></li>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedurl = match[0]
        scrapedtitle = match[1]
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="listvideos", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    return itemlist

def DocuTag(item):
    logger.info("[guaridavalencianista.py] DocuTag")
    itemlist=[]
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    #~ patronvideos  =    "<a dir='ltr' href='([^']+)'>([^<]+)</a>[^<]+<span class='label-count' dir='ltr'>(.+?)</span>"
    patronvideos  =    "<li[^<]+<a dir='ltr' href='([^']+)'>([^<]+)</a[^<]+<span dir='ltr'>[^0-9]+([0-9]+)[^<]+</span[^<]+</li[^<]+"
    #~ patronvideos  =    "<li[^<]+<a dir='ltr' href='([^']+)'[^<]+([^<]+)</a>"
    #~ [^<]+<span class='label-count' dir='ltr'>(.+?)</span>"
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedurl = match[0]
	#Se debe quitar saltos de linea en match[1]
        scrapedtitle = match[1][1:-1] + " (" + match[2] + ")"
	#~ scrapedtitle = match[1]
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="listvideos", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    return itemlist

def DocuARCHIVO(item):
    logger.info("[guaridavalencianista.py] DocuSeries")
    itemlist=[]

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    patronvideos = "<a class='post-count-link' href='([^']+)'>([^<]+)</a>[^<]+"
    patronvideos +=    "<span class='post-count' dir='ltr'>(.+?)</span>"
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedurl = match[0]
        scrapedtitle = match[1] + " " + match[2]
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="listvideos", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    return itemlist
    
def DocuCat(item):
    logger.info("[guaridavalencianista.py] peliscat")
    itemlist=[]

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patronvideos  = '<li class="cat-item cat-item[^"]+"><a href="([^"]+)" title="[^"]+">([^<]+)</a>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        # Atributos
        scrapedtitle = match[1]
        scrapedurl = match[0]
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        xbmctools.addnewfolder( __channel__ , "listvideos" , category , scrapedtitle , scrapedurl , scrapedthumbnail, scrapedplot )

    # Propiedades
    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=category )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

def listvideos(item):
    logger.info("[guaridavalencianista.py] listvideos")
    itemlist=[]

    scrapedthumbnail = ""
    scrapedplot = ""

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    patronvideos  = "<h3 class='post-title entry-title'[^<]+"
    patronvideos += "<a href='([^']+)'>([^<]+)</a>.*?"
    patronvideos += "<div class='post-body entry-content'(.*?)<div class='post-footer'>"
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = match[1]
        scrapedtitle = re.sub("<[^>]+>"," ",scrapedtitle)
        scrapedtitle = scrapertools.unescape(scrapedtitle)[1:-1]
        scrapedurl = match[0]
        regexp = re.compile(r'src="(http[^"]+)"')
        
        matchthumb = regexp.search(match[2])
        if matchthumb is not None:
            scrapedthumbnail = matchthumb.group(1)
        matchplot = re.compile('<div align="center">(<img.*?)</span></div>',re.DOTALL).findall(match[2])

        if len(matchplot)>0:
            scrapedplot = matchplot[0]
            #print matchplot
        else:
            scrapedplot = ""

        scrapedplot = re.sub("<[^>]+>"," ",scrapedplot)
        scrapedplot = scrapertools.unescape(scrapedplot)
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        #xbmctools.addnewfolder( __channel__ , "findevi" , category , scrapedtitle , scrapedurl , scrapedthumbnail, scrapedplot )
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Extrae la marca de siguiente página
    patronvideos = "<a class='blog-pager-older-link' href='([^']+)'"
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedtitle = "Página siguiente"
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append( Item(channel=__channel__, action="listvideos", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    return itemlist

#~ def findvideos(item):
    #~ logger.info("[guaridavalencianista.py] findvideos")
    #~ itemlist=[]
    
    #~ # Descarga la página
    #~ data = scrapertools.cachePage(item.url)
    #~ data = scrapertools.get_match(data,"<div� class='post-body entry-content'(.*?)<div class='post-footer'>")

    #~ # Busca los enlaces a los videos
    #~ listavideos = servertools.findvideos(data)

    #~ for video in listavideos:
        #~ videotitle = scrapertools.unescape(video[0])
        #~ url = video[1]
        #~ server = video[2]
        #~ #xbmctools.addnewvideo( __channel__ , "play" , category , server ,  , url , thumbnail , plot )
        #~ itemlist.append( Item(channel=__channel__, action="play", server=server, title=videotitle , url=url , thumbnail=item.thumbnail , plot=item.plot , fulltitle = item.title , folder=False) )

    #~ return itemlist
def findvideos(item):
    logger.info("[guaridavalencianista.py] findvideos")
    data = scrapertools.cachePage(item.url)
    
    
    # Busca los enlaces a los videos
    
    listavideos = servertools.findvideos(data)

    if item is None:
        item = Item()

    itemlist = []
    for video in listavideos:
        scrapedtitle = video[0].strip() + " - " + item.title.strip()
        scrapedurl = video[1]
        server = video[2]
        
        itemlist.append( Item(channel=item.channel, title=scrapedtitle , action="play" , server=server, page=item.page, url=scrapedurl, thumbnail=item.thumbnail, show=item.show , plot=item.plot , folder=False) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    # mainlist
    mainlist_items = mainlist(Item())
    
    # Da por bueno el canal si alguno de los vídeos de "Novedades" devuelve mirrors
    documentales_items = listvideos(mainlist_items[0])
    
    bien = False
    for documental_item in documentales_items:
        mirrors = findvideos(documental_item)
        if len(mirrors)>0:
            bien = True
            break
    
    return bien