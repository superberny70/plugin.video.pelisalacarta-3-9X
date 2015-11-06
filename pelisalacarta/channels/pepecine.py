# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para Pepecine
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys
import ast

from core import logger
from core import config
from core import scrapertools
from core import jsontools
from core.item import Item
from servers import servertools

__adult__ = "false"
__category__ = "F,S"
__type__ = "generic"
__title__ = "Pepecine"
__channel__ = "pepecine"
__language__ = "ES"
__creationdate__ = "20151025"
__thumbnail__ ="https://d12.usercdn.com/i/02278/nwm6todp6yyk.png"
__url_base__ = "http://pepecine.com"

fanart_host= "https://d12.usercdn.com/i/02278/u875vjx9c0xs.png"


def isGeneric():
    return True

def mainlist(item):
    logger.info("[pepecine.py] mainlist")

    itemlist = []
    itemlist.append( myItem(channel=__channel__, action="listado", title="[COLOR 0xFFEB7600][B]Películas[/B][/COLOR]", 
                            url=urlparse.urljoin(__url_base__,"plugins/last_update_links.php?type=movie&offset=0&limit=30"), 
                            extra="movie", fanart=fanart_host, thumbnail="https://d5.usercdn.com/dl/i/02360/swdcjg65xzj0.png"))
    itemlist.append( myItem(channel=__channel__, action="sub_filtrar", title="     [COLOR 0xFFEB7600]Filtrar películas por género[/COLOR]", 
                            url=urlparse.urljoin(__url_base__,"plugins/last_update_links.php?type=movie&offset=0&limit=30"), 
                            extra="movie", fanart=fanart_host, thumbnail="https://d5.usercdn.com/dl/i/02360/k0x1sqi7d0sb.png"))
    itemlist.append( myItem(channel=__channel__, action="search", title="     [COLOR 0xFFEB7600]Buscar películas por título[/COLOR]", 
                            url=urlparse.urljoin(__url_base__,"plugins/last_update_links.php?type=movie&offset=0&limit=30"), 
                            extra="movie", fanart=fanart_host, thumbnail="https://d5.usercdn.com/dl/i/02360/196ccvz5nkfq.png"))
    
    itemlist.append( myItem(channel=__channel__, action="listado", title="[COLOR 0xFFEB7600][B]Series[/B][/COLOR]", 
                            url=urlparse.urljoin(__url_base__,"plugins/last_update_links.php?type=series&offset=0&limit=30"), 
                            extra="series", fanart=fanart_host, thumbnail="https://d5.usercdn.com/dl/i/02360/a99fzwbqdaen.png"))
    itemlist.append( myItem(channel=__channel__, action="sub_filtrar", title="     [COLOR 0xFFEB7600]Filtrar series por género[/COLOR]", 
                            url=urlparse.urljoin(__url_base__,"plugins/last_update_links.php?type=series&offset=0&limit=30"), 
                            extra="series", fanart=fanart_host, thumbnail="https://d5.usercdn.com/dl/i/02360/evnj5mxsvh0h.png"))
    itemlist.append( myItem(channel=__channel__, action="search", title="     [COLOR 0xFFEB7600]Buscar series por título[/COLOR]", 
                            url=urlparse.urljoin(__url_base__,"plugins/last_update_links.php?type=series&offset=0&limit=30"), 
                            extra="series", fanart=fanart_host, thumbnail="https://d5.usercdn.com/dl/i/02360/him4zov0aa37.png"))
    itemlist.append( myItem(channel=__channel__, action="listado", title="     [COLOR 0xFFEB7600]Ultimos capítulos actualizados[/COLOR]",
                            url=urlparse.urljoin(__url_base__,"plugins/combined_json.php?&offset=0&limit=30&type=series"), 
                            extra="series_novedades", fanart=fanart_host, thumbnail="https://d5.usercdn.com/dl/i/02360/a99fzwbqdaen.png"))
    
    #itemlist.append( myItem( channel=__channel__, action="test", title="Test", url="http://pepecine.com/series-online/8763-breaking-bad/seasons/1/episodes/7", extra="series", fanart=fanart_host ) )
    return itemlist
 
