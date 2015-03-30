# -*- coding: UTF-8 -*-
#------------------------------------------------------------
# Gestión de parámetros de canal multiplataforma
#------------------------------------------------------------
# pelisalacarta
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
# Creado por: superberny para pelisalacarta
# Basado en el trabajo de: Jesús (tvalacarta@gmail.com)
# Licencia: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
#------------------------------------------------------------
# Historial de cambios:
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import sys, os
import json
from core import config
from core import logger
from core.item import Item
from core import dialog
      
__channel__ = "config_channel"

def isGeneric():
    return True

def get_paths_config(channel):
    path_fichero_version_canal = os.path.join( config.get_runtime_path(), 'pelisalacarta' , 'channels' , channel +".xml" )
    #Comprobar si no existe path_fichero_version_canal ...
    if not os.path.exists(path_fichero_version_canal):
        # ...no existe el canal.xml en el ruta indicada, busquemos en config.get_runtime_path() + "pelisalacarta/" ... 
        path_fichero_version_canal = os.path.join( config.get_runtime_path(), 'pelisalacarta' , channel +".xml" ) # buscador.py seria un ejemplo
        if not os.path.exists(path_fichero_version_canal):
            # ...si aqui tampoco esta, devolvemos una cadena vacia indicando el error.
            path_fichero_version_canal =''
    
    #Comprobamos si existe el directorio '\userdata\addon_data\plugin.video.pelisalacarta\channels' y si no lo creamos
    directorio_path_config= os.path.join( config.get_data_path() , 'channels')
    if not os.path.exists(directorio_path_config):
        logger.info("[config_channel] Creando directorio "+ directorio_path_config)
        os.mkdir(directorio_path_config)
        
    path_fichero_config_canal = os.path.join( directorio_path_config , channel +".xml" )
        
    logger.info("[config_channel] path_fichero_version_canal:" + path_fichero_version_canal)
    logger.info("[config_channel] path_fichero_config_canal:" + path_fichero_config_canal)
    return path_fichero_version_canal, path_fichero_config_canal
    
def mainlist(item):
    itemlist=[]
    channel= item.extra.split('|')[0]
    action= item.extra.split('|')[1]
    lista_controles=[]
    
    from xml.dom import minidom
    path_fichero_version_canal, path_fichero_config_canal= get_paths_config(channel)
    
    if path_fichero_version_canal=='':
        # ...si no existe el fichero \pelisalacarta\channels\channel.xml , devolvemos un Item indicando el error.
            itemlist.append( Item(title="Error: No hay parametros de configuración.", channel=channel , action=action))
            return itemlist
            
    
    #Cargar diccinario IDs/Values
    dic_setting_value, none= read_settings(channel)
    #logger.info("[config_channel] open_settings: dic_setting_value:" + str(len(dic_setting_value)))
        
    #Abrimos el fichero version
    fichero_version = minidom.parse(path_fichero_version_canal)
    lista_category = fichero_version.getElementsByTagName("category")
    
    for categoria in lista_category:
        categoria_label=categoria.getAttribute("label")
        lista_controles.append(dialog.Control(type='controlDLabel',id='cat_'+categoria_label,label=categoria_label))
        
        lista_settings= categoria.getElementsByTagName("setting")
        for setting in lista_settings:
            setting_type=setting.getAttribute("type")
            if setting_type=="sep":
                # Add separacion
                pass
            else:
                setting_id=setting.getAttribute("id") #id solo caracteres ascii !!!
                setting_label=setting.getAttribute("label")
                
                if setting.hasAttribute("visible"): 
                    setting_visible=setting.getAttribute("visible") 
                else: 
                    setting_visible= 'True'
                if setting.hasAttribute("enabled"): 
                    setting_enabled=setting.getAttribute("enabled") 
                else: 
                    setting_enabled= 'True'
                
                #Segun el type:
                if setting_type=="text":
                    if setting.hasAttribute("option"): 
                        setting_option=setting.getAttribute("option") 
                    else: 
                        setting_option=""
                    # Add controlDEdit a la lista de controles
                    lista_controles.append(dialog.Control(type='controlDEdit',id=setting_id,label=setting_label,value=dic_setting_value[setting_id], visible=setting_visible, enabled=setting_enabled, opcion=setting_option))
                elif setting_type=="number":
                    # Add un ControlTextBox solo numerico a la lista de controles
                    lista_controles.append(dialog.Control(type='controlDNumerico',id=setting_id,label=setting_label,value=dic_setting_value[setting_id], visible=setting_visible, enabled=setting_enabled))
                elif setting_type=="bool":
                    # Add ControlRadioButton a la lista de controles
                    lista_controles.append(dialog.Control(type='controlDRadioButton',id=setting_id,label=setting_label,value=dic_setting_value[setting_id], visible=setting_visible, enabled=setting_enabled))
                elif setting_type=="enum":
                    setting_values=setting.getAttribute("lvalues")
                    # Add ControlEnum a la lista de controles
                    lista_controles.append(dialog.Control(type='controlDLista',id=setting_id,label=setting_label,value=dic_setting_value[setting_id], visible=setting_visible, enabled=setting_enabled, lvalues=setting_values))
                else:
                    #Error type no reconocido aun
                    pass
    
   
    # Agregar Control tipo boton para guardar los cambios
    lista_controles.append(dialog.Control(type='controlDButton',id='_save_',label="Guardar los cambios",opcion=item.extra)) #opcion= canal q ha llamado a config_channel + '|' + action a ejecutar   
    #Crear la ventana y add el listado de controles
    
    itemlist.extend(dialog.getMenu(lista_controles))
    
    #logger.info("[config_channel] open_settings: FIN" )
    return itemlist
    
