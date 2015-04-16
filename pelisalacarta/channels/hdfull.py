# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para hdfull
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__adult__ = "false"
__channel__ = "hdfull"
__category__ = "F,S,D"
__type__ = "generic"
__title__ = "HDFull"
__language__ = "ES"
__thumbnail__ = "http://s6.postimg.org/eqgu6ues1/hdful.jpg"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.hdfull mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="menupeliculas" , title="Películas" , url="http://hdfull.tv/", folder=True))
    itemlist.append( Item(channel=__channel__, action="menuseries"    , title="Series" , url="http://hdfull.tv/", folder=True))
    itemlist.append( Item(channel=__channel__, action="listado_series"    , title="Listado de todas las series" , url="http://hdfull.tv/series/list", folder=True))
    itemlist.append( Item(channel=__channel__, action="search"        , title="Buscar..."))
    return itemlist

def menupeliculas(item):
    logger.info("pelisalacarta.channels.hdfull menupeliculas")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="fichas" , title="Últimas películas" , url="http://hdfull.tv/peliculas", folder=True))
    itemlist.append( Item(channel=__channel__, action="fichas" , title="Últimas películas de estreno" , url="http://hdfull.tv/peliculas-estreno", folder=True))
    itemlist.append( Item(channel=__channel__, action="fichas" , title="Últimas películas actualizadas" , url="http://hdfull.tv/peliculas-actualizadas", folder=True))
    itemlist.append( Item(channel=__channel__, action="generos" , title="Últimas películas por género" , url="http://hdfull.tv/", folder=True))
    return itemlist

def menuseries(item):
    logger.info("pelisalacarta.channels.hdfull menuseries")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="novedades_episodios" , title="Últimos episodios emitidos" , url="http://hdfull.tv/ultimos-episodios", folder=True))
    itemlist.append( Item(channel=__channel__, action="novedades_episodios" , title="Últimos episodios estreno" , url="http://hdfull.tv/episodios-estreno", folder=True))
    itemlist.append( Item(channel=__channel__, action="novedades_episodios" , title="Últimos episodios actualizados" , url="http://hdfull.tv/episodios-actualizados", folder=True))
    itemlist.append( Item(channel=__channel__, action="fichas"    , title="Últimas series" , url="http://hdfull.tv/series", folder=True))
    itemlist.append( Item(channel=__channel__, action="fichas"    , title="Series más valoradas" , url="http://hdfull.tv/series/imdb_rating", folder=True))
    itemlist.append( Item(channel=__channel__, action="generos_series" , title="Últimas series por género" , url="http://hdfull.tv/", folder=True))
    return itemlist

def search(item,texto):
    logger.info("pelisalacarta.channels.hdfull search")

    data = scrapertools.cachePage("http://hdfull.tv/")

    texto = texto.replace('+','%20')

    sid = scrapertools.get_match(data, '.__csrf_magic. value="(sid:[^"]+)"')
    item.extra = urllib.urlencode({'__csrf_magic':sid})+'&menu=search&query='+texto
    item.url = "http://hdfull.tv/buscar"

    try:
        return fichas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def listado_series(item):
    logger.info("pelisalacarta.channels.hdfull listado_series")

    itemlist = []

    #<div class="list-item"><a href="http://hdfull.tv/serie/009-1" title="009-1">009-1</a></div>
    data = scrapertools.cachePage(item.url)
    ## Agrupa los datos
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>','',data)
    data = re.sub(r'\s+',' ',data)
    data = re.sub(r'<!--.*?-->','',data)

    patron = '<div class="list-item"><a href="([^"]+)"[^>]+>([^<]+)</a></div>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle in matches:
        itemlist.append( Item(channel=__channel__, action="episodios", title=scrapedtitle, url=scrapedurl, show=scrapedtitle))

    return itemlist

