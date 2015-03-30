# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys, random

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "aquitorrent"
__category__ = "F"
__type__ = "generic"
__title__ = "Aquitorrent"
__language__ = "ES"

host = "http://www.aquitorrent.com/"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.aquitorrent mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Peliculas"      , action="peliculas", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=PELICULAS", thumbnail="http://imgc.allpostersimages.com/images/P-473-488-90/37/3710/L3YAF00Z/posters/conrad-knutsen-cinema.jpg", fanart="http://s6.postimg.org/m8dipognl/aquitorrentfanart2.jpg"))
    itemlist.append( Item(channel=__channel__, action="peliculas", title="Series", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=SERIES", thumbnail="http://s6.postimg.org/nbxn1n1ap/aquitserielogo.jpg", fanart="http://s6.postimg.org/x6os7v58x/aquitorretseries.jpg"))
    itemlist.append( Item(channel=__channel__, action="peliculas", title="Películas HD", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=Peliculas%20HD", thumbnail="http://s6.postimg.org/4uymx2vyp/aquithdlogo.jpg", fanart="http://s6.postimg.org/umxqri72p/aquitphd3.jpg"))
    itemlist.append( Item(channel=__channel__, action="peliculas", title="Películas 3D", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=PELICULAS%203D", thumbnail="http://s6.postimg.org/53rm99jdd/aquit3dlogo.jpg", fanart="http://s6.postimg.org/9i03l3txt/aquit3d.jpg"))
    itemlist.append( Item(channel=__channel__, action="peliculas", title="Películas V.O.S.", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=PELICULAS%20V.O.S.", thumbnail="http://s6.postimg.org/fofbx2s0h/aquitvostub2.jpg", fanart="http://s6.postimg.org/wss1m0aj5/aquitvos.jpg"))
    itemlist.append( Item(channel=__channel__, action="peliculas", title="Docus y TV", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=Docus%20y%20TV",  thumbnail="http://s6.postimg.org/5mnir1w0h/tv_docaquit.jpg", fanart="http://s6.postimg.org/5lrd2uyc1/aquitdoctv3_an.jpg"))
    itemlist.append( Item(channel=__channel__, action="peliculas", title="Clásicos Disney", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=CLASICOS%20DISNEY", thumbnail="http://s6.postimg.org/87xosbas1/Walt_Disney.jpg", fanart="http://s6.postimg.org/5m0jucd3l/aquitwalt.jpg"))
    itemlist.append( Item(channel=__channel__, action="peliculas", title="F1 2014", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=F1%202014", thumbnail="http://s6.postimg.org/42vyxvrrl/aquitf1tub.png", fanart="http://s6.postimg.org/sbqhvuhjl/aquitf1f.jpg"))
    itemlist.append( Item(channel=__channel__, action="peliculas", title="MotoGP 2014", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=MotoGP%202014", thumbnail="http://s6.postimg.org/flquwhyz5/aquit_Moto_GP_Logo.jpg", fanart="http://s6.postimg.org/sv06iuyc1/aquitmgpf2.jpg"))
    itemlist.append( Item(channel=__channel__, action="peliculas", title="Mundial 2014", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=Mundial%202014", thumbnail="http://s6.postimg.org/sgyuj9e8h/aquitmundial_TUB.png", fanart="http://s6.postimg.org/7vk2rcwnl/aquitmundiall.jpg"))
    itemlist.append( Item(channel=__channel__, action="search", title="Buscar...", url="", thumbnail="http://s6.postimg.org/gninw2o9d/searchaquittub.jpg", fanart="http://s6.postimg.org/b4kpslglt/searchaquit.jpg"))
    
    

    return itemlist


                

def search(item,texto):
    logger.info("[pelisalacarta.aquitorrent search texto="+texto)
    
    item.url = "http://www.aquitorrent.com/buscar.asp?pagina=1&buscar=%s" % (texto)
    try:
        
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []




def peliculas(item):
    logger.info("pelisalacarta.aquitorrent peliculas")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    #quitamos los titulos de los href en enlaces<
    data = re.sub(r'&/[^"]+">','">',data)
    
    patron = '<div class="div_pic" align="center">'
    patron += '<a href="([^"]+)".*?>'
    patron += '<img src="([^"]+)".*?'
    patron += 'alt="([^"]+)"'
    

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches)==0 :
        itemlist.append( Item(channel=__channel__, title="[COLOR gold][B]No hay resultados...[/B][/COLOR]", thumbnail ="http://s6.postimg.org/t48ttay4x/aquitnoisethumb.png", fanart ="http://s6.postimg.org/4wjnb0ksx/aquitonoisefan.jpg",folder=False) )
    
   
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle= scrapedtitle.replace(scrapedtitle,"[COLOR white]"+scrapedtitle+"[/COLOR]")
        # Arregla la url y thumbnail
        #scrapedurl = fix_url(scrapedurl)
        scrapedthumbnail = fix_url(scrapedthumbnail)
        
        if "tipo=Docus" in item.url or "tipo=F1" in item.url or "tipo=MotoGP" in item.url or "tipo=Mundia" in item.url:
            action= "findvideos"
        else:
            action = "fanart"
        itemlist.append( Item(channel=__channel__, title =scrapedtitle , url=scrapedurl, action=action, fanart="http://s9.postimg.org/lmwhrdl7z/aquitfanart.jpg", thumbnail=scrapedthumbnail) )

    ## Paginación
    pagina = int(scrapertools.get_match(item.url,"pagina=(\d+)"))+1
    pagina = "pagina=%s" % (pagina)
    next_page = re.sub(r"pagina=\d+", pagina, item.url)
    title= "[COLOR green]Pagina siguiente>>[/COLOR]"
    if pagina in data:
        itemlist.append( Item(channel=__channel__, title=title, url=next_page, fanart="http://s9.postimg.org/lmwhrdl7z/aquitfanart.jpg", thumbnail="http://s6.postimg.org/4hpbrb13l/texflecha2.png",
            action="peliculas", folder=True) )


    
    return itemlist

def fanart(item):
    logger.info("pelisalacarta.aquitorrent fanart")
    itemlist = []
    url = item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|\(.*?\)|&nbsp;","",data)
    if "PELICULAS" in item.url:
        title= scrapertools.get_match(data,'<td class="wrapper_pic_td">.*?alt="([^"]+)"')
        title= re.sub(r"3D|SBS|-|V.S.O.|VOS|","",title)
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
                itemlist.append( Item(channel=__channel__, title =item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra , folder=True) )
                
    elif "Peliculas" in item.url:
          title= scrapertools.get_match(data,'<td class="wrapper_pic_td">.*?alt="([^"]+)"')
          title= re.sub(r"3D|SBS|-|V.S.O.|VOS|","",title)
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
                  itemlist.append( Item(channel=__channel__, title =item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra , folder=True) )
    elif "DISNEY" in item.url:
        title= scrapertools.get_match(data,'<title>([^"]+) -')
        title= re.sub(r"3D|SBS|-|V.S.O.|VOS|","",title)
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
        
                itemlist.append( Item(channel=__channel__, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra , folder=True) )

    else:
        title= scrapertools.get_match(data,'<td class="wrapper_pic_td">.*?alt="([^"]+)"')
        title= re.sub(r"[0-9]|x|DVB|-|","",title)
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
                
                    itemlist.append( Item(channel=__channel__, title =item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.extra , folder=True) )
    title ="Info"
    title = title.replace(title,"[COLOR skyblue][B]"+title+"[/B][/COLOR]")
    if len(item.extra)==0:
        fanart=item.thumbnail
    if len(item.extra)>0:
        fanart=item.extra

    itemlist.append( Item(channel=__channel__, action="info" , title=title , url=item.url, thumbnail=item.thumbnail, fanart=fanart, folder=False ))

    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.aquitorrent findvideos")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    
    # Torrent en zip
    patron = '<td class="wrapper_pic_td">.*? '
    patron+= 'alt="([^"]+)".*? '
    patron+= 'href="(.*?\.zip)".*?'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)>0:
        for scrapedtitle, scrapedzip in matches:
            # Arregla la url y extrae el torrent
            scrapedtorrent = unzip(fix_url(scrapedzip))
            
            itemlist.append( Item(channel=__channel__, title =item.title+"[COLOR green][B] [torrent][/B][/COLOR]" , url=scrapedtorrent,  action="play", server="torrent", thumbnail=item.thumbnail, fanart=item.fanart , folder=False) )

    #Vamos con el normal

    patron = '<td class="wrapper_pic_td">.*? '
    patron+= 'alt="([^"]+)".*? '
    patron+= 'href="(magnet[^"]+)".*?'
    patron+= 'title="Visionado Online".*?'
    patron += '<a href="http://www.bitlet.org/video/play.torrent=([^&]+)&.*?'

    
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedtitle, scrapedmagnet, scrapedtorrent in matches:
        itemlist.append( Item(channel=__channel__, title =item.title+"[COLOR red][B] [magnet][/B][/COLOR]" , url=scrapedmagnet,  action="play", server="torrent", thumbnail=item.thumbnail, fanart=item.fanart , folder=False) )
        itemlist.append( Item(channel=__channel__, title =item.title+"[COLOR green][B] [torrent][/B][/COLOR]" , url=scrapedtorrent,  action="play", server="torrent", thumbnail=item.thumbnail, fanart=item.fanart ,folder=False) )
    #nueva variacion
    if len(itemlist) == 0:
       patron = '<td class="wrapper_pic_td">.*? '
       patron+= 'alt="([^"]+)".*? '
       patron+= 'href="([^"]+)".*?'
       
       matches = re.compile(patron,re.DOTALL).findall(data)
    
       for scrapedtitle, scrapedtorrent in matches:
           itemlist.append( Item(channel=__channel__, title =scrapedtitle+"[COLOR green][B] [torrent][/B][/COLOR]", url=scrapedtorrent, action="play", server="torrent", thumbnail=item.thumbnail, fanart=item.fanart , folder=False) )


    
    return itemlist


def fix_url(url):
    if url.startswith("/"):
        url = url[1:]
        if not url.startswith("http://"):
            url = host+url
    return url

def unzip(url):
    import zipfile
    
    # Path para guardar el zip como tem.zip los .torrent extraidos del zip
    torrents_path = config.get_library_path()+'/torrents'
    if not os.path.exists(torrents_path):
        os.mkdir(torrents_path)

    ## http://stackoverflow.com/questions/4028697/how-do-i-download-a-zip-file-in-python-using-urllib2
    # Open the url
    try:
        f = urllib2.urlopen(url)
        with open( torrents_path+"/temp.zip", "wb") as local_file:
            local_file.write(f.read())
        
        # Open our local file for writing
        fh = open(torrents_path+"/temp.zip", 'rb')
        z = zipfile.ZipFile(fh)
        for name in z.namelist():
            z.extract(name, torrents_path)
        fh.close()

    #handle errors
    except urllib2.HTTPError, e:
        print "HTTP Error:", e.code, url
    except urllib2.URLError, e:
        print "URL Error:", e.reason, url

    torrent = "file:///"+torrents_path+"/"+name

    if not torrents_path.startswith("/"):
        torrents_path = "/"+torrents_path
    
    torrent = "file://"+torrents_path+"/"+name
    
    return torrent

def info(item):
    logger.info("pelisalacarta.aquitorrents info")
    
    url=item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    title= scrapertools.get_match(data,'<title>([^"]+) -')
    title = title.replace(title,"[COLOR aqua][B]"+title+"[/B][/COLOR]")
    
    if "DISNEY" in item.url or "Series" in item.url or "PELICULAS-3D" in item.url or "PELICULAS-VOS" in item.url:
        scrapedplot = scrapertools.get_match(data,'"2"><br><br>(.*)<br><br><img')
        plotformat = re.compile('(.*?:).*?<br />',re.DOTALL).findall(scrapedplot)
        # Reemplaza las etiquetas con etiquetas formateadas con color azul y negrita
        for plot in plotformat:
            scrapedplot = scrapedplot.replace(plot,"[COLOR green][B]"+plot+"[/B][/COLOR]")
            plot = plot.replace(plot,"[COLOR white]"+plot+"[/COLOR]")
        
        # reemplaza los <br /> por saltos de línea del xbmc
        scrapedplot = scrapedplot.replace("<br />","[CR]")
        # codifica el texto en utf-8 para que se puedan ver las tíldes y eñes
        scrapedplot = unicode( scrapedplot, "iso-8859-1" , errors="replace" ).encode("utf-8")
        fanart="http://s11.postimg.org/qu66qpjz7/zentorrentsfanart.jpg"
        tbd = TextBox("DialogTextViewer.xml", os.getcwd(), "Default")
        tbd.ask(title, scrapedplot,fanart)
        del tbd
        return
    else:
        if "PELICULAS" in item.url or "peliculas" in item.url:
            scrapedplot = scrapertools.get_match(data,'<br><br>>(.*)<br><br><img')
            plotformat = re.compile('(.*?:).*?<br />',re.DOTALL).findall(scrapedplot)
            # Reemplaza las etiquetas con etiquetas formateadas con color azul y negrita
            for plot in plotformat:
                scrapedplot = scrapedplot.replace(plot,"[COLOR green][B]"+plot+"[/B][/COLOR]")
                plot = plot.replace(plot,"[COLOR white]"+plot+"[/COLOR]")
            # reemplaza los <br /> por saltos de línea del xbmc
            scrapedplot = scrapedplot.replace("<br />","[CR]")
            # codifica el texto en utf-8 para que se puedan ver las tíldes y eñes
            scrapedplot = unicode( scrapedplot, "iso-8859-1" , errors="replace" ).encode("utf-8")
            fanart="http://s11.postimg.org/qu66qpjz7/zentorrentsfanart.jpg"
            tbd = TextBox("DialogTextViewer.xml", os.getcwd(), "Default")
            tbd.ask(title, scrapedplot,fanart)
            del tbd
            return
        else:
            scrapedplot = scrapertools.get_match(data,'"2"><br><br>(.*)<br><br><img')
            plotformat = re.compile('(.*?:).*?<br />',re.DOTALL).findall(scrapedplot)
            # Reemplaza las etiquetas con etiquetas formateadas con color azul y negrita
            for plot in plotformat:
                scrapedplot = scrapedplot.replace(plot,"[COLOR green][B]"+plot+"[/B][/COLOR]")
                plot = plot.replace(plot,"[COLOR white]"+plot+"[/COLOR]")
            # reemplaza los <br /> por saltos de línea del xbmc
            scrapedplot = scrapedplot.replace("<br />","[CR]")
            # codifica el texto en utf-8 para que se puedan ver las tíldes y eñes
            scrapedplot = unicode( scrapedplot, "iso-8859-1" , errors="replace" ).encode("utf-8")
            fanart="http://s11.postimg.org/qu66qpjz7/zentorrentsfanart.jpg"
            tbd = TextBox("DialogTextViewer.xml", os.getcwd(), "Default")
            tbd.ask(title, scrapedplot,fanart)
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











