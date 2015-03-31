# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta
# XBMC Plugin
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys, time,datetime,io
import codecs, json
import scrapertools, config, logger
from core.item import Item
from distutils.version import StrictVersion
 

PLUGIN_NAME = "pelisalacarta"
ROOT_DIR = config.get_runtime_path()
REMOTE_VERSION_FILE = "http://blog.tvalacarta.info/descargas/"+PLUGIN_NAME+"-version.xml"
LOCAL_VERSION_FILE = os.path.join( ROOT_DIR , "version.xml" )
URL_BASE_REPOSITORIO= "http://xbmc-tvalacarta.googlecode.com/svn/trunk/"+PLUGIN_NAME
LOCAL_FILE = os.path.join( ROOT_DIR , PLUGIN_NAME+"-" )
DIRECTORIO_PATH_CONFIG= os.path.join( config.get_data_path() , 'channels')
PATH_LIST_CHANNELS_JSON= os.path.join( config.get_data_path() , "list_channels.json" )
PATH_LIST_SERVERS_JSON= os.path.join( config.get_data_path() , "list_servers.json" )


try:
    logger.info("[updater.py] get_platform=" + config.get_platform())
    logger.info("[updater.py] get_system_platform=" + config.get_system_platform())
    
    REMOTE_FILE = "http://blog.tvalacarta.info/descargas/" + PLUGIN_NAME
    if config.get_platform()=="xbmcdharma" and config.get_system_platform() == "xbox":
        # Añadida a la opcion : si plataforma xbmcdharma es "True", no debe ser con la plataforma de la xbox
        # porque seria un falso "True", ya que el xbmc en las xbox no son dharma por lo tanto no existen los addons
        REMOTE_FILE =""
    elif config.get_platform()=="xbmc":
        REMOTE_FILE += "-xbmc-plugin-"
        import xbmc
        DESTINATION_FOLDER = xbmc.translatePath( "special://home/plugins/video")
    elif config.get_platform().startswith("xbmc"):  
        REMOTE_FILE += config.get_platform().replace("xbmc","-xbmc-addon-") + "-"
        import xbmc
        DESTINATION_FOLDER = xbmc.translatePath( "special://home/addons")    
    elif config.get_platform()=="wiimc":
        REMOTE_FILE += "-wiimc-"
        DESTINATION_FOLDER = os.path.join(config.get_runtime_path(),"..")
    elif config.get_platform()=="rss":
        REMOTE_FILE += "-rss-"
        DESTINATION_FOLDER = os.path.join(config.get_runtime_path(),"..")

except:
    import xbmc
    REMOTE_FILE = "http://blog.tvalacarta.info/descargas/"+PLUGIN_NAME+"-xbmc-plugin-"
    DESTINATION_FOLDER = xbmc.translatePath( os.path.join( ROOT_DIR , ".." ) )

    
##################################################
# Actualizar plugin
##################################################    
def checkforupdates():
    '''
    Comprueba si hay una nueva version del plugin
    Retorna un lista de items con un solo item si hay nueva version o vacia si no la hay.
    '''
    logger.info("[updater.py] checkforupdates")
    itemlist=[]
    data = scrapertools.cachePage(REMOTE_VERSION_FILE)
    patron  = '<tag>([^<]+)</tag>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    versiondescargada = matches[0]
    archivo = open(os.path.join( config.get_runtime_path() , "version.xml" ))
    data = archivo.read()
    archivo.close()
    matches = re.compile(patron,re.DOTALL).findall(data)
    versionlocal = matches[0]    
    
    if StrictVersion(versiondescargada) > StrictVersion(versionlocal):
      itemlist.append(Item(title="Descargar version "+versiondescargada, channel="updater", url=versiondescargada,action ="update", thumbnail=channelselector.get_thumbnail_path() + "Crystal_Clear_action_info.png"))
      
    return itemlist

