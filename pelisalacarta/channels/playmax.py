# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core import jsontools
from core.item import Item
from servers import servertools

DEBUG = config.get_setting("debug")

__category__ = "F"
__type__ = "generic"
__title__ = "PlayMax"
__channel__ = "playmax"
__language__ = "ES"
__creationdate__ = "20141217"
__thumbnail__ = "http://s6.postimg.org/lkvqa9wsx/playmax.jpg" 

host = "http://playmax.es/"

def isGeneric():
    return True

def openconfig(item):
    if "xbmc" in config.get_platform() or "boxee" in config.get_platform():
        config.open_settings( )
    return []

def mainlist(item):
    logger.info("pelisalacarta.channels.playmax mainlist")

    itemlist = []

    ## Sólo se usa 'login' en findvideos. El que no esté registrado podrá ojear pero no verá enlaces alos vídeos 
    if config.get_setting("playmaxaccount")!="true":
        itemlist.append( Item( channel=__channel__ , title="Habilita tu cuenta en la configuración para poder ver los enlaces a los vídeos..." , action="openconfig" , url="" , folder=False ) )
    #else:
    #    itemlist.append( Item(channel=__channel__, action="series", title="Series", url=host + "catalogo.php?tipo=1" ))
    itemlist.append( Item(channel=__channel__, action="series", title="Series", url=host + "catalogo.php?tipo=1" ))

    return itemlist

def series(item):
    logger.info("pelisalacarta.channels.playmax menuseries")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    ## Agrupa los datos
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>','',data)
    data = re.sub(r'\s+',' ',data)
    data = re.sub(r'<!--.*?-->','',data)

    #<div onMouseOver="marcar_on('281', '1')" onMouseOut="marcar_of('281', '1')" class="divjustify" id="281" name="1" style="position: relative; margin-bottom: 5px; height:225px; width: 135px; margin-left: 19px; margin-right: 19px; text-align: center; sans-serif; color: #333;"><a href="./the-walking-dead-f281"><img title="The Walking Dead" class="bimg" style="border-radius: 3px; height:200px; width: 135px;" src="./caratula281"></a> <br> <span style="text-overflow: ellipsis;overflow: hidden;width: 145px;white-space: nowrap;word-wrap: normal;text-align: center;display: block; margin-left: -5px;">The Walking Dead</span><div style="position: absolute;top: 0px;width: 30px; height: 30px;right: 0px;font-size: 13px; font-weight: bold; color: #f77f00; text-align: center; line-height: 30px; background-color: rgba(255, 255, 255, 0.8); border-bottom-left-radius: 3px;">9.3</div></div> <span id="pos1"></span>

    patron = '<a href="([^"]+)"><img title="([^"]+)".*?src="([^"]+)"></a>.*?<div[^>]+>([^<]+)</div>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedpuntuacion in matches:
        title = scrapedtitle+" ("+scrapedpuntuacion+")" 
        itemlist.append( Item(channel=__channel__, title=title, url=urlparse.urljoin(host,scrapedurl), action="episodios", thumbnail=urlparse.urljoin(host,scrapedthumbnail), show=scrapedtitle) )

    # paginación
    patron = '<a href="([^"]+)">Siguiente</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)>0:
        itemlist.append( Item(channel=__channel__, title=">> Página siguiente", url=urlparse.urljoin(host,matches[0].replace("amp;","")), action="series") )

    return itemlist

