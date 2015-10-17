# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------------------------------------------------
# Scraper para pelisalacarta, palco y otros plugin de XBMC/Kodi basado en el Api de https://www.themoviedb.org/
#   version: 1.2
#   Uso:
#   Metodos constructores:
#    Tmdb(texto_buscado, tipo)
#        Parametros:
#            texto_buscado:(str) Texto o parte del texto a buscar
#            tipo: ("movie" o "tv") Tipo de resultado buscado peliculas o series. Por defecto "movie"
#            (opcional) idioma_busqueda: (str) codigo del idioma segun ISO 639-1
#            (opcional) include_adult: (bool) Se incluyen contenidos para adultos en la busqueda o no. Por defecto 'False'
#            (opcional) year: (str) Año de lanzamiento.
#            (opcional) page: (int) Cuando hay muchos resultados para una busqueda estos se organizan por paginas. 
#                            Podemos cargar la pagina que deseemos aunque por defecto siempre es la primera.
#        Return:
#            Esta llamada devuelve un objeto Tmdb que contiene la primera pagina del resultado de buscar 'texto_buscado'
#            en la web themoviedb.org. Cuantos mas parametros opcionales se incluyan mas precisa sera la busqueda.
#            Ademas el objeto esta inicializado con el primer resultado de la primera pagina de resultados.
#    Tmdb(id_Tmdb,tipo)
#       Parametros:
#           id_Tmdb: (str) Codigo identificador de una determinada pelicula o serie en themoviedb.org
#           tipo: ("movie" o "tv") Tipo de resultado buscado peliculas o series. Por defecto "movie"
#           (opcional) idioma_busqueda: (str) codigo del idioma segun ISO 639-1
#       Return:
#           Esta llamada devuelve un objeto Tmdb que contiene el resultado de buscar una pelicula o serie con el identificador id_Tmd
#           en la web themoviedb.org.
#    Tmdb(external_id, external_source, tipo)
#       Parametros:
#           external_id: (str) Codigo identificador de una determinada pelicula o serie en la web referenciada por 'external_source'.
#           external_source: (Para series:"imdb_id","freebase_mid","freebase_id","tvdb_id","tvrage_id"; Para peliculas:"imdb_id")
#           tipo: ("movie" o "tv") Tipo de resultado buscado peliculas o series. Por defecto "movie"
#           (opcional) idioma_busqueda: (str) codigo del idioma segun ISO 639-1
#       Return:
#           Esta llamada devuelve un objeto Tmdb que contiene el resultado de buscar una pelicula o serie con el identificador 'external_id' de
#           la web referenciada por 'external_source' en la web themoviedb.org.
#
#   Metodos principales:
#    get_id(): Retorna un str con el identificador Tmdb de la pelicula o serie cargada o una cadena vacia si no hubiese nada cargado.
#    get_sinopsis(): Retorna un str con la sinopsis de la serie o pelicula cargada.
#    get_poster (tipo_respuesta,size): Obtiene el poster o un listado de posters.
#    get_backdrop (tipo_respuesta,size): Obtiene una imagen de fondo o un listado de imagenes de fondo.
#    get_fanart (tipo,idioma,temporada): Obtiene un listado de imagenes del tipo especificado de la web Fanart.tv
#    get_episodio (temporada, capitulo): Obtiene un diccionario con datos especificos del episodio.
#   
#   Otros metodos:
#    load_resultado(resultado, page): Cuando la busqueda devuelve varios resultados podemos seleccionar que resultado concreto y de que pagina cargar los datos.
#
# Informacion sobre la api : http://docs.themoviedb.apiary.io
#--------------------------------------------------------------------------------------------------------------------------------------------
import urllib2
import traceback

from core import logger