def update(item):
    '''
    Descarga una nueva version y actualiza el plugin instalado
    '''
    # Descarga el ZIP
    logger.info("[updater.py] update")
    remotefilename = REMOTE_FILE+item.url+".zip"
    localfilename = LOCAL_FILE+ item.url+".zip"
    logger.info("[updater.py] remotefilename=%s" % remotefilename)
    logger.info("[updater.py] localfilename=%s" % localfilename)
    logger.info("[updater.py] descarga fichero...")
    inicio = time.clock()
    
    #urllib.urlretrieve(remotefilename,localfilename)
    from core import downloadtools
    downloadtools.downloadfile(remotefilename, localfilename)
    
    fin = time.clock()
    logger.info("[updater.py] Descargado en %d segundos " % (fin-inicio+1))
    
    # Lo descomprime
    logger.info("[updater.py] descomprime fichero...")
    import ziptools
    unzipper = ziptools.ziptools()
    destpathname = DESTINATION_FOLDER
    logger.info("[updater.py] destpathname=%s" % destpathname)
    unzipper.extract(localfilename,destpathname)
    
    # Borra el zip descargado
    logger.info("[updater.py] borra fichero...")
    os.remove(localfilename)
    logger.info("[updater.py] ...fichero borrado")
    
    # Eliminamos list_channels.json para forzar su actualizacion
    if os.path.exists(PATH_LIST_CHANNELS_JSON): # Si existe list_channels.json lo borramos
        logger.info("[updater.py] borra fichero " + PATH_LIST_CHANNELS_JSON + "...")
        os.remove(PATH_LIST_CHANNELS_JSON)
        logger.info("[updater.py] ...fichero borrado")
        

    
    
#################################################
# Actualizar canal
#################################################
def get_path_url_channel(channel_name):
    if channel_name == "channelselector":
        #remote_files_url= URL_BASE_REPOSITORIO + '/' + channel_name
        remote_files_url="https://raw.githubusercontent.com/superberny70/plugin.video.pelisalacarta/master/channelselector.py"
        local_files_path=os.path.join( config.get_runtime_path() , channel_name)
    else:
        #remote_files_url= URL_BASE_REPOSITORIO + '/' + PLUGIN_NAME + '/' + "channels" + '/' + channel_name  
        remote_files_url = "https://raw.githubusercontent.com/superberny70/plugin.video.pelisalacarta/master/pelisalacarta/channels/" +  channel_name 
        local_files_path=os.path.join( config.get_runtime_path(), PLUGIN_NAME , 'channels' , channel_name)
    return remote_files_url, local_files_path
   
def updatechannel(channel_name):
    '''
    Funcion experimental para actualizar el canal desde github basandose en la fecha de modificacion de los archivos.
    '''
    remote_files_url = "https://github.com/superberny70/plugin.video.pelisalacarta/tree/master/pelisalacarta/channels"
    local_files_path=os.path.join( config.get_runtime_path(), PLUGIN_NAME , 'channels' , channel_name+'.py')
 
    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)","",scrapertools.cache_page(remote_files_url))
    #last_commit= scrapertools.find_single_match(data,'<time class="updated" datetime="([^"]+)"')
    
    patron = '<td class="content">.*?title="'+ channel_name +'\.py".*?' 
    patron += '<time datetime="([^"]+)"' # date_time
    
    date= scrapertools.find_single_match(data,patron).replace('T',' ').replace('Z','')
    
    if date =='': # El canal no esta en el repositorio remoto
        return False
        
    struct= time.strptime(date,'%Y-%m-%d %H:%M:%S')    
    dt_remote = datetime.datetime.fromtimestamp(time.mktime(struct))
    
    if os.path.exists(local_files_path):
        dt_local =datetime.datetime.fromtimestamp(os.path.getmtime (local_files_path))
    
    #logger.info("[updater.py] remote_data= "+str(dt_remote) + " local_data= " + str(dt_local ))
    if dt_remote > dt_local:
        return download_channel(channel_name)
        
    return False
    
