# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para pordede
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__category__ = "F,S,D"
__adult__= "false"
__type__ = "generic"
__title__ = "Torrentestrenos"
__channel__ = "torrentestrenos"
__language__ = "ES"
__thumbnail__ = "http://s6.postimg.org/lq96iccb5/torrentestrenos.jpg"

host = "http://www.torrentestrenos.com"

DEBUG = config.get_setting("debug")



def isGeneric():
    return True

def login():
    
    url = "http://www.torrentestrenos.com/index.php"
    post = "login="+config.get_setting("torrentestrenosuser")+"&password="+config.get_setting("torrentestrenospassword")+"&Submit=ENTRAR"
    data = scrapertools.cache_page(url,post=post)



def mainlist(item):
    logger.info("pelisalacarta.torrentestrenos mainlist")
    
    itemlist = []
    
    if config.get_setting("torrentestrenosaccount")!="true":
        itemlist.append( Item( channel=__channel__ , title="Habilita tu cuenta en la configuraci—n..." , action="openconfig" , url="" , folder=False ) )
    else:
        login()
        
        itemlist.append( Item(channel=__channel__, title="Exterenos Cartelera" , action="peliculas"           , url="http://www.torrentestrenos.com/ver_torrents_1-id_en_estrenos_de_cartelera.html", thumbnail="http://s6.postimg.org/7fpx8gnrl/tecartelerath.jpg", fanart="http://s6.postimg.org/c84bxn7td/tecartelera.jpg"))
        itemlist.append( Item(channel=__channel__, title="PelisMicroHD" , action="peliculas"           , url="http://www.torrentestrenos.com/ver_torrents_41-id_en_peliculas_microhd.html", thumbnail="http://s6.postimg.org/copjk2vkh/temhdthu.jpg", fanart="http://s6.postimg.org/e8zgw7tch/temhdfan.jpg"))
        itemlist.append( Item(channel=__channel__, title="PelisBluray-rip" , action="peliculas"           , url="http://www.torrentestrenos.com/ver_torrents_33-id_en_peliculas_bluray--rip.html", thumbnail="http://s6.postimg.org/wptvn19ap/teripthub.jpg", fanart="http://s6.postimg.org/j3t5uhro1/teripfan6.jpg"))
        itemlist.append( Item(channel=__channel__, title="PelisDvd-Rip" , action="peliculas"           , url="http://www.torrentestrenos.com/ver_torrents_9-id_en_peliculas_dvd--rip.html", thumbnail="http://s6.postimg.org/gcaeasmkx/tethubdvdrip.jpg", fanart="http://s6.postimg.org/m6pak4h8x/tefandvdrip.jpg"))
        itemlist.append( Item(channel=__channel__, title="Series" , action="peliculas"           , url="http://www.torrentestrenos.com/ver_torrents_10-id_en_series.html", thumbnail="http://s6.postimg.org/gl7gtt5xt/teserthub2.jpg", fanart="http://s6.postimg.org/oa4tcfzv5/teserfan.jpg"))
        itemlist.append( Item(channel=__channel__, title="SeriesHD" , action="peliculas"           , url="http://www.torrentestrenos.com/ver_torrents_38-id_en_series_hd.html", thumbnail="http://s6.postimg.org/bk02sfyhd/tesehdth.jpg", fanart="http://s6.postimg.org/ralnszb69/teserhdfan.jpg" ))
        itemlist.append( Item(channel=__channel__, title="Documentales" , action="peliculas"           , url="http://www.torrentestrenos.com/ver_torrents_23-id_en_documentales.html", thumbnail="http://s6.postimg.org/5t5b0z13l/tedocuthub.jpg", fanart="http://s6.postimg.org/aqivm332p/tedocufan.jpg" ))
        itemlist.append( Item(channel=__channel__, action="search", title="Buscar...", url="", thumbnail="http://s6.postimg.org/42qvd88y9/tesearchfan.jpg", fanart="http://s6.postimg.org/x7p12vyvl/tesearchfan2.jpg"))
    
    
    return itemlist

def openconfig(item):
    if "xbmc" in config.get_platform() or "boxee" in config.get_platform():
        config.open_settings( )
    return []

