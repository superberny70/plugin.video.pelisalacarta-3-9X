# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para sinluces
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

__channel__ = "sinluces"
__category__ = "F,S,D"
__type__ = "generic"
__title__ = "Sinluces"
__language__ = "ES"

DEBUG = config.get_setting("debug")

host = "http://www.sinluces.com/"


def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.sinluces mainlist")
    itemlist = []
    title ="Estrenos"
    title = title.replace(title,"[COLOR skyblue]"+title+"[/COLOR]")
    itemlist.append( Item(channel=__channel__, title=title      , action="peliculas", url="http://www.sinluces.com/search/label/estreno", fanart="http://s17.postimg.org/rnup1a333/sinlestfan.jpg", thumbnail="http://s23.postimg.org/p1a2tyejv/sinlestthu.jpg"))
    title ="HD"
    title = title.replace(title,"[COLOR skyblue]"+title+"[/COLOR]")
    itemlist.append( Item(channel=__channel__, title=title      , action="peliculas", url="http://www.sinluces.com/search/label/HD", fanart="http://s11.postimg.org/6736sxxr7/sinlhdfan.jpg", thumbnail="http://s12.postimg.org/d5w5ojuql/sinlhdth.jpg"))
    title ="Buscar"
    title = title.replace(title,"[COLOR skyblue]"+title+"[/COLOR]")
    itemlist.append( Item(channel=__channel__, title=title      , action="search", url="", fanart="http://s22.postimg.org/3tz2v05ap/sinlbufan.jpg", thumbnail="http://s30.postimg.org/jhmn0u4jl/sinlbusthub.jpg"))
    

    
    
    
    return itemlist
def search(item,texto):
    logger.info("pelisalacarta.sinluces search")
    texto = texto.replace(" ","+")
    
    item.url = "http://www.sinluces.com/search?q=%s" % (texto)
    try:
        return peliculas(item)
    # Se captura la excepciÛn, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def peliculas(item,paginacion=True):
    logger.info("pelisalacarta.sinluces peliculas")
    itemlist = []
   
    
   
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    patron  = '<div class=\'post hentry\'.*?'
    patron += '<meta content=\'([^\']+)\'.*?'
    patron += '<meta content.*?<meta content.*?<meta content=\'([^\']+)\'.*?'
    patron += '<a class=\'imovie\' href=\'([^\']+)\''
    
    
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches)==0 :
        itemlist.append( Item(channel=__channel__, title="[COLOR gold][B]No hay resultados...[/B][/COLOR]", thumbnail ="http://s6.postimg.org/55zljwr4h/sinnoisethumb.png", fanart ="http://s6.postimg.org/avfu47xap/sinnoisefan.jpg",folder=False) )
    
    
    for scrapedthumbnail, scrapedtitle, scrapedurl in matches:
        scrapedtitle = scrapedtitle.replace(scrapedtitle,"[COLOR white]"+scrapedtitle+"[/COLOR]")
        
        
        itemlist.append( Item(channel=__channel__, action="fanart", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail ,  viewmode="movie", extra=scrapedtitle, fanart="http://s30.postimg.org/4gugdsygx/sinlucesfan.jpg") )
        
        #paginacio
    

    # Extrae el paginador
    ## Paginación
    patronvideos  = '<a class=\'blog-pager-older-link btn btn-primary\' href=\'([^\']+)\''
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        title ="siguiente>>"
        title = title.replace(title,"[COLOR skyblue]"+title+"[/COLOR]")
        itemlist.append( Item(channel=__channel__, action="peliculas", title=title , url=scrapedurl , thumbnail="http://s16.postimg.org/lvzzttkol/pelisvkflecha.png", fanart="http://s30.postimg.org/4gugdsygx/sinlucesfan.jpg" , folder=True) )

    return itemlist