def sub_filtrar(item):
    logger.info("[pepecine.py] sub_filtrar")
    itemlist=[]
    generos=("acción","animación","aventura","ciencia ficción","comedia","crimen",
             "documental","drama","familia","fantasía","guerra","historia","misterio",
             "música","musical","romance","terror","thriller","western")
    thumbnail=('https://d12.usercdn.com/i/02278/spvnq8hghtok.jpg',
               'https://d12.usercdn.com/i/02278/olhbpe7phjas.jpg',
               'https://d12.usercdn.com/i/02278/8xm23q2vewtt.jpg',
               'https://d12.usercdn.com/i/02278/o4vuvd7q4bau.jpg',
               'https://d12.usercdn.com/i/02278/v7xq7k9bj3dh.jpg',
               'https://d12.usercdn.com/i/02278/yo5uj9ff7jmg.jpg',
               'https://d12.usercdn.com/i/02278/ipeodwh6vw6t.jpg',
               'https://d12.usercdn.com/i/02278/0c0ra1wb11ro.jpg',
               'https://d12.usercdn.com/i/02278/zn85t6f2oxdv.jpg',
               'https://d12.usercdn.com/i/02278/ipk94gsdqzwa.jpg',
               'https://d12.usercdn.com/i/02278/z5hsi6fr4yri.jpg',
               'https://d12.usercdn.com/i/02278/nq0jvyp7vlb9.jpg',
               'https://d12.usercdn.com/i/02278/tkbe7p3rjmps.jpg',
               'https://d12.usercdn.com/i/02278/is60ge4zv1ve.jpg',
               'https://d12.usercdn.com/i/02278/86ubk310hgn8.jpg',
               'https://d12.usercdn.com/i/02278/ph1gfpgtljf7.jpg',
               'https://d12.usercdn.com/i/02278/bzp3t2edgorg.jpg',
               'https://d12.usercdn.com/i/02278/31i1xkd8m30b.jpg',
               'https://d12.usercdn.com/i/02278/af05ulgs20uf.jpg')

    for g, t in zip(generos,thumbnail):
        url=item.url + "&genre=" + g
        itemlist.append( myItem(channel=__channel__, action="listado",title='[COLOR 0xFFEB7600]' + g.capitalize() + '[/COLOR]',url=url,extra=item.extra,thumbnail=t,fanart=fanart_host) )
   
    return itemlist 

def search(item,texto):
    logger.info("[pepecine.py] search:" + texto)
    item.url = item.url + "&query=" + texto 
    return listado(item) 

