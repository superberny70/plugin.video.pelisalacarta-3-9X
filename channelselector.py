# -*- coding: utf-8 -*-
import urlparse,urllib2,urllib,re
import os, sys
import json

from core import config
from core import logger
from core import scrapertools
from core import updater
from core.item import Item

__channel__ = "channelselector"

PATH_LIST_CHANNELS_JSON= os.path.join( config.get_data_path() , "list_channels.json" )

def mainlist(item):
    logger.info("channelselector.mainlist")

    # Obtiene el idioma, y el literal
    idioma = config.get_setting("languagefilter")
    logger.info("channelselector.mainlist idioma=%s" % idioma)
    langlistv = [config.get_localized_string(30025),config.get_localized_string(30026),config.get_localized_string(30027),config.get_localized_string(30028),config.get_localized_string(30029)]
    try:
        idiomav = langlistv[int(idioma)]
    except:
        idiomav = langlistv[0]
   
    # Añade los canales que forman el menú principal
    itemlist = []
    itemlist.append( Item(title=config.get_localized_string(30118)+" ("+idiomav+")" , channel="channelselector" , action="listchannels", category='*', thumbnail = urlparse.urljoin(config.get_thumbnail_path(),"channelselector.png") ) ) # Canales
    itemlist.append( Item(title=config.get_localized_string(30119)+" ("+idiomav+")" , channel="channelselector" , action="channeltypes", thumbnail = urlparse.urljoin(config.get_thumbnail_path(),"channelselector.png") ) ) # Seleccione una categoria
    itemlist.append( Item(title=config.get_localized_string(30103) , channel="buscador" , action="mainlist" , thumbnail = urlparse.urljoin(config.get_thumbnail_path(),"buscador.png")) )
    itemlist.append( Item(title=config.get_localized_string(30128) , channel="trailertools" , action="mainlist" , thumbnail = urlparse.urljoin(config.get_thumbnail_path(),"trailertools.png")) )
    itemlist.append( Item(title=config.get_localized_string(30102) , channel="favoritos" , action="mainlist" , thumbnail = urlparse.urljoin(config.get_thumbnail_path(),"favoritos.png")) )
    if config.get_platform() in ("wiimc","rss") :itemlist.append( Item(title="Wiideoteca (Beta)" , channel="wiideoteca" , action="mainlist", thumbnail = urlparse.urljoin(config.get_thumbnail_path(),"wiideoteca.png")) )
    if config.get_platform()=="rss":itemlist.append( Item(title="pyLOAD (Beta)" , channel="pyload" , action="mainlist" , thumbnail = urlparse.urljoin(config.get_thumbnail_path(),"pyload.png")) )
    itemlist.append( Item(title=config.get_localized_string(30101) , channel="descargas" , action="mainlist", thumbnail = urlparse.urljoin(config.get_thumbnail_path(),"descargas.png")) )
    
    if "xbmceden" in config.get_platform():
        itemlist.append( Item(title=config.get_localized_string(30100) , channel="configuracion" , action="mainlist", thumbnail = urlparse.urljoin(config.get_thumbnail_path(),"configuracion.png"), folder=False) )
    else:
        itemlist.append( Item(title=config.get_localized_string(30100) , channel="configuracion" , action="mainlist", thumbnail = urlparse.urljoin(config.get_thumbnail_path(),"configuracion.png")) )

    if config.get_platform()!="rss": itemlist.append( Item(title=config.get_localized_string(30104) , channel="ayuda" , action="mainlist", thumbnail = urlparse.urljoin(config.get_thumbnail_path(),"ayuda.png")) )
     
    return itemlist
  
def channeltypes(item):
    logger.info("channelselector.channeltypes")
       
    itemlist = []
    itemlist.append( Item( title=config.get_localized_string(30121) , channel="channelselector" , action="listchannels" , category="*"   , thumbnail=urlparse.urljoin(config.get_thumbnail_path(),"channelselector")))
    itemlist.append( Item( title=config.get_localized_string(30122) , channel="channelselector" , action="listchannels" , category="F"   , thumbnail=urlparse.urljoin(config.get_thumbnail_path(),"peliculas")))
    itemlist.append( Item( title=config.get_localized_string(30123) , channel="channelselector" , action="listchannels" , category="S"   , thumbnail=urlparse.urljoin(config.get_thumbnail_path(),"series")))
    itemlist.append( Item( title=config.get_localized_string(30124) , channel="channelselector" , action="listchannels" , category="A"   , thumbnail=urlparse.urljoin(config.get_thumbnail_path(),"anime")))
    itemlist.append( Item( title=config.get_localized_string(30125) , channel="channelselector" , action="listchannels" , category="D"   , thumbnail=urlparse.urljoin(config.get_thumbnail_path(),"documentales")))
    itemlist.append( Item( title=config.get_localized_string(30136) , channel="channelselector" , action="listchannels" , category="VOS" , thumbnail=urlparse.urljoin(config.get_thumbnail_path(),"versionoriginal")))
    itemlist.append( Item( title=config.get_localized_string(30126) , channel="channelselector" , action="listchannels" , category="M"   , thumbnail=urlparse.urljoin(config.get_thumbnail_path(),"musica")))
    itemlist.append( Item( title=config.get_localized_string(30127) , channel="channelselector" , action="listchannels" , category="G"   , thumbnail=urlparse.urljoin(config.get_thumbnail_path(),"servidores")))
    #itemlist.append( Item( title=config.get_localized_string(30134) , channel="channelselector" , action="listchannels" , category="NEW" , thumbnail=urlparse.urljoin(config.get_thumbnail_path(),"novedades")))
        
    return itemlist
        
