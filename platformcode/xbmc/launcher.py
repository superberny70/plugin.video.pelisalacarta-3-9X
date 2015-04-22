# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta
# XBMC Launcher (xbmc / xbmc-dharma / boxee)
# http://blog.tvalacarta.info/plugin-xbmc/
#------------------------------------------------------------

#Imports:
import urllib, urllib2
import os,sys
import base64
from core import logger
from core import config
from core import scrapertools
from core.item import Item
from core import updater
import xbmcgui
import xbmcplugin
import xbmc
import channelselector as channelselector
from platformcode.xbmc import library


#Funcion principal.----------->OK
def run():
    logger.info("[launcher.py] run")
    config.verify_directories_created()
    itemlist=[]
    item = ExtraerItem()
    logger.info("-----------------------------------------------------------------------")
    logger.info("Item Recibido: " + item.tostring())
    logger.info("-----------------------------------------------------------------------")
    itemlist = EjecutarFuncion(item)
    # Mostrar los resultados, si los hay
    if type(itemlist)==list:  #Utilizado para no devolver ningun Item en funciones que no tienen que devolver nada (p.e play)
      MostrarResultado(itemlist, item)
      
      

#Sección encargada de recoger el Item y ejecutar su accion:----------->OK
def EjecutarFuncion(item):
    logger.info("[launcher.py] EjecutarFuncion")
    logger.info("-----------------------------------------------------------------------")
    logger.info("EjecutarFuncion: Canal=" + item.channel + " Acción=" + item.action)    
    logger.info("-----------------------------------------------------------------------")
    itemlist = []

    #Si la acción es mainlist comprueba si hay actualizaciónes para el canal antes de cargarlo.
    if item.action == "mainlist":
        if item.channel=="channelselector":
            '''
            Esta advertencia es solo para la version beta
            '''
            dialog = xbmcgui.Dialog()
            dialog.ok(u'Atención',u'Esta es una versión no oficial de pelisalacarta de uso exclusivo para desarrolladores.',
                u'Puede descargar la versión oficial en http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/')
            
            if config.get_setting("updatecheck2")=="true": 
                itemlist.extend(ActualizarPlugin())
            if config.get_setting("updatechannels")=="true" and len(itemlist)==0: # Si hay una nueva version del plugin no actualizar canales
                itemlist.append(ActualizarCanal(item.channel,config.get_localized_string(30064)))
                itemlist.append(ActualizarServers())
                updater.sincronizar_canales()
        elif config.get_setting("updatechannels")=="true": 
            itemlist.append(ActualizarCanal(item.channel,"¡Canal descargado y actualizado!"))
        

    # Importa el canal
    if item.channel: channelmodule = ImportarCanal(item.channel)
    