def listado(item):
    #import json
    logger.info("[pepecine.py] listado")
    itemlist = []
    
    try:
        data_dict = jsontools.load_json(scrapertools.cache_page(item.url))
    except:
        return itemlist # Devolvemos lista vacia
        
    offset= scrapertools.get_match(item.url,'offset=(\d*)')
    limit= scrapertools.get_match(item.url,'limit=(\d*)')
       
    for i in data_dict["result"]:
        infoLabels={}
        plot={}
        
        if item.extra=="movie":
            action="get_movie"
            title='[COLOR 0xFFFFE6CC]'  + i["title"] + '[/COLOR] [COLOR 0xFFFFCE9C](' + i['year'] + ')[/COLOR]'
            url= urlparse.urljoin(__url_base__,"peliculas-online/" + str(i["id"])) #+"-"+i["title"]).lower().replace(" ","-")))
        elif item.extra=="series": 
            action="get_temporadas"
            title='[COLOR 0xFFFFE6CC]'  + i["title"] + '[/COLOR]'
            infoLabels['tvshowtitle']= i["title"]
            url= urlparse.urljoin(__url_base__,"series-online/" + str(i["id"])) #+"-"+i["title"]).lower().replace(" ","-")))
        else: #item.extra=="series_novedades": 
            action="get_only_episodio"
            infoLabels['season']=i['season']
            infoLabels['episode']=i['episode'].zfill(2)
            item.extra=infoLabels["season"] + "x" + infoLabels["episode"]
            infoLabels['tvshowtitle']= i["title"]
            title='[COLOR 0xFF994D00]'  + i["title"] + '[/COLOR] [COLOR 0xFFFFCE9C]'  + item.extra + '[/COLOR] [COLOR 0xFFFFE6CC](' + i['label'] + ')[/COLOR]'
            url= urlparse.urljoin(__url_base__,"series-online/" + str(i["id"])) #+"-"+i["title"]).lower().replace(" ","-"))) 
        
        if i.has_key("poster") and i["poster"]: 
            thumbnail=re.compile("/w\d{3}/").sub("/w500/",i["poster"])
        else:
            thumbnail= item.thumbnail
        if i.has_key("background") and i["background"]: 
            fanart= i["background"]
        else:
            fanart= item.fanart
        
        # Rellenamos el diccionario de infoLabels
        infoLabels['title_id']=i['id'] # title_id: identificador de la pelicula/serie en pepecine.com
        infoLabels['titleraw']= i["title"] # titleraw: titulo de la pelicula/serie sin formato
        if i['genre']: infoLabels['genre']=i['genre']
        if i['year']: infoLabels['year']=i['year']
        if i['tagline']: infoLabels['plotoutline']=i['tagline']
        if i['plot']: 
            infoLabels['plot']=i['plot']
        else:
            infoLabels['plot']=""
        if i['runtime']: infoLabels['duration']=int(i['runtime'])*60
        if i['imdb_rating']:
            infoLabels['rating']=i['imdb_rating']
        elif i['tmdb_rating']:
            infoLabels['rating']=i['tmdb_rating']
        
        if infoLabels: 
            plot['infoLabels']=infoLabels
        
        itemlist.append( myItem( channel=__channel__, action=action, title=title, url=url, extra=item.extra, fanart=fanart, plot=str(plot), thumbnail=thumbnail, viewmode="movie_with_plot") )
    
    # Paginacion
    if int(data_dict["total_results"]) == int(limit):
        url=item.url.replace('offset='+offset,'offset='+ str(int(offset)+ int(limit)))
        itemlist.append( myItem( channel=__channel__, action="listado", title="[COLOR 0xFF994D00]>> [/COLOR] [COLOR 0xFFFFCE9C]Pagina siguiente[/COLOR][COLOR 0xFF994D00]  >>[/COLOR]", url=url, extra=item.extra, fanart=fanart_host) )
    
    return itemlist      
              
def get_movie(item):
    logger.info("[pepecine.py] get_movie")
    itemlist = []
    plot={}
       
    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)","",scrapertools.cache_page(item.url))
    patron ='vars.title =(.*?)};'
    try:
        data_dict= jsontools.load_json(scrapertools.get_match(data,patron) +'}')
    except:
        return itemlist # Devolvemos lista vacia
    
    infoLabels=get_infoLabels(item)
    if data_dict.has_key("actor"):
        cast=[]
        rol=[]
        for actor in data_dict["actor"]:
            cast.append(actor['name'])
            rol.append(actor['pivot']['char_name'])
        infoLabels['cast'] = cast
        infoLabels['castandrole'] = zip(cast,rol)
        
    if data_dict.has_key("writer"):
        writers_list=[]
        for writer in data_dict["writer"]:
            writers_list.append(writer['name'])
        infoLabels['writer'] = ", ".join(writers_list )
        
    if data_dict.has_key("director"):    
        director_list=[]
        for director in data_dict["director"]:
            director_list.append(director['name'])    
        infoLabels['director'] = ", ".join(director_list )
    
    
    plot['infoLabels']= infoLabels
    item.plot = str(plot)
    item.url=str(data_dict["link"])
    
    return findvideos (item)
    
