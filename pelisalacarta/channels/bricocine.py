# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "bricocine"
__category__ = "F"
__type__ = "generic"
__title__ = "bricocine"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.bricocine mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Pelis-MicroHD"      , action="peliculas", url="http://www.bricocine.com/c/hd-microhd/", thumbnail="http://s6.postimg.org/5vgi38jf5/HD_brico10.jpg", fanart="http://s16.postimg.org/6g9tc2nyt/brico_pelifan.jpg"))
    itemlist.append( Item(channel=__channel__, title="Pelis Bluray-Rip" , action="peliculas", url="http://www.bricocine.com/c/bluray-rip/",  thumbnail="http://s6.postimg.org/5w82dorpt/blueraybrico.jpg", fanart="http://i59.tinypic.com/11rdnjm.jpg"))
    itemlist.append( Item(channel=__channel__, title="Pelis DvdRip" , action="peliculas", url="http://www.bricocine.com/c/dvdrip/", thumbnail="http://s6.postimg.org/d2dlld4y9/dvd2.jpg", fanart="http://s6.postimg.org/hcehbq5w1/brico_blue_fan.jpg"))
    itemlist.append( Item(channel=__channel__, title="Pelis 3D" , action="peliculas", url="http://www.bricocine.com/c/3d/", thumbnail="http://www.eias3d.com/wp-content/uploads/2011/07/3d2_5.png", fanart="http://s6.postimg.org/u18rvec0h/bric3dd.jpg"))
    itemlist.append( Item(channel=__channel__, title="Series"         , action="peliculas", url="http://www.bricocine.com/c/series", thumbnail="http://img0.mxstatic.com/wallpapers/bc795faa71ba7c490fcf3961f3b803bf_large.jpeg", fanart="http://s6.postimg.org/z1ath370x/bricoseries.jpg"))
    itemlist.append( Item(channel=__channel__, title="Buscar"         , action="search", url="", thumbnail="http://fc04.deviantart.net/fs70/i/2012/285/3/2/poltergeist___tv_wallpaper_by_elclon-d5hmmlp.png", fanart="http://s6.postimg.org/f44w84o5t/bricosearch.jpg"))
    

    return itemlist


def search(item,texto):
    logger.info("pelisalacarta.bricocine search")
    texto = texto.replace(" ","+")
    item.url = "http://www.bricocine.com/index.php/?s=%s" % (texto)
    try:
        return peliculas(item)
    # Se captura la excepciÛn, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def peliculas(item):
    logger.info("pelisalacarta.bricocine peliculas")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    '''
   <div class="post-10888 post type-post status-publish format-standard hentry category-the-leftovers tag-ciencia-ficcion tag-drama tag-fantasia tag-misterio"><div class="entry"> <a href="http://www.bricocine.com/10888/leftovers-temporada-1/"> <img src="http://www.bricocine.com/wp-content/plugins/wp_movies/files/thumb_185_the_leftovers_.jpg" alt="The Leftovers " /> </a></div><div class="entry-meta"><div class="clearfix"><div itemprop="aggregateRating" itemscope itemtype="http://schema.org/AggregateRating" class="rating"  title="Puntos IMDB: 7.4"><div class="rating-stars imdb-rating"><div class="stars" style="width:74%"></div></div><div itemprop="ratingValue" class="rating-number"> 7.4</div></div><div itemprop="aggregateRating" itemscope itemtype="http://schema.org/AggregateRating" class="rating"  title="Puntos Bricocine: 6.2"><div class="rating-stars brico-rating"><div class="stars" style="width:62%"></div></div><div itemprop="ratingValue" class="rating-number"> 6.2</div></div> <span class="vcard author none"> Publicado por <a class="fn" href="" rel="author" target="_blank"></a> </span> <span class="date updated none">2014-10-07T23:36:17+00:00</span></div></div><h2 class="title2 entry-title"> <a href="http://www.bricocine.com/10888/leftovers-temporada-1/"> The Leftovers  &#8211; Temporada 1 </a></h2></div> </article> <article class="hentry item-entry"><div class="post-10088 post type-post status-publish format-standard hentry category-the-last-ship tag-accion tag-ciencia-ficcion tag-drama tag-the tag-thriller"><div class="entry"> <a href="http://www.bricocine.com/10088/last-ship-temporada-1/"> <img src="http://www.bricocine.com/wp-content/plugins/wp_movies/files/thumb_185_the_last_ship_.jpg" alt="The Last Ship " /> </a></div><div class="entry-meta"><div class="clearfix"><div itemprop="aggregateRating" itemscope itemtype="http://schema.org/AggregateRating" class="rating"  title="Puntos IMDB: 7.4"><div class="rating-stars imdb-rating"><div class="stars" style="width:74%"></div></div><div itemprop="ratingValue" class="rating-number"> 7.4</div></div><div itemprop="aggregateRating" itemscope itemtype="http://schema.org/AggregateRating" class="rating"  title="Puntos Bricocine: 7.0"><div class="rating-stars brico-rating"><div class="stars" style="width:70%"></div></div><div itemprop="ratingValue" class="rating-number"> 7.0</div></div> <span class="vcard author none"> Publicado por <a class="fn" href="" rel="author" target="_blank"></a> </span> <span class="date updated none">2014-10-07T23:32:25+00:00</span></div></div><h2 class="title2 entry-title"> <a href="http://www.bricocine.com/10088/last-ship-temporada-1/"> The Last Ship &#8211; Temporada 1 </a></h2></div> </article> <article class="hentry item-entry">

    '''

    patron = '<div class="entry"> '
    patron += '<a href="([^"]+)"> '
    patron += '<img src="([^"]+)".*?'
    patron += 'alt="([^"]+)".*?'
    patron += 'class="rating-number">([^<]+)</div></div>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches)==0 :
        itemlist.append( Item(channel=__channel__, title="[COLOR gold][B]No hay resultados...[/B][/COLOR]", thumbnail ="http://s6.postimg.org/fay99h9ox/briconoisethumb.png", fanart ="http://s6.postimg.org/uie8tu1jl/briconoisefan.jpg",folder=False) )

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedcreatedate in matches:
        scrapedcreatedate = scrapedcreatedate.replace(scrapedcreatedate,"[COLOR sandybrown][B]"+scrapedcreatedate+"[/B][/COLOR]")
        scrapedtitle = scrapedtitle.replace(scrapedtitle,"[COLOR white]"+scrapedtitle+"[/COLOR]")
        scrapedtitle = scrapedtitle + "(Puntuación:" + scrapedcreatedate + ")"
       
        itemlist.append( Item(channel=__channel__, title=scrapedtitle, url=scrapedurl, action="fanart", thumbnail=scrapedthumbnail, fanart="http://s15.postimg.org/id6ec47vf/bricocinefondo.jpg", folder=True) )
    
    
    ## Paginación
    #<span class='current'>1</span><a href='http://www.bricocine.com/c/hd-microhd/page/2/'
    
    # Si falla no muestra ">> Página siguiente"
    try:
        next_page = scrapertools.get_match(data,"<span class='current'>\d+</span><a href='([^']+)'")
        title= "[COLOR red]Pagina siguiente>>[/COLOR]"
        itemlist.append( Item(channel=__channel__, title=title, url=next_page, action="peliculas", fanart="http://s15.postimg.org/id6ec47vf/bricocinefondo.jpg", thumbnail="http://s7.postimg.org/w2e0nr7hn/pdksiguiente.jpg", folder=True) )
    except: pass
    
    return itemlist