#######################################################################
#        Aqui se ejecuta cada función segun el canal                  #
#  si no se cumple ninguna condición se ejecuta la funcion generica:  #
#               itemlist = canal.accion(item)                         #
#######################################################################

    
    #Si no hay canal, ejecuta la función dentro de este launcher
    if item.channel=="":
      exec "itemlist = "+item.action+"(item)"
    
    else:
      # play - es el menú de reproducción de un vídeo
      if item.action=="play":
          logger.info("ACCION PLAY")
          if hasattr(channelmodule, 'play'):
              logger.info("[launcher.py] executing channel 'play' method")
              logger.info(channelmodule.__file__)
              itemlist = channelmodule.play(item)
          else:
              logger.info("[launcher.py] no channel 'play' method, executing core method")
              itemlist.append(item)
              
          if len(itemlist)>0:
              itemlist = play(itemlist[0])

      # search - es para abrir el teclado y enviar el texto
      elif item.action=="search":
          logger.info("ACCION SEARCH")
          keyboard = xbmc.Keyboard("")
          keyboard.doModal()
          if (keyboard.isConfirmed()):
              tecleado = keyboard.getText()
              itemlist = channelmodule.search(item,tecleado)
          else:
              itemlist = []

      # Todas las demas Funciones
      else:
          #Si existe la funcion en el canal la ejecuta
          if hasattr(channelmodule, item.action):
              logger.info("[launcher.py] - Ejectuando accion: " + item.channel + "." + item.action + "(item)")
              exec "itemlist = channelmodule." + item.action + "(item)"
          #Si existe la funcion en el launcher la ejecuta
          elif hasattr(sys.modules[__name__], item.action):
              logger.info("[launcher.py] - Ejectuando accion: " + item.action + "(item)")
              exec "itemlist =" + item.action + "(item)"
          #Si no existe devuelve un error
          else:
              logger.info("[launcher.py] - No se ha encontrado la accion ["+ item.action + "] en el canal ["+item.channel+"] ni en el launcher")
 
    #Si no es una lista lo convierte a un string, para que no se muestre en pantalla ni de error por ser NoneType         
    if not type(itemlist)==list: itemlist=""
    
    #Aplicar varias modificaciones a los resultados (fanarts, menus contextuales predefinidos, etc...)
    for x, item in enumerate(itemlist):
      if item.show:
          if itemlist[x].context:
            itemlist[x].context= itemlist[x].context + "|Añadir esta serie a la biblioteca,add_serie_to_library|Descargar todos los episodios de la serie,download_all_episodes"
          else:
            itemlist[x].context="Añadir esta serie a la biblioteca,add_serie_to_library|Descargar todos los episodios de la serie,download_all_episodes"
          itemlist[x].refered_action=item.action
      if item.action=="play" or item.action =="findvideos":
          if itemlist[x].context:
            itemlist[x].context= itemlist[x].context + "|Buscar Trailer,search_trailer"
          else:
            itemlist[x].context="Buscar Trailer,search_trailer"

      if item.fanart=="":
        channel_fanart = os.path.join( config.get_runtime_path(), 'resources', 'images', 'fanart', item.channel+'.jpg')
        if os.path.exists(channel_fanart):
            item.fanart = channel_fanart
        else:
            item.fanart = os.path.join(config.get_runtime_path(),"fanart.jpg")

    logger.info("[launcher.py] - EjecutarFuncion - Items devueltos")  
    logger.info("-----------------------------------------------------------------------")
    for item in itemlist:
      logger.info(item.tostring())
    logger.info("-----------------------------------------------------------------------")
    
    return itemlist


# Funcion para Mostrar los resultados en XBMC:----------->OK
def MostrarResultado(itemlist, refereditem):
    logger.info("[launcher.py] - MostrarResultado")# + str(sys.argv))
    
    Mostrar = True    
    for item in itemlist:
      #Funciones para "launcher", si un Item tiene función "launcher" no muestra los items, sino que ejecuta dicha funcion
      if item.channel=="launcher":
        Mostrar = False
        if item.action=="refresh":
          xbmc.executebuiltin( "Container.Refresh" )
        if item.action=="alert":
          xbmcgui.Dialog().ok(refereditem.title,item.title)
        itemlist.remove(item)
      else:
        Mostrar = True
        AddItem(item, len(itemlist))
    
    if Mostrar:         
      xbmcplugin.endOfDirectory( handle=int(sys.argv[1]), succeeded=True )
      if config.get_setting("forceview")=="true":
        if refereditem.viewmode=="list":
            xbmc.executebuiltin("Container.SetViewMode(50)")
        elif refereditem.viewmode=="movie_with_plot":
            xbmc.executebuiltin("Container.SetViewMode(503)")
        elif refereditem.viewmode=="movie":
            xbmc.executebuiltin("Container.SetViewMode(500)")


#Funcion especifica para importar el canal:----------->OK
def ImportarCanal(channel):
  channelmodule=""
  if os.path.exists(os.path.join( config.get_runtime_path(),"pelisalacarta","channels",channel+".py")):
    exec "from pelisalacarta.channels import "+channel+" as channelmodule"
  elif os.path.exists(os.path.join( config.get_runtime_path(),"pelisalacarta",channel+".py")):
    exec "from pelisalacarta import "+channel+" as channelmodule"
  elif os.path.exists(os.path.join( config.get_runtime_path(),"core",channel+".py")):
    exec "from core import "+channel+" as channelmodule"
  elif os.path.exists(os.path.join( config.get_runtime_path(),channel+".py")):
    exec "import "+channel+" as channelmodule"
  return channelmodule


#Sección encargada de comprobar la actualizacion de un canal:----------->OK
def ActualizarCanal(channel, Texto="Actualizado con exíto"):
  itemlist=[]
  try:
    logger.info("Verificando actualización de: " + channel)
    actualizado = updater.updatechannel(channel)
    if actualizado:
        itemlist.append(Item(channel="launcher", action="alert", title=Texto))
  except:
      import sys
      for line in sys.exc_info():
          logger.error( "%s" % line )
  return itemlist