def fanart(item):
    logger.info("pelisalacarta.peliculasdk fanart")
    itemlist = []
    url = item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    title= scrapertools.get_match(data,'<div class=\'post hentry\'.*?<meta content.*?<meta content.*?<meta content.*?<meta content=\'(.*?)\.*? \(')
    title= re.sub(r"3D|SBS|-|","",title)
    title= title.replace('Ver','')
    title= title.replace('Online','')
    title= title.replace('Gratis','')
    title= title.replace(' ','%20')
    url="http://api.themoviedb.org/3/search/movie?api_key=57983e31fb435df4df77afb854740ea9&query=" + title + "&language=es&include_adult=false"
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    patron = '"page":1.*?"backdrop_path":"(.*?)".*?,"id"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)==0:
        itemlist.append( Item(channel=__channel__, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.thumbnail , folder=True) )
    else:
        for fan in matches:
            fanart="https://image.tmdb.org/t/p/original" + fan
            item.extra= fanart
    itemlist.append( Item(channel=__channel__, title =item.title , url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra, folder=True) )
    #trailer

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    #logger.info("data="+data)
    
    
    #trailer
    patron = '<div class="tab-pane fade in active" id="trailer1">.*?'
    patron += '<p><iframe.*?src="(//[^"]+)"'
    
    
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    
    for scrapedurl in matches:
        title ="Trailer"
        title = title.replace(title,"[COLOR red]"+title+"[/COLOR]")
        
        
        itemlist.append( Item(channel=__channel__, action="trailer",  title=title  , url=scrapedurl , thumbnail=item.thumbnail , plot=item.plot , fulltitle = item.title , fanart=item.extra, folder=True) )
    title ="Info"
    title = title.replace(title,"[COLOR skyblue]"+title+"[/COLOR]")
    itemlist.append( Item(channel=__channel__, action="info" , title=title , url=item.url, thumbnail=item.thumbnail, fanart=item.extra, folder=False ))
    return itemlist






def findvideos(item):
    logger.info("pelisalacarta.sinluces findvideos")
    itemlist = []
    
    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
       #enlaces por idioma, calidad
    patron = '<em>opción \d+, ([^<]+)</em>.*?'
    # Datos que contienen los enlaces para sacarlos con servertools.findvideos
    patron+= '<div class="contenedor_tab">(.*?)<div style="clear:both;">'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for idioma, datosEnlaces in matches:
        
        listavideos = servertools.findvideos(datosEnlaces)
        
    
        for video in listavideos:
            videotitle = scrapertools.unescape(video[0])+"-"+idioma
            url = video[1]
            server = video[2]
            videotitle = videotitle.replace(videotitle,"[COLOR skyblue]"+videotitle+"[/COLOR]")
            title_first="[COLOR gold]Ver en--[/COLOR]"
            title= title_first + videotitle
            idioma = idioma.replace(idioma,"[COLOR white]"+idioma+"[/COLOR]")
            itemlist.append( Item(channel=__channel__, action="play", server=server, title=title , url=url , thumbnail=item.thumbnail , fulltitle = item.title , fanart = item.fanart, folder=False) )


    if not "opción 1" in data :
           # idioma, calidad
           patron = '<strong>.*?</strong>.*?">([^<]+)</span>].*?'

           # Datos que contienen los enlaces para sacarlos con servertools.findvideos
           patron += '<div class="contenedor_tab">(.*?)<div style="clear:both;">'
           matches = re.compile(patron,re.DOTALL).findall(data)
    
    for idioma, datosEnlaces in matches:
        
        listavideos = servertools.findvideos(datosEnlaces)
        
        for video in listavideos:
            videotitle = scrapertools.unescape(video[0])+"-"+idioma
            url = video[1]
            server = video[2]
            videotitle = videotitle.replace(videotitle,"[COLOR skyblue]"+videotitle+"[/COLOR]")
            title_first="[COLOR gold]Ver en--[/COLOR]"
            title= title_first + videotitle
            idioma = idioma.replace(idioma,"[COLOR white]"+idioma+"[/COLOR]")
            itemlist.append( Item(channel=__channel__, action="play", server=server, title=title  , url=url , thumbnail=item.thumbnail , fulltitle = item.title , fanart = item.fanart, folder=False) )


    # Datos que contienen los enlaces para sacarlos con servertools.findvideos
    patron = 'ovideo\d+"><p><iframe src=(.*?)<div class="alert alert-warning visible-phone">'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for  datosEnlaces in matches:
        
        listavideos = servertools.findvideos(datosEnlaces)
        
        
        for video in listavideos:
            videotitle = scrapertools.unescape(video[0])
            url = video[1]
            server = video[2]
            videotitle = videotitle.replace(videotitle,"[COLOR skyblue]"+videotitle+"[/COLOR]")
            title_first="[COLOR gold]Ver en--[/COLOR]"
            title= title_first + videotitle
            idioma = idioma.replace(idioma,"[COLOR white]"+idioma+"[/COLOR]")
            itemlist.append( Item(channel=__channel__, action="play", server=server, title=title , url=url , thumbnail=item.thumbnail , fulltitle = item.title , fanart = item.fanart, folder=False) )



    return itemlist


