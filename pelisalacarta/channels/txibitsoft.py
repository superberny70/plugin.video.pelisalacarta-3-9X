# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para txibitsoft
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys


from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__category__ = "F,S"
__adult__ = "false"
__type__ = "generic"
__title__ = "Txibitsoft"
__channel__ = "txibitsoft"
__language__ = "ES"
__thumbnail__ = "http://s27.postimg.org/hx5ohryxf/tblogo.jpg"

host = "http://www.txibitsoft.com/"

DEBUG = config.get_setting("debug")



def isGeneric():
    return True



def mainlist(item):
    logger.info("pelisalacarta.txibitsoft mainlist")
    
    itemlist = []
    
    
    
    title="[COLOR white][B]Peliculas[/B][/COLOR]"
    itemlist.append( Item(channel=__channel__, title=title , action="peliculas", url="http://www.txibitsoft.com/torrents.php?procesar=1&categorias='Peliculas'&pagina=1", thumbnail="http://s27.postimg.org/nbbeles4j/tbpelithu.jpg", fanart="http://s14.postimg.org/743jqty35/tbpelifan.jpg"))
    title="[COLOR white][B]1080[/B][/COLOR]"
    itemlist.append( Item(channel=__channel__, title=title , action="peliculas" , url="http://www.txibitsoft.com/torrents.php?procesar=1&categorias='Cine%20Alta%20Definicion%20HD'&subcategoria=1080p&pagina=1", thumbnail="http://s4.postimg.org/t4i9vgjgd/tb1080th.jpg", fanart="http://s17.postimg.org/7z5pnf5tb/tb1080fan.jpg"))
    title="[COLOR white][B]Series[/B][/COLOR]"
    itemlist.append( Item(channel=__channel__, title=title , action="peliculas" , url="http://www.txibitsoft.com/torrents.php?procesar=1&categorias='Series'&pagina=1", thumbnail="http://s12.postimg.org/4ao5ekygd/tbseriethu.jpg", fanart="http://s12.postimg.org/oymstbjot/tbseriefan.jpg"))
    title="[COLOR white][B]Buscar...[/B][/COLOR]"
    itemlist.append( Item(channel=__channel__, title=title      , action="search", url="", fanart="http://s1.postimg.org/f5mnv2pcf/tbbusfan.jpg", thumbnail="http://s28.postimg.org/r2911z0rx/tbbusthu.png"))
    return itemlist

def search(item,texto):
    logger.info("pelisalacarta.txibitsoft search")
    texto = texto.replace(" ","+")
    
    item.url = "http://www.txibitsoft.com/torrents.php?procesar=1&texto=%s" % (texto)
    try:
        return buscador(item)
    # Se captura la excepciÛn, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def buscador(item):
    logger.info("pelisalacarta.txibitsoft buscador")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|&amp;","",data)
    item.url = re.sub(r"&amp;","",item.url)
    # corrige la falta de imagen
    data = re.sub(r'<img src="<!doctype html><html xmlns="','</div><img src="http://s30.postimg.org/8n4ej5j0x/noimage.jpg" texto ><p>',data)
    
    #<div class="torrent-container-2 clearfix"><img class="torrent-image" src="uploads/torrents/images/thumbnails2/4441_step--up--all--in----blurayrip.jpg" alt="Imagen de Presentaci&oacute;n" /><div class="torrent-info"><h4><a href ="/descargar_torrent_27233-id_step_up_all_in_microhd_1080p_ac3_5.1--castellano--ac3_5.1_ingles_subs.html">Step Up All In MicroHD 1080p AC3 5.1-Castellano-AC3 5.1 Ingles Subs</a> </h4><p>19-12-2014</p><p>Subido por: <strong>TorrentEstrenos</strong> en <a href="/ver_torrents_41-id_en_peliculas_microhd.html" title="Peliculas MICROHD">Peliculas MICROHD</a><br />Descargas <strong><a href="#" style="cursor:default">46</a></strong></p><a class="btn-download" href ="/descargar_torrent_27233-id_step_up_all_in_microhd_1080p_ac3_5.1--castellano--ac3_5.1_ingles_subs.html">Descargar</a></div></div>
    
    patron =  '<dl class=".*?dosColumnasDobles"><dt>'
    patron += '<a href="([^"]+)" '
    patron += 'title.*?:([^<]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += 'Idioma: <span class="categoria">([^<]+).*?'
    patron += 'Tama&ntilde;o: <span class="categoria">([^<]+)'
    
    
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches)==0 :
       itemlist.append( Item(channel=__channel__, title="[COLOR gold][B]No se ha encontrado nada en la busqueda...[/B][/COLOR]", thumbnail ="http://s6.postimg.org/vhczf38ep/oops.png", fanart ="http://pop-verse.com/wp-content/uploads/2014/11/000494946_prevstill.jpeg",folder=False) )


    
    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedlenguage, scrapedsize in matches:
        scrapedurl = "http://www.txibitsoft.com" + scrapedurl
        scrapedlenguage = scrapedlenguage.replace(scrapedlenguage,"[COLOR blue]"+scrapedlenguage+"[/COLOR]")
        scrapedsize = scrapedsize.replace(scrapedsize,"[COLOR gold]"+scrapedsize+"[/COLOR]")
        scrapedtitle = scrapedtitle.replace(scrapedtitle,"[COLOR white]"+scrapedtitle+"[/COLOR]")
        scrapedtitle = scrapedtitle + "-(Idioma:" + scrapedlenguage + ")" + "-(Tamaño: " + scrapedsize +")"
        
        
        itemlist.append( Item(channel=__channel__, title=scrapedtitle, url=scrapedurl, action="fanart", thumbnail=scrapedthumbnail, fanart ="http://s21.postimg.org/w0lgvyud3/tbfanartgeneral2.jpg",fulltitle=scrapedtitle, folder=True) )
    return itemlist