def updatechannel2(channel_name):
    '''
    Esta funcion no se usa actualmente. 
    Actualizacion desde el repositorio oficial basandose en el numero de version del xml
    '''
    logger.info("[updater.py] updatechannel('"+channel_name+"')")
      
    remote_files_url, local_files_path= get_path_url_channel(channel_name)
    
    # Version remota
    try:
        data = scrapertools.cachePage(remote_files_url+ '.xml')
        #logger.info("[updater.py] remote_data="+data)
        remote_version = scrapertools.find_single_match(data,'<tag>([^<]+)</tag>')
        if '.' not in remote_version: remote_version +='.0'
    except:
        remote_version = '0.0'
    logger.info("[updater.py] remote_version=%s" % remote_version)

    # Version local
    if os.path.exists(local_files_path+ '.xml'):
        infile = open(local_files_path+ '.xml')
        data = infile.read()
        infile.close();
        #logger.info("[updater.py] local_data="+data)
        local_version = scrapertools.find_single_match(data,'<tag>([^<]+)</tag>')
        if '.' not in local_version: local_version +='.0'
    else:
        local_version = '0.0'
    logger.info("[updater.py] local_version=%s" % local_version)
    
    # Comprueba si ha cambiado
    if StrictVersion(remote_version) > StrictVersion(local_version):
        logger.info("[updater.py] updated")
        return download_channel(channel_name)

    return False

def download_channel(channel_name):
    logger.info("[updater.py] download_channel('"+channel_name+"')")
    ret= True
    remote_files_url, local_files_path= get_path_url_channel(channel_name)
    
    # Descarga el canal
    for ext in ['.xml', '.py']:
        try:
            updated_data = scrapertools.cachePage(remote_files_url + ext)
            if scrapertools.find_single_match(updated_data,'<title>Page not found') !="": 
                continue
            
            outfile = open(local_files_path + ext ,"w")
            outfile.write(updated_data)
            outfile.flush()
            outfile.close()
            logger.info("[updater.py] Grabado a " + local_files_path + ext)
           
            if ext=='.py' and channel_name != "channelselector" :
                # Actualizar listado de canales
                if os.path.exists(PATH_LIST_CHANNELS_JSON): # Si existe list_channels.json lo abrimos...
                    with codecs.open(PATH_LIST_CHANNELS_JSON,'r','utf-8') as input_file:
                        indice_canales= json.load(input_file)
                    
                    # ... actualizamos los atributos del canal...
                    indice_canales[channel_name + '.py']= scraper_channel_py(updated_data)
                    
                    #...y lo volvemos a guardar
                    with codecs.open(PATH_LIST_CHANNELS_JSON,'w','utf-8') as outfile:
                        json.dump(indice_canales,outfile,sort_keys = True, indent = 4, ensure_ascii=False,encoding="utf8")
                       
                else: # Si no existe list_channels.json lo creamos
                    ini_list_channels_json()
        except:
            logger.info("[updater.py] Error al grabar " + local_files_path)
            ret= False
            for line in sys.exc_info():
                logger.error( "%s" % line )
            break
                
    if os.path.exists(local_files_path + '.pyo'):
        os.remove(local_files_path + '.pyo')
    
    return ret
        
##################################################################
# Actualizar el listado de canales
##################################################################

def list_remote_channels():
    '''
    Obtiene una lista de los canales remotos, analizando la web del repositorio.
    '''
    remote_files_url = "https://github.com/superberny70/plugin.video.pelisalacarta/tree/master/pelisalacarta/channels"
            
    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)","",scrapertools.cache_page(remote_files_url))
    #patron = '<li><a href="([a-zA-Z0-9]+\.py)">.*?</a></li>'
    patron = '<td class="content">.*?title="([a-zA-Z0-9]+\.py)">'
    files_remotos= re.compile(patron,re.DOTALL).findall(data)
        
    #logger.info("updater.list_remote_channels :"  + str(files_remotos))
    return files_remotos
    
def list_local_channels():  
    '''
    Obtiene una lista de los canales locales (archivos con extension py y que no comienzan con guion bajo)
    '''
    local_files_path = os.path.join( config.get_runtime_path(), 'pelisalacarta', 'channels')
            
    files_locales= os.listdir(local_files_path)
    files_locales= [c for c in files_locales if c.endswith('.py') and not c.startswith('_')]
    
    #logger.info("updater.list_local_channels :"  + str(files_locales))
    return files_locales
    