def fichas(item):
    logger.info("pelisalacarta.channels.hdfull series")
    itemlist = []

    if item.title == "Buscar...":
        data = scrapertools.cachePage(item.url,post=item.extra)
        s_p = scrapertools.get_match(data, '<h3 class="section-title">(.*?)<div id="footer-wrapper">').split('<h3 class="section-title">')

        if len(s_p) == 1 and 'Lo sentimos</h3>' in s_p[0]:
            return [ Item(channel=__channel__, title="[COLOR gold][B]HDFull:[/B][/COLOR] [COLOR blue]"+texto.replace('%20',' ')+"[/COLOR] sin resultados") ]
        data = s_p[0]+s_p[1]
    else:
        data = scrapertools.cachePage(item.url)

    ## Agrupa los datos
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>','',data)
    data = re.sub(r'\s+',' ',data)
    data = re.sub(r'<!--.*?-->','',data)

    patron  = '<div class="item"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img.*?src="([^"]+)".*?'
    patron += '<div class="rating-pod"[^<]+'
    patron += '<div class="left"(.*?)</div>.*?'
    patron += '<h5 class="left"[^<]+'
    patron += '<div class="title-overflow"></div[^<]+'
    patron += '<a class="[^"]+" href="[^"]+" title="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,bloqueidiomas,scrapedtitle in matches:

        thumbnail = scrapertools.find_single_match(scrapedthumbnail,"timthumb.php.src=([^\&]+)&")
        title = scrapedtitle.strip()
        show = title
        if bloqueidiomas != ">":
            textoidiomas = extrae_idiomas(bloqueidiomas)
            title = title+" ("+textoidiomas[:-1]+")"
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""

        action = {}
        action['nextPage'] = scrapertools.get_match(url+"/",".tv/([^/]+)/")

        if action['nextPage'] == "serie":
            action['item'] = "episodios"
        else:
            action['item'] = "findvideos"
        if item.title == "Buscar...":
            title = title+"  - [COLOR blue]"+action['nextPage'].capitalize()+"[/COLOR]"
        extra = action['nextPage']

        itemlist.append( Item(channel=__channel__, action=action['item'], title=title , fulltitle = title, url=url , thumbnail=thumbnail , plot=plot , folder=True, show=show, extra=extra, viewmode="movie", context="0"))

    next_page_url = scrapertools.find_single_match(data,'<a href="([^"]+)">.raquo;</a> ')
    if next_page_url!="":
        itemlist.append( Item(channel=__channel__, action=action['nextPage']+"s", title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page_url) , folder=True) )

    return itemlist

def extrae_idiomas(bloqueidiomas):
    logger.info("idiomas="+bloqueidiomas)
    patronidiomas = '([a-z0-9]+).png"'
    idiomas = re.compile(patronidiomas,re.DOTALL).findall(bloqueidiomas)
    textoidiomas = ""
    for idioma in idiomas:
        textoidiomas = textoidiomas + idioma + "/"

    return textoidiomas

def episodios(item):
    logger.info("pelisalacarta.channels.hdfull episodios")
    itemlist = []

    temporadas_items = temporadas(item)

    for temporada_item in temporadas_items:
        episodios_temporada_items = episodios_temporada(temporada_item)

        for episodio in episodios_temporada_items:
            itemlist.append(episodio)

    if (config.get_platform().startswith("xbmc") or config.get_platform().startswith("boxee")) and len(itemlist)>0:
        itemlist.append( Item(channel=item.channel, title="Añadir esta serie a la biblioteca de XBMC", url=item.url, action="add_serie_to_library", extra="episodios", show=item.show))
        itemlist.append( Item(channel=item.channel, title="Descargar todos los episodios de la serie", url=item.url, action="download_all_episodes", extra="episodios", show=item.show))

    return itemlist

def temporadas(item):
    logger.info("pelisalacarta.channels.hdfull temporadas")
    itemlist = []

    '''
    <div class="flickr item left home-thumb-item">
    <a href='http://hdfull.tv/serie/stargate-sg-1/temporada-5' rel="bookmark">
    <img class="tooltip" original-title="Temporada 5" alt="Temporada 5" src="http://hdfull.tv/templates/hdfull/timthumb.php?src=http://hdfull.tv/thumbs/season_527af04264f6516e9a324dd1d3ded7f8.jpg&amp;w=130&amp;h=190&amp;zc=1" />
    <h5>Temporada 5</h5>
    </a>
    </div>
    '''

    patron  = '<div class="flickr[^<]+'
    patron += "<a href='([^']+)'[^<]+"
    patron += '<img class="tooltip" original-title="([^"]+)" alt="[^"]+" src="([^"]+)"'

    data = scrapertools.cachePage(item.url)
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:

        thumbnail = scrapertools.find_single_match(scrapedthumbnail,"timthumb.php.src=([^\&]+)&")
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="episodios_temporada", title=title , fulltitle = title, url=url , thumbnail=thumbnail , plot=plot , show=item.show, folder=True))

    return itemlist