def search(item,texto):
    logger.info("pelisalacarta.torrentestrenos search")
    texto = texto.replace(" ","+")
    
    item.url = "http://www.torrentestrenos.com/main.php?q=%s" % (texto)
    try:
        return buscador(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

    


    return itemlist

def buscador(item):
    logger.info("pelisalacarta.torrentstrenos buscador")
    itemlist = []

# Descarga la p‡gina
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    
    #<div class="torrent-container-2 clearfix"><img class="torrent-image" src="uploads/torrents/images/thumbnails2/4441_step--up--all--in----blurayrip.jpg" alt="Imagen de Presentaci&oacute;n" /><div class="torrent-info"><h4><a href ="/descargar_torrent_27233-id_step_up_all_in_microhd_1080p_ac3_5.1--castellano--ac3_5.1_ingles_subs.html">Step Up All In MicroHD 1080p AC3 5.1-Castellano-AC3 5.1 Ingles Subs</a> </h4><p>19-12-2014</p><p>Subido por: <strong>TorrentEstrenos</strong> en <a href="/ver_torrents_41-id_en_peliculas_microhd.html" title="Peliculas MICROHD">Peliculas MICROHD</a><br />Descargas <strong><a href="#" style="cursor:default">46</a></strong></p><a class="btn-download" href ="/descargar_torrent_27233-id_step_up_all_in_microhd_1080p_ac3_5.1--castellano--ac3_5.1_ingles_subs.html">Descargar</a></div></div>
    
    patron =  '<div class="torrent-container-2 clearfix">.*?'
    patron += 'src="([^"]+)".*? '
    patron += 'href ="([^"]+)".*?'
    patron += '>([^<]+)</a>.*?'
    patron += '<p>([^<]+)</p>'
    
    
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches)==0 :
        itemlist.append( Item(channel=__channel__, title="[COLOR gold][B]No se encontraron coincidencias...[/B][/COLOR]", thumbnail ="http://s6.postimg.org/w7nc1wh8x/torrnoisethumb.png", fanart ="http://s6.postimg.org/jez81z5n5/torrnoisefan.jpg",folder=False) )
    
    for scrapedthumbnail, scrapedurl, scrapedtitulo, scrapedcreatedate in matches:
        scrapedtitulo = scrapedtitulo + "(Torrent:" + scrapedcreatedate + ")"
        scrapedthumbnail = "http://www.torrentestrenos.com/" + scrapedthumbnail
        scrapedurl = "http://www.torrentestrenos.com" + scrapedurl
        
        
        itemlist.append( Item(channel=__channel__, title=scrapedtitulo, url=scrapedurl, action="findvideos", thumbnail=scrapedthumbnail, fanart="http://s6.postimg.org/44tc7dtg1/tefanartgeneral.jpg", fulltitle=scrapedtitulo, folder=True) )

    return itemlist

def peliculas(item):
    logger.info("pelisalacarta.torrentstrenos peliculas")
    itemlist = []
    
    # Descarga la p‡gina
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    
    #<div class="torrent-container-2 clearfix"><img class="torrent-image" src="uploads/torrents/images/thumbnails2/4441_step--up--all--in----blurayrip.jpg" alt="Imagen de Presentaci&oacute;n" /><div class="torrent-info"><h4><a href ="/descargar_torrent_27233-id_step_up_all_in_microhd_1080p_ac3_5.1--castellano--ac3_5.1_ingles_subs.html">Step Up All In MicroHD 1080p AC3 5.1-Castellano-AC3 5.1 Ingles Subs</a> </h4><p>19-12-2014</p><p>Subido por: <strong>TorrentEstrenos</strong> en <a href="/ver_torrents_41-id_en_peliculas_microhd.html" title="Peliculas MICROHD">Peliculas MICROHD</a><br />Descargas <strong><a href="#" style="cursor:default">46</a></strong></p><a class="btn-download" href ="/descargar_torrent_27233-id_step_up_all_in_microhd_1080p_ac3_5.1--castellano--ac3_5.1_ingles_subs.html">Descargar</a></div></div>
    
    patron =  '<div class="torrent-container-2 clearfix">.*?'
    patron += 'src="([^"]+)".*? '
    patron += 'href ="([^"]+)".*?'
    patron += '>([^<]+)</a>.*?'
    patron += '<p>([^<]+)</p>'
    
    
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    
    for scrapedthumbnail, scrapedurl, scrapedtitulo, scrapedcreatedate in matches:
        scrapedtitulo= scrapedtitulo.replace(scrapedtitulo,"[COLOR khaki]"+scrapedtitulo+"[/COLOR]")
        scrapedcreatedate= scrapedcreatedate.replace(scrapedcreatedate,"[COLOR white]"+scrapedcreatedate+"[/COLOR]")
        torrent_tag="[COLOR green]Torrent:[/COLOR]"
        scrapedtitulo = scrapedtitulo +  "(" +torrent_tag + scrapedcreatedate + ")"
        scrapedthumbnail = "http://www.torrentestrenos.com/" + scrapedthumbnail
        scrapedurl = "http://www.torrentestrenos.com" + scrapedurl
        
        if "peliculas" in item.url or "cartelera" in item.url:
            action = "fanart_pelis"
        else:
            action = "fanart_series"
        
        
        itemlist.append( Item(channel=__channel__, title=scrapedtitulo, url=scrapedurl, action=action, thumbnail=scrapedthumbnail, fulltitle=scrapedtitulo, fanart="http://s6.postimg.org/44tc7dtg1/tefanartgeneral.jpg", folder=True) )
    
   

