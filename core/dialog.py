# -*- coding: UTF-8 -*-
#------------------------------------------------------------
# Presentacion grafica para xbmc de los parámetros de canal 
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
import sys, os, urllib
import json
import xbmc, xbmcgui
from core.item import Item
from core import logger

__channel__ = "dialog"

def isGeneric():
    #realmente no lo es ya que import xbmc y xbmcgui
    return True 
 
def getMenu(listaControl):
    
    listaControlStr=[]
    for c in listaControl:
        listaControlStr.append(c.serialize())
    logger.info("[dialog] listaControl:" + str(listaControlStr))
    itemlist=[]
    for c in listaControl:
        if c.visible:
            itemlist.append(getControl(c,listaControlStr))
    return itemlist

def getControl(c,listaControlStr):
    #logger.info("[dialog] " + str(len(listaControl)))
    
    if c.type=="controlDEdit":
        titulo= c.label + ":" + (' ' * 5) + '[B]' + c.value + '[/B]'
        return Item(channel=__channel__, action="controlDEdit_click", title=titulo, url=c.id,extra= c.value, fulltitle=json.dumps(listaControlStr))
     
    elif c.type=="controlDRadioButton":
        if str(c.value).capitalize() in ['True', 'Si', 'Yes', 'Ok', '1']: 
            titulo= c.label + ":" + (' ' * 5) + '[B]Si[/B]'
        else: 
            titulo= c.label + ":" + (' ' * 5) + '[B]No[/B]'
        return Item(channel=__channel__, action="controlDRadioButton_click", title=titulo, url=c.id, fulltitle=json.dumps(listaControlStr))
    
    elif c.type=="controlDButton":
        if c.id=='_save_':
            return Item(channel="config_channel", title=c.label,action="save_settings", fulltitle=json.dumps(listaControlStr), extra=c.opcion) #c.opcion= canal q ha llamado a config_channel + '|' + action a ejecutar
        else:
            return Item(channel=c.opcion.split('|')[0], title=c.label,action=c.opcion.split('|')[1], url=c.id, fulltitle=json.dumps(listaControlStr), extra=c.id)
    
    elif c.type=="controlDLabel":
        titulo= (' ' * (59 - len(c.label)/2)) +'[I][B]' + c.label.encode('utf-8') + '[/B][/I]'
        return Item(channel=__channel__, title= titulo, action="cambiar_valor", url ="__None__", fulltitle=json.dumps(listaControlStr)) #Si se pulsa sobre el se vuelve a escribir el mismo itemlist
    
    elif c.type=="controlDNumerico":
        titulo= c.label + ":" + (' ' * 5) + '[B]' + c.value + '[/B]'
        return Item(channel=__channel__, action="controlDNumerico_click", title=titulo, url=c.id,extra= c.value, fulltitle=json.dumps(listaControlStr))
     
    elif c.type=="controlDLista":
        #logger.info("[dialog] lista: " + c.lvalues.encode('utf-8'))
        titulo= c.label + ":" + (' ' * 5) + '[B]' + c.lvalues.split('|')[int(c.value.encode('utf-8'))] + '[/B]'
        return Item(channel=__channel__, action="controlDLista_click", title=titulo, url=c.id, extra= c.lvalues.encode('utf-8'), fulltitle=json.dumps(listaControlStr))
    
        
def controlDEdit_click (item):  
    keyboard = xbmc.Keyboard(item.extra,item.title.split(':')[0])
    keyboard.doModal()
    if keyboard.isConfirmed():
        item.extra = keyboard.getText().decode('utf-8')    
    return cambiar_valor(item)
    
           
def controlDRadioButton_click (item):
    itemlist = []
    itemlist.append(Item(channel=__channel__, title="Si", url=item.url, action="cambiar_valor", extra="true", fulltitle=item.fulltitle))
    itemlist.append(Item(channel=__channel__, title="No", url=item.url, action="cambiar_valor", extra="false", fulltitle=item.fulltitle))
    return itemlist
    
def controlDNumerico_click (item):
    dialog = xbmcgui.Dialog()
    d = dialog.numeric(0, item.title.split(':')[0], item.extra)      
    if d!='': 
        item.extra=d
    return cambiar_valor(item)
    
def controlDLista_click (item):
    itemlist = []
    k=0
    for v in item.extra.split('|'):
        itemlist.append(Item(channel=__channel__, title=v, url=item.url, action="cambiar_valor", extra=str(k), fulltitle=item.fulltitle))
        k+=1
    return itemlist
 
def cambiar_valor(item):
    #Reconstruir la lista
    listaControlStr=json.loads(item.fulltitle)
    #logger.info("[dialog] fulltitle " + item.fulltitle)
    
    listaControl=[]
    for s in listaControlStr:
        c= Control()
        c.deserialize(s)
        listaControl.append(c)
        
    for c in listaControl:
        if c.id==item.url:
            c.value=item.extra
    return getMenu(listaControl)
  

    
class Control(object):
    type= ""
    id= ""
    label= ""
    value= ""
    visible= True
    enabled= True #No soportado de momento
    extra= ""
    opcion= ""
    lvalues= ""
        
    def __init__(self, type="", id="", label="", value="" , visible=True, enabled=True, extra="", opcion="", lvalues=""):
        self.type= type
        self.id= id
        self.label= label
        self.value= value
        self.visible=  str(visible).capitalize() in ['True', 'Si', 'Yes', 'Ok', '1']
        self.enabled=  str(enabled).capitalize() in ['True', 'Si', 'Yes', 'Ok', '1']
        self.extra= extra
        self.opcion= opcion
        self.lvalues= lvalues
        
    def serialize(self):
        separator = "|>|<|"
        devuelve = ""
        devuelve = devuelve + self.type + separator
        devuelve = devuelve + self.id + separator
        devuelve = devuelve + self.label + separator
        devuelve = devuelve + self.value + separator
        devuelve = devuelve + str(self.visible) + separator
        devuelve = devuelve + str(self.enabled) + separator
        devuelve = devuelve + self.extra + separator
        devuelve = devuelve + self.opcion + separator
        devuelve = devuelve + self.lvalues + separator
        return devuelve
    
    def deserialize(self,cadena):
        trozos=cadena.split("|>|<|")
        self.type = trozos[0]
        self.id = trozos[1]
        self.label = trozos[2]
        self.value = trozos[3]
        self.visible =  str(trozos[4]).capitalize() in ['True', 'Si', 'Yes', 'Ok', '1']
        self.enabled =  str(trozos[5]).capitalize() in ['True', 'Si', 'Yes', 'Ok', '1']
        self.extra = trozos[6]
        self.opcion = trozos[7]
        self.lvalues = trozos[8]