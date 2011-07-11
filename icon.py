import pygame
from pygame.locals import *

from sprite import *
from button import *

__all__ = ['Icon']

class Icon(Button):
    """
Wrapper around the Button base class

Set callbacks for mouse click events using set_leftaction and
    set_rightaction. These callbacks must be function objects. 
    

to call:
myicon = Icon(pos, containers, [obj, padding, sound, num_pics])
pos - tuple(x,y) of upper-left corner of button
containers - pygame.sprite.Group() objects 
obj - a string or image that will be placed onto the button center
padding - tuple(x,y) of pixels that will extend the width/height of button
sound - a string filename of a valid sound object will be played on mouseover event
num_pics - a tuple(x,y) containing the number of pictures in the x
    and y directions that the passed image contains. 

to show:
myicon.show() - defined by Button
    """
    def __init__(self, pos, containers, obj = None, padding = (10,10), \
            sound = None, num_pics = (1,1) ):
        Button.__init__(self, pos, containers, obj, padding, num_pics)

        self.img = obj

        self.rightaction = None
        self.leftaction = None
        self.containers = containers
        if sound != None:
            self.set_sound(sound)
        else:
            self.sound = None
   
    def set_leftaction(self, leftaction, name):
        self.name = name
        self.leftaction = leftaction

    def set_rightaction(self, rightaction):
        self.rightaction = rightaction

    def set_sound(self, sound):
        self.sound = pygame.mixer.Sound(sound)

    def play_sound(self):
        if self.sound != None:
            self.sound.play()

    def left_click(self):
        try:
            self.leftaction(self.name)
        except:
            pass

    def right_click(self):
        try:
            self.rightaction()
        except:
            pass