def sincronizar_canales():
    '''
    Actualiza el fichero "config.get_data_path() + channels/list_channels.json" con los canales añadidos 
    o eliminados (segun config.get_setting("outsider_channel")).
    Dicho fichero se utiliza como indice de canales
    Retorna el objeto JSON que representa al indice de canales
    '''
    logger.info("[updater] sincronizar_canales")

    lista_borrables=[]
    lista_nuevos=[]
    files_locales= list_local_channels()
    files_remotos= list_remote_channels()

    for channel in files_remotos:
        if channel not in files_locales:
            lista_nuevos.append(channel)
            dialogo('Nuevos canales', 'Añadiendo canal ' + channel.replace('.py','') )
            download_channel(channel.replace('.py',''))

    files_locales.extend(lista_nuevos)
    logger.info("updater.sincronizar_canales Canales nuevos: "  + str(len(lista_nuevos)))
    
    ''' Opciones para config.get_setting("outsider_channel")
        Opcion Mostrar (por defecto): config.get_setting("outsider_channel")=='0' Los canales seran mostrados en el menu como si estuviesen en SVN tambien. 
        Opcion Ignorar: config.get_setting("outsider_channel")=='1' Los canales no seran borrados, ni mostrados en el menu.
        Opcion Eliminar: config.get_setting("outsider_channel")=='2' Elimina todos los canales locales que no este subidos al SVN.
    '''
    for channel in files_locales:
        if channel not in files_remotos:
            if config.get_setting("outsider_channel")=="2": # Elimina todos los canales locales que no este subidos al SVN.
                lista_borrables.append(channel)
                files_locales.remove(channel)
                #Borra definitivamente el canal de nuestro HDD!!!
                os.remove(os.path.join(config.get_runtime_path(), 'pelisalacarta/channels',channel))
                if os.path.exists (os.path.join(config.get_runtime_path(), 'pelisalacarta/channels',channel.replace('.py','.pyo'))):
                    os.remove (os.path.join(config.get_runtime_path(), 'pelisalacarta/channels',channel.replace('.py','.pyo')))
                if os.path.exists (os.path.join(config.get_runtime_path(), 'pelisalacarta/channels',channel.replace('.py','.xml'))):
                    os.remove (os.path.join(config.get_runtime_path(), 'pelisalacarta/channels',channel.replace('.py','.xml')))
                if os.path.exists (os.path.join(DIRECTORIO_PATH_CONFIG,channel.replace('.py','.xml'))):
                    os.remove (os.path.join(DIRECTORIO_PATH_CONFIG,channel.replace('.py','.xml')))
            elif config.get_setting("outsider_channel")=='1': # Los canales no seran borrados, ni mostrados en el menu.
                lista_borrables.append(channel)
                files_locales.remove(channel)                      
            else: #  Los canales seran mostrados en el menu como si estuviesen en SVN tambien. 
                #lista_nuevos.append(channel)
                pass
    
    if not os.path.exists(PATH_LIST_CHANNELS_JSON): #si no existe el json lo creamos 
        ini_list_channels_json()
		
    indice_canales={}    
         
    logger.info("updater.sincronizar_canales Canales eliminados: "  + str(len(lista_borrables)))
    #if len(lista_nuevos) >0 or len(lista_borrables)>0:  
    if len(lista_borrables)>0:
        logger.info("updater.sincronizar_canales editar " + PATH_LIST_CHANNELS_JSON)
        
        with codecs.open(PATH_LIST_CHANNELS_JSON,'r','utf-8') as input_file:
            indice_canales= json.load(input_file)
        
        #logger.info("updater.sincronizar_canales indice_canales: " + str(indice_canales))
        
        for c in lista_borrables:
            if c in indice_canales:
                del indice_canales[c]
            
        # Guardamos de nuevo list_channels.json
        with codecs.open(PATH_LIST_CHANNELS_JSON, 'w','utf-8') as outfile:
            json.dump(indice_canales, outfile, sort_keys = True, indent = 4, ensure_ascii=False, encoding="utf8")
    
        logger.info("updater.sincronizar_canales Canales totales: "  + str(len(files_locales)))
    return indice_canales

