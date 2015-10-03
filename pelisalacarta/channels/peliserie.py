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
    return scrapertools.get_match( data, '"type":([^,]+),' )
    
def mainlist(item):
    logger.info("[peliserie.py] mainlist")
        
    itemlist = []
    itemlist.append( Item(channel=__channel__, action="listado", title="Películas", url=__url_base__+'/movies', extra="peliculas") )
    itemlist.append( Item(channel=__channel__, action="submenu", title="Filtrar películas por género y década", url=__url_base__+'/movies', extra="peliculas") )
    itemlist.append( Item(channel=__channel__, action="listado", title="Series", url=__url_base__+'/series', extra="series") )
    itemlist.append( Item(channel=__channel__, action="submenu", title="Filtrar series por género y década", url=__url_base__+'/series', extra="series") )
    itemlist.append( Item(channel=__channel__, action="search", title="Buscar") )
    
    #itemlist.append( Item(channel=__channel__, action="tmdb", title="TMDB") )
    logger.info("[peliserie.py] login: "+ str(login()))
    
    return itemlist

def search(item,texto):
    logger.info("[peliserie.py] search:" + texto)
    itemlist = []
    
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
    #patron = '<div class="grid-list(.*?)<div class="footer">'
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
            if item.extra=='peliculas':
                show += '|' + year #pasamos el año para buscar el fanart
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
                    itemlist.append( Item(channel=__channel__, action=action, title=title, url=url, thumbnail=thumbnail, extra=item.extra,  show=show ) )
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
    
    if item.extra != 'serie_add':
        #obtener fanart
        oTvdb= TvDb()
        serieID= oTvdb.get_serieId_by_title(item.show)
        if serieID !='0':
            list_fanart = oTvdb.get_graphics_by_serieId(serieID)
    if len(list_fanart) > 0:
        item.fanart=random.choice(list_fanart)
    else:
        item.fanart=''
                
    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)","",scrapertools.cache_page(item.url))
    patron = '<div class="nav-pills(.*?)</div></div></div>'
    try:
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
            
            itemlist.append(Item(channel=__channel__, action=action, title=title, url=url, show=show ,fanart= item.fanart, thumbnail= item.thumbnail,extra='series'))
        
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
        item.fanart= get_fanart_tmdb(item.show, year= year)
        
    else: # 'series' y 'play_from_library'
        # Solo mostramos enlaces para ver online
        patron= 'id="view-list">(.*?)</ul>'
        # Si quisiseramos mostrarlos todos: patron= 'id="id="view-list">(.*?)class="list-end"'
    
    
    # Descarga la página
    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)","",scrapertools.cache_page(item.url))    
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
            itemlist.append( Item(channel=__channel__, action="play", server=servidor, title=title , thumbnail=item.thumbnail, fanart= item.fanart, fulltitle = item.title, url=url , extra=item.extra, folder=False) )

    
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
      

'''
tmdb
'''  
def search_movie(titulo, page ='1', idioma='es', include_adult='false', year=''):
    # informacion: http://docs.themoviedb.apiary.io/#reference/search/searchmovie/get 
    headers = {
      'Accept': 'application/json'
    }
    
    url='http://api.themoviedb.org/3/search/movie?api_key=57983e31fb435df4df77afb854740ea9&query=%s&language=%s&include_adult=%s' %(titulo.replace(' ','%20') , idioma, include_adult)
    if year !='': url+= '&year=' + year 
    
    #logger.info("[peliserie.py] url:" + url)
    request = urllib2.Request(url , headers=headers)
    response_body = urllib2.urlopen(request).read()
    
    ''' 
    # Convierte un string JSON en Objeto
    import json   
    h2o = lambda x: (type('jo', (), {k: h2o(v) for k, v in x.items()}) if isinstance(x,dict) else x)
    json_to_obj = lambda s: h2o(json.loads(s))
    '''
    logger.info("[peliserie.py] TMDB_JSON: " + str(response_body))
    '''
    obj=json_to_obj(response_body)
    
    return obj
    '''
    return scrapertools.find_single_match(response_body,'"backdrop_path":"([^"]+)",')
    
def get_fanart_tmdb (titulo, size='w1280', page ='1', idioma='es', include_adult='false', year=''):
    '''obj_TMDB= search_movie(titulo, page, idioma, include_adult, year)
    res =''
    # size: "w300", "w780", "w1280", "original"
    if obj_TMDB.total_results > 0:
        imagen=obj_TMDB.results[0]['backdrop_path']
        if type(imagen) is str or type(imagen) is unicode:
            res= 'http://image.tmdb.org/t/p/' + size + imagen
    '''
    imagen= search_movie(titulo, page, idioma, include_adult, year)
    res =''
    # size: "w300", "w780", "w1280", "original"
    if len(imagen) > 0:
        res= 'http://image.tmdb.org/t/p/' + size + imagen
    
    logger.info("[peliserie.py] get_fanart_tmdb: " + res)    
    return res
      