def get_temporadas(item):
    logger.info("[pepecine.py] get_temporadas")
    itemlist = []
    plot = {}
    infoLabels = {}
    
    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)","",scrapertools.cache_page(item.url))
    patron ='vars.title =(.*?)};'
    try:
        data_dict= jsontools.load_json(scrapertools.get_match(data,patron) +'}')
    except:
        return itemlist # Devolvemos lista vacia
    
    if item.extra == "serie_add":
        item.extra=str(data_dict['tmdb_id'])
        item.url=str(data_dict["link"])
        infoLabels['titleraw'] = data_dict["title"]
        infoLabels['tvshowtitle'] = data_dict["title"]
        infoLabels['title_id'] = data_dict['id']
        plot['infoLabels']= infoLabels
        item.plot = str(plot)
        itemlist= get_episodios(item)
    else:
        infoLabels=get_infoLabels(item)
        if data_dict.has_key("actor"):
            cast=[]
            rol=[]
            for actor in data_dict["actor"]:
                cast.append(actor['name'])
                rol.append(actor['pivot']['char_name'])
            infoLabels['cast'] = cast
            infoLabels['castandrole'] = zip(cast,rol)
            
        if data_dict.has_key("writer"):    
            writers_list=[]
            for writer in data_dict["writer"]:
                writers_list.append(writer['name'])
            infoLabels['writer'] = ", ".join(writers_list )
        
        if data_dict.has_key("director"):  
            director_list=[]
            for director in data_dict["director"]:
                director_list.append(director['name'])    
            infoLabels['director'] = ", ".join(director_list )
    
        if len(data_dict["season"]) == 1: 
            # Si solo hay una temporada ...
            item.extra=str(data_dict['tmdb_id'])
            item.url=str(data_dict["link"])
            if infoLabels.has_key("plot"):
                plot['infoLabels']= infoLabels
                item.plot = str(plot)
            itemlist= get_episodios(item)
        else: #... o si hay mas de una temporada y queremos el listado por temporada...
            item.extra=str(data_dict['tmdb_id'])
            data_dict["season"].sort(key=lambda x:(x['number'])) # ordenamos por numero de temporada
            for season in data_dict["season"]:
                url= filter(lambda l: l["season"]== season['number'],data_dict["link"]) #filtramos enlaces por temporada
                if url:
                    if season['overview']: infoLabels['plot']=season['overview']
                    if season['number']: infoLabels['season']=season['number']
                    if season["poster"]: item.thumbnail=re.compile("/w\d{3}/").sub("/w500/",season["poster"])
                    if season["release_date"]: infoLabels['premiered']= season['release_date']
                    
                    if infoLabels.has_key("plot"):
                        plot['infoLabels']= infoLabels
                        item.plot = str(plot)
                    title=item.title + ' [COLOR 0xFFFFCE9C]' + season["title"].lower().replace('season','temporada').capitalize() + '[/COLOR]'
                    
                    itemlist.append( myItem( channel=__channel__, action="get_episodios", title=title, url=str(url), extra=item.extra, fanart=item.fanart, plot=item.plot, thumbnail=item.thumbnail, viewmode="movie_with_plot") )
            
            if config.get_library_support() and itemlist:
                url= urlparse.urljoin(__url_base__,"series-online/" + str(data_dict['id']))
                itemlist.append( myItem(channel=__channel__, title="[COLOR 0xFFe5ffcc]Añadir esta serie a la biblioteca[/COLOR]", url=url, action="add_serie_to_library", extra='episodios###serie_add', show= data_dict["title"], thumbnail = 'https://d5.usercdn.com/dl/i/02360/a99fzwbqdaen.png'))

    return itemlist      

