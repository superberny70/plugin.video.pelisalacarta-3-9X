# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import sys

from core import config
from core import logger
from core.item import Item
from core import scrapertools
import channelselector
import os


DEBUG = config.get_setting("debug")

__type__ = "generic"
__title__ = "Buscador"
__channel__ = "buscador"

logger.info("[buscador.py] init")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[buscador.py] mainlist")
    itemlist =[]
    itemlist.append( Item(channel="buscador", action="search", title=config.get_localized_string(30103)+"...", thumbnail="http://pelisalacarta.mimediacenter.info/squares/search.png"))
    itemlist.append( Item(channel="buscador", action="MenuConfig", title="Configuración"))
    itemlist.extend(listar_busquedas())

    return itemlist
    
def MenuConfig(item):
    logger.info("[buscador.py] MenuConfig")
    itemlist =[]
    itemlist.append( Item(channel="buscador", action="Canales", title="Activar/Desactivar Canales"))
    itemlist.append( Item(channel="buscador", action="Reset", title="Resetear estadisticas"))
    if config.get_setting("buscador_resultados") =="0":
      itemlist.append( Item(channel="buscador", action="CambiarModo", title="Resultados: Todo junto"))
    else:
      itemlist.append( Item(channel="buscador", action="CambiarModo", title="Resultados: Por canales"))
    return itemlist

def search(item,tecleado):
    logger.info("[buscador.py] search "+tecleado)
    item.url=tecleado
    return por_tecleado(item)
    
def CambiarModo(item):
  itemlist=[]
  if config.get_setting("buscador_resultados") =="0":
    config.set_setting("buscador_resultados",'1')
    itemlist.append( Item(channel="launcher", action="refresh", title="Cambiado a: Por canales"))
  else:
    config.set_setting("buscador_resultados",'0')
    itemlist.append( Item(channel="launcher", action="refresh", title="Cambiado a: Todo junto"))


  return itemlist

def Canales(item):
    logger.info("[buscador.py] Canales")
    itemlist=[]
    Canales =  channelselector.listchannels(Item(category=""))
    Canales.remove(Canales[0])
    itemlist.append(Item(channel="buscador", action="ActivarTodos", title="Activar Todos"))
    itemlist.append(Item(channel="buscador", action="DesactivarTodos", title="Desactivar Todos"))
    for Canal in Canales:
      IndexConfig, ConfigCanales = ExtraerIndice(Canal.channel)  
      if ConfigCanales[IndexConfig].split(",")[1] == "1":
        Titulo = "[x] - " + Canal.title
      else:
        Titulo = "[  ] - " + Canal.title
        
      if ConfigCanales[IndexConfig].split(",")[2] <> "0":
        Titulo =("["+ "%05.2f" % float(float(ConfigCanales[IndexConfig].split(",")[3]) / float(ConfigCanales[IndexConfig].split(",")[2])) +" Seg] - ").replace(".", ",") + Titulo
      else:
        Titulo = "[00,00 Seg] - "+ Titulo 
      itemlist.append(Item(channel="buscador", action="ActivarDesactivar", title=Titulo, url=Canal.channel))

    return itemlist
    
def Reset(item):
    logger.info("[buscador.py] Reset")
    itemlist=[]
    ConfigCanales = []
    if config.get_setting("canales_buscador"):
      ConfigCanales.extend(config.get_setting("canales_buscador").split("|"))
      IndexConfig = -1
      for x, Config in enumerate(ConfigCanales):
        ConfigCanales[x] = ConfigCanales[x].split(",")[0] + "," + ConfigCanales[x].split(",")[1] + "," +"0" + "," +"0"
      config.set_setting("canales_buscador",'|'.join(ConfigCanales))
    
    itemlist.append( Item(channel="launcher", action="alert", title="Estadisticas reseteadas"))
    return itemlist

def ExtraerIndice(Canal):
    logger.info("[buscador.py] ExtraerIndice")
    ConfigCanales = []
    if config.get_setting("canales_buscador"):
      ConfigCanales.extend(config.get_setting("canales_buscador").split("|"))
    IndexConfig = -1
    for x, Config in enumerate(ConfigCanales):
      if Canal in Config:
        IndexConfig = x
        break
    if IndexConfig == -1: 
      logger.info("[buscador.py] EstraerIndice Creando configuración para: "+ Canal)
      ConfigCanales.append(Canal + "," + "1" + "," + "0" + "," + "0")
      config.set_setting("canales_buscador",'|'.join(ConfigCanales))
      IndexConfig = len(ConfigCanales) - 1

    return IndexConfig, ConfigCanales
    
def ActivarDesactivar(item):
    logger.info("[buscador.py] ActivarDesactivar")
    IndexConfig, ConfigCanales = ExtraerIndice(item.url)
    Activo = ConfigCanales[IndexConfig].split(",")[1]
    if Activo == "1":
      Activo ="0"
    else:
      Activo ="1"  
    ConfigCanales[IndexConfig] =  ConfigCanales[IndexConfig].split(",")[0] +","+ Activo+"," + ConfigCanales[IndexConfig].split(",")[2]+"," + ConfigCanales[IndexConfig].split(",")[3]
    config.set_setting("canales_buscador",'|'.join(ConfigCanales))
    itemlist=[]
    if Activo =="1":
      itemlist.append( Item(channel="launcher", action="refresh", title="Canal activado"))
    else:
      itemlist.append( Item(channel="launcher", action="refresh", title="Canal desactivado"))
    return itemlist
    
