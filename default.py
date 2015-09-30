# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta
# XBMC entry point
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

# Constants
__plugin__  = "pelisalacarta 3.9X"
__author__  = "pelisalacarta"
__url__     = "http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/"
__date__ = "27/03/2015"
__version__ = "3.91.99"

import os
import sys
from core import config
from core import logger

logger.info("[default.py] pelisalacarta 3.9X init...")

librerias = xbmc.translatePath( os.path.join( config.get_runtime_path(), 'lib' ) )
sys.path.append (librerias)

# Runs xbmc launcher
from platformcode.xbmc import launcher
launcher.run()