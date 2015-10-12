# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para newpct1
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys, random

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

DEBUG = config.get_setting("debug")
__adult__ = "false"
__category__ = "F,S"
__type__ = "generic"
__title__ = "Peliserie"
__channel__ = "peliserie"
__language__ = "ES"
__creationdate__ = "20150312"
__thumbnail__ = "http://i.imgur.com/KfFpe4l.png"
__url_base__="http://www.peliserie.com"

def isGeneric():
    return True

   
def mainlist(item):
    logger.info("[peliserie.py] mainlist")
        
    itemlist = []
    itemlist.append( Item(channel=__channel__, action="listado", title="Películas", url=__url_base__+'/movies', extra="peliculas") )
    itemlist.append( Item(channel=__channel__, action="submenu", title="Filtrar películas por género y década", url=__url_base__+'/movies', extra="peliculas") )
    itemlist.append( Item(channel=__channel__, action="listado", title="Series", url=__url_base__+'/series', extra="series") )
    itemlist.append( Item(channel=__channel__, action="submenu", title="Filtrar series por género y década", url=__url_base__+'/series', extra="series") )
    itemlist.append( Item(channel=__channel__, action="search", title="Buscar") )
    
    #itemlist.append( Item(channel=__channel__, action="tmdb", title="Test TMDB") )
    #logger.info("[peliserie.py] login: "+ str(login()))
    
    return itemlist

def search(item,texto):
    logger.info("[peliserie.py] search:" + texto)
    itemlist = []
    texto=texto.replace(' ','%20')
    item.url = __url_base__ + "/search?q=" + texto + '&type=movies'
    item.extra="peliculas"
    itemlist = listado(item)
    
    item.url = __url_base__ + "/search?q=" + texto + '&type=series'
    item.extra="series"
    itemlist.extend (listado(item))
    
    return itemlist

def submenu(item):
    logger.info("[peliserie.py] submenu")
    itemlist=[]

    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)","",scrapertools.cache_page(item.url))
    
    patron = '<div class="grid-filter">(.*?)</div>'
    data = scrapertools.get_match(data,patron)

    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for value, title in matches:
        if value !='':
            if len(value)< 4: 
                url = item.url + '?gender=' + value
            else:
                url = item.url + '?decade=' + value  
                
        itemlist.append( Item(channel=__channel__, action="listado" ,title=title, url=url, extra=item.extra) )
       
    return itemlist

def listado(item):
    logger.info("[peliserie.py] listado")
    itemlist = []
    
    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)","",scrapertools.cache_page(item.url))
    data= data.replace('<div class="list-end">','</div></div><div class="list-end">')
    patron = '<div class="grid-list(.*?)</a></div></div></div>'
    
            
    try:
        fichas = scrapertools.get_match(data,patron) + '</a>'
    except:
        return itemlist # Devolvemos lista vacia
    
    '''<a href="/movie/6916/Big-Eyes-2014-online" 
    title="Big Eyes" data-ajax="true" data-label="Big Eyes - 2014" data-page="movies">
    <div class="mask-container">
    <div class="poster">
    <div class="X9G8W3" data-image="/images/posters/670b9a082a8c9dc40e48b039501da7d1.png"></div>
    <div class="quality c4">DVD Rip</div>
    <div class="lang"><img src="./images/flags/lang/flag_0.png"/></div> o <div class="lang"></div>
    <div class="gender">Drama</div>
    <div class="title">Big Eyes</div></div></div>
    </a>
    '''
    patron  = '<a href="([^"]+).*?' #url
    patron += 'title="([^"]+).*?' #titulo
    patron += 'data-label=".*?(\d{4})".*?' #año
    patron += '<div class="poster">(.*?)</a>' #info
    matches = re.compile(patron,re.DOTALL).findall(fichas)
    logger.info("[peliserie.py] listado: matches " + str(len(matches)))
    
    pag_actual= 1
    i=0
    if 'search?q=' not in item.url:
        #Preparar paginacion
        if not 'page=' in item.url:
                #http://www.peliserie.com/series
                item.url += '?page=1'
        else: 
            #http://www.peliserie.com/series?page=3
            pag_actual= float(scrapertools.get_match(item.url,'page=(\d+)'))
            
    if item.extra=='series':
        action = 'getEpisodios'
    else:
        action = "findvideos"
                        
    for url, title, year, info in matches:
        i += 1
        if i > ((pag_actual-1) * 56):
        
            # Recuperar informacion
            thumbnail = __url_base__ + scrapertools.get_match(info,'data-image="([^"]+)"></div>.*?') 
            show = title
            show += '|' + year   #pasamos el año para buscar el fanart
            url=__url_base__ + url
            
            if 'search?q=' in item.url:
                # Resultado de busquedas
                itemlist.append( Item(channel=__channel__, action=action, title=title, url=url, thumbnail=thumbnail, extra=item.extra, show=show ) )
            else:
                idiomas=''
                try:
                    idiomas = scrapertools.get_match(info,'<div class="lang">(.*?)</div>')
                    lang=[]
                    if 'flag_0.png' in idiomas: lang.append('Es')
                    if 'flag_1.png' in idiomas: lang.append('Lat')
                    if 'flag_2.png' in idiomas: lang.append('VO')
                    if 'flag_3.png' in idiomas: lang.append('VOSE')
                    if len(lang) > 0:
                        idiomas=' [' +  "/".join(lang)+']'
                except: #Si no incluye idiomas no pasa nada
                    pass    
                try:
                    logger.info("[peliserie.py] listado item.extra: " + item.extra)
                    calidad = ' [' + scrapertools.get_match(info,'<div class="quality[^"]+">([^<]*)</div>.*?') + ']'
                    title = title + calidad + idiomas
                    itemlist.append( Item(channel=__channel__, action=action, title=title, url=url, thumbnail=thumbnail, extra=item.extra, show=show ) )
                except: #Si no incluye la calidad no hay enlaces aun
                    pass
             
    #Paginacion
    if not '<div class="list-end">' in data: 
        url_next_page  = item.url[:item.url.rfind(str(pag_actual))] + str(pag_actual+1)
        itemlist.append( Item(channel=__channel__, action="listado" , title=">> Página siguiente" , url=url_next_page, extra=item.extra))            
    logger.info("[peliserie.py] listado: itemlist " + str(len(itemlist)))
    return itemlist
    
