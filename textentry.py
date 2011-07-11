import pygame
from pygame.locals import *
from string import maketrans

from constants import *
from font import *
from button import *

from textgrab import TextGrab

__all__ = ['Textentry', 'PermaText']


class Textentry(pygame.sprite.Sprite):
    def __init__(self, pos, containers, callback, heading='Enter Text..',
                                    num_chars=10, background=None):
        """ A text entry widget. 

    Args:
        pos - tuple describing position (can be None and set later).
        containers - pygame groups that this text module will join.
        callback - a function to call with the string return value or None.
        [heading] - an optional argument to specify a string to prompt user.
        [num_chars] - the number of characters to allow user to enter.
        [background] - set the background colour.
    Return:
        a string if save or enter is hit, None if cancelled.
        """
        if background is None:
            background = BUTTON_INNER_BASE

        pygame.sprite.Sprite.__init__(self, containers)

        self._heading = small_font(heading, WHITE, background)

        # allow for one extra character the prompt pipe.
        num_chars += 1
        self._charwidth = small_font('A' * num_chars, WHITE, background)
        # maximum amount of characters allowed. 
        self._maximum = num_chars

        # call on saving text.
        self._callback = callback

        self._containers = containers

        # make close\save button.
        self._buttons = pygame.sprite.Group()

        # set the button's position relative to this panel.
        button_posx = self._charwidth.get_width() + 2
        button_posy = self._heading.get_height() 
        button_pos = (button_posx, button_posy)

        button = Exit_button(button_pos, containers=[self._buttons], 
                            left_click=self.save, obj='save', padding=(4,0))

        self._button = button

        self.pos = pos
        # create a readonly background panel, and our writeable image.
        image, self.rect = self._make_panel(background)
        self.image = pygame.Surface(self.rect.size)
        self.image.blit(image, (0,0))

        self.text = "|"
        self.displayed_text = ""

        #translation between key and SHIFT + key
        self.translate = maketrans("0123456789,./'-=;", ')!@#$%^&*(<>?"_+:')
        self.events = {"backspace": self.del_char, "return": self.save,\
                "left shift": self.__set_shift, "right shift": self.__set_shift}
        self.allowable = 'abcdefghijklmnopqrstuvwxyz0123456789!@$%&()<>.,?\'"+-=_:; '
        self.shift = False

        self.kill()

    def _make_panel(self, background):
        # make textentry surface.
        self.textentry = pygame.Surface(self._charwidth.get_size())
        self.textentry.fill(BUTTON_BACK)
        # define the inner surface, a different colour to outer.
        self.inner = pygame.Surface(
                                    (
                                        self._charwidth.get_width() - 2, 
                                        self._charwidth.get_height() - 2
                                    )
                                )
        self.inner.fill(TEXT_ENTRY_INNER)
        self.textentry.blit(self.inner, (1,1))
        self.textentry_posy = self.textentry.get_height()

        # make overall surface.
        sizex = self._charwidth.get_width() + self._button.image.get_width() + 2
        sizey = self._heading.get_height() + self._charwidth.get_height()
        box = pygame.Surface((sizex, sizey))
        box.fill(background)

        box.blit(self._heading, (2,0))
        box.blit(self.textentry, (2, self.textentry_posy))

        self.panel = box
        rect = pygame.Rect(self.pos, box.get_size())

        return box, rect

    def show(self, containers=None):
        txtmarshal = TextGrab()
        txtmarshal.register(self.get_char)
        if containers:
            self.add(containers)
        else:
            self.add(self._containers)
        self._button.show()

    def set_pos(self, pos):
        self.pos = pos
        self.rect.topleft = pos

    def get_char(self, keycode):
        char = pygame.key.name(keycode)
        try:
            function = self.events[char]
            return function()
        except KeyError:
            pass
        if char == 'space': #manually set space
            char = ' '
        if self.shift:
            char = char.upper()
            char = char.translate(self.translate)
        if char.lower() in self.allowable:
            if len(self.text) < self._maximum:
                self.text = self.text.strip('|')
                self.text += char + '|'
        self.shift = False


    def del_char(self):
        self.text = self.text[:len(self.text) - 2] + '|'

    def save(self):
        self._callback(self.displayed_text.strip('|'))
        self.close()

    def update(self, *args):
        mouse = self._mouseevent(args[0])

        self._buttons.clear(self.image, self.panel)
        self._buttons.update(mouse)
        self._buttons.draw(self.image)

        if self.text == self.displayed_text:
            return
        text = small_font(self.text, BLACK, TEXT_ENTRY_INNER)
        self.textentry.blit(self.inner, (1,1))
        self.textentry.blit(text, (1,0))
        self.image.blit(self.textentry, (2,self.textentry_posy))
        self.displayed_text = self.text

    def _mouseevent(self, mouse):
        """
        mouse object:
        tuple(tuple(x,y), tuple(m1,m2.m3))
        """
        rawpos, button_state = mouse
        left, middle, right = button_state

        # get pos relative to this panel.
        pos = self._relativepos(rawpos)

        if not (rawpos in self):
            self._mousedown(left, right, pos)
            return (pos, button_state)
        if not self._mousedown(left, right, pos):
            self._mouseover(pos)

        return (pos, button_state)

    def _mousedown(self, left, right, pos):
        if left:
            index = 1
        elif right:
            index = 3
        else:
            return False

        for button in self._buttons:
            if button.get_state():
                click = button.click(index)

        return True

    def _mouseover(self, pos):
        for button in self._buttons:
            if pos in button:
                button.mouse_over(1)
            else:
                button.mouse_over(0)

    def _relativepos(self, pos):
        pos_x = pos[0] - self.pos[0]
        pos_y = pos[1] - self.pos[1]
        return (pos_x, pos_y)

    def close(self):
        txtmarshal = TextGrab()
        txtmarshal.deregister()
        self._button.kill()
        self.kill()

    def __set_shift(self):
        self.shift = True
        
    def __contains__(self, pos):
        if self.alive():
            return self.rect.collidepoint(pos)
        return True

class PermaText(Textentry):
    """A permanent text entry, only closes when explicitly told."""
    def save(self):
        self._callback(self.displayed_text.strip('|'))
        self.text = '|'