## Extrae el paginador ##
# a class="paginator-items" href="/ver_torrents_41-id_en_peliculas_microhd_pag_1.html" title="Pagina de torrent 1">1</a>
    if "_pag_" in item.url:
       current_page_number = int(scrapertools.get_match(item.url,'_pag_(\d+)'))
       item.url = re.sub(r"_pag_\d+","_pag_%s",item.url)
    else:
        current_page_number = 1
        item.url = item.url.replace(".html","_pag_%s.html")

    next_page_number = current_page_number + 1
    next_page = item.url % (next_page_number)
    
    title= "[COLOR green]Pagina siguiente>>[/COLOR]"
    if next_page.replace("http://www.torrentestrenos.com","") in data:
        itemlist.append( Item(channel=__channel__, title=title, url=next_page, action="peliculas", thumbnail="http://s6.postimg.org/4hpbrb13l/texflecha2.png", fanart="http://s6.postimg.org/44tc7dtg1/tefanartgeneral.jpg", folder=True) )


    return itemlist

def fanart_pelis(item):
    logger.info("pelisalacarta.torrentestrenos fanart_pelis")
    itemlist = []
    url = item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|DTS|TS|DVD|\(.*?\)|HDTV|HDRip|Rip|RIP|\(.*?\)|Duologia|Espa.*?ol|2015|2014|&nbsp;","",data)
    
    title= scrapertools.get_match(data,'<h4>([^<]+)</h4>')
    title= re.sub(r"3D|SBS|-|","",title)
    title=title.replace('Espa–ol','Espanol')
    title=title.replace('MicroHD','')
    title=title.replace('1080p','')
    title=title.replace('720p','')
    title=title.replace('Bluray','')
    title=title.replace('BluRay','')
    title=title.replace('Line','')
    title=title.replace('LINE','')
    title=title.replace('CamRip','')
    title=title.replace('Camrip','')
    title=title.replace('Web','')
    title=title.replace('Screener','')
    title=title.replace('AC3','')
    title=title.replace('Ac3','')
    title=title.replace('5.1Castellano','')
    title=title.replace('5.1Thailandes','')
    title=title.replace('5.1','')
    title=title.replace('2.0','')
    title=title.replace('Castellano','')
    title=title.replace('Frances','')
    title=title.replace('Ingles','')
    title=title.replace('Latino','')
    title=title.replace('Part 1','')
    title=title.replace('Subs','')
    title= title.replace(' ','%20')
    url="http://api.themoviedb.org/3/search/movie?api_key=57983e31fb435df4df77afb854740ea9&query=" + title + "&language=es&include_adult=false"
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    patron = '"page":1.*?"backdrop_path":"(.*?)".*?,"id"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)==0:
        item.extra=item.thumbnail
        itemlist.append( Item(channel=__channel__, title =item.title , url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra, folder=True) )
    else:
        for fan in matches:
            fanart="https://image.tmdb.org/t/p/original" + fan
            item.extra= fanart
            itemlist.append( Item(channel=__channel__, title =item.title , url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra, folder=True) )
    title ="Info"
    title = title.replace(title,"[COLOR skyblue][B]"+title+"[/B][/COLOR]")
    itemlist.append( Item(channel=__channel__, action="info" , title=title , url=item.url, thumbnail=item.thumbnail, fanart=item.extra, folder=False ))
    
    return itemlist