def fanart(item):
    logger.info("pelisalacarta.bricocine fanart")
    itemlist = []
    url = item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|\(.*?\)|\[.*?\]|&nbsp;","",data)
    if "temporada" in item.url:
        title= scrapertools.get_match(data,'<title>(.*?)-')
        title= re.sub(r"3D|'|,|#|;|´|SBS|-|","",title)
        title= title.replace('Temporada','')
        title= title.replace('Fin','')
        title= title.replace('x','')
        title= title.replace('Anatomía','Anatomia')
        title= title.replace(' ','%20')
        url="http://thetvdb.com/api/GetSeries.php?seriesname=" + title + "&language=es"
        if "Erase%20una%20vez" in url:
            url ="http://thetvdb.com/api/GetSeries.php?seriesname=Erase%20una%20vez%20(2011)&language=es"
        data = scrapertools.cachePage(url)
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
        patron = '<Data><Series><seriesid>([^<]+)</seriesid>'
        matches = re.compile(patron,re.DOTALL).findall(data)
        if len(matches)==0:
            itemlist.append( Item(channel=__channel__, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.thumbnail , folder=True) )
        else:
            for id in matches:
                id_serie = id
                url ="http://thetvdb.com/api/1D62F2F90030C444/series/"+id_serie+"/banners.xml"
                if "Castle" in title:
                    url ="http://thetvdb.com/api/1D62F2F90030C444/series/83462/banners.xml"
                data = scrapertools.cachePage(url)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
                patron = '<Banners><Banner>.*?<VignettePath>(.*?)</VignettePath>'
                matches = re.compile(patron,re.DOTALL).findall(data)
                if len(matches)==0:
                    itemlist.append( Item(channel=__channel__, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.thumbnail , folder=True) )
            for fan in matches:
                fanart="http://thetvdb.com/banners/" + fan
                item.extra= fanart
                
                itemlist.append( Item(channel=__channel__, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=item.thumbnail, fanart=item.extra,  folder=True) )
    else:
            title= scrapertools.get_match(data,'<title>(.*?)-')
            title= re.sub(r"3D|SBS|\(.*?\)|\[.*?\]|-|","",title)
            title= title.replace('Torrent','')
            title= title.replace(' ','%20')
            url="http://api.themoviedb.org/3/search/movie?api_key=57983e31fb435df4df77afb854740ea9&query=" + title + "&language=es&include_adult=false"
            data = scrapertools.cachePage(url)
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
            patron = '"page":1.*?"backdrop_path":"(.*?)".*?,"id"'
            matches = re.compile(patron,re.DOTALL).findall(data)
            if len(matches)==0:
                itemlist.append( Item(channel=__channel__, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.thumbnail , folder=True) )
            else:
                for fan in matches:
                    fanart="https://image.tmdb.org/t/p/original" + fan
                    item.extra= fanart
    
                    itemlist.append( Item(channel=__channel__, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=item.thumbnail, fanart=item.extra,  folder=True) )
    title ="Info"
    title = title.replace(title,"[COLOR skyblue]"+title+"[/COLOR]")
    itemlist.append( Item(channel=__channel__, action="info" , title=title , url=item.url, thumbnail=item.thumbnail, fanart=item.extra, folder=False ))
    title= "[COLOR crimson]Trailer[/COLOR]"
    itemlist.append( Item(channel=__channel__, action="trailer", title=title , url=item.url , thumbnail=item.thumbnail , plot=item.plot , fulltitle = item.title , fanart=item.extra, folder=True) )
    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.bricocine findvideos")
    
    itemlist = []
    data = scrapertools.cache_page(item.url)
   
    
    #id_torrent = scrapertools.get_match(item.url,"(\d+)-")
    
    patron = '<span class="title">([^"]+)</span>.*?'
    patron += 'id="([^"]+)" href="([^"]+)".*?'
    patron += 'Torrent.*?([^"]+) '
    matches = re.compile(patron,re.DOTALL).findall(data)
    import base64
    for title_links, title_torrent, url_torrent, fanart_title in matches:
        ## torrent
        title_torrent = "["+title_torrent.replace("file","torrent")+"]"
        title_torrent = title_torrent.replace(title_torrent,"[COLOR green]"+title_torrent+"[/COLOR]")
        title_links = title_links.replace(title_links,"[COLOR sandybrown]"+title_links+"[/COLOR]")
        title_torrent = title_links+"- "+title_torrent
        url_torrent = base64.decodestring(url_torrent.split('&u=')[1][::-1])
        
        
        
        
        itemlist.append( Item(channel=__channel__, title = title_torrent , action="play", url=url_torrent, server="torrent", thumbnail=item.thumbnail, fanart=item.fanart,  folder=False) )

    
   


    return itemlist
