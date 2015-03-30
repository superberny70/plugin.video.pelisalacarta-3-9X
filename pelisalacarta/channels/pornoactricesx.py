# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para pornoactricesx
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os
import sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "pornoactricesx"
__category__ = "F"
__type__ = "generic"
__title__ = "pornoactricesx"
__language__ = "ES"
__adult__ = "true"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[pornoactricesx.py] mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, action="videos"          , title="Útimos videos"     , url="http://www.pornoactricesx.com/"))
    itemlist.append( Item(channel=__channel__, action="listactrices"    , title="Listado Actrices"  , url="http://www.pornoactricesx.com/todas-las-actrices"))
    itemlist.append( Item(channel=__channel__, action="search"          , title="Buscar"            , url="http://www.pornoactricesx.com/search/content/"))

    return itemlist

def search(item,texto):
    logger.info("[pornoactricesx.py] search")
    texto = texto.replace( " ", "+" )
    item.url = item.url + texto
    
    return videos(item)

def videos(item):
    logger.info("[pornoactricesx.py] videos")
    itemlist = []
    mas= True
    data = ""
    url= item.url
    while len(itemlist) < 25 and mas== True:
      data = scrapertools.downloadpage(url)
      data = scrapertools.unescape(data)
      patron = '<div class="field field-name-title field-type-ds field-label-hidden view-mode-teaser"><div class="field-items"><div class="field-item even"><h1><a href="([^"]+)">([^"]+)</a></h1></div></div></div>  </div>'
      patron +='[^<]{4}<div class="group-left">[^<]{5}<div class="field field-name-field-imagen-del-video field-type-image field-label-hidden view-mode-teaser"><div class="field-items">'
      patron +='<figure class="clearfix field-item even"><a href="([^"]+)"><img class="image-style-medium" src="([^"]+)"'
      matches = re.compile(patron,re.DOTALL).findall(data)
      for url,title,url2,thumbnail in matches:

          scrapedtitle = title.replace(" Vídeo porno completo.","")
          scrapedurl = urlparse.urljoin( "http://www.pornoactricesx.com" , url )
          scrapedthumbnail = thumbnail
          scrapedplot = ""
          # Depuracion
          if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")            
          itemlist.append( Item(channel=__channel__, action='play', title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot) )
          
      #Patron 2 para busquedas
      patron='<div class="field field-name-title field-type-ds field-label-hidden view-mode-search_result">'
      patron +='<div class="field-items"><div class="field-item even"><h1><a href="([^"]+)">([^"]+)</a></h1></div></div></div>  </div>'
      patron +='[^<]{4}<div class="group-left">[^<]{5}<div class="field field-name-field-imagen-del-video field-type-image field-label-hidden view-mode-search_result"><div class="field-items"><figure class="clearfix field-item even"><a href="([^"]+)"><img class="image-style-medium" src="([^"]+)" width='
      matches = re.compile(patron,re.DOTALL).findall(data)
      for url,title, url2, thumbnail in matches:

          scrapedtitle = title.replace(" Vídeo porno completo.","")
          scrapedurl = urlparse.urljoin( "http://www.pornoactricesx.com" , url )
          scrapedthumbnail = thumbnail
          scrapedplot = ""
          # Depuracion
          if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")            
          itemlist.append( Item(channel=__channel__, action='play', title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot) )
      patron = '<a title="Ir a la página siguiente" href="([^<]+)">siguiente ›</a>'
      matches = re.compile(patron,re.DOTALL).findall(data)
      if len(matches) >0:
        url="http://www.pornoactricesx.com"+matches[0]
        mas=True
      else:
        mas=False
        
    #Paginador
    patron = '<a title="Ir a la página siguiente" href="([^<]+)">siguiente ›</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)  
    if len(matches) >0:
      scrapedurl = "http://www.pornoactricesx.com"+matches[0]
      itemlist.append( Item(channel=__channel__, action="videos", title="Página Siguiente" , url=scrapedurl , thumbnail="" , folder=True) )
      
    return itemlist

def play(item):
    logger.info("[pornoactricesx.py] findvideos")
    itemlist=[]
    # Descarga la página
    data = scrapertools.downloadpage(item.url)
    data = scrapertools.unescape(data)
    logger.info(data)
    from servers import servertools
    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        videoitem.thumbnail = item.thumbnail
        videoitem.channel=__channel__
        videoitem.action="play"
        videoitem.folder=False
        videoitem.title = item.title

    return itemlist

def listactrices(item):
    logger.info("[pornoactricesx.py] listcategorias")
    itemlist = []
    data = scrapertools.downloadpage(item.url)
    data = scrapertools.unescape(data)
    patron = '<span class="field-content"><a href="([^"]+)">([^"]+)</a></span>  </span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url, actriz in matches:
      url="http://www.pornoactricesx.com"+url
      itemlist.append( Item(channel=__channel__, action="videos" , title=actriz, url=url))
    
    #Paginador
    patron = '<a title="Ir a la página siguiente" href="([^"]+)">siguiente ›'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches) >0:
      url="http://www.pornoactricesx.com"+matches[0]
      itemlist.append( Item(channel=__channel__, action="listactrices" , title="Página Siguiente", url=url))

    return itemlist
    
# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True

    # mainlist
    mainlist_itemlist = mainlist(Item())
    video_itemlist = videos(mainlist_itemlist[0])
    
    # Si algún video es reproducible, el canal funciona
    for video_item in video_itemlist:
        play_itemlist = play(video_item)

        if len(play_itemlist)>0:
            return True

    return False