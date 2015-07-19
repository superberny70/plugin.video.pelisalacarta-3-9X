# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para oranline
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import re
import sys

from core import logger
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "oranline"
__category__ = "F"
__type__ = "generic"
__title__ = "oranline"
__language__ = "ES"

host = "http://www.oranline.com"

def isGeneric():
    return True

def mainlist( item ):
    logger.info( "pelisalacarta.channels.oranline mainlist" )

    itemlist = []

    itemlist.append( Item( channel=__channel__, action="menupeliculas", title="Peliculas" ) )
    itemlist.append( Item( channel=__channel__, action="peliculas", title="Documentales", url=host + "/Pel%C3%ADculas/documentales/" ) )
    itemlist.append( Item( channel=__channel__, action="search", title="Buscar..." ) )
    itemlist.append( Item( channel=__channel__, action="search", title="Buscar... (sin paginación)" ) )

    return itemlist

def menupeliculas( item ):
    logger.info( "pelisalacarta.channels.oranline menupeliculas" )

    itemlist = []

    path = "/Pel%C3%ADculas/peliculas"

    itemlist.append( Item( channel=__channel__, action="peliculas", title="Ordenadas por fecha", url=host + path + "/?orderby=date" ) )
    itemlist.append( Item( channel=__channel__, action="peliculas", title="Ordenadas por título", url=host + path + "/?orderby=title" ) )
    itemlist.append( Item( channel=__channel__, action="peliculas", title="Ordenadas por valoración", url=host + path + "/?gdsr_sort=rating&gdsr_multi=" ) )
    itemlist.append( Item( channel=__channel__, action="letras", title="A-Z" ) )
    itemlist.append( Item( channel=__channel__, action="letras", title="A-Z (sin paginación)" ) )
    itemlist.append( Item( channel=__channel__, action="generos", title="Últimas por géneros", url=host ) )
    itemlist.append( Item( channel=__channel__, action="idiomas", title="Últimas por idioma", url=host ) )

    return itemlist

def search( item ,texto ):
    logger.info( "pelisalacarta.channels.oranline search" )

    item.url = host + "/?s=" + texto

    try:
        if "(" in item.title:
            item.extra = "peliculas"
            return completo( item )
        else:
            return peliculas( item )

    ## Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def peliculas( item ):
    logger.info( "pelisalacarta.channels.oranline peliculas" )

    itemlist = []

    ## Descarga la página
    data = agrupa_datos( scrapertools.cache_page( item.url ) )

    patron  = '<div class="post-thumbnail">'
    patron += '<a href="([^"]+)" title="([^"]+)">'
    patron += '<img src="([^"]+)".*?'
    patron += '<span>([^<]+)</span>.*?'
    patron += '<p>([^<]+)</p>.*?'
    patron += '<div id="campos_idiomas">(.*?)</div>'

    matches = re.compile( patron, re.DOTALL ).findall( data )

    for scrapedurl, scrapedtitle, scrapedthumbnail, calidad, scrapedplot, text_idiomas in matches:
        scrapedtitle = re.sub( r'\s*ver online y descargar*', '', scrapedtitle, flags=re.I )
        title = scrapedtitle + " (" +  calidad + ") (" + get_idiomas( text_idiomas ) + ")"

        itemlist.append( Item( channel=__channel__, action="ver_descargar", title=title, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot ) )

    try:
        next_page = scrapertools.get_match( data, "<a href='([^']+)'>\&rsaquo\;</a>" )
        itemlist.append( Item( channel=__channel__, action="peliculas", title=">> Página siguiente", url=next_page ) )
    except:
        try:
            next_page = scrapertools.get_match( data, "<span class='current'>\d+</span><a href='([^']+)'" )
            itemlist.append( Item( channel=__channel__, action="peliculas", title=">> Página siguiente", url=next_page ) )
        except:
            pass
        pass

    return itemlist

def letras( item ):
    logger.info( "pelisalacarta.channels.oranline letras" )

    itemlist = []

    az = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    for letra in az:
        url = host + "/?s=letra-%s" % letra.lower()
        if "(" in item.title:
            itemlist.append( Item( channel=__channel__, action='completo', title=letra, url=url, extra="peliculas" ) )
        else:
            itemlist.append( Item( channel=__channel__, action='peliculas', title=letra, url=url ) )

    return itemlist

def generos( item ):
    logger.info( "pelisalacarta.channels.oranline generos" )

    itemlist = []

    ## Descarga la página
    data = agrupa_datos( scrapertools.cache_page( item.url ) )

    data = scrapertools.get_match( data, '<li class="cat-item cat-item-\d+"><a href="http://www.oranline.com/Pel.*?s/generos/"[^<]+</a>(.*?)</ul>' )
    data = re.sub( r'\((\d)\.(\d+)\)', r'(\1\2)', data)

    ## Extrae las entradas
    patron  = '<li class="cat-item cat-item-\d+"><a href="([^"]+)"[^>]+>([^<]+)</a>\((\d+)\)'

    matches = re.compile( patron, re.DOTALL ).findall( data )

    for scrapedurl, scrapedtitle, cuantas in matches:
        title = scrapedtitle + " (" + cuantas + ")"

        itemlist.append( Item( channel=__channel__, action="peliculas", title=title, url=scrapedurl ) )

    return itemlist

