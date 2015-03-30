# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Buscador de Trailers en youtube
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import sys
import xbmc
import string


import gdata.youtube
import gdata.youtube.service
from servers import youtube

from core import scrapertools
from core import logger
from core import config
from core.item import Item
import os

DEBUG = config.get_setting("debug")

__type__ = "generic"
__title__ = "Trailers"
__channel__ = "trailertools"

logger.info("[trailertools.py] init")

def isGeneric():
    return True

def mainlist(item):
  itemlist=[]
  logger.info("[trailertools.py] mainlist")
  itemlist =[]
  itemlist.append( Item(channel="trailertools", action="search", title="Buscar Trailer...", thumbnail="http://pelisalacarta.mimediacenter.info/squares/search.png"))

  return itemlist
    

def search(item, texto):
  item.title=texto

  return buscartrailer(item)
        
        
def GetFrom_Trailersdepeliculas(titulovideo):
    logger.info("[trailertools.py] Modulo: GetFrom_Trailersdepeliculas(titulo = %s)"  % titulovideo)
    itemlist = []

    titulo = LimpiarTitulo(titulovideo)
    # ---------------------------------------
    #  Busca el video en la pagina de www.trailerdepeliculas.org,
    #  la busqueda en esta pagina es porque a veces tiene los
    #  trailers en ingles y que no existen en español
    # ----------------------------------------
    c = 0
    url1 ="http://www.trailersdepeliculas.org/"
    url  ="http://www.trailersdepeliculas.org/buscar.html"
    urldata=getpost(url,{'busqueda': titulo})
    #logger.info("post url  :  "+urldata)
    patronvideos = "<td><h2><a href='([^']+)'>(.*?)<.*?src='([^']+)'.*?"
    matches  = re.compile(patronvideos,re.DOTALL).findall(urldata)
    if len(matches)>0:
        for urlpage, title, tubmnail in matches:
            logger.info("Trailers encontrados en www.trailerdepeliculas.org :  "+title)
            
            if titulo in string.lower(LimpiarTitulo(title)):
                urlpage = urlparse.urljoin(url1,urlpage)
                thumbnail = urlparse.urljoin(url1,thumbnail)
                data     = scrapertools.cachePage(urlpage)
                logger.info("Trailer elegido :  "+title)
                
                patronvideos = 'movie" value="http://www.youtube.com([^"]+)"'
                matches2 = re.compile(patronvideos,re.DOTALL).findall(data)
                
                for link in matches2:
                    logger.info("link yt del Trailer encontrado :  "+link)
                    itemlist.append(Item(channel="trailertools", action="play", server="youtube", title=title, url=link, tumbnail=thumbail))

    logger.info('%s Trailers encontrados en Modulo: GetFrom_Trailersdepeliculas()' % str(len(itemlist)))
    return itemlist

def GetFromYoutubePlaylist(titulovideo):
    print "[trailertools.py] Modulo: GetFromYoutubePlaylist(titulo = %s)"  % titulovideo
    devuelve = []    
    #
    # ---------------------------------------
    #  Busca el video en las listas de youtube
    # ---------------------------------------
    c = 0
    #http://www.youtube.com/results?search_type=search_playlists&search_query=luna+nueva+trailer&uni=1
    for i in ["+trailer+espa%C3%B1ol","+trailer"]:
        listyoutubeurl  = "http://www.youtube.com/results?search_type=search_playlists&search_query="
        listyoutubeurl += titulovideo.replace(" ","+")+i+"&uni=1"
        listyoutubeurl = listyoutubeurl.replace(" ","")
        logger.info("Youtube url parametros de busqueda  :"+listyoutubeurl)
        data = scrapertools.cachePage(listyoutubeurl)

        thumbnail=""
        patronyoutube  = '<span><a class="hLink" title="(.*?)" href="(.*?)">.*?'
        #patronyoutube += '<span class="playlist-video-duration">(.*?)</span>'
        matches  = re.compile(patronyoutube,re.DOTALL).findall(data)
        if len(matches)>0:
            for match in matches:
                logger.info("Trailer Titulo encontrado :"+match[0])
                logger.info("Trailer Url    encontrado :"+match[1])
                logger.info("Trailer Titulo Recortado  :"+string.lower(LimpiarTitulo(match[0])))
                if (titulovideo) in (string.lower(LimpiarTitulo(match[0]))):
                    campo = match[1]
                    longitud = len(campo)
                    campo = campo[-11:]
                    logger.info("codigo del video :  "+campo)
                    scrapedurl = "http://www.youtube.com/watch?v="+campo
                    patron    = "(http\:\/\/i[^/]+/vi/"+campo+"/default.jpg)"
                    matches2  = re.compile(patron,re.DOTALL).findall(data)
                    if len(matches2)>0:
                        thumbnail = matches2[0]
                    c = c + 1
                    logger.info("Trailer elegido :  "+match[1])
                    devuelve.append( [scrapedurl, match[0] , thumbnail,""] )
                    #scrapedthumbnail = thumbnail
                    #scrapedtitle     = match[0]
                    #scrapedurl       = match[1]
                    if c == 6 :
                        break
            #logger.info(" Total de links encontrados U "+str(len(match)))
        if c == 6:break
    print '%s Trailers encontrados en Modulo: GetFromYoutubePlaylist()' % str(c)
    return devuelve