def listchannels(item):
    logger.info("channelselector.listchannels") 
    itemlist = channels_list(item.category)
    return itemlist
       
def channels_history_list():
    itemlist = []
    return itemlist

def channels_list(category='*'):
    langlistv = ["","ES","EN","IT","PT"] # Esto no me gusta mucho
    idioma = langlistv[int(config.get_setting("languagefilter"))]
    
    itemlist = []
    if category=='*': 
        itemlist.append( Item( viewmode="movie", title="Tengo una URL", channel="tengourl", action='mainlist',language="", category="F,S,D,A", type="generic"))
    if config.get_setting("personalchannel")=="true":
        itemlist.append( Item( title=config.get_setting("personalchannelname"), channel="personal", action='mainlist', language="", category="*", type="generic",thumbnail= config.get_setting("personalchannellogo")))
    if config.get_setting("personalchannel2")=="true":
        itemlist.append( Item( title=config.get_setting("personalchannelname2"), channel="personal2", action='mainlist', language="", category="*", type="generic",thumbnail=config.get_setting("personalchannellogo2")))
    if config.get_setting("personalchannel3")=="true":
        itemlist.append( Item( title=config.get_setting("personalchannelname3"), channel="personal3", action='mainlist', language="", category="*", type="generic",thumbnail=config.get_setting("personalchannellogo3")))
    if config.get_setting("personalchannel4")=="true":
        itemlist.append( Item( title=config.get_setting("personalchannelname4"), channel="personal4", action='mainlist', language="", category="*", type="generic", thumbnail=config.get_setting("personalchannellogo4")))
    if config.get_setting("personalchannel5")=="true":
        itemlist.append( Item( title=config.get_setting("personalchannelname5"), channel="personal5", action='mainlist', language="", category="*", type="generic", thumbnail=config.get_setting("personalchannellogo5")))
    
    if os.path.exists(PATH_LIST_CHANNELS_JSON): # Si existe list_channels.json lo abrimos...
        indice_canales= json.load(open(PATH_LIST_CHANNELS_JSON))
    else: # Si no existe list_channels.json lo creamos
        indice_canales= updater.comparar_canales()
        
    for channel in sorted(indice_canales):
        
        # Control parental
        if config.get_setting("enableadultmode") == "false" and indice_canales[channel]['adult']=='true': continue 
        
        # Canales especiales (personal.py, libreria.py, etc..)
        if indice_canales[channel]['title']=='' or not(indice_canales[channel]['type'] == "generic" or indice_canales[channel]['type'] == "xbmc"): continue
        
        # Filtrado por categoria y añadimos plot
        categoria= indice_canales[channel]['category'].encode('utf8')
        if category<>"*" and category not in categoria: continue
        plot = categoria.replace("VOS","Versión original subtitulada").replace("F","Películas").replace("S","Series").replace("D","Documentales").replace("A","Anime").replace(",",", ")
        
        # Filtrado por idioma
        if indice_canales[channel]['language'] !='' and idioma !="" and idioma not in indice_canales[channel]['language']: continue
        
        # Añadimos el thumbnail
        thumbnail= indice_canales[channel]['thumbnail']
        if thumbnail=='':
            thumbnail=urlparse.urljoin(config.get_thumbnail_path(),indice_canales[channel]['channel'] +".png")
        
        itemlist.append(Item(title= indice_canales[channel]['title'].encode('utf8'), channel=indice_canales[channel]['channel'].encode('utf8'), action='mainlist', language=indice_canales[channel]['language'], category=categoria, type=indice_canales[channel]['type'], thumbnail= thumbnail, plot=plot)) 
        #logger.info("[channelselector] channel: " + str(channel))
    return itemlist