#Sección encargada de comprobar las actualizaciones del plugin:----------->OK
def ActualizarPlugin():
  itemlist = []
  logger.info("[launcher.py] - ActualizarPlugin")
  try:
      itemlist.extend(updater.checkforupdates())
  except:
      xbmcgui.Dialog().ok("No se puede conectar","No ha sido posible comprobar","si hay actualizaciones")
      logger.info("[launcher.py] - ActualizarPlugin: Fallo al verificar la actualización")
      pass

  return itemlist

#Sección encargada de comprobar las actualizaciones de los servers/conectores:----------->OK
def ActualizarServers(Texto="Servidores actualizados con exíto"):
  itemlist=[]
  try:
    logger.info("Verificando actualización de conectores" )
    actualizado = updater.updaterservers()
    if actualizado:
      itemlist.append(Item(channel="launcher",action="alert", title=Texto))
  except:
      import sys
      for line in sys.exc_info():
          logger.error( "%s" % line )
  return itemlist


#Seccion encargada de añadir un Item al Listitem:----------->OK
def AddItem(item, totalitems):
    #logger.info("[launcher.py] - AddItem " + str(sys.argv))
    titulo = item.title
    import time   
    if item.duration:
      if item.duration > 3599: 
        Tiempo = time.strftime("%H:%M:%S", time.gmtime(item.duration))
      else:
        Tiempo= time.strftime("%M:%S", time.gmtime(item.duration))
    if item.action <> "mainlist":
      if config.get_setting("duracionentitulo")<>"true" and item.duration: titulo = titulo + " (" + Tiempo + ")"
      if config.get_setting("calidadentitulo")<>"true" and item.quality: titulo = titulo + " [" + item.quality + "]"   
      if config.get_setting("idiomaentitulo")<>"true" and item.language: titulo = titulo + " [" + item.language + "]"

    listitem = xbmcgui.ListItem( titulo, iconImage="DefaultFolder.png", thumbnailImage=item.thumbnail)
    listitem.setInfo( "video", { "Title" : item.title, "Plot" : item.plot, "Studio" : item.channel } )

    if item.fanart!="":
        listitem.setProperty('fanart_image',item.fanart) 
        xbmcplugin.setPluginFanart(int(sys.argv[1]), item.fanart)
        
        
    if "," in item.context:
      contextCommands=[]
      for menuitem in item.context.split("|"):
        if "," in menuitem:
          from copy import deepcopy
          Menu = deepcopy(item)
          if len(menuitem.split(",")) == 2:
            Titulo = menuitem.split(",")[0]
            Menu.action = menuitem.split(",")[1]
          elif len(menuitem.split(",")) == 3:
            Titulo = menuitem.split(",")[0]
            Menu.channel = menuitem.split(",")[1]
            Menu.action =menuitem.split(",")[2]
          contextCommands.append((Titulo,"XBMC.RunPlugin("+ConstruirURL(Menu)+")"))
      if len(contextCommands)>0:
        listitem.addContextMenuItems ( contextCommands, replaceItems=False)
        
    if item.folder:
      xbmcplugin.addDirectoryItem( handle = int(sys.argv[1]), url = ConstruirURL(item) , listitem=listitem, isFolder=True, totalItems=totalitems)
    else:
      if config.get_setting("player_mode")=="1": # SetResolvedUrl debe ser siempre "isPlayable = true"
        listitem.setProperty('IsPlayable', 'true')
      xbmcplugin.addDirectoryItem( handle = int(sys.argv[1]), url = ConstruirURL(item) , listitem=listitem, isFolder=False, totalItems=totalitems)

# Crea le url con el item serializado:----------->OK
def ConstruirURL(item):
  itemurl = sys.argv[ 0 ] + "?" + item.serialize()
  return itemurl


# Extrae el Item del los parametros de XBMC:----------->OK 
def ExtraerItem():
    logger.info("[launcher.py] - ExtraerItem")
    item = Item()
    itemserializado = sys.argv[2].replace("?","")
    if itemserializado:
      item.deserialize(itemserializado)
    else:
      item = Item(channel="channelselector", action="mainlist")
    return item
   
   