def peliculas(item):
    logger.info("pelisalacarta.txibitsoft peliculas")
    itemlist = []
    
    # Descar<div id="catalogheader">ga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|&amp;","",data)
    item.url = re.sub(r"&amp;","",item.url)
    # corrige la falta de imagen
    data = re.sub(r'<img src="<!doctype html><html xmlns="','</div><img src="http://s30.postimg.org/8n4ej5j0x/noimage.jpg" texto ><p>',data)
    
    #<div class="torrent-container-2 clearfix"><img class="torrent-image" src="uploads/torrents/images/thumbnails2/4441_step--up--all--in----blurayrip.jpg" alt="Imagen de Presentaci&oacute;n" /><div class="torrent-info"><h4><a href ="/descargar_torrent_27233-id_step_up_all_in_microhd_1080p_ac3_5.1--castellano--ac3_5.1_ingles_subs.html">Step Up All In MicroHD 1080p AC3 5.1-Castellano-AC3 5.1 Ingles Subs</a> </h4><p>19-12-2014</p><p>Subido por: <strong>TorrentEstrenos</strong> en <a href="/ver_torrents_41-id_en_peliculas_microhd.html" title="Peliculas MICROHD">Peliculas MICROHD</a><br />Descargas <strong><a href="#" style="cursor:default">46</a></strong></p><a class="btn-download" href ="/descargar_torrent_27233-id_step_up_all_in_microhd_1080p_ac3_5.1--castellano--ac3_5.1_ingles_subs.html">Descargar</a></div></div>
    
    patron =  '<dl class=".*?dosColumnasDobles"><dt>'
    patron += '<a href="([^"]+)" '
    patron += 'title.*?:([^<]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += 'Idioma: <span class="categoria">([^<]+).*?'
    patron += 'Tama&ntilde;o: <span class="categoria">([^<]+)'
    
    
    
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    
    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedlenguage, scrapedsize in matches:
        scrapedurl = "http://www.txibitsoft.com" + scrapedurl
        scrapedlenguage = scrapedlenguage.replace(scrapedlenguage,"[COLOR blue]"+scrapedlenguage+"[/COLOR]")
        scrapedsize = scrapedsize.replace(scrapedsize,"[COLOR gold]"+scrapedsize+"[/COLOR]")
        scrapedtitle = scrapedtitle.replace(scrapedtitle,"[COLOR white]"+scrapedtitle+"[/COLOR]")
        scrapedtitle = scrapedtitle + "-(Idioma:" + scrapedlenguage + ")" + "-(Tamaño: " + scrapedsize +")"
        
        
        itemlist.append( Item(channel=__channel__, title=scrapedtitle, url=scrapedurl, action="fanart", thumbnail=scrapedthumbnail, fanart= "http://s21.postimg.org/w0lgvyud3/tbfanartgeneral2.jpg", fulltitle=scrapedtitle, folder=True) )
    
    # Extrae el paginador
    ## Paginación
    
    if "pagina=" in item.url:
       current_page_number = int(scrapertools.get_match(item.url,'pagina=(\d+)'))
       item.url = re.sub(r"pagina=\d+","pagina={0}",item.url)
    else:
        current_page_number = 1

    

    next_page_number = current_page_number + 1
    next_page = item.url.format(next_page_number)
    
    
        
        

    title ="siguiente>>"
    title = title.replace(title,"[COLOR orange]"+title+"[/COLOR]")
    itemlist.append( Item(channel=__channel__, action="peliculas", title=title , url=next_page , thumbnail="http://s18.postimg.org/4l9172cqx/tbsiguiente.png", fanart="http://s21.postimg.org/w0lgvyud3/tbfanartgeneral2.jpg" , folder=True) )
    
    
    
    
    
    
    return itemlist