def idiomas( item ):
    logger.info( "pelisalacarta.channels.oranline idiomas" )

    itemlist = []

    ## Descarga la página
    data = agrupa_datos( scrapertools.cache_page( item.url ) )

    data = scrapertools.get_match( data, '<div class="widget"><h3>Últimos estrenos</h3>(.*?)</ul>' )
    data = re.sub( r'\((\d)\.(\d+)\)', r'(\1\2)', data)

    ## Extrae las entradas
    patron  = '<li class="cat-item cat-item-\d+"><a href="([^"]+)" >([^<]+)</a>\((\d+)\)'

    matches = re.compile( patron, re.DOTALL ).findall( data )

    for scrapedurl, scrapedtitle, cuantas in matches:
        title = scrapedtitle + " (" + cuantas + ")"

        itemlist.append( Item( channel=__channel__, action="peliculas", title=title, url=scrapedurl ) )

    return itemlist

def ver_descargar( item ):
    logger.info( "pelisalacarta.channels.oranline ver_descargar" )

    itemlist = []

    ## Descarga la pagina
    data = agrupa_datos( scrapertools.cache_page( item.url ) )

    url_youtube = scrapertools.find_single_match( data, 'src=".*?(www.youtube.com/embed/[^"]+)"' )
    if url_youtube != "":
        url_youtube = "https://" + url_youtube

        itemlist.append( Item( channel=__channel__, action="play", title="Trailer [YouTube]", url=url_youtube, server="youtube", fulltitle=item.title, folder=False ) )

    descargar = scrapertools.find_single_match( data, '<div id="descarga">.*?(<p><span><img.*?</p>)</div></div>' )
    ver = scrapertools.find_single_match( data, '<div id="veronline">.*?(<p><span><img.*?</p>)</div></div>' )

    itemlist.append( Item( channel=__channel__, action="findvideos", title="Enlaces para ver", extra=ver, fulltitle=item.title ) )
    itemlist.append( Item( channel=__channel__, action="findvideos", title="Enlaces para descargar", extra=descargar, fulltitle=item.title ) )

    return itemlist

def findvideos( item ):
    logger.info( "pelisalacarta.channels.oranline pre_findvideos" )

    itemlist = []

    patron = 'src="([^"]+)".*?'
    patron+= '<span>([^<]+)</span>.*?'
    patron+= '<a href="(/wp-content/themes/reviewit/enlace.php.id=\d+)".*?'
    patron+= 'src="([^"]+)"'

    matches = re.compile( patron, re.DOTALL ).findall( item.extra )

    for text_idiomas, calidad, scrapedurl, scrapedthumbnail in matches:
        tipo = "Ver en "
        if item.title == "Enlaces para descargar": tipo = "Descragar de "

        server = scrapertools.get_match( scrapedthumbnail, 'servidores/([^\.]+)\.' )
        title = tipo + server + " (" + calidad + ") (" + get_idiomas( text_idiomas ) + ")"
        url = "http://oranline.com" + scrapedurl

        itemlist.append( Item( channel=__channel__, action="play", title=title, url=url, thumbnail=scrapedthumbnail, server=server, fulltitle=item.fulltitle, folder=False ) )

    return itemlist

def play( item ):
    logger.info( "pelisalacarta.channels.oranline play" )

    itemlist = []

    data = agrupa_datos( scrapertools.cache_page( item.url ) )

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.fulltitle
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist

def get_idiomas( text_idiomas ):
    logger.info( "pelisalacarta.channels.oranline get_idiomas" )

    text = ""

    if "s.png" in text_idiomas:
        text+= "ESP,"
    if "l.png" in text_idiomas:
        text+= "LAT,"
    if "i.png" in text_idiomas:
        text+= "ING,"
    if "v.png" in text_idiomas:
        text+= "VOSE,"

    if "1.png" in text_idiomas:
        text+= "ESP,"
    if "2.png" in text_idiomas:
        text+= "LAT,"
    if "3.png" in text_idiomas:
        text+= "VOSE,"
    if "4.png" in text_idiomas:
        text+= "ING,"

    return text[:-1]

## --------------------------------------------------------------------------------
## --------------------------------------------------------------------------------

## Agrupa los items de una función con paginación.
## item.extra debe contener en nombre de la función con
## paginación de la que se quiere agrupar los items.
def completo( item ):
    logger.info( "pelisalacarta.channels.oranline completo" )

    itemlist = []

    ## Carga la primera página de items de la función contenida en item.extra
    exec "items_programas = " + item.extra + "( item )"
    if len( items_programas ) == 0: return []

    salir = False
    while not salir:

        ## Saca la URL de la siguiente página
        ultimo_item = items_programas[ len( items_programas )-1 ]

        ## Páginas intermedias
        if ultimo_item.action == item.extra:
            ## Quita el elemento de "Página siguiente" 
            ultimo_item = items_programas.pop()

            ## Añade los items de la página a la lista completa
            itemlist.extend( items_programas )
    
            ## Carga la sigiuente página
            exec "items_programas = " + item.extra + "( ultimo_item )"

        ## Última página
        else:
            ## Añade a la lista completa la última página y sale
            itemlist.extend( items_programas )
            salir = True

    return itemlist

## Agrupa los datos
def agrupa_datos( data ):
    logger.info( "pelisalacarta.channels.oranline agrupa_datos" )

    data = re.sub( r'\n|\r|\t|&nbsp;|<br>|<br/>|<br\s/>|<!--.*?-->', '', data )

    data = re.sub( r'\s+', ' ', data )

    data = re.sub( r'>\s<', '><', data )
    data = re.sub( r'>\s*([^<]+)\s*<', r'>\1<', data )

    data = re.sub( r'"\s"', '""', data )
    data = re.sub( r'="\s*([^"]+)\s*"', r'="\1"', data )

    data = re.sub( r"'\s'", "''", data )
    data = re.sub( r"='\s*([^']+)\s*'", r"='\1'", data )

    data = scrapertools.decodeHtmlentities( data )

    return data

## --------------------------------------------------------------------------------
## --------------------------------------------------------------------------------
