# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Configuración
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

from core import downloadtools
from core import config
from core import logger
from core.item import Item

def mainlist(item):
    logger.info("[configuracion.py] mainlist")
    if config.get_setting("enableadultmode") == "true":
        itemlist = []
        print config.get_thumbnail_path()
        itemlist.append( Item(title='Abrir configuración',channel='configuracion', action='open_settings', folder=False, thumbnail = config.get_thumbnail_path() + "configuracion.png"))
        itemlist.append( Item(title='Modificar contraseña para adultos',channel='', action='modificar_password', folder=False, thumbnail = config.get_thumbnail_path() + "configuracion.png"))
        return itemlist
    else:
        open_settings(None)
        
def open_settings(item):
    config.open_settings( )
