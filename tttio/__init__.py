#!/usr/bin/env python

import logging
import pygame
import ai
import boards
import players
import tttoe

logging.basicConfig(format='%(asctime)s %(funcName)s (%(module)s): %(message)s', level=logging.DEBUG,
                    datefmt='%b %d %H:%M:%S', filename='log.log')
pygame.init()

