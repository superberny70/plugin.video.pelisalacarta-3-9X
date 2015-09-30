# -*- coding: utf-8 -*-

class Item(object):
    channel = ""
    title = ""
    url = ""
    page = ""
    thumbnail = ""
    plot = ""
    duration = 0
    fanart = ""
    folder = True
    action = ""
    server = "directo"
    extra = ""
    show = ""
    category = ""
    childcount = 0
    language = ""
    type = ""
    context = ""
    subtitle = ""
    totalItems =0
    overlay = ""
    password = ""
    fulltitle = ""
    viewmode = "list"
    hd = False
    quality = ""
    refered_action = ""
    
    def __init__(self,  channel = "", title = "", url = "", page = "", thumbnail = "", plot = "", duration = 0, fanart = "", folder = True, action = "", server = "directo" , extra = "", show = "", category = "", childcount = 0, language = "", type = "", context = "", subtitle = "", totalItems =0, overlay = "", password = "", fulltitle = "", viewmode = "list", hd = False, quality="", refered_action = ""):   
      
      self.channel = channel
      self.title = title
      self.url = url
      if page=="":
        self.page = url
      else:
        self.page = page
      
      self.thumbnail = thumbnail
      self.plot = plot
      self.duration = self.StringToTime(duration)
      self.fanart = fanart
      self.folder = bool(folder)
      self.action = action
      self.server = server
      self.extra = extra
      self.show = show
      self.category = category
      self.childcount = int(childcount)
      self.language = language
      self.type = type      
      self.context = context
      self.subtitle = subtitle
      self.totalItems = int(totalItems)
      self.overlay = overlay
      self.password = password
      self.fulltitle = fulltitle
      self.viewmode = viewmode
      self.hd = bool(hd)
      self.quality=quality
      self.refered_action = refered_action


    def StringToTime(self,string):
      import datetime
      import time
      import math
      Segundos=0
      
      #Si el valor recivido es un Strign, extrae los Segundos, Minutos y Horas y lo pasa a Segundos.
      #Formatos válidos: H:M:S, M:S, S
      if type(string)==str:
        Segundos = 0
        Minutos = 0
        Horas = 0
        for x, tiempo in enumerate(string.split(":")):
          if string.count(":") - x ==0:
            Segundos = int(tiempo)
          if string.count(":") - x ==1:
            Minutos = int(tiempo)
          if string.count(":") - x ==2:
            Horas = int(tiempo)
        Segundos = Segundos + (Minutos*60) + (Horas*60*60)
      else:
        Segundos=string
      return int(Segundos)

    #Devuelve el ítem en un string con todos los campos, para ver en el log
    def tostring(self):
      devuelve=""
      for property, value in vars(self).iteritems():
        if not devuelve:
          devuelve = property + "=["+str(value)+"]"
        else:
          devuelve = devuelve + " ," + property + "=["+str(value)+"]"

      return devuelve
    
    #Serializa todas las propiedades.
    def serialize(self):
        separator = "|"
        devuelve = ""
        import base64
        import urllib
        for property, value in vars(self).iteritems():
          if str(value)=="False":value=""
          devuelve = devuelve + base64.b64encode(property + "=" + str(value)) + separator
        return urllib.quote_plus(base64.b64encode(devuelve))
        
    #Deserializa todas las propiedades.
    def deserialize(self,cadena): 
        separator = "|"
        import base64
        import urllib
        for encoded in base64.b64decode(urllib.unquote_plus(cadena)).split(separator):
          decoded = base64.b64decode(encoded)
          if len(decoded.split("=")) > 1:
            property = decoded.split("=")[0]
            value = decoded.replace(property+"=","",1)
            exec "self."+property+" = type(self."+property+")(value)"
          
