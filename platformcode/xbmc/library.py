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
  allchars = string.maketrans('', '')
  deletechars = '\\/:*"<>|?' #Caracteres no váidos en nombres de archivo
  return string.translate(nombre,allchars,deletechars)
    
     
def Guardar(item):
    logger.info("[library.py] Guardar")
    if item.category != "Series": item.category = "Cine"  
    if item.category == "Cine":
        Archivo = os.path.join(MOVIES_PATH, LimpiarNombre(item.title + ".strm"))
    elif item.category == "Series":
        if item.show == "": 
            CarpetaSerie = os.path.join(SERIES_PATH, "Serie_sin_titulo")
        else:
            CarpetaSerie = os.path.join(SERIES_PATH, LimpiarNombre(item.show))
        if not os.path.exists(CarpetaSerie.decode("utf8")): os.mkdir(CarpetaSerie.decode("utf8"))
        
        from  core import scrapertools
        Archivo = os.path.join(CarpetaSerie,scrapertools.get_season_and_episode(LimpiarNombre(item.title + ".strm")))  
  
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
    xbmcgui.Dialog().ok(config.get_localized_string(30101) , item.title , config.get_localized_string(30135)) # 'Se ha añadido a la Biblioteca'
    
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