def get_only_episodio(item):
    logger.info("[pepecine.py] get_only_episodio")
    itemlist = []
    plot={}
    
    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)","",scrapertools.cache_page(item.url))
    patron ='vars.title =(.*?)};'
    try:
        data_dict= jsontools.load_json(scrapertools.get_match(data,patron) +'}')
    except:
        return itemlist # Devolvemos lista vacia
        
    try:
        from core.tmdb import Tmdb
        oTmdb= Tmdb(id_Tmdb= data_dict['tmdb_id'],tipo="tv")
    except:
        pass
    
    infoLabels=get_infoLabels(item)
    cast=[]
    rol=[]
    for actor in data_dict["actor"]:
        cast.append(actor['name'])
        rol.append(actor['pivot']['char_name'])
    
    writers_list=[]
    for writer in data_dict["writer"]:
        writers_list.append(writer['name'])
        
    director_list=[]
    for director in data_dict["director"]:
        director_list.append(director['name'])    
    
    infoLabels['cast'] = cast
    infoLabels['castandrole'] = zip(cast,rol)
    infoLabels['writer'] = ", ".join(writers_list )
    infoLabels['director'] = ", ".join(director_list )
    infoLabels['season'], infoLabels['episode']= item.extra.split('x')
    try:
        # añadimos sinopsis e imagenes del capitulo
        datos_tmdb=oTmdb.get_episodio(temporada= infoLabels['season'],capitulo= infoLabels['episode'])
        if datos_tmdb["episodio_sinopsis"] !="": infoLabels['plot']= datos_tmdb["episodio_sinopsis"]
        if datos_tmdb["episodio_imagen"] !="": item.thumbnail= datos_tmdb["episodio_imagen"]
        #if datos_tmdb["episodio_titulo"] !="": title = title + " [COLOR 0xFFFFE6CC]" + datos_tmdb["episodio_titulo"].replace('\t','') + "[/COLOR]"
    except:
            pass
    
    def cap(l): 
        try:
            temporada_link = int(l["season"])
            capitulo_link = int(l['episode'])
        except:
            return False
        return True if temporada_link== int(infoLabels['season'])  and capitulo_link == int(infoLabels['episode']) else False    
    item.url= str(filter(cap, data_dict["link"])) #filtramos enlaces por capitulo
    
    plot['infoLabels']= infoLabels
    item.plot = str(plot)
    item.extra=str(data_dict['tmdb_id'])
    
    return findvideos(item)

def get_episodios(item):
    logger.info("[pepecine.py] get_episodios")
    itemlist = []
    plot={}
    
    try:
        from core.tmdb import Tmdb
        oTmdb= Tmdb(id_Tmdb= item.extra,tipo="tv")
    except:
        pass
    
    infoLabels=get_infoLabels(item)

    lista_links=ast.literal_eval(item.url) 
    # Agrupar enlaces por episodios  temXcap
    temXcap_dict={}
    for link in lista_links:
        title_id = link['id']
        id= str(link['season']) + "x" + str(link['episode']).zfill(2)
        if temXcap_dict.has_key(id):
            l= temXcap_dict[id]
            l.append(link)
            temXcap_dict[id]= l
        else:
            temXcap_dict[id]= [link]
            
    # Ordenar lista de enlaces por temporada y capitulo
    temXcap_list=temXcap_dict.items()
    temXcap_list.sort(key=lambda x: (int(x[0].split("x")[0]),int(x[0].split("x")[1])))
    for episodio in temXcap_list:
        title= '[COLOR 0xFF994D00]' + infoLabels['titleraw'] + '[/COLOR] [COLOR 0xFFFFCE9C](' + episodio[0] + ')[/COLOR]'
        infoLabels['season'], infoLabels['episode']=  episodio[0].split('x')
        try:
            # añadimos sinopsis e imagenes para cada capitulo
            datos_tmdb=oTmdb.get_episodio(temporada= infoLabels['season'],capitulo= infoLabels['episode'])
            if datos_tmdb["episodio_sinopsis"] !="": infoLabels['plot']= datos_tmdb["episodio_sinopsis"]
            if datos_tmdb["episodio_imagen"] !="": item.thumbnail= datos_tmdb["episodio_imagen"]
            if datos_tmdb["episodio_titulo"] !="": title = title + " [COLOR 0xFFFFE6CC]" + datos_tmdb["episodio_titulo"].replace('\t','') + "[/COLOR]"
        except:
                pass
        
        if infoLabels.has_key("plot"):
            plot['infoLabels']= infoLabels
            item.plot = str(plot)
        itemlist.append( myItem( channel=__channel__, action="findvideos", title=title, url=str(episodio[1]), extra=item.extra, show=infoLabels['tvshowtitle'], fanart=item.fanart, plot=item.plot, thumbnail=item.thumbnail, viewmode="movie_with_plot") )
    
    if config.get_library_support() and itemlist:
        url= urlparse.urljoin(__url_base__,"series-online/" + str(title_id))
        #url= urlparse.urljoin(__url_base__,"series-online/" + (str(infoLabels['title_id']) +"-"+ infoLabels['titleraw']))
        itemlist.append( myItem(channel=__channel__, title="[COLOR 0xFFe5ffcc]Añadir esta serie a la biblioteca[/COLOR]", url=url, action="add_serie_to_library", extra='episodios###serie_add', show= infoLabels['tvshowtitle'], thumbnail = 'https://d5.usercdn.com/dl/i/02360/a99fzwbqdaen.png'))

    
    return itemlist
       