def ini_setting(channel):
    from xml.dom import minidom
    dic={}
    lista_settings_to_xml=[]
    
    path_version, path__config= get_paths_config(channel)
    
    if path_version=='' or path__config=='':
        logger.info("[config_channel] Error no existen ficheros de configuracion.")
    else:
        #Abrimos version
        fichero_version = minidom.parse(path_version)
        lista_settings= fichero_version.getElementsByTagName("setting")
        #logger.info("[config_channel] lista_settings: "+ str(len(lista_settings)))
        
        for setting in lista_settings:
            if setting.getAttribute("type") !="sep" :
                id=setting.getAttribute("id")
                value=""
                if setting.hasAttribute("default"):
                    value=setting.getAttribute("default").encode('utf-8')          
                #logger.info("[config_channel] ini_setting: " + id + " : " + value)
                dic[id]=value
                lista_settings_to_xml.append([id,value])
                
        write_xml_config(lista_settings_to_xml,channel)
    
    #retorna un diccionario de IDs/values y una lista con pares [ID,value]
    return dic, lista_settings_to_xml    
                      
def read_settings(channel):
    from xml.dom import minidom
    dic={}
    lista_settings_to_xml=[]
    
    none, path_fichero_config_canal= get_paths_config(channel)
    
    #Comprobamos que exista el fichero de configuracion para este canal ...
    if os.path.exists(path_fichero_config_canal):
        #Abrimos fichero de configuracion
        fichero_config = minidom.parse(path_fichero_config_canal)
        lista_settings= fichero_config.getElementsByTagName("setting")

        for setting in lista_settings:
            id=setting.getAttribute("id")
            value=setting.getAttribute("value").encode('utf-8')
            dic[id]=value
            lista_settings_to_xml.append([id,value])
    else:
       #... si no existe se inicializa
        dic, lista_settings_to_xml= ini_setting(channel) 
    
    #retorna un diccionario de IDs/values y una lista con pares [ID,value]
    return dic, lista_settings_to_xml  
    
def get_setting( name, channel):
    dic, none= read_settings(channel)
    if dic.has_key(name):  
        return dic[name]
    else:
        return ""  
   
def set_setting( name, value, channel):
    none, lista_settings= read_settings(channel)
    for setting in lista_settings:
        if setting[0]==name:
            setting[1]=value
            write_xml_config(lista_settings, channel)
            return 1 # Cambio ok
    return 0 # Cambio no ok
    
def save_settings(item):
    logger.info("[config_channel] fulltitle " + item.fulltitle)
    # fulltitle ["controlDLabel|>|<|cat_General|>|<|General|>|<||>|<|True|>|<|True|>|<||>|<||>|<|", "controlDRadioButton|>|<|updatecheck2|>|<|pepe|>|<|true|>|<|True|>|<|True|>|<||>|<||>|<|", "controlDLabel|>|<|cat_Opciones2|>|<|Opciones2|>|<||>|<|True|>|<|True|>|<||>|<||>|<|", "controlDRadioButton|>|<|updatechannels|>|<|pepe2|>|<|false|>|<|True|>|<|True|>|<||>|<||>|<|", "controlDEdit|>|<|alldebriduser|>|<|Jose|>|<|Pep|>|<|True|>|<|True|>|<||>|<||>|<|", "controlDButton|>|<|_save_|>|<|Guardar los cambios|>|<||>|<|True|>|<|True|>|<||>|<|newpct1|mainlist|>|<|"]
    
    #item.extra= canal q ha llamado a config_channel + '|' + action a ejecutar
    channel= item.extra.split('|')[0]
    action= item.extra.split('|')[1]
            
    lista_settings=[]
    for s in json.loads(item.fulltitle):
        c = s.split('|>|<|')
        if c[0] != 'controlDLabel' and c[0] !='controlDButton':
            id= c[1]
            value= c[3]
            lista_settings.append([id,value])
    write_xml_config(lista_settings, channel)
    
    # Devolvemos itemlist con un solo item de confirmacion
    itemlist=[]
    itemlist.append(Item(channel=channel, title="Cambios guardados."+ (" " * 30) + "Volver a " + channel.capitalize(), action=action))
    return itemlist
        

def write_xml_config(lista_settings, channel):
    #Creamos nuevo xml
    from xml.dom import minidom
    settings_config = minidom.getDOMImplementation().createDocument(None, "settings", None)
    settings_config_raiz = settings_config.documentElement
    
    for i in lista_settings:
        #logger.info("[config_channel] id: " + i[0])
        #logger.info("[config_channel] value: " + i[1])
        nodo = settings_config.createElement("setting")
        nodo.setAttribute("id",i[0])
        nodo.setAttribute("value",i[1])
        settings_config_raiz.appendChild(nodo)
            
    # Abrimos fichero en donde guardar el documento XML.
    none, path_fichero_config_canal= get_paths_config(channel)
    fichero = open(path_fichero_config_canal, "w")
    
    # Escribimos mediante el metodo writexml en la cabecera la codificacion
    settings_config.writexml(fichero, encoding='utf-8',  addindent="\t", newl="\n")

    # Finalmente cerramos el fichero.
    fichero.close()
    logger.info("[config_channel] write_xml_config: Guardando fichero:" + path_fichero_config_canal)
        
    