#Función findvideos generica:----------->OK
def findvideos(item):
    logger.info("findvideos")
    from core import scrapertools
    from servers import servertools
    from servers import longurl
    import copy
    data = scrapertools.cache_page(item.url)
    data=longurl.get_long_urls(data)  
    listavideos = servertools.findvideos(data)  
    itemlist = []
    for video in listavideos:
        NuevoItem = copy.deepcopy(item)
        NuevoItem.fulltitle = item.title
        NuevoItem.title = item.title + " - [" + video[2] + "]"
        NuevoItem.url = video[1]
        NuevoItem.server = video[2]
        NuevoItem.action = "play"
        NuevoItem.folder=False
        itemlist.append(NuevoItem)
    if len(itemlist)==1:
      itemlist = play(itemlist[0])

    return itemlist


#Función para el menú de reproduccion:----------->OK
def play(item):
  itemlist = MenuVideo(item)
  Resultado = MostrarMenuVideo(item,itemlist)
  if Resultado <> -1:
    exec itemlist[Resultado].action+"(item, itemlist[Resultado])"
  else:
    listitem = xbmcgui.ListItem( item.title, iconImage="DefaultVideo.png", thumbnailImage=item.thumbnail)
    xbmcplugin.setResolvedUrl(int(sys.argv[ 1 ]),False,listitem)    # JUR Added


#Función para añadir una serie a la Libreria:----------->OK
def add_serie_to_library(item):
  channelmodule = ImportarCanal(item.channel)
  if item.extra: 
    action = item.extra
  elif item.refered_action: 
    action = item.refered_action
  if "###" in action:
    item.extra = action.split("###")[1]
    action = action.split("###")[0]
  
  exec "itemlist = channelmodule."+action+"(item)"
  library.GuardarSerie (itemlist)
  '''
  for item in itemlist:
    if item.action!="add_serie_to_library" and item.action!="download_all_episodes":
        item.category='Series'
        library.Guardar(item)
  library.ActualizarBiblioteca(item)   '''



#Función para descargar todos los episodios de una serie:----------->OK
def download_all_episodes(item):
    from servers import servertools
    from core import downloadtools
    from core import scrapertools

    # Esto es poco elegante...
    # Esta marca es porque el item tiene algo más aparte en el atributo "extra"
    if item.extra: action = item.extra
    if item.refered_action: action = item.refered_action
    if "###" in item.extra:
      action = item.extra.split("###")[0]
      item.extra = item.extra.split("###")[1]
    else:
      action = item.extra
      
    #Importamos el canal    
    channel = ImportarCanal(item.channel)
    
    #Ejecutamos la funcion
    exec "itemlist = channel."+action+"(item)"
    
    #Quitamos estos dos elementos de la lista (si los hay)
    for episodio in itemlist:
      if episodio.action=="add_serie_to_library" or episodio.action=="download_all_episodes":
        itemlist.remove(episodio)
    

    #Abrimos el dialogo
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('pelisalacarta', 'Descargando ' + item.show)
    
    for x, episodio in enumerate(itemlist):
    
      #Si se presiona cancelar, se cancela
      if pDialog.iscanceled():
        return
      #Extraemos la Temporada y el Episodio  
      episodio.title = scrapertools.get_season_and_episode(episodio.title)
      
      #Actualizamos el progreso
      pDialog.update(((x)*100)/len(itemlist), 'Descargando ' + item.show, 'Descargando episodio: ' + episodio.title)

      # Extrae los mirrors
      if hasattr(channel, 'findvideos'):
          mirrors_itemlist = channel.findvideos(episodio)
      else:
          mirrors_itemlist = findvideos(episodio,episodio.channel)
      
      
      descargado = False
      
      #Descarga el primer mirror que funcione
      for mirror_item in mirrors_itemlist:
      
        if hasattr(channel, 'play'):
            video_items = channel.play(mirror_item)
        else:
            video_items = [mirror_item]
            
        if len(video_items)>0:
            video_item = video_items[0]
            
            # Comprueba que esté disponible
            video_urls, puedes, motivo = servertools.resolve_video_urls_for_playing( video_item.server , video_item.url , video_password="" , muestra_dialogo=False)
            
            # Lo descarga
            if puedes:
            
              # El vídeo de más calidad es el último
              devuelve = downloadtools.downloadbest(video_urls,item.show+" "+episodio.title+" ["+video_item.server+"]",continuar=False)
              if devuelve==0:
                  logger.info("[launcher.py] download_all_episodes - Archivo Descargado")
                  descargado = True
                  break
              elif devuelve==-1:
                  pDialog.close()
                  logger.info("[launcher.py] download_all_episodes - Descarga abortada")
                  advertencia = xbmcgui.Dialog()
                  resultado = advertencia.ok("pelisalacarta" , "La descarga ha sido cancelada")
                  return
              else:
                  continue
    pDialog.close()
    