def ActivarTodos(item):
    logger.info("[buscador.py] ActivarTodos")
    itemlist=[]
    ConfigCanales = []
    if config.get_setting("canales_buscador"):
      ConfigCanales.extend(config.get_setting("canales_buscador").split("|"))
      
    for x, Config in enumerate(ConfigCanales):
      ConfigCanales[x] =  ConfigCanales[x].split(",")[0] +","+ "1" +"," + ConfigCanales[x].split(",")[2]+"," + ConfigCanales[x].split(",")[3]
    config.set_setting("canales_buscador",'|'.join(ConfigCanales))
    itemlist.append( Item(channel="launcher", action="refresh", title="Canales Activados"))
    return itemlist

def DesactivarTodos(item):
    logger.info("[buscador.py] DesactivarTodos")
    itemlist=[]
    ConfigCanales = []
    if config.get_setting("canales_buscador"):
      ConfigCanales.extend(config.get_setting("canales_buscador").split("|"))
      
    for x, Config in enumerate(ConfigCanales):
      ConfigCanales[x] =  ConfigCanales[x].split(",")[0] +","+ "0" +"," + ConfigCanales[x].split(",")[2]+"," + ConfigCanales[x].split(",")[3]
    config.set_setting("canales_buscador",'|'.join(ConfigCanales))
    itemlist.append( Item(channel="launcher", action="refresh", title="Canales Activados"))
    return itemlist
    
def GuardarTiempo(Canal,Tiempo):
    logger.info("[buscador.py] GuardarTiempo")
    if not config.get_setting("canales_buscador"): Canales(Item())
    ConfigCanales = config.get_setting("canales_buscador").split("|")
    for x, Config in enumerate(ConfigCanales):
      if Canal in Config:
        IndexConfig = x
        break
    Busquedas = int(ConfigCanales[x].split(",")[2]) + 1
    Tiempos = float(ConfigCanales[x].split(",")[3]) + Tiempo
    ConfigCanales[x] =  ConfigCanales[x].split(",")[0] +","+ ConfigCanales[x].split(",")[1]+"," + str(Busquedas)+"," + str(Tiempos)
    config.set_setting("canales_buscador",'|'.join(ConfigCanales))

def por_tecleado(item):
    import time
    logger.info("[buscador.py] por_tecleado")
    tecleado =item.url
    itemlist = []
    salvar_busquedas(item)
    channels =  channelselector.listchannels(Item(category=""))
    channels.remove(channels[0])
    for channel in channels:
      IndexConfig, ConfigCanales = ExtraerIndice(channel.channel)  
      if ConfigCanales[IndexConfig].split(",")[1] == "1":
        Inicio = time.time()
        itemlist.extend(buscar(channel, tecleado))
        GuardarTiempo(channel.channel, time.time()-Inicio)
    itemlist.sort(key=lambda item: item.title.lower().strip())

    return itemlist
    
def buscar(modulo, texto):
    logger.info("Lanzando búseda en: "+ modulo.channel)
    ListaCanales = []
    try:
      exec "from pelisalacarta.channels import "+modulo.channel+" as channel"
      mainlist_itemlist = channel.mainlist(Item())
      for item in mainlist_itemlist:
          if item.action =="search":
            url = item.url
            itemlist = []
            itemlist.extend(channel.search(item, texto))
            if config.get_setting("buscador_resultados") =="1":
              if len(itemlist)>0:  
                cantidad = str(len(itemlist))
                if len(itemlist) >1:
                  if itemlist[len(itemlist)-1].action <> itemlist[len(itemlist)-2].action:
                    cantidad = str(len(itemlist)) + "+"
                ListaCanales.append( Item(channel=__channel__ , action='buscar_canal', url=modulo.channel +"{}"+ url +"{}"+ texto, title=modulo.title + " (" + cantidad + ")" ))
            else:
              
              if len(itemlist) >1:
                if itemlist[len(itemlist)-1].action <> itemlist[len(itemlist)-2].action:
                    itemlist.remove(itemlist[len(itemlist)-1])
              ListaCanales.extend(itemlist)
              
    except:
      logger.info("No se puede buscar en: "+ modulo.channel)  
    return  ListaCanales
    
def buscar_canal(item):
    itemlist = []
    logger.info("[buscador.py] buscar_canal")
    exec "from pelisalacarta.channels import "+item.url.split("{}")[0]
    exec "itemlist.extend("+item.url.split("{}")[0]+".search(Item(url=item.url.split('{}')[1]), item.url.split('{}')[2]))"

    return itemlist
    
def salvar_busquedas(item):
    logger.info("[buscador.py] salvar_busquedas")
    limite_busquedas =int(config.get_setting( "limite_busquedas" ))
    presets = config.get_setting("presets_buscados").split("|")
    logger.info(len(presets))
    if item.url in presets: presets.remove(item.url) 
    presets.insert(0,item.url)     
    if limite_busquedas>0:
          presets = presets[:limite_busquedas]
    config.set_setting("presets_buscados",'|'.join(presets))
        
def listar_busquedas():
    logger.info("[buscador.py] listar_busquedas")
    itemlist=[]
    presets = config.get_setting("presets_buscados").split("|")
    for preset in presets:
        if preset <> "": itemlist.append( Item(channel=__channel__ , context="Borrar,borrar_busqueda", action="por_tecleado", title="- " + preset ,  url=preset))       
    return itemlist
    
def borrar_busqueda(item):
    logger.info("[buscador.py] borrar_busqueda")
    itemlist = []
    presets = config.get_setting("presets_buscados").split("|")
    presets.remove(item.url)
    config.set_setting("presets_buscados",'|'.join(presets))
    itemlist.append( Item(channel="launcher", action="refresh", title="Registro borrado"))
    return itemlist