def episodios(item):
    logger.info("pelisalacarta.channels.playmax episodios")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    ## Agrupa los datos
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>','',data)
    data = re.sub(r'\s+',' ',data)
    data = re.sub(r'<!--.*?-->','',data)

    #function load_links(value){var url = './c_enlaces.php?ficha=128&id=' + value + '&key=ZHB6YXE=';
    #^_______API+Número de la ficha:______^______Lo que usaremos________^______No nos interesa_____^

    patron = "var url = '([^']+)'"
    enlace = scrapertools.get_match(data,patron)

    #onclick="load_links_dos('5126', 'Viendo The Walking Dead 1x01 - Días pasados', 'Días pasados', '1X01', '5125', '5127')"
    #_API+Número de episodio_^_id_^_________^_________scrapedtitle_______________^__^___________No nos interesa___________^

    patron = "load_links_dos.'([^']+)', 'Viendo ([^']+)'"
    all_episodes = re.compile(patron,re.DOTALL).findall(data)

    for id, scrapedtitle in all_episodes:
        url = enlace + id + "&key=ZHp6ZG0="
        itemlist.append( Item(channel=__channel__, title=scrapedtitle, url=urlparse.urljoin(host,url), action="findvideos", thumbnail=item.thumbnail, show=item.show) )

    ## Opción "Añadir esta serie a la biblioteca de XBMC"
    if (config.get_platform().startswith("xbmc") or config.get_platform().startswith("boxee")) and len(itemlist)>0:
        itemlist.append( Item(channel=__channel__, title="Añadir esta serie a la biblioteca de XBMC", url=item.url, action="add_serie_to_library", extra="episodios", show=item.show) )

    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.playmax findvideos")

    if config.get_setting("playmaxaccount")=="true": login()

    itemlist = []

    ## Descarga la página
    data = scrapertools.cache_page(item.url)
    ## Agrupa los datos
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>','',data)
    data = re.sub(r'\s+',' ',data)
    data = re.sub(r'<!--.*?-->','',data)

    #<divdd class="capitulo" id="el500167"><a onclick="cvd('5126'); pulsed('500167')" href="./redirect.php?url=aHR0cDovL2FsbG15dmlkZW9zLm5ldC95ZTBmYzc3dXB6aXA=&id=281" target="_blank"><divd class="servidor"><img style="margin-top: 5px;" src="./styles/prosilver/imageset/allmyvideos.png"></divd><divd class="calidad">720p HD</divd><divd class="idioma">Inglés</divd><divd class="subtitulos">Sin subtítulos</divd><divd class="calidadaudio">Rip</divd></a><a href="./memberlist.php?mode=viewprofile&u=14204" target="_blank"><divd class="uploader">shara</divd></a><divd class="botonesenlaces"><divd><divd style="float: left;" id="linkmas500167"><divd class="positive_evaluation" onclick="valorar_noticia(500167, 1)"></divd></divd><divd style="float: left; color: #c21200;; text-align: center; width: 21px;" id="value_evaluation500167">-1</divd><divd style="float: left;" id="linkmenos500167"><divd onclick="valorar_noticia(500167, 2)" class="negative_evaluation"></divd></divd></divd></divd></divdd>

    patron = '<divdd class="capitulo" id="[^"]+">'
    patron+= '<a onclick="[^"]+" href="([^"]+)".*?'
    patron+= 'src="([^"]+)"></divd>'
    patron+= '<divd class="calidad">([^<]+)</divd>'
    patron+= '<divd class="idioma">([^<]+)</divd>'
    patron+= '<divd class="subtitulos">([^<]+)</divd>'
    patron+= '<divd class="calidadaudio">([^<]+)</divd>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    if len(matches) == 0: 
        itemlist.append( Item(channel=__channel__, title ="No hay enlaces", folder=False ) )
        return itemlist

    for scrapedurl, scrapedthumbnail, calidad, idioma, subtitulos, calidadaudio in matches:
        servidor = scrapertools.get_match(scrapedthumbnail,'imageset/([^\.]+)\.')
        title = item.title + " [" + servidor + "] [" + calidad + "] [" + idioma + "] [" + subtitulos + "] [" + calidadaudio + "]"
        itemlist.append( Item(channel=__channel__, title =title, url=urlparse.urljoin(host,scrapedurl), action="play", thumbnail=urlparse.urljoin(host,scrapedthumbnail), fanart=item.thumbnail, show=item.show ) )

    return itemlist

def play(item):
    logger.info("pelisalacarta.channels.playmax play url="+item.url)

    ## stopbot - url
    url = scrapertools.get_header_from_response(item.url, header_to_get="location")

    ## Descarga la página
    data = scrapertools.cache_page(url)
    ## Agrupa los datos
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>','',data)
    data = re.sub(r'\s+',' ',data)
    data = re.sub(r'<!--.*?-->','',data)

    ## stopbot - POST tipo 1
    #$.ajax({ type: "POST", url: "./bot.php", data: "key=qdWmuqaRhpbdxtrx5cK7lt%2FNb8+XvpvbvGXXvaSv5MnRmuA%3D%3D&id=6539&k=MXVUVzE5TFg3dExkMGclM0QlM0Q=&tipo=1",

    ## stopbot - POST tipo 2
    #$.ajax({ type: "POST", url: "./bot.php", data: "dc=" + m + "&key=qdWmuqaRhpbdxtrx5cK7lt%2FNb8+XvpvbvGXXvaSv5MnRmuA%3D%3D&id=6539&k=MXVUVzE5TFg3dExkMGclM0QlM0Q=&tipo=2",

    tipo_1 = scrapertools.get_match(data,'data: "([^"]+)"')
    tipo_1 = scrapertools.cache_page('http://stopbot.tk/bot.php',post=tipo_1)

    tipo_2 = scrapertools.get_match(data,'data: "dc=" . m . "([^"]+)"')
    tipo_2 = "dc="+tipo_1+tipo_2

    data = scrapertools.cache_page('http://stopbot.tk/bot.php',post=tipo_2)

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.channel = __channel__

    return itemlist

def login():
    logger.info("pelisalacarta.channels.playmax login")

    login_form = "ucp.php?mode=login"
    data = scrapertools.cache_page(urlparse.urljoin(host,login_form))

    patron = '<input type="hidden" name="sid" value="([^"]+)" />'
    sid = scrapertools.find_single_match(data,patron)

    post = "username="+config.get_setting('playmaxuser')+"&password="+config.get_setting('playmaxpassword')+"&sid="+sid+"&redirect=index.php&login=Identificarse&redirect=.%2Fucp.php%3Fmode%3Dlogin"

    data = scrapertools.cache_page("http://playmax.es/ucp.php?mode=login",post=post)