###########################################################################
#                          MENU DE REPRODUCCIÓN                           #
#         ESPACIO ENCARGADO DEL MENÚ DE REPRODUCCIÓN DEL VÍDEO            #
#                        Y SUS DISTINTAS OPCIONES                         #
###########################################################################

#Función encargada de construir el menu de reproduccion de los videos:----------->OK
def MenuVideo(item):
    logger.info("[launcher.py] MenuVideo")
    
    # Lista de Opciones Disponibles
    OpcionesDisponibles =[]
    OpcionesDisponibles.append(config.get_localized_string(30151)) #"Ver el vídeo"
    OpcionesDisponibles.append(config.get_localized_string(30164)) #"Borrar este fichero"
    OpcionesDisponibles.append(config.get_localized_string(30153)) #"Descargar"
    OpcionesDisponibles.append(config.get_localized_string(30154)) #"Quitar de favoritos"
    OpcionesDisponibles.append(config.get_localized_string(30155)) #"Añadir a favoritos"
    OpcionesDisponibles.append(config.get_localized_string(30161)) #"Añadir a Biblioteca"
    OpcionesDisponibles.append(config.get_localized_string(30157)) #"Añadir a lista de descargas"
    OpcionesDisponibles.append(config.get_localized_string(30159)) #"Borrar descarga definitivamente"
    OpcionesDisponibles.append(config.get_localized_string(30160)) #"Pasar de nuevo a lista de descargas"
    OpcionesDisponibles.append(config.get_localized_string(30156)) #"Quitar de lista de descargas"
    OpcionesDisponibles.append(config.get_localized_string(30158)) #"Enviar a JDownloader"
    OpcionesDisponibles.append(config.get_localized_string(30158).replace("jDownloader","pyLoad")) # "Enviar a pyLoad"
    OpcionesDisponibles.append(config.get_localized_string(30162)) #"Buscar Trailer"
    
    
    itemlist = []
    if item.server=="": item.server="directo"   
    default_action = config.get_setting("default_action")
    
    # Extrae las URL de los vídeos, y si no puedes verlo te dice el motivo
    from servers import servertools
    video_urls,puedes,motivo = servertools.resolve_video_urls_for_playing(item.server,item.url,item.password, True)
    
 
    
    # Si puedes ver el vídeo, presenta las opciones
    if puedes:
      for video_url in video_urls:
        itemlist.append(Item(title=OpcionesDisponibles[0] + " " + video_url[0], url=video_url, action="play_video"))
        
      if item.server=="local":
        itemlist.append(Item(title=OpcionesDisponibles[1], url=video_urls, action="delete"))

      if not item.server=="local":
        itemlist.append(Item(title=OpcionesDisponibles[2], url=video_urls, action="download")) #"Descargar"

      if item.channel=="favoritos":
        itemlist.append(Item(title=OpcionesDisponibles[3], url=video_urls, action="remove_from_favorites")) #"Quitar de favoritos"
      
      if not item.channel=="favoritos":
        itemlist.append(Item(title=OpcionesDisponibles[4], url=video_urls, action="add_to_favorites"))  #"Añadir a favoritos"
      
      if not item.channel=="library":
        itemlist.append(Item(title=OpcionesDisponibles[5], url=video_urls, action="add_to_library")) #"Añadir a Biblioteca"
      if item.channel=="library":
        itemlist.append(Item(title="Quitar de la Biblioteca", url=video_urls, action="remove_from_library")) #"Añadir a Biblioteca"

      if not item.channel=="descargas":
        itemlist.append(Item(title=OpcionesDisponibles[6], url=video_urls, action="add_to_downloads")) #"Añadir a lista de descargas"
            
      if item.channel =="descargas" and item.category=="errores":
        itemlist.append(Item(title=OpcionesDisponibles[7], url=video_urls, action="remove_from_error_downloads")) #"Borrar descarga definitivamente"
        itemlist.append(Item(title=OpcionesDisponibles[8], url=video_urls, action="add_again_to_downloads")) #"Pasar de nuevo a lista de descargas"          
      if item.channel =="descargas" and item.category=="pendientes": 
        itemlist.append(Item(title=OpcionesDisponibles[9], url=video_urls, action="remove_from_downloads")) #"Quitar de lista de descargas"

      if config.get_setting("jdownloader_enabled")=="true": 
        itemlist.append(Item(title=OpcionesDisponibles[10], url=video_urls, action="send_to_jdownloader")) #"Enviar a JDownloader"
          
      if config.get_setting("pyload_enabled")=="true": 
        itemlist.append(Item(title=OpcionesDisponibles[11], url=video_urls, action="send_to_pyLoad")) #"Enviar a pyLoad"

      if not item.channel in ["trailertools","ecarteleratrailers"]: 
        itemlist.append(Item(title=OpcionesDisponibles[12], url=video_urls, action="search_trailer")) # "Buscar Trailer" 
        
    else:
        if item.server!="":
            advertencia = xbmcgui.Dialog()
            if "<br/>" in motivo:
                resultado = advertencia.ok( "No puedes ver ese vídeo porque...",motivo.split("<br/>")[0],motivo.split("<br/>")[1],item.url)
            else:
                resultado = advertencia.ok( "No puedes ver ese vídeo porque...",motivo,item.url)
        else:
            resultado = advertencia.ok( "No puedes ver ese vídeo porque...","El servidor donde está alojado no está","soportado en pelisalacarta todavía",url)

            if item.channel=="favoritos":
              itemlist.append(Item(title=OpcionesDisponibles[3], url=video_urls, action="remove_from_favorites")) #"Quitar de favoritos"
            if item.channel=="library":
              itemlist.append(Item(title="Quitar de la Biblioteca", url=video_urls, action="remove_from_library")) #"Añadir a Biblioteca"

            if item.channel =="descargas" and item.category=="errores":
              itemlist.append(Item(title=OpcionesDisponibles[7], url=video_urls, action="remove_from_error_downloads")) #"Borrar descarga definitivamente"         
            if item.channel =="descargas" and not item.category=="errores": 
              itemlist.append(Item(title=OpcionesDisponibles[9], url=video_urls, action="remove_from_downloads")) #"Quitar de lista de descargas"

    return itemlist