def fanart(item):
    logger.info("pelisalacarta.txibitsoft fanart")
    itemlist = []
    url = item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    if "peliculas" in item.url:
        title= scrapertools.get_match(data,'<form name="frm" id="frm" method="get" action="torrent.php">.*?alt="([^<]+)"')
        title= re.sub(r"3D|SBS|\[.*?\]|\(.*?\)|-|","",title)
        title= title.replace('Reparado','')
        title= title.replace(' ','%20')
        url="http://api.themoviedb.org/3/search/movie?api_key=57983e31fb435df4df77afb854740ea9&query=" + title + "&language=es&include_adult=false"
        data = scrapertools.cachePage(url)
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
        patron = '"page":1.*?"backdrop_path":"(.*?)".*?,"id"'
        matches = re.compile(patron,re.DOTALL).findall(data)
        if len(matches)==0:
            item.extra=item.thumbnail
            itemlist.append( Item(channel=__channel__, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra,folder=True) )
        else:
            for fan in matches:
                fanart="https://image.tmdb.org/t/p/original" + fan
                item.extra= fanart
                itemlist.append( Item(channel=__channel__, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra,folder=True) )
    elif "cine" in item.url:
          title= scrapertools.get_match(data,'alt="([^<]+) \[')
          title= re.sub(r"3D|SBS|\[.*?\]|\(.*?\)|-|","",title)
          title= title.replace(' ','%20')
          url="http://api.themoviedb.org/3/search/movie?api_key=57983e31fb435df4df77afb854740ea9&query=" + title + "&language=es&include_adult=false"
          data = scrapertools.cachePage(url)
          data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
          patron = '"page":1.*?"backdrop_path":"(.*?)".*?,"id"'
          matches = re.compile(patron,re.DOTALL).findall(data)
          if len(matches)==0:
              item.extra=item.thumbnail
              itemlist.append( Item(channel=__channel__, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra,folder=True) )
          else:
              for fan in matches:
                  fanart="https://image.tmdb.org/t/p/original" + fan
                  item.extra= fanart
                  itemlist.append( Item(channel=__channel__, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra,folder=True) )

    elif "series" in item.url:
          title= title= scrapertools.get_match(data,'</script><title>([^<]+)')
          title= re.sub(r"3D|[0-9]|\[.*?\]|\(.*?\)|SBS|-|Txibit|Soft|","",title)
          title= title.replace('Temporada','')
          title= title.replace('Fin','')
          title= title.replace('x','')
          title= title.replace(' ','%20')
          url="http://thetvdb.com/api/GetSeries.php?seriesname=" + title + "&language=es"
          data = scrapertools.cachePage(url)
          data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
          patron = '<Data><Series><seriesid>([^<]+)</seriesid>'
          matches = re.compile(patron,re.DOTALL).findall(data)
          if len(matches)==0:
             itemlist.append( Item(channel=__channel__, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.thumbnail,folder=True) )
          else:
               for id in matches:
                   id_serie = id
                   url ="http://thetvdb.com/api/1D62F2F90030C444/series/"+id_serie+"/banners.xml"
                   data = scrapertools.cachePage(url)
                   data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
                   patron = '<Banners><Banner>.*?<VignettePath>(.*?)</VignettePath>'
                   matches = re.compile(patron,re.DOTALL).findall(data)
                   if len(matches)==0:
                      itemlist.append( Item(channel=__channel__, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.thumbnail,folder=True) )
                   for fan in matches:
                       fanart="http://thetvdb.com/banners/" + fan
                       item.extra= fanart
                       itemlist.append( Item(channel=__channel__, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra,folder=True) )

    title ="Info"
    title = title.replace(title,"[COLOR skyblue][B]"+title+"[/B][/COLOR]")
    if len(item.extra)==0:
        fanart=item.thumbnail
    if len(item.extra)>0:
        fanart=item.extra
    itemlist.append( Item(channel=__channel__, action="info" , title=title , url=item.url, thumbnail=item.thumbnail, fanart=fanart, folder=False ))
    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.txibitsoft findvideos")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    
    patron = '<form name="frm" id="frm" method="get" action="torrent.php">.*?'
    patron += 'alt="([^<]+)".*?'
    patron += '<p class="limpiar centro"><a class="torrent" href="([^"]+)"'
    
    
    
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedtitle, scrapedurl in matches:
        
        scrapedurl = "http://www.txibitsoft.com" + scrapedurl
        
        
        title_tag="[COLOR orange]Ver--[/COLOR]"
        scrapedtitle = scrapedtitle.replace(scrapedtitle,"[COLOR magenta][B]"+scrapedtitle+"[/B][/COLOR]")
        scrapedtitle = title_tag + scrapedtitle
        itemlist.append( Item(channel=__channel__, title=scrapedtitle, url=scrapedurl, action="play", server="torrent", thumbnail=item.thumbnail, fanart=item.fanart,folder=False) )
      
    return itemlist
