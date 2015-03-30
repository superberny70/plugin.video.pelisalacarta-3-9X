# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Lista de vÃ­deos descargados
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os
import sys

from core import config
from core import logger
from core import samba
from core.item import Item
from core import downloadtools
from servers import servertools

CHANNELNAME = "descargas"
DEBUG = config.get_setting("debug")

DOWNLOAD_LIST_PATH = config.get_setting("downloadlistpath")
DOWNLOAD_PATH = config.get_setting("downloadpath")
ERROR_PATH = os.path.join( DOWNLOAD_PATH, 'error' )
IMAGES_PATH = os.path.join(config.get_runtime_path(), 'resources' , 'images')


if not DOWNLOAD_LIST_PATH.upper().startswith("SMB://"):
    if not os.path.exists(DOWNLOAD_LIST_PATH):
        os.mkdir(DOWNLOAD_LIST_PATH)
if not ERROR_PATH.upper().startswith("SMB://"):
    if not os.path.exists(ERROR_PATH):
        os.mkdir(ERROR_PATH)

def isGeneric():
    return True
    
def usingsamba(path):
    return path.upper().startswith("SMB://")
    
def mainlist(item):
    logger.info("[descargas.py] mainlist")
    itemlist=[]
    
    itemlist.append( Item( channel="descargas", action="pendientes", title="Descargas pendientes"))
    itemlist.append( Item( channel="descargas", action="errores", title="Descargas con error"))
    if usingsamba(DOWNLOAD_PATH):
        ficheros = samba.get_files(DOWNLOAD_PATH)
    else:
        ficheros = os.listdir(DOWNLOAD_PATH)
    for fichero in ficheros:
      url = os.path.join( DOWNLOAD_PATH , fichero )
      if not os.path.isdir(url) and not fichero.endswith(".nfo") and not fichero.endswith(".tbn"):
        itemlist.append( Item(channel="descargas", action="play", title=fichero, url=url, server="local", folder=False))

    return itemlist

def pendientes(item):
    logger.info("[descargas.py] pendientes")
    itemlist=[]
    if usingsamba(DOWNLOAD_LIST_PATH):
        ficheros = samba.get_files(DOWNLOAD_LIST_PATH)
    else:
        ficheros = os.listdir(DOWNLOAD_LIST_PATH)
    ficheros.sort()
    for fichero in ficheros:
      item = LeerDescarga(fichero,DOWNLOAD_LIST_PATH)
      itemlist.append(item)
      
    itemlist.append( Item( channel=CHANNELNAME , action="downloadall" , title="(Empezar la descarga de la lista)", thumbnail=os.path.join(IMAGES_PATH, "Crystal_Clear_action_db_update.png") , folder=False ))
    return itemlist

def errores(item):
    logger.info("[descargas.py] errores")
    itemlist=[]
    if usingsamba(ERROR_PATH):
        ficheros = samba.get_files(ERROR_PATH)
    else:
        ficheros = os.listdir(ERROR_PATH)
    ficheros.sort()
    for fichero in ficheros:
      item = LeerDescarga(fichero,ERROR_PATH)
      item.extra = extra=os.path.join(ERROR_PATH, fichero)
      itemlist.append(item)
    return itemlist

