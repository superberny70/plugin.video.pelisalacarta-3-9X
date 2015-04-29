# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os,time,sys

import xbmcgui, xbmc

from core import scrapertools
from core import config
from core import logger
from core.item import Item
from servers import servertools
from platformcode.xbmc import library
from platformcode.xbmc import launcher


def actualizarSerie(serie):    
    logger.info("[library_service.py] serie="+serie)
    serie = serie.split("|")
    
    if multihilo:
        import threading
        #listahilos[threading.current_thread().name] ["serie"] =serie[0]
        msg= "[library_service.py] Actualizando "+serie[0]+" en hilo: "+ threading.current_thread().name
    else:
        msg= "[library_service.py] Actualizando "+serie[0]
    
    ruta = os.path.join( config.get_library_path() , "SERIES" , serie[0] )
    logger.info("[library_service.py] ruta =#"+ruta+"#")
    if os.path.exists( ruta ):
        logger.info(msg)
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
       



#############################################################
# Main                                                      #
#############################################################
logger.info("[library_service.py] Actualizando series...")
Inicio = time.time() 

try:
    if config.get_setting("updatelibrary")=="true":
        SERIES_PATH = os.path.join(config.get_library_path(), 'SERIES')
        if not os.path.exists(SERIES_PATH): os.mkdir(SERIES_PATH)
        
        nombre_fichero_listado_series = os.path.join( config.get_library_path() , "series.xml" )
        if not os.path.exists(nombre_fichero_listado_series):
            nombre_fichero_listado_series = os.path.join( config.get_data_path() , "series.xml" )
            
        fichero_listado_series = open( nombre_fichero_listado_series , "r" )

        multihilo= (config.get_setting("multithread") !='false' ) #Por defecto esta activado
        listahilos=[]
        for serie in fichero_listado_series.readlines():
            if multihilo:
                from threading import Thread
                Trd = Thread(target=actualizarSerie,args=[serie])
                listahilos.append(Trd)
                Trd.start()
            else:
                actualizarSerie(serie)

        if multihilo:
            #esperar a q todos los hilo acaben
            for hilo in listahilos:
                while hilo.isAlive():
                  time.sleep(0.5)

        import xbmc
        xbmc.executebuiltin('UpdateLibrary(video)')
    else:
        logger.info("No actualiza la biblioteca, está desactivado en la configuración de pelisalacarta")

except:
    logger.info("[library_service.py] No hay series para actualizar")

logger.info("[library_service.py] Tiempo empleado: " + str(time.time()-Inicio))