def getEpisodios (item):
    # Devuelve todos los capitulos de una serie
    logger.info("[peliserie.py] getEpisodios")
    itemlist = []  
    list_fanart=''
    
    # Buscamos el fanart en TMDB
    year=item.show.split('|')[1]
    item.show = item.show.split('|')[0]
    try:
        from core.tmdb import Tmdb
        oTmdb= Tmdb(texto_buscado=item.show,year=year,tipo="tv")
        item.fanart=oTmdb.get_fanart()
    except:
        pass
  
    try:           
        data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)","",scrapertools.cache_page(item.url))
        sinopsis= scrapertools.entityunescape(scrapertools.get_match(data,'<p class="sinopsis">(.*?)</p>'))
        
        patron = '<div class="nav-pills(.*?)</div></div></div>'
        data = scrapertools.get_match(data,patron)
        patron= '<a href="([^"]+).*?' #url
        patron += '<strong>(\d+[x|X]\d+).*?</strong>.*?' #capitulo
        patron += '<img(.*?)</div>' # info:idiomas
        matches = re.compile(patron,re.DOTALL).findall(data)
        
        for url, capitulo, idiomas in matches:
            #logger.info("[peliserie.py] getEpisodios idiomas: " +idiomas)
            #idiomas = scrapertools.get_match(info,'src="(.*?)</div>')
            lang=[]
            if 'flag_0.png' in idiomas: lang.append('Es')
            if 'flag_1.png' in idiomas: lang.append('Lat')
            if 'flag_2.png' in idiomas: lang.append('VO')
            if 'flag_3.png' in idiomas: lang.append('VOSE')
            if len(lang) > 0:
                idiomas=' [' +  "/".join(lang)+']'
            else:
                idiomas=''
                    
            url=__url_base__ + url
            show = item.show
            title = show + ' ' + capitulo + idiomas
            action = "findvideos"
            
            itemlist.append(Item(channel=__channel__, action=action, title=title, viewmode="movie_with_plot", url=url, show=show ,fanart= item.fanart, thumbnail= item.thumbnail,extra='series',plot=sinopsis))
        
        if config.get_library_support() and len(itemlist)>0 and item.extra.startswith("serie"):
            itemlist.append( Item(channel=__channel__, title="Añadir esta serie a la biblioteca", url=item.url, action="add_serie_to_library", extra='episodios###series', show= item.show))
    except:
        pass
        
    return itemlist 
 