def episodios_temporada(item):
    logger.info("pelisalacarta.channels.hdfull episodios_temporada")
    itemlist = []

    '''
    <div class="item">
    <a href="http://hdfull.tv/serie/forever-2014/temporada-1/episodio-11" class="spec-border-ie" title="">
    <img class="img-preview spec-border show-thumbnail-wide"  src="http://hdfull.tv/templates/hdfull/timthumb.php?src=http://hdfull.tv/thumbs/ethumb_tt3487382_1_11.jpg&amp;w=220&amp;h=124&amp;zc=1" alt="Temp 1. Ep 11" title="Temp 1. Ep 11" />
    </a>
    </div>
    <div class="rating-pod">
    <div class="left">
    <img src="http://hdfull.tv/templates/hdfull/images/eng.png" style="margin-right: 1px;"/>
    <img src="http://hdfull.tv/templates/hdfull/images/engsub.png" style="margin-right: 1px;"/>
    <img src="http://hdfull.tv/templates/hdfull/images/spa.png" style="margin-right: 1px;"/>
    <img src="http://hdfull.tv/templates/hdfull/images/sub.png" style="margin-right: 1px;"/>
    </div>
    <div class="right">
    <div class="rating">1<b class="sep">x</b>11</div>
    </div>
    </div>
    <h5 class="left">
    <div class="title-overflow"></div>
    <a class="link" href="http://hdfull.tv/serie/forever-2014/temporada-1/episodio-11" title="Skinny Dipper">Skinny Dipper</a>
    '''

    patron  = '<div class="item"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img class="[^"]+"\s+src="([^"]+)"[^<]+'
    patron += '</a[^<]+'
    patron += '</div[^<]+'
    patron += '<div class="rating-pod"[^<]+'
    patron += '<div class="left"(.*?)</div[^<]+'
    patron += '<div class="right"[^<]+'
    patron += '<div class="rating">(.*?)</div[^<]+'
    patron += '</div[^<]+'
    patron += '</div[^<]+'
    patron += '<h5 class="left"[^<]+'
    patron += '<div class="title-overflow"></div[^<]+'
    patron += '<a[^>]+>([^<]+)</a>'

    data = scrapertools.cachePage(item.url)
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,bloqueidiomas,episodenumber,episodetitle in matches:

        thumbnail = scrapertools.find_single_match(scrapedthumbnail,"timthumb.php.src=([^\&]+)&")
        title = scrapertools.htmlclean(episodenumber).strip()+" "+episodetitle.strip()
        textoidiomas = extrae_idiomas(bloqueidiomas)
        title = title.strip()+" ("+textoidiomas[:-1]+")"
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=title , fulltitle = title, url=url , thumbnail=thumbnail , plot=plot , show=item.show, folder=True))

    return itemlist