def findvideos(item):
    logger.info("[pepecine.py] findvideos")
    itemlist = []
 
    
    for link in ast.literal_eval(item.url):
        url= link["url"]
        idioma=link["label"]
        calidad=(' [COLOR 0xFFFFCE9C][' +link["quality"]+ '][/COLOR]') if link["quality"] !="?" else ""
        video= find_videos(link["url"])
    
        if video["servidor"]!="":
            servidor=video["servidor"]
            url=video["url"]
            title= "[COLOR 0xFF994D00]Ver en " + servidor.capitalize() + "[/COLOR]" + calidad + ' [COLOR 0xFFFFE6CC](' + idioma + ')[/COLOR]'
            itemlist.append( myItem(channel=__channel__, action="play", viewmode="list", server=servidor, title=title, thumbnail=item.thumbnail, fanart= item.fanart, plot= item.plot, url=url, folder=False) )
            
    return itemlist
    
def find_videos(url):
    #logger.info("[pepecine.py] find_videos") 
    ret = {'titulo':"",
           'url':"",
           'servidor':""}
    
    # Ejecuta el find_videos en cada servidor hasta que encuentra una coicidencia
    for serverid in servertools.ENABLED_SERVERS:
        try:
            servers_module = __import__("servers."+serverid)
            server_module = getattr(servers_module,serverid)
            devuelve= server_module.find_videos(url)
            
            if devuelve:
                ret["titulo"]=devuelve[0][0]
                ret["url"]=devuelve[0][1]
                ret["servidor"]=devuelve[0][2]
                # reordenar el listado, es probable q el proximo enlace sea del mismo servidor
                servertools.ENABLED_SERVERS.remove(serverid)
                servertools.ENABLED_SERVERS.insert(0,serverid)
                break
           
        except ImportError:
            logger.info("No existe conector para #"+serverid+"#")
            #import traceback
            #logger.info(traceback.format_exc())
        except:
            logger.info("Error en el conector #"+serverid+"#")
            import traceback
            logger.info(traceback.format_exc())
    
    return ret
    
    pass
    
def episodios(item):
    # Necesario para las actualizaciones automaticas
    return get_temporadas(myItem(url=item.url, show=item.show, extra= "serie_add"))
 
def get_infoLabels(item):
    try:
        return ast.literal_eval(item.plot)['infoLabels']
    except:
        ret={} 
        if item.title:
            ret["title"]=item.title
            ret["titleraw"]=item.title
            ret["tvshowtitle"]=item.title
        return ret
    

 
    
