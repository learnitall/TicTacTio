#!/usr/bin/env python

import logging
from logging.handlers import RotatingFileHandler
import sys
import pygame
import ai
import boards
import players
import tttoe


logFormat = logging.Formatter('%(asctime)s %(funcName)s (%(module)s): %(message)s')

# 20mb max file size, holding 3 logs
fileHandler = RotatingFileHandler('log.log', maxBytes=(20 * 10**6), backupCount=3)
fileHandler.setFormatter(logFormat)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormat)

rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)
rootLogger.addHandler(fileHandler)
rootLogger.addHandler(consoleHandler)

logging.debug("Logging initiated")
result = pygame.init()
logging.debug("Pygame initiated {}".format(result))
if result[1] != 0:
    logging.warning("WARNING: {} pygame module(s) unsuccessfully initiated (error: {})".format(result[1],
                                                                                               pygame.get_error()))

