import pygame

from constants import *
from font import small_font


__all__ = ['Button', 'load_img', 'Exit_button']

def load_img(filename, num_pics=(1,1)):
    try:
        image = pygame.image.load(filename)
        colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey)
        image.convert_alpha()
        w, h = image.get_size()
        x_step = float(w) / num_pics[0] #width of each sub image
        y_step = float(h) / num_pics[1] #height of each sub image

        images = []
        for x in range(num_pics[0]):
            for y in range(num_pics[1]):
                images.append(image.subsurface((x_step*x, y_step*y, x_step, y_step)))

    except Exception, msg:
        print "Error in Load Image: ", msg
        images = None
    return images

class Button(pygame.sprite.Sprite):
    def __init__(self, pos, containers, obj=None, 
                    padding=(10,10), num_pics=(1,1)):
        txt = None
        img = None
        if '.' in obj:
            img = obj
        else:
            txt = obj

        pygame.sprite.Sprite.__init__(self, containers)

        self.pos = pos
        self.containers = containers
        
        self.img_index = 0 #currently indexed image
        self.num_images = num_pics[0]*num_pics[1]

        if txt:
            self.text = small_font(txt, TEXT_COL)
        else:
            self.text = None

        if img:
            self.icons = load_img(img, num_pics)
        else:
            self.icons = None


        self.current_state = BUTTON_OFF
        self.colours = { BUTTON_OFF: BUTTON_INNER_BASE, \
                            BUTTON_ON: BUTTON_INNER_HOVER}
        self.shown = False
        self.pad = padding
        self.redraw()
        self.kill()

    def show(self, containers=None):
        try:
            if containers != None:
                self.containers = [containers]
        except Exception, msg:
            print msg
        self.add(self.containers)
        self.redraw()

    def redraw(self, colour=BUTTON_INNER_BASE):
        if self.text:
            button_rect = self.text.get_rect().inflate(self.pad[0], self.pad[1])
        else:
            button_rect = pygame.Rect(0,0,0,0)
        if not self.icons is None:
            width, height = self.icons[self.img_index].get_size()
            button_rect.inflate_ip(self.pad[0] + width, height + self.pad[1])
        
        #make outer box
        button = pygame.Surface(button_rect.size) 
        button.fill(BUTTON_BACK)

        # make the inner box
        inner = pygame.Surface((button_rect.width - 2, button_rect.height - 2))
        inner.fill(colour)
        button.blit(inner, (1,1))
        
        self.__blit_button(button)

    def __blit_button(self, button):
        self.image = button
        self.rect = button.get_rect()
        self.rect.topleft = self.pos #absolute position
        self.__render_content()
        self.shown = True

    def __render_content(self):
        if self.text:
            textpos = self.text.get_rect(center = (
                                                  self.image.get_rect().centerx, 
                                                  self.image.get_rect().centery
                                                )
                                        )
            self.image.blit(self.text, textpos)
        if self.icons:
            imagepos = self.icons[self.img_index].get_rect(center = (
                                                self.image.get_rect().centerx, 
                                                self.image.get_rect().centery
                                                )
                                            )

            self.image.blit(self.icons[self.img_index], imagepos)

    def __contains__(self, item):
        if self.shown:
            return self.rect.collidepoint(item)
        return False

    def mouse_over(self, new_state):
        #state = 1: on 0: off
        if self.current_state != new_state:
            if self.current_state == 0 and new_state == 1:
                self.play_sound()
            self.current_state = new_state
            colour = self.colours[new_state] #get colour
            self.redraw(colour)

    def update(self, *args, **kwargs):
        if not self.shown:
            self.redraw()

    def set_pos(self, pos):
        self.pos = pos
        self.rect.topleft = pos
        
    def get_state(self):
        return self.current_state == BUTTON_ON

    def click(self, button):
        if button == 1: #left click
            return self.left_click()
        elif button == 3: #right click
            return self.right_click()

    def increment_image(self,increment = 1):
        self.img_index = (self.img_index + increment) % self.num_images
        self.redraw()

class Exit_button(Button):
    def __init__(self, pos, containers, left_click, obj, padding = (10,10)):
        Button.__init__(self, pos, containers, obj, padding)
        self.left_click = left_click

    def right_click(self):
        return None
    def play_sound(self):
        pass