#Función encargada de Mostrar el Menú de Reproduccion y devolver la opción seleccionada en XBMC:----------->OK
def MostrarMenuVideo(item,itemlist):
    opciones = []
    Reproducible = False
    seleccion = -1
    for itemopcion in itemlist:
      opciones.append(itemopcion.title)
      if itemopcion.action=="play": Reproducible = True

    if len(opciones)>0:    
      default_action = config.get_setting("default_action")
      if default_action=="0" or not Reproducible: #Preguntar
          seleccion = xbmcgui.Dialog().select(config.get_localized_string(30163), opciones) #"Elige una opción"
      elif default_action=="1": #Ver en Calidad Baja
          seleccion = 0
      elif default_action=="2": #Ver en Calidad Alta
          seleccion = len(video_urls)-1
      elif default_action=="3": #Mandar a jDownloader
        if config.get_setting("jdownloader_enabled")=="true":
          seleccion = opciones.index(OpcionesDisponibles[10])
      else:
          seleccion=0
    return seleccion


#Función para descargar un vídeo:----------->OK
def download(item, itemSeleccion=-1): 
  from core import downloadtools
  keyboard = xbmc.Keyboard(downloadtools.limpia_nombre_excepto_1(item.title))
  keyboard.doModal()
  if (keyboard.isConfirmed()):
      title = keyboard.getText()
      devuelve = downloadtools.downloadbest(itemSeleccion.url,title)
      if devuelve==0: xbmcgui.Dialog().ok("pelisalacarta" , "Descargado con éxito")
      elif devuelve==-1: xbmcgui.Dialog().ok("pelisalacarta" , "Descarga cancelada")
      else: xbmcgui.Dialog().ok("pelisalacarta" , "Error en la descarga")


#Función para añadir un vídeo a Favoritos:----------->OK
def add_to_favorites(item, itemSeleccion=-1):
  from core import favoritos
  from core import downloadtools
  keyboard = xbmc.Keyboard(item.title)
  keyboard.doModal()
  if keyboard.isConfirmed():
      item.title = keyboard.getText()
      favoritos.GuardarFavorito(item)
      xbmcgui.Dialog().ok(config.get_localized_string(30102) , item.title , config.get_localized_string(30108)) # 'se ha añadido a favoritos'