def buscartrailer(item):
    logger.info("[trailertools.py] - gettrailer: "+ item.title)
    titulo = re.sub('\([^\)]+\)','',item.title)
    sopa_palabras_invalidas = ("dvdrip" ,  "dvdscreener2" ,"tsscreener" , "latino" ,     # Esto es para peliculasyonkis o parecidos
                               "dvdrip1",  "dvdscreener"  ,"tsscreener1", "latino1",
                               "latino2",  "dvdscreener1" ,"screener"    ,
                               "mirror" ,  "megavideo"    ,"vose"        , "subtitulada"
                               )
                                   
    titulo = LimpiarTitulo(titulo)
    logger.info("El titulo es :%s" %titulo)
    trozeado = titulo.split()
    for trozo in trozeado:
        if trozo in sopa_palabras_invalidas:
            titulo = titulo.replace(trozo ,"")
    titulo = re.sub(' $','',titulo)
    titulo = titulo.replace("ver pelicula online vos","").strip()
    titulo = titulo.replace("ver pelicula online","").strip()
    titulo = titulo.replace("mirror 1","").strip()
    titulo = titulo.replace("parte 1","").strip()
    titulo = titulo.replace("part 1","").strip()
    titulo = titulo.replace("pt 1","").strip()        
    titulo = titulo.replace("peliculas online","").strip()
    
    itemlist = []
    if len(titulo)==0:
        titulo = "El_video_no_tiene_titulo"

    itemlist.extend(GetFrom_Trailersdepeliculas(titulo))    # Primero busca en www.trailerdepeliculas.org
    itemlist.extend(GetVideoFeed(titulo) )                  # luego busca con el API de youtube 
    itemlist.extend(GetFromYoutubePlaylist(titulo))       # si no encuentra, busca en las listas de la web de youtube
    
    return itemlist

def LimpiarTitulo(title):
        title = string.lower(title)
        #title = re.sub('\([^\)]+\)','',title)
        title = re.sub(' $','',title)
        title = title.replace("Ã‚Â", "")
        title = title.replace("ÃƒÂ©","e")
        title = title.replace("ÃƒÂ¡","a")
        title = title.replace("ÃƒÂ³","o")
        title = title.replace("ÃƒÂº","u")
        title = title.replace("ÃƒÂ­","i")
        title = title.replace("ÃƒÂ±","ñ")
        title = title.replace("Ã¢â‚¬Â", "")
        title = title.replace("Ã¢â‚¬Å“Ã‚Â", "")
        title = title.replace("Ã¢â‚¬Å“","")
        title = title.replace("Ã©","e")
        title = title.replace("Ã¡","a")
        title = title.replace("Ã³","o")
        title = title.replace("Ãº","u")
        title = title.replace("Ã­","i")
        title = title.replace("Ã±","ñ")
        title = title.replace("Ãƒâ€œ","O")
        title = title.replace("@","")
        title = title.replace("é","e")
        title = title.replace("á","a")
        title = title.replace("ó","o")
        title = title.replace("ú","u")
        title = title.replace("í","i")
        title = title.replace('ñ','n')
        title = title.replace('Á','a')
        title = title.replace('É','e')
        title = title.replace('Í','i')
        title = title.replace('Ó','o')
        title = title.replace('Ú','u')
        title = title.replace('Ñ','n')
        title = title.replace(":"," ")
        title = title.replace("&","")
        title = title.replace('#','')
        title = title.replace('-','')
        title = title.replace('?','')
        title = title.replace('¿','')
        title = title.replace(",","")
        title = title.replace("*","")
        title = title.replace("\\","")
        title = title.replace("/","")
        title = title.replace("'","")
        title = title.replace('"','')
        title = title.replace("<","")
        title = title.replace(">","")
        title = title.replace(".","")
        title = title.replace("_"," ")
        title = title.replace("\("," ")
        title = title.replace("\)"," ")
        title = title.replace('|','')
        title = title.replace('!','')
        title = title.replace('¡','')
        title = title.replace("  "," ")
        title = title.replace("\Z  ","")
        return(title)