def novedades_episodios(item):
    logger.info("pelisalacarta.channels.hdfull novedades_episodios")
    itemlist = []

    '''
    <div class="item" style="text-align:center">
    <a href="http://hdfull.tv/pelicula/magic-in-the-moonlight" class="spec-border-ie" title="">
    <img class="img-preview spec-border"  src="http://hdfull.tv/templates/hdfull/timthumb.php?src=http://hdfull.tv/thumbs/movie_8378be0c7f5ef678fa082b5f8e04eac4.jpg&amp;w=130&amp;h=190&amp;zc=1" alt="Magia a la luz de la luna" title="Magia a la luz de la luna" style="width:130px;height:190px;background-color: #717171;"/>
    </a>
    </div>

    <div class="rating-pod">
    <div class="left">
    <img src="http://hdfull.tv/templates/hdfull/images/spa.png" style="margin-right: 1px;"/>
    <img src="http://hdfull.tv/templates/hdfull/images/lat.png" style="margin-right: 1px;"/>
    </div>
    '''
    '''
    <div class="item" style="text-align:center">
    <a href="http://hdfull.tv/serie/the-legend-of-korra/temporada-4/episodio-11" class="spec-border-ie" title="">
    <img class="img-preview spec-border show-thumbnail-wide"  src="http://hdfull.tv/templates/hdfull/timthumb.php?src=http://hdfull.tv/thumbs/ethumb_tt1695360_4_11.jpg&amp;w=220&amp;h=124&amp;zc=1" alt="" title="" />
    </a>
    </div>

    <div class="rating-pod">
    <div class="left">
    <img src="http://hdfull.tv/templates/hdfull/images/eng.png" style="margin-right: 1px;" class="flag-lang-eng"/>
    <img src="http://hdfull.tv/templates/hdfull/images/sub.png" style="margin-right: 1px;" class="flag-lang-espsub"/>
    </div>

    <div class="right">
    <div class="rating">4<b class="sep">x</b>11</div>
    </div>
    </div>

    <h5 class="left">
    <div class="title-overflow"></div>
    <a class="link" href="http://hdfull.tv/serie/the-legend-of-korra/temporada-4/episodio-11" title="The Legend of Korra">
    The Legend of Korra
    </a>
    </h5>
    <p class="left">Kuvira's Gambit</p>
    <div id="seen22893"></div>                      
    <div class="clear"></div>
    '''

    patron  = '<div class="item"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img.*?src="([^"]+)"[^<]+'
    patron += '</a[^<]+'
    patron += '</div[^<]+'
    patron += '<div class="rating-pod"[^<]+'
    patron += '<div class="left"(.*?)</div[^<]+'
    patron += '<div class="right"[^<]+'
    patron += '<div class="rating">(.*?)</div[^<]+'
    patron += '</div[^<]+'
    patron += '</div[^<]+'
    patron += '<h5 class="left"[^<]+'
    patron += '<div class="title-overflow"></div[^<]+'
    patron += '<a[^>]+>([^<]+)</a[^<]+'
    patron += '</h5[^<]+'
    patron += '<p class="left">([^<]+)</p>'

    data = scrapertools.cachePage(item.url)
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,bloqueidiomas,episode_number,serie_title,episode_title in matches:

        thumbnail = scrapertools.find_single_match(scrapedthumbnail,"timthumb.php.src=([^\&]+)&")
        logger.info("idiomas="+bloqueidiomas)
        patronidiomas = '([a-z0-9]+).png"'
        idiomas = re.compile(patronidiomas,re.DOTALL).findall(bloqueidiomas)
        textoidiomas = ""
        for idioma in idiomas:
            textoidiomas = textoidiomas + idioma + "/"

        show = serie_title.strip()
        title = serie_title.strip()+" "+scrapertools.htmlclean(episode_number.strip())+" "+episode_title.strip()+" ("+textoidiomas[:-1]+")"
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=title , fulltitle = title, url=url , thumbnail=thumbnail , plot=plot , show=show, folder=True))

    next_page_url = scrapertools.find_single_match(data,'<a href="([^"]+)">.raquo;</a> ')
    if next_page_url!="":
        itemlist.append( Item(channel=__channel__, action="findvideos", title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page_url) , folder=True) )

    return itemlist

def generos(item):
    logger.info("pelisalacarta.channels.hdfull generos")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    data = scrapertools.find_single_match(data,'<li class="dropdown"><a href="http://hdfull.tv/peliculas"(.*?)</ul>')

    patron  = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = ""
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="fichas", title=title , url=url , folder=True) )

    return itemlist