def read_channel_py(file_channel_py):
    '''
    Abre file_channel_py y retorna un diccionario con las siguientes claves:
    title, channel, language, category, type, adult, thumbnail y version.
    '''
    path_fichero_canal = os.path.join( config.get_runtime_path(), 'pelisalacarta' , 'channels' , file_channel_py )
    infile = open(path_fichero_canal)
    data = infile.read()
    infile.close()
    
    return scraper_channel_py(data)
    
def scraper_channel_py(data_channel_py):
    '''
    Analiza el parametro 'data_channel_py' y retorna un diccionario con las siguientes claves:
    title, channel, language, category, type, adult, thumbnail y version.
    '''
    data_channel_py= data_channel_py.replace(' ','')
    title= scrapertools.find_single_match(data_channel_py,'__title__="([^"]+)"').decode('utf-8')
    channel= scrapertools.find_single_match(data_channel_py,'__channel__="([^"]+)"').decode('utf-8')
    language= scrapertools.find_single_match(data_channel_py,'__language__="([^"]+)"').decode('utf-8')
    category= scrapertools.find_single_match(data_channel_py,'__category__="([^"]+)"').decode('utf-8')
    type= scrapertools.find_single_match(data_channel_py,'__type__="([^"]+)"').decode('utf-8')
    adult= scrapertools.find_single_match(data_channel_py,'__adult__="([^"]+)"').decode('utf-8')
    thumbnail= scrapertools.find_single_match(data_channel_py,'__thumbnail__="([^"]+)"').decode('utf-8')
    '''
    version= scrapertools.find_single_match(data_channel_py,'__version__="([^"]+)"').decode('utf-8')
    if version=='': version=u'0'
    return {"title": title, "channel":channel, "language":language, "category":category, "type":type, "adult":adult, "thumbnail":thumbnail, "version":version}
    '''
    return {"title": title, "channel":channel, "language":language, "category":category, "type":type, "adult":adult, "thumbnail":thumbnail}

def ini_list_channels_json():
    '''
        Inicializa un archivo json con el listado de canales instalados
    '''
    logger.info("[updater.py] Iniciar list_channels.json")
    local_files_path =  list_local_channels()
    
    indice_canales= {}
    for c in local_files_path:
        # Abrir channel.py y buscar title, channel, language, category, type, adult y thumbnail
        indice_canales[c]= read_channel_py(c)
         
    # Guardamos de nuevo list_channels.json
    with codecs.open(PATH_LIST_CHANNELS_JSON, 'w','utf-8') as outfile:
        json.dump(indice_canales, outfile, sort_keys = True, indent = 4, ensure_ascii=False, encoding="utf8")
    
    logger.info("updater.ini_list_channels_json Canales totales: "  + str(len(local_files_path)))
    return indice_canales   
        
            
##########################################################
# Actualizar el listado de conectores/servers
##########################################################
def list_remote_servers():
    '''
        Obtiene un diccionario de los servers remotos y su fecha de la ultima actualizacion, analizando la web del repositorio GitHub.
        Cuando se porte pelisalacarta a la GitHub oficial hay q modificar la url.
    '''
    remote_files_url = "https://github.com/superberny70/plugin.video.pelisalacarta/tree/master/servers"
    
    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)","",scrapertools.cache_page(remote_files_url))
    #last_commit= scrapertools.find_single_match(data,'<time class="updated" datetime="([^"]+)"')
    
    patron = '<td class="content">.*?title="([a-zA-Z0-9]+\.py)".*?' # name_server
    patron += '<time datetime="([^"]+)"' # date_time

    matches= re.compile(patron,re.DOTALL).findall(data)
    d={}
    for name_server, date_time in matches:
        d[name_server]= date_time.replace('T',' ').replace('Z','')
  
    logger.info("updater.list_remote_servers :"  + str(d))
    return d

    