def trailer(item):
    
    logger.info("pelisalacarta.bricocine trailer")
    
    itemlist = []
    data = scrapertools.cache_page(item.url)
    
    
    #trailer
    patron = "<iframe width='570' height='400' src='//([^']+)"
    
    # Busca los enlaces a los videos
    listavideos = servertools.findvideos(data)
    
    for video in listavideos:
        videotitle = scrapertools.unescape(video[0])
        url = video[1]
        server = video[2]
        
        #xbmctools.addnewvideo( __channel__ , "play" , category , server ,  , url , thumbnail , plot )
        title= "[COLOR crimson]Trailer - [/COLOR]"
        itemlist.append( Item(channel=__channel__, action="play", server=server, title=title + videotitle  , url=url , thumbnail=item.thumbnail , plot=item.plot , fulltitle = item.title , fanart="http://s23.postimg.org/84vkeq863/movietrailers.jpg", folder=False) )
    return itemlist

def info(item):
    logger.info("pelisalacarta.bricocine trailer")
    url=item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    if "temporada" in item.title:
       title= scrapertools.get_match(data,'<span class="title">.*?Torrent.*?([^"]+) ')
    else:
    
        title= scrapertools.get_match(data,'<span class="title">([^"]+)</span>')
        title = title.replace(title,"[COLOR aqua][B]"+title+"[/B][/COLOR]")
        plot = scrapertools.get_match(data,'<div class="description" itemprop="text.*?">([^<]+).*?</div></div></div>')
        plot_title = "Sinopsis" + "[CR]"
        plot_title = plot_title.replace(plot_title,"[COLOR red]"+plot_title+"[/COLOR]")
        plot= plot_title + plot
        plot = plot.replace(plot,"[COLOR white][B]"+plot+"[/B][/COLOR]")
        fanart="http://s11.postimg.org/qu66qpjz7/zentorrentsfanart.jpg"
        tbd = TextBox("DialogTextViewer.xml", os.getcwd(), "Default")
        tbd.ask(title, plot,fanart)
        del tbd
        return

try:
    import xbmc, xbmcgui
    class TextBox( xbmcgui.WindowXMLDialog ):
        """ Create a skinned textbox window """
        def __init__( self, *args, **kwargs):
            
            pass
        
        def onInit( self ):
            try:
                self.getControl( 5 ).setText( self.text )
                self.getControl( 1 ).setLabel( self.title )
            except: pass
        
        def onClick( self, controlId ):
            pass
        
        def onFocus( self, controlId ):
            pass
        
        def onAction( self, action ):
            self.close()
        
        def ask(self, title, text, image ):
            self.title = title
            self.text = text
            self.doModal()

except:
    pass