def downloadall(item):
    logger.info("[descargas.py] downloadall")

    if usingsamba(DOWNLOAD_LIST_PATH):
        ficheros = samba.get_files(DOWNLOAD_LIST_PATH)
    else:
        ficheros = os.listdir(DOWNLOAD_LIST_PATH)
    ficheros.sort()
    
    for fichero in ficheros:
        if fichero.endswith('.txt'):
            try:
                item = LeerDescarga(fichero,DOWNLOAD_LIST_PATH)
                video_urls,puedes,motivo = servertools.resolve_video_urls_for_playing(item.server,item.url,"",False)
                # La última es la de mayor calidad, lo mejor para la descarga
                mediaurl = video_urls[ len(video_urls)-1 ][1]

                # Genera el NFO
                nfofilepath = downloadtools.getfilefromtitle("sample.nfo",item.title)
                outfile = open(nfofilepath,"w")
                outfile.write("<movie>\n")
                outfile.write("<title>("+item.title+")</title>\n")
                outfile.write("<originaltitle></originaltitle>\n")
                outfile.write("<rating>0.000000</rating>\n")
                outfile.write("<year>2009</year>\n")
                outfile.write("<top250>0</top250>\n")
                outfile.write("<votes>0</votes>\n")
                outfile.write("<outline></outline>\n")
                outfile.write("<plot>"+item.plot+"</plot>\n")
                outfile.write("<tagline></tagline>\n")
                outfile.write("<runtime></runtime>\n")
                outfile.write("<thumb>"+item.thumbnail+"</thumb>\n")
                outfile.write("<mpaa>Not available</mpaa>\n")
                outfile.write("<playcount>0</playcount>\n")
                outfile.write("<watched>false</watched>\n")
                outfile.write("<id>tt0432337</id>\n")
                outfile.write("<filenameandpath></filenameandpath>\n")
                outfile.write("<trailer></trailer>\n")
                outfile.write("<genre></genre>\n")
                outfile.write("<credits></credits>\n")
                outfile.write("<director></director>\n")
                outfile.write("<actor>\n")
                outfile.write("<name></name>\n")
                outfile.write("<role></role>\n")
                outfile.write("</actor>\n")
                outfile.write("</movie>")
                outfile.flush()
                outfile.close()
                
                # Descarga el thumbnail
                if item.thumbnail != "":
                   thumbnailfile = downloadtools.getfilefromtitle(item.thumbnail,item.title)
                   thumbnailfile = thumbnailfile[:-4] + ".tbn"
                   try:
                       downloadtools.downloadfile(item.thumbnail,thumbnailfile)
                   except:
                       logger.info("[descargas.py] error al descargar thumbnail")
                       for line in sys.exc_info():
                           logger.error( "%s" % line )
                
                dev = downloadtools.downloadbest(video_urls,item.title)
                if dev == -1:
                    logger.info("[descargas.py] Descarga cancelada")
                    break
                elif dev == -2:
                    logger.info("[descargas.py] ERROR EN DESCARGA DE "+fichero)
                    BorrarDescarga(item, DOWNLOAD_LIST_PATH)
                    GuardarDescarga(item, ERROR_PATH)
                else:
                    BorrarDescarga(item, DOWNLOAD_LIST_PATH)
            except:
                logger.info("[descargas.py] ERROR EN DESCARGA DE "+fichero)
                import sys
                for line in sys.exc_info():
                    logger.error( "%s" % line )
                    GuardarDescarga(item,ERROR_PATH)
                    BorrarDescarga(item, DOWNLOAD_LIST_PATH)
    
    return ""  
                    
def LeerDescarga(Nombre, Ruta=DOWNLOAD_LIST_PATH):
    logger.info("[descargas.py] LeerDescarga")

    if usingsamba(Ruta):
        Archivo = samba.get_file_handle_for_reading(Nombre, Ruta)
    else:
        filepath = os.path.join( Ruta , Nombre )
        Archivo = open(filepath)
        
    lines = Archivo.readlines()
    Archivo.close();
    item = Item()
    item.deserialize(lines[0])
    
    return item

def GuardarDescarga(item, Ruta=DOWNLOAD_LIST_PATH):
    logger.info("[descargas.py] GuardarDescarga")
    if usingsamba(Ruta):
        ficheros = samba.get_files(Ruta)
    else:
        ficheros = os.listdir(Ruta)
    ficheros.sort()
    
    # Averigua el último número
    if len(ficheros)>0:
        # XRJ: Linea problemática, sustituida por el bucle siguiente
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
    logger.info("[descargas.py] GuardarDescarga filename="+fullfilename)
    
    # Genera el contenido
    if Ruta==DOWNLOAD_LIST_PATH: item.category="pendientes"
    if Ruta==ERROR_PATH: item.category="errores"
    item.channel="descargas"
    item.extra=fullfilename
    item.folder=False
    
    filecontent = item.serialize()

    # Graba el fichero
    if not usingsamba(Ruta):
        bookmarkfile = open(fullfilename.decode("utf-8"),"w")
        bookmarkfile.write(filecontent)
        bookmarkfile.flush();
        bookmarkfile.close()
    else:
        samba.write_file(filename, filecontent, Ruta)

def BorrarDescarga(item,Ruta=DOWNLOAD_LIST_PATH):
    logger.info("[descargas.py] BorrarDescarga")
    if not usingsamba(Ruta):
        os.remove(item.extra)
    else:
        fullfilename = item.extra.replace("\\","/")
        partes = fullfilename.split("/")
        filename = partes[len(partes)-1]
        samba.remove_file(filename,Ruta)
        
def delete_error_bookmark(item):
    BorrarDescarga(item,ERROR_PATH)

def mover_descarga_error_a_pendiente(item):
    item = LeerDescarga(item.extra.replace(DOWNLOAD_LIST_PATH,""),DOWNLOAD_LIST_PATH)
    BorrarDescarga(item,ERROR_PATH)
    GuardarDescarga(item)
    