def trailer(item):
    logger.info("pelisalacarta.sinluces play url="+item.url)
    
    itemlist = servertools.find_video_items(data=item.url)
    
    for videoitem in itemlist:
        videoitem.title_first= "[COLOR gold]Ver en--[/COLOR]"
        videoitem.title_second = "Youtube"
        videoitem.title_second = videoitem.title_second.replace(videoitem.title_second,"[COLOR skyblue]"+videoitem.title_second+"[/COLOR]")
        videoitem.title= videoitem.title_first + videoitem.title_second
        videoitem.channel = __channel__
        videoitem.fanart = "http://s23.postimg.org/84vkeq863/movietrailers.jpg"
        videoitem.thumbnail = item.thumbnail
    
       
    

    return itemlist

def info(item):
    logger.info("pelisalacarta.sinluces trailer")
    url=item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    title= scrapertools.get_match(data,'<div class=\'post hentry\'.*?<meta content.*?<meta content.*?<meta content.*?<meta content=\'(.*?)\.*? \(')
    title = title.replace(title,"[COLOR aqua][B]"+title+"[/B][/COLOR]")
    title = title.replace("Ver","")
    scrapedplot = scrapertools.get_match(data,'<div class=\'fltl ipost-de\'><div><span><i class=\'icon icon-ok\'>(.*?)</div></div>')
    plotformat = re.compile('</i> (.*?)</span>',re.DOTALL).findall(scrapedplot)
    scrapedplot = scrapedplot.replace(scrapedplot,"[COLOR white]"+scrapedplot+"[/COLOR]")
    for plot in plotformat:
        scrapedplot = scrapedplot.replace(plot,"[COLOR skyblue][B]"+plot+"[/B][/COLOR]")
        scrapedplot = scrapedplot.replace("</span>","[CR]")
        scrapedplot = scrapedplot.replace("</i>","")
        scrapedplot = scrapedplot.replace("&#8220","")
        scrapedplot = scrapedplot.replace("<b>","")
        scrapedplot = scrapedplot.replace("</b>","")
        scrapedplot = scrapedplot.replace(" &#8203;&#8203;","")
        scrapedplot = scrapedplot.replace("&#8230","")
        scrapedplot = scrapedplot.replace("</div> </div> <div class='clear'>","")
        scrapedplot = scrapedplot.replace("</div><div><span><i class='icon icon-ok'>","[CR]")
    fanart="http://s11.postimg.org/qu66qpjz7/zentorrentsfanart.jpg"
    tbd = TextBox("DialogTextViewer.xml", os.getcwd(), "Default")
    tbd.ask(title, scrapedplot,fanart)
    del tbd
    return

try:
    import xbmc, xbmcgui
    class TextBox( xbmcgui.WindowXMLDialog ):
        """ Create a skinned textbox window """
        def __init__( self, *args, **kwargs):
            
            pass
        
        def onInit( self ):
            try:
                self.getControl( 5 ).setText( self.text )
                self.getControl( 1 ).setLabel( self.title )
            except: pass
        
        def onClick( self, controlId ):
            pass
        
        def onFocus( self, controlId ):
            pass
        
        def onAction( self, action ):
            self.close()
        
        def ask(self, title, text, image ):
            self.title = title
            self.text = text
            self.doModal()

except:
    pass



