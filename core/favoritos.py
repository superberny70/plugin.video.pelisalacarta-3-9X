# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Lista de vídeos favoritos
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urllib
import os
import sys
import downloadtools
import config
import logger
import samba
from item import Item

CHANNELNAME = "favoritos"
DEBUG = config.get_setting("debug")
BOOKMARK_PATH = config.get_setting( "bookmarkpath" )

if not BOOKMARK_PATH.upper().startswith("SMB://"):
    if BOOKMARK_PATH=="":
        BOOKMARK_PATH = os.path.join( config.get_data_path() , "bookmarks" )
    if not os.path.exists(BOOKMARK_PATH):
        logger.debug("[favoritos.py] Path de bookmarks no existe, se crea: "+BOOKMARK_PATH)
        os.mkdir(BOOKMARK_PATH)

logger.info("[favoritos.py] path="+BOOKMARK_PATH)

def isGeneric():
    return True

def mainlist(item):
    logger.info("[favoritos.py] mainlist")
    itemlist=[]

    # Crea un listado con las entradas de favoritos
    if usingsamba(BOOKMARK_PATH):
        ficheros = samba.get_files(BOOKMARK_PATH)
    else:
        ficheros = os.listdir(BOOKMARK_PATH)
    ficheros.sort()
    
    # Rellena el listado
    for fichero in ficheros:
      itemlist.append(LeerFavorito(fichero))
    return itemlist

def LeerFavorito(Nombre,Ruta=BOOKMARK_PATH):
    logger.info("[favoritos.py] LeerFavorito")

    if usingsamba(Ruta):
        Archivo = samba.get_file_handle_for_reading(Nombre, Ruta)
    else:
        Archivo = open(os.path.join(Ruta, Nombre))
        
    lines = Archivo.readlines()
    Archivo.close();
    item = Item()
    item.deserialize(lines[0])
    
    return item

def GuardarFavorito(item, Ruta=BOOKMARK_PATH):
    logger.info("[favoritos.py] GuardarFavorito")

    # Lee todos los ficheros
    if usingsamba(Ruta):
        ficheros = samba.get_files(Ruta)
    else:
        ficheros = os.listdir(Ruta)
    ficheros.sort()
    
    # Averigua el ÃƒÂºltimo nÃƒÂºmero
    if len(ficheros)>0:
        # XRJ: Linea problemÃƒÂ¡tica, sustituida por el bucle siguiente
        #filenumber = int( ficheros[len(ficheros)-1][0:-4] )+1
        filenumber = 1
        for fichero in ficheros:
            logger.info("[favoritos.py] fichero="+fichero)
            try:
                tmpfilenumber = int( fichero[0:8] )+1
                if tmpfilenumber > filenumber:
                    filenumber = tmpfilenumber
            except:
                pass
    else:
        filenumber=1

    # Genera el nombre de fichero
    from core import scrapertools
    filename = '%08d-%s.txt' % (filenumber,scrapertools.slugify(item.title))
    fullfilename = os.path.join(Ruta,filename)
    logger.info("[favoritos.py] savebookmark filename="+filename)
    
    # Genera el contenido
    item.channel = "favoritos"
    item.extra = fullfilename
    filecontent = item.serialize()
    item.folder = False

    # Graba el fichero
    if not usingsamba(Ruta):
        bookmarkfile = open(fullfilename.decode("utf-8"),"w")
        bookmarkfile.write(filecontent)
        bookmarkfile.flush();
        bookmarkfile.close()
    else:
        samba.write_file(filename, filecontent, Ruta)

def BorrarFavorito(item,Ruta=BOOKMARK_PATH):
    logger.info("[favoritos.py] BorrarFavorito")

    if not usingsamba(Ruta):
        os.remove(item.extra)
    else:
        fullfilename = item.extra.replace("\\","/")
        partes = fullfilename.split("/")
        filename = partes[len(partes)-1]
        samba.remove_file(filename,Ruta)

def usingsamba(path):
    return path.upper().startswith("SMB://")