def getpost(url,values): # Descarga la pagina con envio de un Form
    
    #url=url
    try:
        data = urllib.urlencode(values)          
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read() 
        return the_page 
    except Exception: 
        return "Err " 
####################################################################################################
# Buscador de Trailer : mediante el servicio de Apis de Google y Youtube                           #
####################################################################################################

# Show first 50 videos from YouTube that matches a search string
def youtube_search(texto):
    devuelve = []

    # Fetch video list from YouTube feed
    data = scrapertools.cache_page( "https://gdata.youtube.com/feeds/api/videos?q="+texto.replace(" ","+")+"&orderby=published&start-index=1&max-results=50&v=2&lr=es" )
    
    # Extract items from feed
    matches = re.compile("<entry(.*?)</entry>",re.DOTALL).findall(data)

    for entry in matches:
        logger.info("entry="+entry)
        # Not the better way to parse XML, but clean and easy
        title = scrapertools.get_match(entry,"<titl[^>]+>([^<]+)</title>")
        thumbnail = scrapertools.get_match(entry,"<media\:thumbnail url='([^']+)'")
        try:
            url = scrapertools.get_match(entry,"http\://www.youtube.com/watch\?v\=([0-9A-Za-z_-]{11})")
        except:
            url = scrapertools.get_match(entry,"https\://www.youtube.com/watch\?v\=([0-9A-Za-z_-]{11})")

        devuelve.append( [ title,thumbnail,url ] )

    return devuelve

def GetVideoFeed(titulo,solo="false"):
    logger.info("[trailertools.py] Modulo: GetVideoFeed(titulo = %s)"  % titulo)
    if solo=="true":
        esp   = ""
        noesp = ""
    else:
        esp   = " trailer espanol"
        noesp = " trailer"
    itemlist = []
    encontrados = set()
    c = 0
    entries = youtube_search(titulo+esp)
    
    for title,thumbnail,url in entries:
        logger.info( 'Video title: %s' % title)
        titulo2 = title
        url = url
        duracion = ""
        if titulo in (string.lower(LimpiarTitulo(titulo2))): 
            if url not in encontrados:
                itemlist.append(Item(channel="trailertools", action="play", server="youtube", title=titulo2, thumbnail=thumbnail, url=url))
                encontrados.add(url)
                c = c + 1
            if c > 10:
                return (itemlist)

    if c < 6:
        entries = youtube_search(titulo+esp)
        for title,thumbnail,url in entries:
            logger.info( 'Video title: %s' % title)
            titulo2 = title
            url = url
            duracion = ""
            if titulo in (string.lower(LimpiarTitulo(titulo2))): 
                if url not in encontrados:
                    itemlist.append(Item(channel="trailertools", action="play", server="youtube", title=titulo2, thumbnail=thumbnail, url=url))
                    encontrados.add(url)
                    c = c + 1
                if c > 10:
                    return (itemlist)
    if c < 6:
        entries = youtube_search(titulo)
        for title,thumbnail,url in entries:
            logger.info( 'Video title: %s' % title)
            titulo2 = title
            url = url
            duracion = ""
            if titulo in (string.lower(LimpiarTitulo(titulo2))): 
                if url not in encontrados:
                    itemlist.append(Item(channel="trailertools", action="play", server="youtube", title=titulo2, thumbnail=thumbnail, url=url))
                    encontrados.add(url)
                    c = c + 1
                if c > 10:
                    return (itemlist)

    logger.info( '%s Trailers encontrados en Modulo: GetVideoFeed()' % str(c))
    return itemlist
    