def generos_series(item):
    logger.info("pelisalacarta.channels.hdfull generos_series")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    data = scrapertools.find_single_match(data,'<li class="dropdown"><a href="http://hdfull.tv/series"(.*?)</ul>')

    patron  = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = ""
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="fichas", title=title , url=url , folder=True) )

    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.channels.hdfull findvideos")
    itemlist=[]

    '''
    <div class="embed-selector" style="background-image: url('http://hdfull.tv/templates/hdfull/images/lat.png')" onclick="changeEmbed(29124,countdown);">

    <h5 class="left">
    <span>
    <b class="key"> Idioma: </b> Audio Latino
    </span>
    <span>
    <b class="key">Servidor:</b><b class="provider" style="background-image: url(http://www.google.com/s2/favicons?domain=powvideo.net)">Powvideo</b>
    </span>
    <span>
    <b class="key">Calidad: </b> HD720
    </span>
    </h5>

    <ul class="filter action-buttons">
    <li class="current right" style="float:right">
    <a href="javascript:void(0);" onclick="reportMovie(29124)" class="danger" title="Reportar"><i class="icon-warning-sign icon-white"></i>&nbsp;</a>
    &nbsp;<a href="http://powvideo.net/q87l85llcifz" target="_blank"><i class="icon-share-alt icon-white"></i> Enlace externo</a>
    </li>
    </ul>
    </div>
    '''
    # Descarga la pagina
    data = scrapertools.cachePage(item.url)

    patron  = '<div class="embed-selector"[^<]+'
    patron += '<h5 class="left"[^<]+'
    patron += '<span[^<]+<b class="key">\s*Idioma.\s*</b>([^<]+)</span[^<]+'
    patron += '<span[^<]+<b class="key">\s*Servidor.\s*</b><b[^>]+>([^<]+)</b[^<]+</span[^<]+'
    patron += '<span[^<]+<b class="key">\s*Calidad.\s*</b>([^<]+)</span[^<]+</h5.*?'
    patron += '<a href="http([^"]+)".*?'
    patron += '</i>([^<]+)</a>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for idioma,servername,calidad,url,opcion in matches:
        opcion = opcion.strip()
        if opcion != "Descargar":
            opcion = "Ver"
        title = opcion+": "+servername.strip()+" ("+calidad.strip()+")"+" ("+idioma.strip()+")"
        title = scrapertools.htmlclean(title)
        thumbnail = item.thumbnail
        plot = item.title+"\n\n"+scrapertools.find_single_match(data,'<meta property="og:description" content="([^"]+)"')
        plot = scrapertools.htmlclean(plot)
        fanart = scrapertools.find_single_match(data,'<div style="background-image.url. ([^\s]+)')
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append(Item(channel=__channel__, action="play", title=title , fulltitle = title, url=url , thumbnail=thumbnail , plot=plot , fanart=fanart, show=item.show, folder=True, viewmode="movie_with_plot"))

    if item.extra == "pelicula":
        # STRM para todos los enlaces de servidores disponibles
        # Si no existe el archivo STRM de la peícula muestra el item ">> Añadir a la biblioteca..."
        try: itemlist.extend( file_cine_library(item) )
        except: pass

    return itemlist

def file_cine_library(item):
    import os
    from platformcode.xbmc import library
    librarypath = os.path.join(config.get_library_path(),"CINE")
    archivo = library.title_to_folder_name(item.show.strip())
    strmfile = archivo+".strm"
    strmfilepath = os.path.join(librarypath,strmfile)

    if not os.path.exists(strmfilepath):
        itemlist = []
        itemlist.append( Item(channel=item.channel, title=">> Añadir a la biblioteca...", url=item.url, action="add_file_cine_library", extra="episodios", show=archivo) )

    return itemlist

def add_file_cine_library(item):
    from platformcode.xbmc import library, xbmctools
    library.savelibrary( titulo=item.show , url=item.url , thumbnail=item.thumbnail , server=item.server , plot=item.plot , canal=item.channel , category="Cine" , Serie="" , verbose=False, accion="play_from_library", pedirnombre=False, subtitle=item.subtitle )
    itemlist = []
    itemlist.append(Item(title='El vídeo '+item.show+' se ha añadido a la biblioteca'))
    xbmctools.renderItems(itemlist, "", "", "")

    return

def play(item):
    logger.info("pelisalacarta.channels.hdfull play")

    itemlist = servertools.find_video_items(data=item.url)

    for videoitem in itemlist:
        videoitem.title = "Enlace encontrado en "+videoitem.server+" ("+scrapertools.get_filename_from_url(videoitem.url)+")"
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist    