def fanart_series(item):
    logger.info("pelisalacarta.torrentestrenos fanart_series")
    itemlist = []
    if "_s" in item.url:
        url = item.url
        data = scrapertools.cachePage(url)
        data = re.sub(r"\n|\r|\t|\s{2}|DTS|TS|\(.*?\)|DVD|HDTV|HDRip|Rip|RIP|\(.*?\)|Duologia|Espa.*?ol|2015|2014|&nbsp;","",data)
        title= scrapertools.get_match(data,'<h4>(.*?) S')
        title= re.sub(r"3D|SBS|-|","",title)
        title=title.replace('Espa–ol','Espanol')
        title=title.replace('MicroHD','')
        title=title.replace('1080p','')
        title=title.replace('720p','')
        title=title.replace('Bluray','')
        title=title.replace('BluRay','')
        title=title.replace('Line','')
        title=title.replace('LINE','')
        title=title.replace('CamRip','')
        title=title.replace('Camrip','')
        title=title.replace('Web','')
        title=title.replace('Screener','')
        title=title.replace('AC3','')
        title=title.replace('Ac3','')
        title=title.replace('5.1Castellano','')
        title=title.replace('5.1Thailandes','')
        title=title.replace('5.1','')
        title=title.replace('2.0','')
        title=title.replace('Castellano','')
        title=title.replace('Frances','')
        title=title.replace('Ingles','')
        title=title.replace('Latino','')
        title=title.replace('Part 1','')
        title=title.replace('Subs','')
        title= title.replace(' ','%20')
        url="http://thetvdb.com/api/GetSeries.php?seriesname=" + title + "&language=es"
        if "Erase%20Una%20Vez" in title:
            url ="http://thetvdb.com/api/GetSeries.php?seriesname=Erase%20una%20vez%20(2011)&language=es"
        data = scrapertools.cachePage(url)
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
        patron = '<Data><Series><seriesid>([^<]+)</seriesid>'
        matches = re.compile(patron,re.DOTALL).findall(data)
        if len(matches)==0:
           itemlist.append( Item(channel=__channel__, title =item.title , url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra, folder=True) )
        else:
           for id in matches:
               id_serie = id
               url ="http://thetvdb.com/api/1D62F2F90030C444/series/"+id_serie+"/banners.xml"
               if "Castle" in title:
                   url ="http://thetvdb.com/api/1D62F2F90030C444/series/83462/banners.xml"
               data = scrapertools.cachePage(url)
               data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
               patron = '<Banners><Banner>.*?<VignettePath>(.*?)</VignettePath>'
               matches = re.compile(patron,re.DOTALL).findall(data)
               if len(matches)==0:
                  itemlist.append( Item(channel=__channel__, title =item.title , url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra, folder=True) )
           for fan in matches:
               fanart="http://thetvdb.com/banners/" + fan
               item.extra= fanart
               itemlist.append( Item(channel=__channel__, title =item.title , url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra, folder=True) )
    else:
        url = item.url
        data = scrapertools.cachePage(url)
        data = re.sub(r"\n|\r|\t|\s{2}|DTS|TS|\(.*?\)|DVD|HDTV|HDRip|Rip|RIP|\(.*?\)|Episodio [0-9]|Espa.*?ol|2015|2014|&nbsp;","",data)
        title= scrapertools.get_match(data,'<h4>(.*?)</h4>')
        title= re.sub(r"3D|SBS|-|","",title)
        title=title.replace('Espa–ol','Espanol')
        title=title.replace('MicroHD','')
        title=title.replace('1080p','')
        title=title.replace('720p','')
        title=title.replace('Bluray','')
        title=title.replace('BluRay','')
        title=title.replace('Line','')
        title=title.replace('LINE','')
        title=title.replace('CamRip','')
        title=title.replace('Camrip','')
        title=title.replace('Web','')
        title=title.replace('Screener','')
        title=title.replace('AC3','')
        title=title.replace('Ac3','')
        title=title.replace('5.1Castellano','')
        title=title.replace('5.1Thailandes','')
        title=title.replace('5.1','')
        title=title.replace('2.0','')
        title=title.replace('Castellano','')
        title=title.replace('Frances','')
        title=title.replace('Ingles','')
        title=title.replace('Latino','')
        title=title.replace('Part 1','')
        title=title.replace('Subs','')
        title= title.replace(' ','%20')
        url="http://thetvdb.com/api/GetSeries.php?seriesname=" + title + "&language=es"
        if "Erase%20Una%20Vez" in title:
            url ="http://thetvdb.com/api/GetSeries.php?seriesname=Erase%20una%20vez%20(2011)&language=es"
        data = scrapertools.cachePage(url)
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
        patron = '<Data><Series><seriesid>([^<]+)</seriesid>'
        matches = re.compile(patron,re.DOTALL).findall(data)
        if len(matches)==0:
           itemlist.append( Item(channel=__channel__, title =item.title , url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra, folder=True) )
        else:
            for id in matches:
                id_serie = id
                url ="http://thetvdb.com/api/1D62F2F90030C444/series/"+id_serie+"/banners.xml"
                if "Castle" in title:
                    url ="http://thetvdb.com/api/1D62F2F90030C444/series/83462/banners.xml"
                data = scrapertools.cachePage(url)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
                patron = '<Banners><Banner>.*?<VignettePath>(.*?)</VignettePath>'
                matches = re.compile(patron,re.DOTALL).findall(data)
                if len(matches)==0:
                   itemlist.append( Item(channel=__channel__, title =item.title , url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra, folder=True) )
            for fan in matches:
                fanart="http://thetvdb.com/banners/" + fan
                item.extra= fanart
                itemlist.append( Item(channel=__channel__, title =item.title , url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra, folder=True) )
    title ="Info"
    title = title.replace(title,"[COLOR skyblue][B]"+title+"[/B][/COLOR]")
    itemlist.append( Item(channel=__channel__, action="info" , title=title , url=item.url, thumbnail=item.thumbnail, fanart=item.extra, folder=False ))

    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.torrentestrenos findvideos")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    

    patron = '<img class="torrent-image.*? '
    patron+= 'src="([^"]+)".*?'
    patron+= '<h4>([^<]+)</h4>.*?'
    patron+= '</p><p>([^<]+)</p><p>.*?'
    patron+= 'href =".*?l=([^"]+)"'
   
    
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedthumbnail, scrapedtitulo, scrapedplot, scrapedurl in matches:
        title_tag="[COLOR green]Ver--[/COLOR]"
        scrapedtitulo= scrapedtitulo.replace(scrapedtitulo,"[COLOR white]"+scrapedtitulo+"[/COLOR]")
        scrapedtitulo= title_tag + scrapedtitulo
        scrapedthumbnail = "http://www.torrentestrenos.com/" + scrapedthumbnail
        scrapedplot = scrapedplot.replace("&aacute;","a")
        scrapedplot = scrapedplot.replace("&iacute;","i")
        scrapedplot = scrapedplot.replace("&eacute;","e")
        scrapedplot = scrapedplot.replace("&oacute;","o")
        scrapedplot = scrapedplot.replace("&uacute;","u")
        scrapedplot = scrapedplot.replace("&ntilde;","–")
        scrapedplot = scrapedplot.replace("&Aacute;","A")
        scrapedplot = scrapedplot.replace("&Iacute;","I")
        scrapedplot = scrapedplot.replace("&Eacute;","E")
        scrapedplot = scrapedplot.replace("&Oacute;","O")
        scrapedplot = scrapedplot.replace("&Uacute;","U")
        scrapedplot = scrapedplot.replace("&Ntilde;","„")

        
        
        
        itemlist.append( Item(channel=__channel__, title =scrapedtitulo , url=scrapedurl, action="play", server="torrent", thumbnail=scrapedthumbnail, fanart=item.fanart, plot=scrapedplot, folder=False) )

    return itemlist

