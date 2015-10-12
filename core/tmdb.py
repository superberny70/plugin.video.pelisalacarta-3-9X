# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------------------------------------------------
# Scraper para pelisalacarta, palco y otros plugin de XBMC/Kodi basado en el Api de https://www.themoviedb.org/
#   version: 1
#   Uso:
#   Metodos constructores:
#    Tmdb(texto_buscado, tipo)
#        Parametros:
#            texto_buscado:(str) Texto o parte del texto a buscar
#            tipo: ("movie", "tv" o "person") Tipo de resultado buscado peliculas, series o personas. Por defecto "movie"
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
#           id_Tmdb: (str) Codigo identificador de una determinada pelicula, serie o persona en themoviedb.org
#           tipo: ("movie", "tv" o "person") Tipo de resultado buscado peliculas, series o personas. Por defecto "movie"
#           (opcional) idioma_busqueda: (str) codigo del idioma segun ISO 639-1
#       Return:
#           Esta llamada devuelve un objeto Tmdb que contiene el resultado de buscar una pelicula, serie o persona con el identitifador id_Tmd
#           en la web themoviedb.org. Cuantos mas parametros opcionales se incluyan mas precisa sera la busqueda.
#           Ademas el objeto esta inicializado con el primer resultado de la primera pagina de resultados.
#
#   Metodos principales:
#    get_sinopsis(): Retorna un str con la sinopsis de la serie o pelicula cargada.
#    get_poster (size,rnd): Ver descripcion mas abajo.
#    get_fanart (size,rnd): Ver descripcion mas abajo.
#       
#   Otros metodos:
#    inicializar(): Elimina todos los datos que puediera tener actualmente cargado el objeto.
#    load_page(page): Cuando el resultado tiene varias paginas podemos seleccionar que pagina cargar.   
#    leer_resultado(resultado, page): Cuando la busqueda devuelve varios resultados podemos seleccionar que resultado concreto y de que pagina cargar los datos.
#
# Informacion sobre la api : http://docs.themoviedb.apiary.io
#--------------------------------------------------------------------------------------------------------------------------------------------
import urllib2
import traceback

from core import logger

