# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Herramientas de integraciÃ³n en LibrerÃ­a
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# Autor: jurrabi
#------------------------------------------------------------
import urllib
import os
import re
import sys
import string
from core import config
from core import logger
from core import downloadtools
from core import scrapertools
from core.item import Item
import xbmc
import xbmcgui

DEBUG = config.get_setting("debug")

__type__ = "generic"
__title__ = "Libreria"
__channel__ = "library"

logger.info("[library.py] init")
MOVIES_PATH = os.path.join(config.get_library_path(), 'CINE')
SERIES_PATH = os.path.join(config.get_library_path(), 'SERIES')

if not os.path.exists(config.get_library_path()): os.mkdir(config.get_library_path())
if not os.path.exists(MOVIES_PATH): os.mkdir(MOVIES_PATH)
if not os.path.exists(SERIES_PATH): os.mkdir(SERIES_PATH)

def isGeneric():
    return True

def LimpiarNombre(nombre):
  nombre=nombre.strip()
  allchars = string.maketrans('', '')
  deletechars = '\\/:*"<>|?' #Caracteres no váidos en nombres de archivo
  return string.translate(nombre,allchars,deletechars)
    
def GuardarSerie(itemlist):
    # Progreso
    pDialog = xbmcgui.DialogProgress()
    ret = pDialog.create('pelisalacarta', 'Añadiendo episodios...')
    pDialog.update(0, 'Añadiendo episodio...')
    totalepisodes = len(itemlist)
    i = 0
    for item in itemlist:
        i = i + 1
        pDialog.update(i*100/totalepisodes, 'Añadiendo episodio...',item.title)
        
        if (pDialog.iscanceled()):
            return
        if item.action!="add_serie_to_library" and item.action!="download_all_episodes": 
            item.category='Series'
            item.action= 'play_from_library'
            Guardar(item)      
    pDialog.close()
    
    #Lista con series para actualizar
    nombre_fichero_listado_series = os.path.join( config.get_library_path() , "series.xml" )
    if not os.path.exists(nombre_fichero_listado_series):
        nombre_fichero_listado_series = os.path.join( config.get_data_path() , "series.xml" )

    #logger.info("nombre_fichero_listado_series="+nombre_fichero_listado_series)
    fichero_listado_series= open(nombre_fichero_listado_series.decode("utf8") ,"a")
    fichero_listado_series.write(LimpiarNombre(item.show)+"|"+item.url+"|"+item.channel+"\n")
    fichero_listado_series.flush()
    fichero_listado_series.close()
    
    ActualizarBiblioteca(item)
    
def AddCapitulos(itemlist):
    #itemlist contiene todos los capitulos de una serie
    logger.info("[library.py] AddCapitulos")
    nuevos=0
    
    CarpetaSerie = os.path.join(SERIES_PATH, LimpiarNombre(itemlist[0].show))
    if os.path.exists(CarpetaSerie.decode("utf8")):
        #obtener los capitulos guardados 
        lista_capitulos= os.listdir(CarpetaSerie)
        lista_capitulos= [os.path.basename(c) for c in lista_capitulos if c.endswith('.strm')]
        
        #obtener capitulos disponibles y guardarlos si no lo estan ya
        for item in itemlist:
            if item.action!="add_serie_to_library" and item.action!="download_all_episodes":
                capitulo= scrapertools.get_season_and_episode(LimpiarNombre(item.title ))+ ".strm"
                if capitulo not in lista_capitulos:
                    item.category='Series'
                    item.action= 'play_from_library'
                    nuevos +=1
                    Guardar(item)            
    else:
        logger.info("[library.py] AddCapitulos Error: No existe el directorio " + CarpetaSerie)
    return nuevos
        
def Guardar(item):
    logger.info("[library.py] Guardar")
    
    if item.category == "Series":
        if item.show == "": 
            CarpetaSerie = os.path.join(SERIES_PATH, "Serie_sin_titulo")
        else:
            CarpetaSerie = os.path.join(SERIES_PATH, LimpiarNombre(item.show))
        if not os.path.exists(CarpetaSerie.decode("utf8")): os.mkdir(CarpetaSerie.decode("utf8"))
        
        Archivo = os.path.join(CarpetaSerie,scrapertools.get_season_and_episode(LimpiarNombre(item.title ))+ ".strm")  
    else: 
        category = "Cine"
        Archivo = os.path.join(MOVIES_PATH, LimpiarNombre(item.title) + ".strm")
        
    if item.action == "play": 
        item.channel="library"
        
    item.extra =Archivo
    logger.info("-----------------------------------------------------------------------")
    logger.info("Guardando en la Libreria: " + Archivo)
    logger.info(item.tostring())
    logger.info("-----------------------------------------------------------------------")
    
    
    LIBRARYfile = open(Archivo.decode("utf8") ,"w")
    from platformcode.xbmc import launcher
    LIBRARYfile.write(launcher.ConstruirURL(item))
    LIBRARYfile.flush()
    LIBRARYfile.close()
    return True

def Borrar(item):
  logger.info("[library.py] Borrar")
  logger.info("-----------------------------------------------------------------------")
  logger.info("Borrando de la Libreria: " + item.extra)
  logger.info(item.tostring())
  logger.info("-----------------------------------------------------------------------")

  os.remove(item.extra.decode("utf8"))
  xbmc.executebuiltin( "Container.Refresh" )

  
  
def ActualizarBiblioteca(item):
    logger.info("[library.py] ActualizarBiblioteca")
    # Pedir confirmación para actualizar la biblioteca
    if xbmcgui.Dialog().yesno('pelisalacarta','¿Deseas que actualice ahora la Biblioteca?'):
        logger.info("Actualizando biblioteca...")
        xbmc.executebuiltin('UpdateLibrary(video)')
    else:
        logger.info("No actualiza biblioteca...")
        
    return True