def ini_list_servers_json():
    '''
        Inicializa un archivo json con el listado de conectores/servers instalados
    '''
    local_files_path = os.path.join( config.get_runtime_path(), 'servers')
            
    files_locales= os.listdir(local_files_path)
    files_locales= [c for c in files_locales if c.endswith('.py') and not c.startswith('_')]
    
    indice_servers={}
    for s in files_locales:
        indice_servers[s]= {"fecha":str(datetime.datetime.fromtimestamp(os.path.getmtime (os.path.join( local_files_path, s))))}
        
    # Guardamos de nuevo list_servers.json
    with codecs.open(PATH_LIST_SERVERS_JSON, 'w','utf-8') as outfile:
        json.dump(indice_servers, outfile, sort_keys = True, indent = 4, ensure_ascii=False, encoding="utf8")
        
    return indice_servers
    
def updaterservers():
    '''
        Comprueba si hay conectores/servers actualizados en el repositorio 
    '''
    logger.info("[updater.py] updaterservers ...")
    ret= False
    if os.path.exists(PATH_LIST_SERVERS_JSON): # Si existe list_servers.json lo abrimos...
        with codecs.open(PATH_LIST_SERVERS_JSON,'r','utf-8') as input_file:
            indice_servers= json.load(input_file)    
    else: # ...sino lo creamos
        indice_servers= ini_list_servers_json()       
    
    for name,date in list_remote_servers().items():
        struct1= time.strptime(date,'%Y-%m-%d %H:%M:%S')
        dt1 = datetime.datetime.fromtimestamp(time.mktime(struct1))
        dc_server= indice_servers.get(name,'')
        if dc_server=='':
            struct2= time.strptime("2014-01-01 00:00:00",'%Y-%m-%d %H:%M:%S')
        else:
            struct2= time.strptime(dc_server["fecha"],'%Y-%m-%d %H:%M:%S')
        dt2 = datetime.datetime.fromtimestamp(time.mktime(struct2))
        
        if dt1 > dt2: 
            logger.info("updater.updaterservers : Actualizar " + name ) 
            dialogo('Actualizando conectores', 'Descargando ' + name.replace('.py','') )
            ret= download_server(name) 
    return ret
    
def download_server(server_name):
    '''
        Descarga un conector/server desde el repositorio
        Cuando se porte pelisalacarta a la GitHub oficial hay q modificar la url.
    '''
    logger.info("[updater.py] download_server('"+server_name+"')")
    ret= True
    remote_files_url = "https://raw.githubusercontent.com/superberny70/plugin.video.pelisalacarta/master/servers/" + server_name
    local_files_path = os.path.join( config.get_runtime_path(), 'servers', server_name)
    
    # Descarga el server
    try:
        outfile = open(local_files_path ,"w")
        outfile.write(scrapertools.cachePage(remote_files_url))
        outfile.flush()
        outfile.close()
        logger.info("[updater.py] Grabando " + local_files_path)
        
        # Actualizar listado de servidores
        if os.path.exists(PATH_LIST_SERVERS_JSON): # Si existe list_servers.json lo abrimos...
            with codecs.open(PATH_LIST_SERVERS_JSON,'r','utf-8') as input_file:
                indice_servers= json.load(input_file)

            indice_servers[server_name]= {"fecha":str(datetime.datetime.fromtimestamp(os.path.getmtime (local_files_path)))}
            with codecs.open(PATH_LIST_SERVERS_JSON, 'w','utf-8') as outfile:
                json.dump(indice_servers, outfile, sort_keys = True, indent = 4, ensure_ascii=False, encoding="utf8")
            
        else: # Si no existe list_servers.json lo creamos
            ini_list_servers_json()
    except:
        logger.info("[updater.py] Error al grabar " + local_files_path)
        ret= False
        for line in sys.exc_info():
            logger.error( "%s" % line )
    return ret
    
########################################################################
# Utilidades
########################################################################    
def dialogo(titulo, mensaje, icono= 0, tiempo=5000):
    # Esta metodo solo sera compatible con xbmc
    # Lo suyo seria crear un metodo equivalente para cada plataforma
    try:
        import xbmcgui
        dialog = xbmcgui.Dialog()
        l_icono=(xbmcgui.NOTIFICATION_INFO , xbmcgui.NOTIFICATION_WARNING, xbmcgui.NOTIFICATION_ERROR)
        dialog.notification(titulo, mensaje, l_icono[icono] ,tiempo)
    except:
        pass
