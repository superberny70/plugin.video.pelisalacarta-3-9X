# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os
import sys
import xbmc,time

from core import scrapertools
from core import config
from core import logger
from core.item import Item
from servers import servertools

logger.info("[library_service.py] Actualizando series...")
import time
Inicio = time.time()

from platformcode.xbmc import library
from platformcode.xbmc import launcher
import xbmcgui
  
directorio = os.path.join(config.get_library_path(),"SERIES")
logger.info ("directorio="+directorio)

if not os.path.exists(directorio):
    os.mkdir(directorio)

nombre_fichero_config_canal = os.path.join( config.get_library_path() , "series.xml" )
if not os.path.exists(nombre_fichero_config_canal):
    nombre_fichero_config_canal = os.path.join( config.get_data_path() , "series.xml" )

try:

    if config.get_setting("updatelibrary")=="true":
        config_canal = open( nombre_fichero_config_canal , "r" )
        
        for serie in config_canal.readlines():
            logger.info("[library_service.py] serie="+serie)
            serie = serie.split("|")
        
            ruta = os.path.join( config.get_library_path() , "SERIES" , serie[0] )
            logger.info("[library_service.py] ruta =#"+ruta+"#")
            if os.path.exists( ruta ):
                logger.info("[library_service.py] Actualizando "+serie[0])
                item = Item(url=serie[1], show=serie[0])
                try:
                    itemlist = []
                    # Todos los canales que quieran actualizar sus series mediente este metodo
                    # han de tener una funcion llamada 'episodios(item)' que retorna el listado de capitulos
                    exec "import pelisalacarta.channels."+ serie[2].strip() +" as channel"
                    itemlist = channel.episodios(item)
                    library.AddCapitulos(itemlist)
                except:
                    import traceback
                    from pprint import pprint
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    lines = traceback.format_exception(exc_type, exc_value, exc_tb)
                    for line in lines:
                        line_splits = line.split("\n")
                        for line_split in line_splits:
                            logger.error(line_split)
                    itemlist = []
            else:
                logger.info("[library_service.py] No actualiza "+serie[0]+" (no existe el directorio)")
                itemlist=[]

            '''for item in itemlist:
                #logger.info("item="+item.tostring())
                try:
                    if item.action!="add_serie_to_library" and item.action!="download_all_episodes":
                        item.show=serie[0].strip()
                        item.category="Series"
                        item.action="play_from_library"
                        library.Guardar(item)
                except:
                    logger.info("[library_service.py] Capitulo no valido")'''

        import xbmc
        xbmc.executebuiltin('UpdateLibrary(video)')
    else:
        logger.info("No actualiza la biblioteca, está desactivado en la configuración de pelisalacarta")

except:
    logger.info("[library_service.py] No hay series para actualizar")

logger.info("[library_service.py] Tiempo empleado: " + str(time.time()-Inicio))