# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Gestión de parámetros de configuración multiplataforma
#------------------------------------------------------------
# pelisalacarta
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
# Creado por: Jesús (tvalacarta@gmail.com)
# Licencia: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
#------------------------------------------------------------
# Historial de cambios:
#   - 'get_setting' y 'set_setting' modificados por Superberny 
#       para permitir la opcion de parametros propios del canal.
#------------------------------------------------------------

import platform_name

PLATFORM_NAME = platform_name.PLATFORM_NAME
print "PLATFORM_NAME="+PLATFORM_NAME
exec "import platformcode."+PLATFORM_NAME+".config as platformconfig"

def force_platform(platform_name):
    global PLATFORM_NAME
    
    PLATFORM_NAME = platform_name
    # En PLATFORM debería estar el módulo a importar
    try:
        exec "import platformcode."+PLATFORM_NAME+".config as platformconfig"
    except:
        exec "import "+PLATFORM_NAME+"config as platformconfig"

def get_platform():
    return PLATFORM_NAME

def get_library_support():
    return (PLATFORM_NAME=="xbmc" or PLATFORM_NAME=="xbmcdharma" or PLATFORM_NAME=="xbmceden" or PLATFORM_NAME=="boxee")

def get_system_platform():
    try:
        exec "import platformcode."+PLATFORM_NAME+".config as platformconfig"
    except:
        exec "import "+PLATFORM_NAME+"config as platformconfig"
    return platformconfig.get_system_platform()

def open_settings():
    try:
        exec "import platformcode."+PLATFORM_NAME+".config as platformconfig"
    except:
        exec "import "+PLATFORM_NAME+"config as platformconfig"
    return platformconfig.open_settings()

def get_setting(name,channel=""):
    try:
        #print "[config.py] get_setting en PLATFORM=%s" % PLATFORM
        exec "import platformcode."+PLATFORM_NAME+".config as platformconfig"
    except:
        exec "import "+PLATFORM_NAME+"config as platformconfig"
    # La cache recibe un valor por defecto la primera vez que se solicita

    if channel=="": #devuelve setting global (del plugin)
        dev=platformconfig.get_setting(name)

        if name=="download.enabled":
            try:
                from core import descargas
                dev="true"
            except:
                #import sys
                #for line in sys.exc_info():
                #    print line
                dev="false"
        
        elif name=="cookies.dir":
            dev=get_data_path()
        
        # TODO: (3.1) De momento la cache está desactivada...
        elif name=="cache.mode" and PLATFORM_NAME!="developer":
            dev="2"
    else: #devuelve setting del canal no del plugin
        from core import config_channel
        dev= config_channel.get_setting( name, channel)
    
    return dev

def set_setting(name,value,channel=""):
    #print "core set_setting ",name,value
    try:
        exec "import platformcode."+PLATFORM_NAME+".config as platformconfig"
    except:
        exec "import "+PLATFORM_NAME+"config as platformconfig"
        
    if channel=="": #cambia setting global (del plugin)
        platformconfig.set_setting(name,value)
    else: #cambia setting del canal no del plugin
        from core import config_channel
        config_channel.set_setting( name, value, channel)

def save_settings():
    try:
        exec "import platformcode."+PLATFORM_NAME+".config as platformconfig"
    except:
        exec "import "+PLATFORM_NAME+"config as platformconfig"
    platformconfig.save_settings()

def get_thumbnail_path():
    thumbnail_type = get_setting("thumbnail_type")
    if thumbnail_type=="0":
        WEB_PATH = "http://pelisalacarta.mimediacenter.info/posters/"
    elif thumbnail_type=="1":
        WEB_PATH = "http://pelisalacarta.mimediacenter.info/banners/"
    elif thumbnail_type=="2" or thumbnail_type=="":
        WEB_PATH = "http://pelisalacarta.mimediacenter.info/squares/"
    else:
        WEB_PATH = ""
    return WEB_PATH
    
def get_localized_string(code):
    try:
        exec "import platformcode."+PLATFORM_NAME+".config as platformconfig"
    except:
        exec "import "+PLATFORM_NAME+"config as platformconfig"
    return platformconfig.get_localized_string(code)

def get_library_path():
    try:
        exec "import platformcode."+PLATFORM_NAME+".config as platformconfig"
    except:
        exec "import "+PLATFORM_NAME+"config as platformconfig"
    return platformconfig.get_library_path()

def get_temp_file(filename):
    try:
        exec "import platformcode."+PLATFORM_NAME+".config as platformconfig"
    except:
        exec "import "+PLATFORM_NAME+"config as platformconfig"
    return platformconfig.get_temp_file(filename)

def get_runtime_path():
    try:
        exec "import platformcode."+PLATFORM_NAME+".config as platformconfig"
    except:
        exec "import "+PLATFORM_NAME+"config as platformconfig"
    return platformconfig.get_runtime_path()

def get_data_path():
    try:
        exec "import platformcode."+PLATFORM_NAME+".config as platformconfig"
    except:
        exec "import "+PLATFORM_NAME+"config as platformconfig"
    return platformconfig.get_data_path()

def get_cookie_data():
    import os
    ficherocookies = os.path.join( get_data_path(), 'cookies.dat' )

    cookiedatafile = open(ficherocookies,'r')
    cookiedata = cookiedatafile.read()
    cookiedatafile.close();

    return cookiedata

# Test if all the required directories are created
def verify_directories_created():
    import logger
    import os
    logger.info("verify_directories_created")

    # Force download path if empty
    download_path = get_setting("downloadpath")
    if download_path=="":
        download_path = os.path.join( get_data_path() , "downloads")
        set_setting("downloadpath" , download_path)

    # Force download list path if empty
    download_list_path = get_setting("downloadlistpath")
    if download_list_path=="":
        download_list_path = os.path.join( get_data_path() , "downloads" , "list")
        set_setting("downloadlistpath" , download_list_path)

    # Force bookmark path if empty
    bookmark_path = get_setting("bookmarkpath")
    if bookmark_path=="":
        bookmark_path = os.path.join( get_data_path() , "bookmarks")
        set_setting("bookmarkpath" , bookmark_path)

    # Create data_path if not exists
    if not os.path.exists(get_data_path()):
        logger.debug("Creating data_path "+get_data_path())
        try:
            os.mkdir(get_data_path())
        except:
            pass

    # Create download_path if not exists
    if not download_path.lower().startswith("smb") and not os.path.exists(download_path):
        logger.debug("Creating download_path "+download_path)
        try:
            os.mkdir(download_path)
        except:
            pass

    # Create download_list_path if not exists
    if not download_list_path.lower().startswith("smb") and not os.path.exists(download_list_path):
        logger.debug("Creating download_list_path "+download_list_path)
        try:
            os.mkdir(download_list_path)
        except:
            pass

    # Create bookmark_path if not exists
    if not bookmark_path.lower().startswith("smb") and not os.path.exists(bookmark_path):
        logger.debug("Creating bookmark_path "+bookmark_path)
        try:
            os.mkdir(bookmark_path)
        except:
            pass

    # Create library_path if not exists
    if not get_library_path().lower().startswith("smb") and not os.path.exists(get_library_path()):
        logger.debug("Creating library_path "+get_library_path())
        try:
            os.mkdir(get_library_path())
        except:
            pass