class Tmdb(object):
    
    dic_generos={}
    
    busqueda={'id':"",
              'texto':"",
              'tipo':'movie', 
              'idioma':"es",
              'include_adult': "false",
              'year':""}
    
    page= 1
    results= []
    total_pages=0
    total_results= 0
    
    result={'adult':"",
            'backdrop_path':"", # ruta imagene de fondo mas valorada
            #belongs_to_collection
            'budget':"", # Presupuesto
            'genres':[], # lista de generos 
            'homepage':"", 
            'id':"", 'imdb_id':"", 'freebase_mid':"", 'freebase_id':"", 'tvdb_id':"", 'tvrage_id':"", # IDs equivalentes
            'original_language':"",
            'original_title':"",
            'overview':"", # sinopsis
            #popularity
            'poster_path':"", 
            #production_companies
            #production_countries
            'release_date':"",
            'revenue':"", # recaudacion
            #runtime
            #spoken_languages
            'status':"",
            'tagline':"", 
            'title':"",
            'video':"", # ("true" o "false") indica si la busqueda movies/id/videos devolvera algo o no
            'vote_average':"",
            'vote_count':"",
            'name':"", # nombre en caso de personas o series (tv)
            'profile_path':"", # ruta imagenes en caso de personas
            'known_for':{}, #Diccionario de peliculas en caso de personas (id_pelicula:titulo)
            'images_backdrops':[], 
            'images_posters':[],
            'images_profiles':[],
            'videos':[] 
            }
            
    fanart={}
    
    temporada={}
               

    
    def __search(self, index_resultado=0, page=1):
        # http://api.themoviedb.org/3/search/movie?api_key=57983e31fb435df4df77afb854740ea9&query=superman&language=es&include_adult=false&page=1
        url='http://api.themoviedb.org/3/search/%s?api_key=57983e31fb435df4df77afb854740ea9&query=%s&language=%s&include_adult=%s&page=%s' %(self.busqueda["tipo"], self.busqueda["texto"].replace(' ','%20') , self.busqueda["idioma"], self.busqueda["include_adult"], str(page))
        if self.busqueda["year"] !='': url+= '&year=' + self.busqueda["year"] 
        buscando= self.busqueda["texto"].capitalize()
        
        logger.info("[Tmdb.py] Buscando '" + buscando + "' en pagina " + str(page))
        #print url
        response_dic= self.__get_json(url)
                    
        self.total_results= response_dic["total_results"]
        self.total_pages= response_dic["total_pages"]
        
        if self.total_results > 0:
            self.results=response_dic["results"]
           
        if len(self.results) >0 :
            self.__leer_resultado(self.results[index_resultado])
        else:
            # No hay resultados de la busqueda
            logger.info("[Tmdb.py] La busqueda de '" + buscando + "' no dio resultados para la pagina " + str(page))

    def __by_id(self,source="tmdb"):
        
        if source=="tmdb":
            # http://api.themoviedb.org/3/movie/1924?api_key=57983e31fb435df4df77afb854740ea9&language=es&append_to_response=images,videos,external_ids&include_image_language=es,null
            url='http://api.themoviedb.org/3/%s/%s?api_key=57983e31fb435df4df77afb854740ea9&language=%s&append_to_response=images,videos,external_ids&include_image_language=%s,null' %(self.busqueda["tipo"], self.busqueda["id"], self.busqueda["idioma"], self.busqueda["idioma"])
            buscando= "id_Tmdb: " + self.busqueda["id"]
            
        else:
            # http://api.themoviedb.org/3/find/%s?external_source=imdb_id&api_key=57983e31fb435df4df77afb854740ea9  
            url='http://api.themoviedb.org/3/find/%s?external_source=%s&api_key=57983e31fb435df4df77afb854740ea9&language=%s' %(self.busqueda["id"], source, self.busqueda["idioma"])
            buscando= source.capitalize() + ": " + self.busqueda["id"]
             
        logger.info("[Tmdb.py] Buscando " + buscando)    
        #print url
        resultado=self.__get_json(url)
        
        if source!="tmdb":
            if self.busqueda["tipo"]=="movie":
                resultado= resultado["movie_results"]
            else:
                resultado= resultado["tv_results"]
            if len(resultado) >0 :
                resultado=resultado[0]
            
        if len(resultado) >0 :
            if self.total_results==0:
                self.results.append(resultado)
                self.total_results= 1
                self.total_pages= 1
            #print resultado
            self.__leer_resultado(resultado)
            
        else: # No hay resultados de la busqueda
            logger.info("[Tmdb.py] La busqueda de " + buscando + " no dio resultados.")
     
    def __get_json(self,url):
        try:
            headers = {'Accept': 'application/json'}
            request = urllib2.Request(url , headers=headers)
            response_body = urllib2.urlopen(request).read()
        except:
            logger.info("[Tmdb.py] Fallo la busqueda")
            logger.info(traceback.format_exc())
            return None
        try:    
            try:
                from core import jsontools # 1ª opcion utilizar jsontools.py ...
                return jsontools.load_json(response_body)
            except:
                import json # ... y si falla probar con el json incluido
                return json.loads(response_body)
        except:
            logger.info("[Tmdb.py] Fallo json")
            logger.info(traceback.format_exc())
            return None
            
    def __inicializar(self):    
        # Inicializamos todos los atributos
        self.busqueda["texto"]=""
        self.busqueda["idioma"]='es'
        self.busqueda["include_adult"]='false'
        self.busqueda["year"]=''
        
        self.page= 1
        self.results= []
        self.total_pages=0
        self.total_results= 0
        
        for i in (self.result, self.fanart, self.temporada):
            for k in self.result.keys():
                if type(self.result[k]) == 'str': 
                    self.result[k]=""
                elif type(self.result[k]) == 'list': 
                    self.result[k]=[]
                elif type(self.result[k]) == 'dict': 
                    self.result[k]={}

    def __init__(self, **kwargs):
        self.__inicializar()
        self.busqueda["idioma"]=kwargs.get('idioma_busqueda','es')
        self.busqueda["tipo"]=kwargs.get('tipo','movie')
        
        if self.busqueda["tipo"] =='movie' or self.busqueda["tipo"] =="tv":
            # Rellenar diccionario de generos en el idioma seleccionado
            url='http://api.themoviedb.org/3/genre/%s/list?api_key=57983e31fb435df4df77afb854740ea9&language=%s' %(self.busqueda["tipo"], self.busqueda["idioma"])
            lista_generos=self.__get_json(url)["genres"]
            for i in lista_generos:
                self.dic_generos[str(i["id"])]=i ["name"]
        else:
            # La busqueda de personas no esta soportada en esta version.
            raise Exception ("Parametros no validos al crear el objeto Tmdb.\nConsulte los modos de uso.")
            
        if kwargs.has_key('id_Tmdb'):
            self.busqueda["id"]=kwargs.get('id_Tmdb')
            self.__by_id()
            
        elif kwargs.has_key('texto_buscado'):
            self.busqueda["texto"]=kwargs.get('texto_buscado')
            self.busqueda["include_adult"]=str(kwargs.get('include_adult','false'))
            self.busqueda["year"]=kwargs.get('year','')
            self.page=kwargs.get('page',1)
              
            self.__search(page=self.page)
            
            
        elif kwargs.has_key('external_source') and kwargs.has_key('external_id'):
            # TV Series: imdb_id, freebase_mid, freebase_id, tvdb_id, tvrage_id
            # Movies: imdb_id  
            if (self.busqueda["tipo"] =='movie' and kwargs.get('external_source')=="imdb_id") or (self.busqueda["tipo"] =='tv' and kwargs.get('external_source') in ("imdb_id","freebase_mid","freebase_id","tvdb_id","tvrage_id")):
                self.busqueda["id"]=kwargs.get('external_id')
                self.__by_id(source=kwargs.get('external_source'))
        else:
            raise Exception ("Parametros no validos al crear el objeto Tmdb.\nConsulte los modos de uso.")
    
    def __leer_resultado(self,data):    
        for k,v in data.items():
            if k=="genre_ids": # Lista de generos
                for i in v:
                    if self.dic_generos.has_key(str(i)): 
                        self.result["genres"].append(self.dic_generos[str(i)])
                        
            elif k=="known_for": # Lista de peliculas de un actor
                for i in v:
                    self.result["known_for"][i['id']]=i['title']
            
            elif k=="images": #Se incluyen los datos de las imagenes
                
                if v.has_key("backdrops"): self.result["images_backdrops"]=v["backdrops"]
                if v.has_key("posters"): self.result["images_posters"]=v["posters"]
                if v.has_key("profiles"): self.result["images_profiles"]=v["profiles"]
               
            elif k=="videos": #Se incluyen los datos de los videos
                self.result["videos"]=v["results"]
  
            elif k=="external_ids": # Listado de IDs externos
                
                for kj, id in v.items():
                    #print kj + ":" + str(id)
                    if self.result.has_key(kj): self.result[kj]=str(id)
                                        
            elif self.result.has_key(k): # el resto
                self.result[k]=v  
    

   
    def load_resultado(self,index_resultado=0,page=1):
        if self.total_results <= 1: # Si no hay mas un resultado no podemos cambiar
            return None 
        if page < 1 or page > self.total_pages: page=1
        if index_resultado < 0: index_resultado=0
        if page !=self.page:
            self.__inicializar()
            self.__search(index_resultado=index_resultado, page=page)
                    
    def get_id(self):
        #--------------------------------------------------------------------------------------------------------------------------------------------
        #   Parametros:
        #       none
        #   Return: (str)
        #       Devuelve el identificador Tmdb de la pelicula o serie cargada o una cadena vacia en caso de que no hubiese nada cargado.
        #       Se puede utilizar este metodo para saber si una busqueda ha dado resultado o no.
        #--------------------------------------------------------------------------------------------------------------------------------------------
        return str(self.result['id'])
        
    def get_sinopsis(self):
        #--------------------------------------------------------------------------------------------------------------------------------------------
        #   Parametros:
        #       none
        #   Return: (str)
        #       Devuelve la sinopsis de una pelicula o serie
        #--------------------------------------------------------------------------------------------------------------------------------------------
        return self.result['overview']
                    
    def get_poster(self, tipo_respuesta="str", size="original"):
        #--------------------------------------------------------------------------------------------------------------------------------------------
        #   Parametros:
        #       tipo_respuesta: ("list", "str") Tipo de dato devuelto por este metodo. Por defecto "str"
        #       size: ("w45", "w92", "w154", "w185", "w300", "w342", "w500", "w600", "h632", "w780", "w1280", "original") 
        #               Indica la anchura(w) o altura(h) de la imagen a descargar. Por defecto "original"
        #   Return:
        #       Si el tipo_respuesta es "list" devuelve un listado con todas las urls de las imagenes tipo poster del tamaño especificado. 
        #       Si el tipo_respuesta es "str" devuelve la url de la imagen tipo poster, mas valorada, del tamaño especificado.
        #       Si el tamaño especificado no existe se retornan las imagenes al tamaño original.
        #--------------------------------------------------------------------------------------------------------------------------------------------
        ret=[]
        if not size in ("w45", "w92", "w154", "w185", "w300", "w342", "w500", "w600", "h632", "w780", "w1280", "original"): size="original"
        if tipo_respuesta !='list':
            if self.result["poster_path"] !="":
                return 'http://image.tmdb.org/t/p/' + size + self.result["poster_path"]
            else: return ""
        elif self.result["id"] == "": return []
        
        if len(self.result['images_posters'])==0:
            # Vamos a lanzar una busqueda por id y releer de nuevo todo
            self.busqueda["id"]=str(self.result["id"])
            self.__by_id()
                    
        if len(self.result['images_posters'])>0:
            for i in self.result['images_posters']:
                imagen_path= i['file_path']
                if size!= "original":
                    # No podemos pedir tamaños mayores que el original
                    if size[1]== 'w' and int(imagen['width']) < int(size[1:]): size="original"
                    elif size[1]== 'h' and int(imagen['height']) < int(size[1:]): size="original"
                ret.append('http://image.tmdb.org/t/p/' + size + imagen_path)
        else:
            ret.append('http://image.tmdb.org/t/p/' + size + self.result["poster_path"])
            
        return ret
    
    def get_backdrop(self, tipo_respuesta="str", size="original"):
        #--------------------------------------------------------------------------------------------------------------------------------------------
        #   Parametros:
        #       tipo_respuesta: ("list", "str") Tipo de dato devuelto por este metodo. Por defecto "str"
        #       size: ("w45", "w92", "w154", "w185", "w300", "w342", "w500", "w600", "h632", "w780", "w1280", "original") 
        #               Indica la anchura(w) o altura(h) de la imagen a descargar. Por defecto "original"
        #   Return:
        #       Si el tipo_respuesta es "list" devuelve un listado con todas las urls de las imagenes tipo backdrop del tamaño especificado. 
        #       Si el tipo_respuesta es "str" devuelve la url de la imagen tipo backdrop, mas valorada, del tamaño especificado.
        #       Si el tamaño especificado no existe se retornan las imagenes al tamaño original.
        #--------------------------------------------------------------------------------------------------------------------------------------------
        ret=[]
        if not size in ("w45", "w92", "w154", "w185", "w300", "w342", "w500", "w600", "h632", "w780", "w1280", "original"): size="original"
        if tipo_respuesta !='list':
            if self.result["backdrop_path"] !="":
                return 'http://image.tmdb.org/t/p/' + size + self.result["backdrop_path"]
            else: return ""
        elif self.result["id"] == "": return []
        
        if len(self.result['images_backdrops'])==0:
            # Vamos a lanzar una busqueda por id y releer de nuevo todo
            self.busqueda["id"]=str(self.result["id"])
            self.__by_id()
                    
        if len(self.result['images_backdrops'])>0:
            for i in self.result['images_backdrops']:
                imagen_path= i['file_path']
                if size!= "original":
                    # No podemos pedir tamaños mayores que el original
                    if size[1]== 'w' and int(imagen['width']) < int(size[1:]): size="original"
                    elif size[1]== 'h' and int(imagen['height']) < int(size[1:]): size="original"
                ret.append('http://image.tmdb.org/t/p/' + size + imagen_path)
        else:
            ret.append('http://image.tmdb.org/t/p/' + size + self.result["backdrop_path"])
            
        return ret
        
    def get_fanart(self, tipo="hdclearart", idioma=["all"], temporada="all"):
        #--------------------------------------------------------------------------------------------------------------------------------------------
        #   Parametros:
        #       tipo: ("hdclearlogo", "poster",	"banner", "thumbs",	"hdclearart", "clearart", "background",	"clearlogo", "characterart", "seasonthumb", "seasonposter", "seasonbanner", "moviedisc")
        #           Indica el tipo de Art que se desea obtener, segun la web Fanart.tv. Alguno de estos tipos pueden estar solo disponibles para peliculas o series segun el caso. Por defecto "hdclearart"
        #       (opcional) idioma: (list) Codigos del idioma segun ISO 639-1, "all" (por defecto) para todos los idiomas o "00" para ninguno. Por ejemplo: idioma=["es","00","en"] Incluiria los resultados en español, sin idioma definido y en ingles, en este orden.
        #       (opcional solo para series) temporada: (str) Un numero entero que representa el numero de temporada, el numero cero para especiales o "all" para imagenes validas para cualquier temporada. Por defecto "all"
        #   Return: (list)
        #       Retorna una lista con las url de las imagenes segun los parametros de entrada y ordenadas segun las votaciones de Fanart.tv
        #--------------------------------------------------------------------------------------------------------------------------------------------
        if self.result["id"] == "": return []
        
        if len(self.fanart)==0: #Si esta vacio acceder a Fanart.tv y cargar el resultado
            if self.busqueda['tipo']=='movie':
                # http://assets.fanart.tv/v3/movies/1924?api_key=dffe90fba4d02c199ae7a9e71330c987
                url ="http://assets.fanart.tv/v3/movies/"+str(self.result["id"])+"?api_key=dffe90fba4d02c199ae7a9e71330c987"
                temporada="" 
            elif self.busqueda['tipo']=='tv':
                # En este caso necesitamos el tvdb_id
                if self.result["tvdb_id"]=='': 
                    # Vamos lanzar una busqueda por id y releer de nuevo todo
                    self.busqueda["id"]=str(self.result["id"])
                    self.__by_id()
                   
                # http://assets.fanart.tv/v3/tv/153021?api_key=dffe90fba4d02c199ae7a9e71330c987
                url ="http://assets.fanart.tv/v3/tv/"+str(self.result["tvdb_id"])+"?api_key=dffe90fba4d02c199ae7a9e71330c987"
            else:
                # 'person' No soportado
                return None
            
            fanarttv= self.__get_json(url)
            if fanarttv is None: #Si el item buscado no esta en Fanart.tv devolvemos una lista vacia
                return [] 
            
            for k,v in fanarttv.items():
                if k in ("hdtvlogo", "hdmovielogo"):
                    self.fanart["hdclearlogo"]= v
                elif k in ("tvposter", "movieposter"):
                    self.fanart["poster"]= v
                elif k in ("tvbanner", "moviebanner"):
                    self.fanart["banner"]= v
                elif k in ("tvthumb", "moviethumb"):
                    self.fanart["thumbs"]= v
                elif k in ("hdclearart", "hdmovieclearart"):
                    self.fanart["hdclearart"]= v
                elif k in ("clearart", "movieart"):
                    self.fanart["clearart"]= v
                elif k in ("showbackground", "moviebackground"):
                    self.fanart["background"]= v
                elif k in ("clearlogo", "movielogo"):
                    self.fanart["clearlogo"]= v
                elif k in ("characterart", "seasonthumb", "seasonposter", "seasonbanner", "moviedisc"):
                    self.fanart[k]= v
        
        
        # inicializamos el diccionario con los idiomas
        ret_dic={}
        for i in idioma:
            ret_dic[i]=[]
        
        for i in self.fanart[tipo]:
            if i["lang"] in idioma:
                if not i.has_key("season"):
                    ret_dic[i["lang"]].append(i["url"])
                elif temporada == "" or  (temporada =='all' and i["season"]== 'all'):
                    ret_dic[i["lang"]].append(i["url"])
                else:
                    if i["season"]=="": 
                        i["season"]=0
                    else:
                        i["season"]=int(i["season"])
                    if i["season"]== int(temporada):
                        ret_dic[i["lang"]].append(i["url"])
            elif "all" in idioma:
                ret_dic["all"].append(i["url"])
                
        ret_list=[]
        for i in idioma:
            ret_list.extend(ret_dic[i])
        
        #print ret_list   
        return ret_list

    def get_episodio(self, temporada=1, capitulo=1):
        #--------------------------------------------------------------------------------------------------------------------------------------------
        #   Parametros:
        #       temporada: (int) Numero de temporada. Por defecto 1.
        #       capitulo: (int) Numero de capitulo. Por defecto 1.
        #   Return: (dic)
        #       Devuelve un dicionario con los siguientes elementos:
        #           "temporada_nombre", "temporada_sinopsis", "temporada_poster", "episodio_titulo", "episodio_sinopsis" y  "episodio_imagen"
        #--------------------------------------------------------------------------------------------------------------------------------------------
        if self.result["id"] == "" or self.busqueda["tipo"] !="tv": return {}
        
        temporada= int(temporada)
        capitulo= int(capitulo)
        if temporada < 0: temporada= 1
        if capitulo <1: capitulo= 1
        
        if not self.temporada.has_key("season_number") or self.temporada["season_number"] != temporada:
            # Si no hay datos sobre la temporada solicitada, consultar en la web
            
            # http://api.themoviedb.org/3/tv/1402/season/4?api_key=57983e31fb435df4df77afb854740ea9&language=es
            url= "http://api.themoviedb.org/3/tv/%s/season/%s?api_key=57983e31fb435df4df77afb854740ea9&language=%s" %( self.result["id"], temporada, self.busqueda["idioma"])
            
            buscando= "id_Tmdb: " + str(self.result["id"]) + " temporada: " + str(temporada) + " capitulo: " + str(capitulo)
            logger.info("[Tmdb.py] Buscando " + buscando)
            
            print url
            self.temporada= self.__get_json(url)
            if self.temporada.has_key("status_code") or len(self.temporada["episodes"]) < capitulo: 
                # Se ha producido un error
                self.temporada={}
                logger.info("[Tmdb.py] La busqueda de " + buscando + " no dio resultados.")
                return {}
                
        ret_dic={}
        ret_dic["temporada_nombre"]=self.temporada["name"]
        ret_dic["temporada_sinopsis"]=self.temporada["overview"]
        ret_dic["temporada_poster"]='http://image.tmdb.org/t/p/original'+ self.temporada["poster_path"]
        
        episodio=self.temporada["episodes"][capitulo -1]
        ret_dic["episodio_titulo"]=episodio["name"]
        ret_dic["episodio_sinopsis"]=episodio["overview"]
        ret_dic["episodio_imagen"]='http://image.tmdb.org/t/p/original'+ episodio["still_path"]
        
        return ret_dic
        
        
        
        
        
      