def info(item):
    logger.info("pelisalacarta.torrentestrenos info")
    
    url=item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    title= scrapertools.get_match(data,'<h4>(.*?)</h4>')
    title = title.replace(title,"[COLOR aqua][B]"+title+"[/B][/COLOR]")
    scrapedplot = scrapertools.get_match(data,'</p><p>([^<]+)</p><p>')
    scrapedplot = scrapedplot.replace(scrapedplot,"[COLOR white]"+scrapedplot+"[/COLOR]")
    plot_tag="[COLOR green][B]Sinopsis[/B][/COLOR]" + "[CR]"
    scrapedplot= plot_tag + scrapedplot
    scrapedplot = scrapedplot.replace("&aacute;","a")
    scrapedplot = scrapedplot.replace("&iacute;","i")
    scrapedplot = scrapedplot.replace("&eacute;","e")
    scrapedplot = scrapedplot.replace("&oacute;","o")
    scrapedplot = scrapedplot.replace("&uacute;","u")
    scrapedplot = scrapedplot.replace("&ntilde;","–")
    scrapedplot = scrapedplot.replace("&Aacute;","A")
    scrapedplot = scrapedplot.replace("&Iacute;","I")
    scrapedplot = scrapedplot.replace("&Eacute;","E")
    scrapedplot = scrapedplot.replace("&Oacute;","O")
    scrapedplot = scrapedplot.replace("&Uacute;","U")
    scrapedplot = scrapedplot.replace("&Ntilde;","„")
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



    