#Función para añadir un vídeo a la Librería:----------->OK
def add_to_library(item, itemSeleccion=-1): 
  from core import downloadtools
  keyboard = xbmc.Keyboard(item.title)
  keyboard.doModal()
  if keyboard.isConfirmed():
    item.title = keyboard.getText()
    library.Guardar(item)
    library.ActualizarBiblioteca(item) 


#Función para borrar un vídeo de la Librería:----------->OK
def remove_from_library(item, itemSeleccion=-1): 
    library.Borrar(item)
    library.ActualizarBiblioteca(item)    
    
    
#Función para añadir un vídeo a la Lista de Descargas:----------->OK
def add_to_downloads(item, itemSeleccion=-1): 
  from core import descargas
  from core import downloadtools
  keyboard = xbmc.Keyboard(downloadtools.limpia_nombre_excepto_1(item.title))
  keyboard.doModal()
  if keyboard.isConfirmed():
      item.title = keyboard.getText()
      descargas.GuardarDescarga(item)
      xbmcgui.Dialog().ok(config.get_localized_string(30101) , item.title , config.get_localized_string(30109)) # 'se ha añadido a la lista de descargas'


#Función para envíar un vídeo a jDownloader:----------->OK pendiente añadir user y password a la config
def send_to_jdownloader(item, itemSeleccion=-1): 
    from core import scrapertools
    User="JD"                              #POR AÑADIR A LA CONFIG
    Password="JD"                          #POR AÑADIR A LA CONFIG
    headers=[]
    headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:20.0) Gecko/20100101 Firefox/20.0"])
    headers.append(["Accept","text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"])
    headers.append(["Accept-Language","es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"])
    headers.append(["Accept-Encoding","gzip, deflate"])
    headers.append(["Authorization","Basic " + base64.b64encode(User + ":" + Password)])
    headers.append(["Content-Type","application/x-www-form-urlencoded"])
    url=config.get_setting("jdownloader")+"/link_adder.tmpl"
    Descargas = item.url
    if item.thumbnail: Descargas = Descargas + "\n" + item.thumbnail
    if item.subtitle: Descargas = Descargas + "\n" + item.subtitle
    try:
      data = scrapertools.downloadpage(url,headers=headers,post="do=Add&addlinks="+ urllib.quote_plus(Descargas))
      xbmcgui.Dialog().ok(config.get_localized_string(30101) , item.title , "Se ha enviado a jDownloader")
    except:
      xbmcgui.Dialog().ok(config.get_localized_string(30101) , item.title , "No se ha podido enviar a jDownloader")
    
    

#Función para envíar un vídeo a pyLoad:----------->OK
def send_to_pyLoad(item, itemSeleccion=-1):    
  logger.info("Opcion seleccionada: Enviar a pyLoad" )
  if item.show!="":
      package_name = item.show
  else:
      package_name = item.title
  from core import pyload_client
  pyload_client.download(url=item.url,package_name=package_name)
  if item.thumbnail: pyload_client.download(url=item.thumbnail,package_name=package_name)
  if item.subtitle: pyload_client.download(url=item.subtitle,package_name=package_name)
  xbmcgui.Dialog().ok(config.get_localized_string(30101) , item.title , "Se ha enviado a pyLoad")



#Función para buscar un Trailer:----------->OK
def search_trailer(item, itemSeleccion=-1): 
  logger.info("Opcion seleccionada: Buscar Trailer" )
  from core import downloadtools
  keyboard = xbmc.Keyboard(downloadtools.limpia_nombre_excepto_1(item.title))
  keyboard.doModal()
  if keyboard.isConfirmed():
      item.title = keyboard.getText()

  item.channel="trailertools"
  item.action="buscartrailer"
  xbmc.executebuiltin("Container.Update("+ConstruirURL(item)+")")


#Función para eliminar un vídeo de Favoritos:----------->OK
def remove_from_favorites(item, itemSeleccion=-1): 
  from core import favoritos
  # En "extra" está el nombre del fichero en favoritos
  favoritos.BorrarFavorito(item)

  xbmcgui.Dialog().ok(config.get_localized_string(30102) , item.title , config.get_localized_string(30105)) # 'Se ha quitado de favoritos'
  xbmc.executebuiltin( "Container.Refresh" )


