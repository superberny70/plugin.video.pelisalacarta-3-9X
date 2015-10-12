# -*- coding: utf-8 -*-
#------------------------------------------------------------
# 
# 
# 
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys, random

from core import scrapertools
from core import logger
from xml.dom import minidom

__idiomaDef__ = "es" #fija el idioma por defecto para el resto de metodos
           
def get_series_by_title( title, idioma=""):
    '''
    Busqueda de series por titulo
    @return:
        Devuelve un documento que representa el xml con todas las series encontradas por orden de mayor similitud
    @params:
        title: Titulo de la serie.
        idioma: Argumento opcional que especifica el idioma de la serie a buscar. Por defecto: idioma seleccionado por defecto al iniciar el objeto
    '''
    
    if idioma=="": idioma= __idiomaDef__
    __getSeriesByTitleUrl ='http://thetvdb.com/api/GetSeries.php?seriesname=%s&language=%s' %(title.replace(' ','%20'), idioma)
    __data = scrapertools.cache_page(__getSeriesByTitleUrl)
    xmldoc= None
    if len(__data)>0:
        xmldoc = minidom.parseString(__data)
        logger.info("[TvDb.get_series_by_title] Titulo= " +title+ "; Series encontradas: " + str(len(xmldoc.getElementsByTagName('Series'))))  
    else:
        logger.info("[TvDb.get_series_by_title] Error de lectura")
    return xmldoc          

def get_series_by_remoteId( imdbid="", zap2it="", idioma=""):
    '''
    Busqueda de series por el identificador de Imdb o Zap2it
    @return:
        Devuelve un documento que representa el xml con las series encontradas
    @params:
        imdbid: The imdb id you're trying to find. Do not use with zap2itid
        zap2it: The Zap2it / SchedulesDirect ID you're trying to find. Do not use with imdbid
        language: The language abbreviation, if not provided default is used.
    '''
    
    if idioma=="": idioma= __idiomaDef__
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

def get_serieId_by_remoteId( imdbid="", zap2it="", idioma=""):
    '''
    Convierte un identificador Imdb o Zap2it en un identificador TvDb
    @return:
        Devuelve una cadena con el identificador TvDb de la serie
    @params:
        imdbid: The imdb id you're trying to find. Do not use with zap2itid
        zap2it: The Zap2it / SchedulesDirect ID you're trying to find. Do not use with imdbid
        language: The language abbreviation, if not provided default is used.
    '''
    
    xmldoc = get_series_by_remoteId(imdbid, zap2it, idioma)
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

def get_serieId_by_title(title, idioma=""):
    '''
    Lleva a cabo una busqueda por titulo de series y devuelve el identificador de la serie con mayor similitud
    @return:
        Devuelve una cadena con el identificador de la serie cuyo titulo mas se asemeje al buscado
    @params:
        title: Titulo de la serie.
        idioma: Argumento opcional que especifica el idioma de la serie a buscar. Por defecto: idioma seleccionado por defecto al iniciar el objeto
    '''
    
    xmldoc = get_series_by_title(title, idioma)
    itemlist = xmldoc.getElementsByTagName('seriesid') 
    if len(itemlist)>0:
        serieId = itemlist[0].childNodes[0].nodeValue
        logger.info("[TvDb.get_serieId_by_title] Titulo= " +title+ "; serieId= " +serieId)
        return serieId
    else:
        logger.info("[TvDb.get_serieId_by_title] Titulo= " +title+ "No encontrada")
        return '0'
             
def get_banners_by_serieId ( serieId):
    '''
    @return:
        Devuelve un documento que representa el xml con todos los graficos de la serie
    @params:
        serieId: Identificador de la serie.
    '''
    
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

def get_banners_by_title(title, idioma=""):
    '''
    @return:
        Devuelve un documento que representa el xml con todos los graficos de la serie
    @params:
        title: Titulo de la serie.
        idioma: Argumento opcional que especifica el idioma de la serie a buscar. Por defecto: idioma seleccionado por defecto al iniciar el objeto
    '''
    
    xmldoc= None
    id= get_serieId_by_title(title,idioma)
    if id>0:
        xmldoc = get_banners_by_serieId(id)
    #return str(len(xmldoc.getElementsByTagName('Banner')))
    return xmldoc
        
def get_graphics_by_serieId ( serieId, bannerType='fanart_vignette', bannerType2='', season=0, *languages  ):
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
        if __idiomaDef__ not in languages: languages.insert(0,__idiomaDef__)
    else:
        if type(languages[0]) is tuple:  languages= list(languages[0])
        
        for lenguage in languages:
            if len(lenguage) != 2:
                logger.info("[TvDb.get_graphics_by_serieId] Error argumento 'languages' no valido")
                return []
    
    # Obtener coleccion de elementos banner de banners.xml
    banners = get_banners_by_serieId(serieId).getElementsByTagName('Banner')
    
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
            
def get_graphics_by_title ( title, bannerType='fanart_vignette', bannerType2='', season=0, *languages  ):
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
    
    ret= []
    if len(languages)==0:
       idioma= __idiomaDef__
       languages= None
    else:
        idioma= languages[0]
    id= get_serieId_by_title(title,idioma)
    if id>0:
        if languages is None:
            ret= get_graphics_by_serieId (id, bannerType, bannerType2, season)
        else:
            ret= get_graphics_by_serieId (id, bannerType, bannerType2, season, languages)
    return ret

def get_episode_by_seasonEpisode ( serieId, season, episode, idioma=""):
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
    
    if idioma=="": idioma= __idiomaDef__
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