'''    
   Clase TvDb
   Esta clase podria ir en un fichero externo para ser utilizado por otros canales
''' 
class TvDb():
    
    def __init__(self,idiomaDef="es"):
        self.__idiomaDef = idiomaDef #fija el idioma por defecto para el resto de metodos
               
    def get_series_by_title(self, title, idioma=""):
        '''
        Busqueda de series por titulo
        @return:
            Devuelve un documento que representa el xml con todas las series encontradas por orden de mayor similitud
        @params:
            title: Titulo de la serie.
            idioma: Argumento opcional que especifica el idioma de la serie a buscar. Por defecto: idioma seleccionado por defecto al iniciar el objeto
        '''
        from xml.dom import minidom
        if idioma=="": idioma= self.__idiomaDef
        __getSeriesByTitleUrl ='http://thetvdb.com/api/GetSeries.php?seriesname=%s&language=%s' %(title.replace(' ','%20'), idioma)
        __data = scrapertools.cache_page(__getSeriesByTitleUrl)
        xmldoc= None
        if len(__data)>0:
            xmldoc = minidom.parseString(__data)
            logger.info("[TvDb.get_series_by_title] Titulo= " +title+ "; Series encontradas: " + str(len(xmldoc.getElementsByTagName('Series'))))  
        else:
            logger.info("[TvDb.get_series_by_title] Error de lectura")
        return xmldoc          
    
    def get_series_by_remoteId(self, imdbid="", zap2it="", idioma=""):
        '''
        Busqueda de series por el identificador de Imdb o Zap2it
        @return:
            Devuelve un documento que representa el xml con las series encontradas
        @params:
            imdbid: The imdb id you're trying to find. Do not use with zap2itid
            zap2it: The Zap2it / SchedulesDirect ID you're trying to find. Do not use with imdbid
            language: The language abbreviation, if not provided default is used.
        '''
        from xml.dom import minidom
        if idioma=="": idioma= self.__idiomaDef
        __getSeriesByRemoteIdUrl="http://thetvdb.com/api/GetSeriesByRemoteID.php?language=%s" %idioma 
        xmldoc= None
        
        if imdbid!='':
            codigo="imdbid=" + imdbid
        elif zap2it !='':
            codigo="zap2it=" + zap2it
        else:
            logger.info("[TvDb.get_series_by_remoteId] Error de parametros")
        
        __data = scrapertools.cache_page(__getSeriesByRemoteIdUrl +"&" + codigo)
        if len(__data)>0:
            xmldoc = minidom.parseString(__data)
            logger.info("[TvDb.get_series_by_remoteId] Codigo " + codigo + "; Series encontradas: " + str(len(xmldoc.getElementsByTagName('Series'))))  
        else:
            logger.info("[TvDb.get_series_by_remoteId] Error de lectura")
        return xmldoc        
    
    def get_serieId_by_remoteId(self, imdbid="", zap2it="", idioma=""):
        '''
        Convierte un identificador Imdb o Zap2it en un identificador TvDb
        @return:
            Devuelve una cadena con el identificador TvDb de la serie
        @params:
            imdbid: The imdb id you're trying to find. Do not use with zap2itid
            zap2it: The Zap2it / SchedulesDirect ID you're trying to find. Do not use with imdbid
            language: The language abbreviation, if not provided default is used.
        '''
        from xml.dom import minidom
        xmldoc = self.get_series_by_remoteId(imdbid, zap2it, idioma)
        itemlist = xmldoc.getElementsByTagName('seriesid') 
        
        if imdbid!='':
            codigo="imdbid=" + imdbid
        elif zap2it !='':
            codigo="zap2it=" + zap2it
        
        if len(itemlist)>0:    
            serieId = itemlist[0].childNodes[0].nodeValue
            logger.info("[TvDb.get_serieId_by_remoteId] Codigo " + codigo + "; serieId= " +serieId)
            return serieId
        else:
            logger.info("[TvDb.get_serieId_by_remoteId] Codigo " + codigo + " no encontrado")
            return '0'
    
    def get_serieId_by_title(self,title, idioma=""):
        '''
        Lleva a cabo una busqueda por titulo de series y devuelve el identificador de la serie con mayor similitud
        @return:
            Devuelve una cadena con el identificador de la serie cuyo titulo mas se asemeje al buscado
        @params:
            title: Titulo de la serie.
            idioma: Argumento opcional que especifica el idioma de la serie a buscar. Por defecto: idioma seleccionado por defecto al iniciar el objeto
        '''
        from xml.dom import minidom
        xmldoc = self.get_series_by_title(title, idioma)
        itemlist = xmldoc.getElementsByTagName('seriesid') 
        if len(itemlist)>0:
            serieId = itemlist[0].childNodes[0].nodeValue
            logger.info("[TvDb.get_serieId_by_title] Titulo= " +title+ "; serieId= " +serieId)
            return serieId
        else:
            logger.info("[TvDb.get_serieId_by_title] Titulo= " +title+ "No encontrada")
            return '0'
                 
    def get_banners_by_serieId (self, serieId):
        '''
        @return:
            Devuelve un documento que representa el xml con todos los graficos de la serie
        @params:
            serieId: Identificador de la serie.
        '''
        from xml.dom import minidom
        __getBannersBySeriesIdUrl = 'http://thetvdb.com/api/1D62F2F90030C444/series/%s/banners.xml' %serieId
        __data = scrapertools.cache_page(__getBannersBySeriesIdUrl)
        xmldoc= None
        
        if len(__data)>0:
            xmldoc = minidom.parseString(__data)
            logger.info("[TvDb.get_banners_by_serieId] serieId= " +str(serieId) + "; Banners encontrados: " + str(len(xmldoc.getElementsByTagName('Banner'))))  
        else:
            logger.info("[TvDb.get_banners_by_serieId] Error de lectura")
        #return str(len(xmldoc.getElementsByTagName('Banner')))
        return xmldoc 
    
    def get_banners_by_title(self,title, idioma=""):
        '''
        @return:
            Devuelve un documento que representa el xml con todos los graficos de la serie
        @params:
            title: Titulo de la serie.
            idioma: Argumento opcional que especifica el idioma de la serie a buscar. Por defecto: idioma seleccionado por defecto al iniciar el objeto
        '''
        from xml.dom import minidom
        xmldoc= None
        id= self.get_serieId_by_title(title,idioma)
        if id>0:
            xmldoc = self.get_banners_by_serieId(id)
        #return str(len(xmldoc.getElementsByTagName('Banner')))
        return xmldoc
            
    def get_graphics_by_serieId (self, serieId, bannerType='fanart_vignette', bannerType2='', season=0, *languages  ):
        '''
        Busqueda por identificador de los graficos de una serie.
        @return: 
            Devuelve una lista de urls de banners de que coinciden con los criterios solicitado.
        @params:
            serieId: Identificador de la serie.
            bannerType: This can be poster, fanart, fanart_vignette, series or season.
            bannerType2: For series banners it can be text, graphical, or blank. For season banners it can be season or seasonwide. For fanart it can be 1280x720 or 1920x1080. For poster it will always be 680x1000.
            season: Opcionalmente se puede especificar una temporada en concreto (Por defecto 0, todas las temporadas)
            languages: Es posible añadir varios separados por comas. (Por defecto se incluyen en ingles y el idioma seleccionado por defecto al iniciar el objeto)
        '''   
        from xml.dom import minidom
        ret= []
        vignette=False
        
        # Comprobamos los parametros pasados
        if bannerType in ('poster', 'fanart', 'fanart_vignette', 'series', 'season'):
            if not str(serieId).isdigit() or not str(season).isdigit():
                logger.info("[TvDb.get_graphics_by_serieId] Error lo argumentos 'serieId' y 'season' deben ser numericos")
                return []
            else:
                if bannerType== 'fanart_vignette':
                    bannerType= 'fanart'
                    vignette= True
                
                if bannerType== 'poster': bannerType2='680x1000'
                elif bannerType== 'fanart' and bannerType2 in ('1280x720', '1920x1080',''): pass
                elif bannerType== 'series ' and bannerType2 in ('text', 'graphical', 'blank'): pass
                elif bannerType== 'season' and bannerType2 in ('season', 'seasonwide'): pass
                else:
                    logger.info("[TvDb.get_graphics_by_serieId] Error argumento 'bannerType2' no valido")
                    return []
        else:
            logger.info("[TvDb.get_graphics_by_serieId] Error argumento 'bannerType' no valido")
            return []
        if len(languages)==0:
            languages= ['en']
            if self.__idiomaDef not in languages: languages.insert(0,self.__idiomaDef)
        else:
            if type(languages[0]) is tuple:  languages= list(languages[0])
            
            for lenguage in languages:
                if len(lenguage) != 2:
                    logger.info("[TvDb.get_graphics_by_serieId] Error argumento 'languages' no valido")
                    return []
        
        # Obtener coleccion de elementos banner de banners.xml
        banners = self.get_banners_by_serieId(serieId).getElementsByTagName('Banner')
        
        for banner in banners:
            # Comprobar si es del mismo tipo
            if banner.getElementsByTagName('BannerType')[0].firstChild.data == bannerType:
                if bannerType2=="" or banner.getElementsByTagName('BannerType2')[0].firstChild.data == bannerType2:
                    idiomas= banner.getElementsByTagName('Language')
                    # Comprobar idioma
                    if len(idiomas)!=0:
                        fi=False
                        for lenguage in languages:
                            if lenguage== idiomas[0].firstChild.data:
                                fi=True
                    else: #no expecifica idioma
                        fi=True
                    # Comprobar temporada
                    if season==0 or banner.getElementsByTagName('Season')[0].firstChild.data== season: #error
                        ft=True  
                    else:
                        ft=False
                    if fi and ft:
                        if vignette and banner.getElementsByTagName('VignettePath')[0].firstChild.data!="":
                            ret.append('http://thetvdb.com/banners/' + banner.getElementsByTagName('VignettePath')[0].firstChild.data)
                        else:
                            ret.append('http://thetvdb.com/banners/' + banner.getElementsByTagName('BannerPath')[0].firstChild.data)
                        logger.info("[TvDb.get_graphics_by_serieId] bannerType2=" +banner.getElementsByTagName('BannerType2')[0].firstChild.data)
        logger.info("[TvDb.get_graphics_by_serieId] serieId=" +str(serieId)+", bannerType="+  bannerType +", bannerType2="+ bannerType2  +", season="+ str(season) +", languages="+ str(languages))
        logger.info("[TvDb.get_graphics_by_serieId] Banners encontrados: "+ str(len(ret)))
        return ret        
                
    def get_graphics_by_title (self, title, bannerType='fanart_vignette', bannerType2='', season=0, *languages  ):
        '''
        Busqueda por titulo de los graficos de una serie.
        @return: 
            Devuelve una lista de urls de banners de que coinciden con los criterios solicitado.
        @params:
            serieId: Identificador de la serie.
            bannerType: This can be poster, fanart, fanart_vignette, series or season.
            bannerType2: For series banners it can be text, graphical, or blank. For season banners it can be season or seasonwide. For fanart it can be 1280x720 or 1920x1080. For poster it will always be 680x1000.
            season: Opcionalmente se puede especificar una temporada en concreto (Por defecto 0, todas las temporadas)
            languages: Es posible añadir varios separados por comas. (Por defecto se incluyen en ingles y el idioma seleccionado por defecto al iniciar el objeto)
        '''  
        from xml.dom import minidom
        ret= []
        if len(languages)==0:
           idioma= self.__idiomaDef
           languages= None
        else:
            idioma= languages[0]
        id= self.get_serieId_by_title(title,idioma)
        if id>0:
            if languages is None:
                ret= self.get_graphics_by_serieId (id, bannerType, bannerType2, season)
            else:
                ret= self.get_graphics_by_serieId (id, bannerType, bannerType2, season, languages)
        return ret
   
    def get_episode_by_seasonEpisode (self, serieId, season, episode, idioma=""):
        '''
        Busca datos de un capitulo en concreto
        @return:
            Devuelve un documento que representa el xml con los datos del capitulo buscado
        @params:
            serieId: Identificador de la serie.
            season: Numero de temporada buscada.
            episode: Numero del episodio dentro de la temporada buscado.
            idioma: Argumento opcional que especifica el idioma de la serie a buscar. Por defecto: idioma seleccionado por defecto al iniciar el objeto 
        '''
        from xml.dom import minidom
        if idioma=="": idioma= self.__idiomaDef
        __getEpisodeBySeasonEpisodeUrl= 'http://thetvdb.com/api/1D62F2F90030C444/series/%s/default/%s/%s/%s.xml' %(serieId, season, episode, idioma)
        __data = scrapertools.cache_page(__getEpisodeBySeasonEpisodeUrl)
        xmldoc= None
        
        if len(__data)>0:
            xmldoc = minidom.parseString(__data)
            logger.info("[TvDb.get_episode_by_seasonEpisode] serieId= " +str(serieId) + ", season="+  str(season) +", episode="+ str(episode) +", idioma="+ idioma)
        else:
            logger.info("[TvDb.get_episode_by_seasonEpisode] Error de lectura")
        #return xmldoc 
        return str(len(xmldoc.getElementsByTagName('Episode')))
        