def findvideos(item):
    logger.info("[peliserie.py] findvideos extra: " + item.extra)
    itemlist=[]
    
    if item.extra=='peliculas':
        # Solo mostramos enlaces para ver online
        patron= 'id="contribution-view">(.*?)</ul>'
        # Si quisiseramos mostrarlos todos: patron= 'id="contribution-view">(.*?)class="list-end"'
        
        # Buscamos el fanart en TMDB
        year=item.show.split('|')[1]
        item.show = item.show.split('|')[0]
        try:
            from core.tmdb import Tmdb
            oTmdb= Tmdb(texto_buscado=item.show,year=year)
            item.fanart=oTmdb.get_fanart()
        except:
            pass
        
        
    else: # 'series' y 'play_from_library'
        # Solo mostramos enlaces para ver online
        patron= 'id="view-list">(.*?)</ul>'
        # Si quisiseramos mostrarlos todos: patron= 'id="id="view-list">(.*?)class="list-end"'
    
    
    # Descarga la página
    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)","",scrapertools.cache_page(item.url))
    if item.plot == '':
        item.plot= scrapertools.entityunescape(scrapertools.get_match(data,'<p class="sinopsis">(.*?)</p>'))
        print item.plot
    data= scrapertools.get_match(data,patron)
    patron = '<li data-id="(.*?)</li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    '''
    <li data-id="53885">
        <div class="column"><strong>Allmyvideos</strong></div>
        <div class="column" style="width:15%">
            <img src="/images/flags/lang/flag_0.png"/>
        </div> 
        <div class="column">BrScreener/Line</div>
        <div class="column">bibiamorant</div>
        <div class="column" style="width:25%">
            <div class="btn s">
                <a href="/external?action=movie&id=53885" class="" target="_blank">Ver online</a>
            </div> 
            <div class="actions">
                <i id="report-contribution" data-id="53885" class="iconx16 icon3"></i> 
            </div>
        </div>
    </li>
    '''
    
    for i in matches:  
        servidor = scrapertools.get_match(i,'<div class="column"><strong>([^<]+)</strong>') 
        
        mostrar_server= True
        if config.get_setting("hidepremium")=="true":
            mostrar_server= servertools.is_server_enabled (servidor)
        
        if mostrar_server:
            idioma = scrapertools.get_match(i,'<img src="(.*?)"/>')
            if 'flag_0.png' in idioma: 
                idioma ='Es'
            elif 'flag_1.png' in idioma: 
                idioma ='Lat'
            elif 'flag_2.png' in idioma: 
                idioma ='VO'
            elif 'flag_3.png' in idioma: 
                idioma ='VOSE'
            calidad=  scrapertools.get_match(i,'<div class="column">([^<]+)</div>')
            url= __url_base__ + scrapertools.get_match(i,'<a href="([^"]+)"')
            
            title= 'Ver en ' + servidor + ' [' + calidad + '] (' + idioma + ')'
            itemlist.append( Item(channel=__channel__, action="play", viewmode="movie_with_plot", server=servidor, title=title , plot=item.plot, thumbnail=item.thumbnail, fanart= item.fanart, fulltitle = item.title, url=url , extra=item.extra, folder=False) )
            #itemlist.append( Item(channel=__channel__, action="play", server=servidor, title=title , plot=item.plot, thumbnail=item.thumbnail, fanart= item.fanart, fulltitle = item.title, url=url , extra=item.extra, folder=False) )

    
    return itemlist

def play(item):
    logger.info("[peliserie.py] play")
        
    if item.extra =='peliculas':
        id = scrapertools.get_match(item.url,"(id=\d+)")
        link = "http://www.peliserie.com/query/movie_get_links.php"
        data=scrapertools.cache_page(link,post=id).replace("\\","")
        item.url = __url_base__+scrapertools.get_match(data,'href="([^"]+)"')

    item.url = scrapertools.get_header_from_response(item.url,header_to_get="location")
   
    itemlist=[]
    itemlist.append(item)
    
    return itemlist
    

def episodios(item):
    # Necesario para las actualizaciones automaticas
    return getEpisodios(Item(url=item.url, show=item.show, extra= "serie_add"))

        
# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    # mainlist
    mainlist_items = mainlist(Item())
    submenu_items = submenu(mainlist_items[0])
    listado_items = listado(submenu_items[0])
    for listado_item in listado_items:
        play_items = findvideos(listado_item)
        
        if len(play_items)>0:
            return True

    return False
      

'''def tmdb(item):
    from core.tmdb import Tmdb
    oTmdb= Tmdb(id_Tmdb='1924',tipo='movie')
    print oTmdb.get_poster(rnd= True, size="w185")
    
def login2():# no funciona
    url= 'http://www.peliserie.com/query/login.php'
    post = "username="+config.get_setting("peliserieuser")+"&password="+config.get_setting("peliseriepassword")
    
    headers=[]
    USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:20.0) Gecko/20100101 Firefox/20.0"
    headers.append(["User-Agent",USER_AGENT])
    headers.append(["Referer",url])
    data = scrapertools.cache_page( url , post=post, headers=headers )
    
    data = scrapertools.cache_page('http://www.peliserie.com')
    logger.info("[peliserie.py] login: " + data)
    
def login():
    url= __url_base__ + '/query/login.php'

    ## con path
    #params = "path=%2F&username="+config.get_setting("peliserieuser")+"&password="+config.get_setting("peliseriepassword")
    ## Normal
    #params = "username="+config.get_setting("peliserieuser")+"&password="+config.get_setting("peliseriepassword")
    params = "username="+config.get_setting("seriesmuuser")+"&password="+config.get_setting("seriesmupassword")
    ## GET
    #data = scrapertools.cache_page( url + '?' + params )

    ## POST
    data = scrapertools.cache_page( url , post=params )

    ## Retorna true o false
    return scrapertools.get_match( data, '"type":([^,]+),' )'''