def info(item):
    logger.info("pelisalacarta.zentorrents info")
    
    url=item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    title= title= scrapertools.get_match(data,'</script><title>([^<]+)</title>')
    title = title.replace(title,"[COLOR aqua][B]"+title+"[/B][/COLOR]")
    scrapedplot = scrapertools.get_match(data,'<textarea.*?">(.*?)</textarea></li>')
    if "Sinopsis" in scrapedplot:
        scrapedplot= scrapertools.get_match(data,'<textarea.*Sinopsis(.*?)</textarea></li>')
    if "SINOPSIS" in scrapedplot:
        scrapedplot= scrapertools.get_match(data,'<textarea.*SINOPSIS(.*?)</textarea></li>')
    if "Sinópsis" in scrapedplot:
        scrapedplot= scrapertools.get_match(data,'<textarea.*Sinópsis(.*?)</textarea></li>')
    if "REPARTO" in scrapedplot:
        scrapedplot= scrapertools.get_match(data,'<textarea.*REPARTO(.*?)</textarea></li>')
    plot_title = "Sinopsis" + "[CR]"
    plot_title = plot_title.replace(plot_title,"[COLOR blue][B]"+plot_title+"[/B][/COLOR]")
    scrapedplot = plot_title + scrapedplot
    scrapedplot = scrapedplot.replace(scrapedplot,"[COLOR magenta]"+scrapedplot+"[/COLOR]")
    scrapedplot = scrapedplot.replace(":","")
    scrapedplot = scrapedplot.replace("&aacute;","a")
    scrapedplot = scrapedplot.replace("&iacute;","i")
    scrapedplot = scrapedplot.replace("&eacute;","e")
    scrapedplot = scrapedplot.replace("&oacute;","o")
    scrapedplot = scrapedplot.replace("&uacute;","u")
    scrapedplot = scrapedplot.replace("&ntilde;","ñ")
    scrapedplot = scrapedplot.replace("&Aacute;","A")
    scrapedplot = scrapedplot.replace("&Iacute;","I")
    scrapedplot = scrapedplot.replace("&Eacute;","E")
    scrapedplot = scrapedplot.replace("&Oacute;","O")
    scrapedplot = scrapedplot.replace("&Uacute;","U")
    scrapedplot = scrapedplot.replace("&Ntilde;","Ñ")
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
