class Tmdb(object):
    
    dic_generos={}
    busqueda={'id_Tmdb':"",
              'texto':"",
              'tipo':'movies', 
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
            'id':"", 
            'imdb_id':"",
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
            'name':"", # nombre en caso de personas
            'profile_path':"", # ruta imagenes en caso de personas
            'known_for':{}, #Diccionario de peliculas en caso de personas (id_pelicula:titulo)
            'images_backdrops':[], 
            'images_posters':[],
            'images_profiles':[],
            'videos':[] 
            }
    
    
        
    def __init__(self, **kwargs):
        self.inicializar()
        self.busqueda["idioma"]=kwargs.get('idioma_busqueda','es')
        self.busqueda["tipo"]=kwargs.get('tipo','movie')
        
        if self.busqueda["tipo"] =='movie' or self.busqueda["tipo"] =="tv":
            # Rellenar diccionario de generos en el idioma seleccionado
            url='http://api.themoviedb.org/3/genre/%s/list?api_key=57983e31fb435df4df77afb854740ea9&language=%s' %(self.busqueda["tipo"], self.busqueda["idioma"])
            lista_generos=self.__get_json(url)["genres"]
            for i in lista_generos:
                self.dic_generos[str(i["id"])]=i ["name"]
        
        if kwargs.has_key('id_Tmdb'):
            self.busqueda["id_Tmdb"]=kwargs.get('id_Tmdb')
            self.load_page(1)
            
        elif kwargs.has_key('texto_buscado'):
            self.busqueda["texto"]=kwargs.get('texto_buscado')
            self.busqueda["include_adult"]=str(kwargs.get('include_adult','false'))
            self.busqueda["year"]=kwargs.get('year','')
            self.page=kwargs.get('page',1)
            
            self.load_page(self.page)   
           
        else:
            raise Exception ("Parametros no validos al crear el objeto Tmdb.\nConsulte los modos de uso.")
     
     
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

            
    def inicializar(self):    
        # Inicializamos todos los atributos
        self.busqueda["texto"]=""
        self.busqueda["idioma"]='es'
        self.busqueda["include_adult"]='false'
        self.busqueda["year"]=''
        
        self.page= 1
        self.results= []
        self.total_pages=0
        self.total_results= 0
        
        for k in self.result.keys():
            if type(self.result[k]) == 'str': 
                self.result[k]=""
            elif type(self.result[k]) == 'list': 
                self.result[k]=[]
            elif type(self.result[k]) == 'dict': 
                self.result[k]={}    
    
           
    def load_page(self,page):
        
        if page !=self.page: self.inicializar()
        self.page=page
        
        if self.busqueda["id_Tmdb"] !='':
            # http://api.themoviedb.org/3/movie/1924?api_key=57983e31fb435df4df77afb854740ea9&language=es&page=1&append_to_response=images,videos&include_image_language=es,null
            url='http://api.themoviedb.org/3/%s/%s?api_key=57983e31fb435df4df77afb854740ea9&language=%s&page=%s&append_to_response=images,videos&include_image_language=%s,null' %(self.busqueda["tipo"], self.busqueda["id_Tmdb"], self.busqueda["idioma"], str(page), self.busqueda["idioma"])
            print url
            buscando= "id_Tmdb: " + self.busqueda["id_Tmdb"]
            logger.info("[Tmdb.py] Buscando " + buscando + " en pagina " + str(page))
            self.results.append(self.__get_json(url))
                        
            self.total_results= 1
            self.total_pages= 1
        else:
            # http://api.themoviedb.org/3/search/movie?api_key=57983e31fb435df4df77afb854740ea9&query=superman&language=es&include_adult=false&page=1
            url='http://api.themoviedb.org/3/search/%s?api_key=57983e31fb435df4df77afb854740ea9&query=%s&language=%s&include_adult=%s&page=%s' %(self.busqueda["tipo"], self.busqueda["texto"].replace(' ','%20') , self.busqueda["idioma"], self.busqueda["include_adult"], str(page))
            if self.busqueda["year"] !='': url+= '&year=' + self.busqueda["year"] 
            buscando= self.busqueda["texto"] 
            
            logger.info("[Tmdb.py] Buscando " + buscando + " en pagina " + str(page))
            response_dic= self.__get_json(url)
                        
            self.total_results= response_dic["total_results"]
            self.total_pages= response_dic["total_pages"]
        
            if self.total_results > 0:
                self.results=response_dic["results"]
            
        if len(self.results) >0 :
            self.leer_resultado(0,page)
            return None
        
        # No hay resultados de la busqueda
        logger.info("[Tmdb.py] La busqueda de " + buscando + " no dio resultados para la pagina " + str(page))
    
    
    def leer_resultado(self,index_resultado=0,page=1):
        if page < 1: page=1
        if page !=self.page:
            self.load_page(page)
        if index_resultado < 0: index_resultado=0
        
        for k,v in self.results[index_resultado].items():
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
                
            elif self.result.has_key(k): # el resto
                self.result[k]=v         
            
        
    def get_sinopsis(self):
        #--------------------------------------------------------------------------------------------------------------------------------------------
        #   Parametros:
        #       none
        #   Return:
        #       Devuelve la sinopsis de una pelicula o serie
        #--------------------------------------------------------------------------------------------------------------------------------------------
        return self.result['overview']
        
        
    def get_poster(self, size="original", rnd= False):
        #--------------------------------------------------------------------------------------------------------------------------------------------
        #   Parametros:
        #       size: ("w45", "w92", "w154", "w185", "w300", "w342", "w500", "w600", "h632", "w780", "w1280", "original") 
        #               Indica la anchura(w) o altura(h) de la imagen a descargar. Por defecto "original"
        #       rnd: (bool) Al azar. Por defecto 'False'
        #   Return:
        #       Si hay varias imagenes y rnd=True retorna una al azar, en caso contrario retorna la imagen mas valorada.
        #       Si el tamaño especificado no existe se retorna la imagen al tamaño original.
        #--------------------------------------------------------------------------------------------------------------------------------------------
        if not size in ("w45", "w92", "w154", "w185", "w300", "w342", "w500", "w600", "h632", "w780", "w1280", "original"): size="original"
        if rnd and len(self.result['images_backdrops'])>0:
            import random
            imagen=random.choice(self.result['images_posters'])
            imagen_path= imagen['file_path']
            if size!= "original":
                if size[1]== 'w' and int(imagen['width']) < int(size[1:]): size="original"
                elif size[1]== 'h' and int(imagen['height']) < int(size[1:]): size="original"
        else:
            imagen= self.result["poster_path"]
        
        return 'http://image.tmdb.org/t/p/' + size + imagen_path
    
    
    def get_fanart(self, size="original", rnd= False):
        #--------------------------------------------------------------------------------------------------------------------------------------------
        #   Parametros:
        #       size: ("w45", "w92", "w154", "w185", "w300", "w342", "w500", "w600", "h632", "w780", "w1280", "original") 
        #               Indica la anchura(w) o altura(h) de la imagen a descargar. Por defecto "original"
        #       rnd: (bool) Al azar. Por defecto 'False'
        #   Return:
        #       Si hay varias imagenes y rnd=True retorna una al azar, en caso contrario retorna la imagen mas valorada.
        #       Si el tamaño especificado no existe se retorna la imagen al tamaño original.
        #--------------------------------------------------------------------------------------------------------------------------------------------
        if not size in ("w45", "w92", "w154", "w185", "w300", "w342", "w500", "w600", "h632", "w780", "w1280", "original"): size="original"
        if rnd and len(self.result['images_backdrops'])>0:
            import random
            imagen=random.choice(self.result['images_backdrops'])
            imagen_path= imagen['file_path']
            if size!= "original":
                if size[1]== 'w' and int(imagen['width']) < int(size[1:]): size="original"
                elif size[1]== 'h' and int(imagen['height']) < int(size[1:]): size="original"
        else:
            imagen_path= self.result["backdrop_path"]
        
        return 'http://image.tmdb.org/t/p/' + size + imagen_path