class myItem(Item):
##########################################################################################
# Hereda de Item y añade:
#   - Formato para el titulo en las versiones xbmc, plex y html. En realidad deberia ser el launcher
#     de cada plataforma el que formateara las etiquetas segun su sistema.
#   - El parametro 'plot' incluye las infoLabels en el caso de que la plataforma sea XBMC/KODI o solo 
#     la sinopsis en caso contrario. En realidad deberia ser xbmctools o equivalente quien se encargara de interpretarlo.
##########################################################################################
    import re
    import ast

    def __init__(self, channel="", title="", url="", page="", thumbnail="", plot="", duration="", fanart="", action="", server="directo", extra="", show="", category = "" , language = "" , subtitle="" , folder=True, context = "",totalItems = 0, overlay = None, type="", password="", fulltitle="", viewmode="list" ):
        Item.__init__(self, channel=channel, title=self.format_text(title), url=url, page=page, thumbnail=thumbnail, 
                      plot=self.format_plot(plot), duration=duration, fanart=fanart, action=action, server=server, extra=extra, 
                      show=show, category =category , language =language , subtitle=subtitle , folder=folder, 
                      context = context,totalItems = totalItems, overlay = overlay, type=type, password=password, 
                      fulltitle=fulltitle, viewmode=viewmode )
        
    def set_title(self,title):
        self.title=format_text(title)
        
    #Devuelve el ítem en un string con todos los campos, para ver en el log
    def tostring(self):
      devuelve=""
      for property, value in vars(self).iteritems():
        if not devuelve:
          devuelve = property + "=["+str(value)+"]"
        else:
          devuelve = devuelve + " ," + property + "=["+str(value)+"]"

      return devuelve
        
    def format_text(self,text):
        '''
        [B]bold[/B] - bold text.
        [I]italics[/I] - italic text.
        [CR] - carriage return (line break).
        [COLOR red]red text[/COLOR] - colored text. http://www.w3schools.com/tags/ref_colornames.asp
        [COLOR 0xAARRGGBB]color text[/COLOR] colored text. http://www.w3schools.com/tags/ref_colorpicker.asp
        
        No implementados aun:
        [UPPERCASE]force text uppercase[/UPPERCASE] - force text to uppercase.
        [LOWERCASE]Force Text Lowercase[/LOWERCASE] - force text to lowercase.
        [CAPITALIZE]Force first letter to uppercase[/CAPITALIZE] - makes the first letter of a sentence a capital letter (Isengard only).
        '''
        
        bbcode= (('[B]','<b>'),
                 ('[/B]','</b>'),
                 ('[I]','<i>'),
                 ('[/I]','</i>'),
                 ('[/COLOR]','</span>'),
                 ('[UPPERCASE]',''),
                 ('[/UPPERCASE]',''),
                 ('[LOWERCASE]',''),
                 ('[/LOWERCASE]',''),
                 ('[CAPITALIZE]',''),
                 ('[/CAPITALIZE]',''),
                 ('[CR]','<br>'))
        
        if not text or config.is_xbmc():
            return text
        elif config.get_platform().startswith("plex") or config.get_platform().startswith("mediaserver"):
            # Plex o html: adaptar bbcode (basado de la funcion bbcode_kodi2html de robalo) 
            
            # COLOR
            color_orig= ('yellow', 'white')
            color_sust= ('gold', 'auto')
            colores = re.findall(r'\[COLOR\s([^\]]+)\]',text)
            for color in colores:
                tag_orig = '\[COLOR\s' + color + '\]'
                if color.startswith('0x'):
                    color= "#" + color[4:]
                elif color in color_orig:
                    color= color_sust[color_orig.index(color)]
                text = re.sub(tag_orig, '<span style="color:' + color + '">', text)
            # Otros TAGs
            for b in bbcode:
                text = text.replace(b[0],b[1])
        else:
            # Plataforma desconocida: eliminar bbcode
            text = re.sub(r'\[COLOR\s([^\]]+)\]','', text)
            for b in bbcode:
                text = text.replace(b[0],'')
            
        return text           
    
    def format_plot(self,plot):
        ret= plot
        
        if not plot:
            return ""
        elif config.is_xbmc():
            try:
                # Comprobamos si existe la funcion xbmctools.set_infoLabels()
                from platformcode import xbmctools
                if hasattr(xbmctools, "set_infoLabels"):
                    return ret
            except:
                pass
                
        # Si no es xbmc o si no existe xbmctools.set_infoLabels():
        #       intentamos recuperar la sinopsis del infoLabels
        try:
            if plot.startswith("{'infoLabels'"):
                infoLabels=ast.literal_eval(plot)['infoLabels']
                ret= infoLabels['plot']
        except:
            pass

        return ret
        