#Función para eliminar un vídeo de la Lista de Descargas:----------->OK
def remove_from_downloads(item, itemSeleccion=-1):
  from core import descargas
  # La categoría es el nombre del fichero en la lista de descargas
  descargas.BorrarDescarga(item)
  xbmcgui.Dialog().ok(config.get_localized_string(30101) , item.title , config.get_localized_string(30106)) # 'Se ha quitado de lista de descargas'
  xbmc.executebuiltin( "Container.Refresh" )


#Función para eliminar un vídeo de Descargas con error:----------->OK
def remove_from_error_downloads(item, itemSeleccion=-1): 
  from core import descargas
  descargas.delete_error_bookmark(item)
  xbmcgui.Dialog().ok(config.get_localized_string(30101) , item.title , config.get_localized_string(30106)) # 'Se ha quitado de la lista'
  xbmc.executebuiltin( "Container.Refresh" )


#Función para añadir de nuevo un vídeo a Descargas desde Descargas con error:----------->OK
def add_again_to_downloads(item, itemSeleccion=-1): 
  from core import descargas
  descargas.mover_descarga_error_a_pendiente(item)
  xbmcgui.Dialog().ok(config.get_localized_string(30101) , item.title , config.get_localized_string(30107)) # 'Ha pasado de nuevo a la lista de descargas'
  xbmc.executebuiltin( "Container.Refresh" )


#Función para eliminar un vídeo de descargado:----------->OK
def delete(item, itemSeleccion=-1): 
  os.remove(item.url)
  tbn = os.path.splitext(item.url)[0]+".tbn"
  if os.path.exists(tbn):
    os.remove(tbn)
  nfo = os.path.splitext(item.url)[0]+".nfo"
  if os.path.exists(nfo):
    os.remove(nfo)
  xbmc.executebuiltin( "Container.Refresh" ) 


#Función encargada de reproducir un vídeo:----------->OK
def play_video(item, itemSeleccion=-1):
        mediaurl = itemSeleccion.url[1]
        if len(itemSeleccion.url)>2:
            wait_time = itemSeleccion.url[2]
        else:
            wait_time = 0

        if wait_time>0:
          handle_wait(wait_time,server,"Cargando vídeo...")
        if item.fulltitle: item.title=item.fulltitle
        xlistitem = xbmcgui.ListItem( item.title, iconImage="DefaultVideo.png", thumbnailImage=item.thumbnail, path=mediaurl)
        xlistitem.setInfo( "video", { "Title": item.title, "Plot" : item.plot , "Studio" : item.channel , "Genre" : item.category } )

        if item.subtitle!="":
            import os
            ficherosubtitulo = os.path.join( config.get_data_path(), 'subtitulo.srt' )
            if os.path.exists(ficherosubtitulo):
                  os.remove(ficherosubtitulo)
        
            from core import scrapertools
            data = scrapertools.cache_page(item.subtitle)
            fichero = open(ficherosubtitulo,"w")
            fichero.write(data)
            fichero.close()
            
    
        if item.channel=="library": #Si es un fichero strm no hace falta el play
          xbmcplugin.setResolvedUrl(int(sys.argv[ 1 ]),True,xlistitem)
          
        else:
          if config.get_setting("player_mode")=="3": #download_and_play
            import download_and_play
            download_and_play.download_and_play( mediaurl , "download_and_play.tmp" , config.get_setting("downloadpath"))
            
          elif config.get_setting("player_mode")=="0" or (config.get_setting("player_mode")=="3" and mediaurl.startswith("rtmp")): #Direct
          
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            playlist.clear()
            playlist.add(mediaurl, xlistitem)
            playersettings = config.get_setting('player_type')
            player_type = xbmc.PLAYER_CORE_AUTO
            if playersettings == "0":
                player_type = xbmc.PLAYER_CORE_AUTO
                logger.info("[xbmctools.py] PLAYER_CORE_AUTO")
            elif playersettings == "1":
                player_type = xbmc.PLAYER_CORE_MPLAYER
                logger.info("[xbmctools.py] PLAYER_CORE_MPLAYER")
            elif playersettings == "2":
                player_type = xbmc.PLAYER_CORE_DVDPLAYER
                logger.info("[xbmctools.py] PLAYER_CORE_DVDPLAYER")
            xbmcPlayer = xbmc.Player(player_type)
            xbmcPlayer.play(playlist)
            
          elif config.get_setting("player_mode")=="1": #setResolvedUrl
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path=mediaurl))
        
          elif config.get_setting("player_mode")=="2": #Built-in
            xbmc.executebuiltin( "PlayMedia("+mediaurl+")" )
