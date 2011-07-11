import pygame
from pygame.locals import *

from constants import *
import textwrap
__all__ = ['small_font', 'large_font']

pygame.font.init()

def large_font(text, colour, background_colour = TRANSPARENT, width=None):
    return font(text, colour, background_colour, HEADING_FONT_SIZE, bold=True, 
            width=width)

def small_font(text, colour, background_colour=TRANSPARENT, width=None):
    return font(text, colour, background_colour, width=width)

def font(text, colour, background_colour, size = DEFAULT_FONT_SIZE, bold=False,
        width=None):
    if width:
        raw_lines = textwrap.wrap(text, width)
    else:
        raw_lines = text.split('\n') 
    font_object = pygame.font.Font('SUPERHEL.ttf', size)
    font_object.set_bold(bold)
    render = font_object.render
    rendered_lines = []
    max_height, max_width = 0, 0
    for line in raw_lines:
        rendered_line = render(line, 1, colour)
        rendered_lines.append(rendered_line)
        width, height = rendered_line.get_size()

        #add the height of new line plus some padding
        max_height += height 
        max_width = max(max_width, width) 

    #return a rectangle large enough for all text plus some padding
    text_rect = pygame.Rect((0,0),(max_width, max_height)).inflate(2, 0)
    text_surface = pygame.Surface(text_rect.size)
    text_surface.fill(background_colour)
    text_surface.set_colorkey(background_colour)

    x = text_surface.get_rect().left + 1
    y = 0
    for line in rendered_lines:
        text_surface.blit(line, (x,y)) 
        y += line.get_height() 

    return text_surface

