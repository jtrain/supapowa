import pygame

from constants import *
from sprite import *
from tiletypes import *

from gamestate import GameState, DefaultTile

__all__ = ['Mesh']


class Mesh(pygame.sprite.Sprite):
    def __init__(self, containers, members, size, pos):
        pygame.sprite.Sprite.__init__(self, containers)

        #make groups
        self.active = pygame.sprite.RenderUpdates()
        self.hidden = pygame.sprite.Group()

        # store the maximum x and y dimensions.
        self._maximums = size
        
        #create an array to hold all tiles
        self.__initarray(members, size)

        mesh = self.__makeback(size)
        self.background = mesh
        self.image = pygame.Surface(mesh.get_size())
        self.image.set_colorkey(TRANSPARENT)
        self.image.fill(TRANSPARENT)
        self.rect = pygame.Rect(pos, self.image.get_size())

        self.pos = pos
        self.kill()

        self.replace_tile = None

    def set_panel(self, panel):
        self.panel = panel

    def show(self, containers):
        self.add(containers)

    def update(self, *args):
        try:
            mouse = self.__mouseevent(args[0])
        except KeyError:
            pass
        self.active.clear(self.image, self.background)
        self.active.update(mouse)
        self.active.draw(self.image)

    def __mouseevent(self, mouse):
        rawpos, button_state = mouse
        left, middle, right = button_state

        pos = self.__relativepos(rawpos)

        #Check if mouse cursor is on any tile (tl) when click occurs
        if sum((pos in tl for tl in self.active)) == 0 and \
                right == 1:
            self.replace_tile = None

        self.__mousedown(left, right, pos)
        self.__mouseover(pos)

        return (pos, button_state)

    def build_tile(self, type):
        self.replace_tile = Tiledict[type]

    def sell_tile(self, soldtile):
        for basetile in self.hidden:
            if soldtile.location == basetile.location:
                soldtile.kill()
                basetile.add(self.active)

        # notify the game state of the tile being removed.
        gs = GameState()
        gs.remove_tile(soldtile.name)

    def __mouseover(self, pos):
        oneactive = False
        for tile in self.active:
            if pos in tile and not oneactive:
                tile.mouse_over(1)
                oneactive = True
            else:
                tile.mouse_over(0)

    def __mousedown(self, left, right, pos):
        if left: #if left click
            index = 1
        elif right: #if right click
            index = 3
        else: #return false if no clicks
            return False

        #if left == 1:
            #for panel in self.panels:
                #if not pos in panel and not self.showing_dynamic:
                    #panel.kill()

        match_found = False
        for tile in self.active:
            if not match_found:
                if pos in tile:
                    match_found = True
                    tile.set_bounding(True)
                else:
                    tile.set_bounding(False)
            else:
                tile.set_bounding(False)
            if pos in tile and tile.current_state == BUTTON_ON:
                if self.replace_tile == None:
                    click = tile.click(index)
                    if click:
                        self.panel.add_dynamic_panel((2,218), click, tile.name)
                        self.panel.show_panel(tile.name)
                else:
                    location = tile.location
                    newtile = self.replace_tile()
                    newtile.set_xy(location)
                    self.addtile(newtile, location)
                    self.replace_tile = None
        return True

    def __relativepos(self, pos):
        pos_x = pos[0] - self.pos[0]
        pos_y = pos[1] - self.pos[1]
        return (pos_x, pos_y)

    def __makeback(self, size):
        xdim = size[0] * TILE_WIDTH
        ydim = size[1] * TILE_HEIGHT + TILE_HEIGHT / 2
        mesh = pygame.Surface((xdim, ydim))
        mesh.fill(GREY)
        mesh.set_colorkey(TRANSPARENT)
        return mesh

    def addtile(self, newtile, pos):
        for tile in self.active:
            if tile.location == pos:
                if tile.type not in ['Water', 'Grass']:
                    # only allow creation of tiles on water or grass tiles.
                    return
                tile.kill()
                dohide = True
                for oldtile in self.hidden:
                    if tile.location == oldtile.location:
                        dohide = False
                if dohide:
                    tile.add(self.hidden)

        x, y = pos

        # save this into the array.
        self.array[y][x] = newtile

        xpos = x * (TILE_WIDTH - TILE_B + 2)
        if x % 2 == 0:
            ypos = y * ((TILE_HEIGHT) - 4)
        else:
            ypos = y * ((TILE_HEIGHT) - 4)+ TILE_HEIGHT / 2 - 3 

        newtile.set_pos((xpos, ypos))
        newtile.show(self.active)
        newtile.mesh = self

        # now update the game state.
        gs = GameState()

        if newtile.type in ['Water', 'Grass']:
            # early exit if this is a default tile.
            return

        # get the adjacent tiles to this tile.
        adjacent = self._adjacent((x, y))

        # remove tiles that are of a grass or water kind.
        connect = [
                    tile.name for tile in adjacent 
                        if tile.type not in ['Water', 'Grass']
                ]

        # set the name if this is a user added tile.
        try:
            newtile.name = gs.add_tile(newtile.type, newtile.info, connections=connect)
            gs.register(newtile.name, newtile.set_info)
            gs.register('rename', newtile.set_name)
        except DefaultTile:
            # can't register default tile with game state.
            pass

    def __initarray(self, members, size):
        xdim = size[0]
        ydim = size[1]
        #get the default tile
        d_tile, args = members['default']
        #create an xdim by ydim sized array of default tiles
        self.array = [
                        [d_tile(*args) for i in range(xdim)] 
                        for j in range(ydim)
                    ]

        for location in members:
            if location == 'default':
                continue #don't do the default tile again
            #members contains a tileobject and init arguments for it
            tileobject, args = members[location]
            #create the tile
            tile = tileobject(*args)
            #slot it into the array
            self.array[location[0]][location[1]] = tile

        for j in range(ydim):
            for i in range(xdim):
                self.array[j][i].set_xy((i,j))
                self.addtile(self.array[j][i], (i,j))

    def __contains__(self, pos):
        return self.rect.collidepoint(pos)

    def _adjacent(self, pos):
        """Find adjacent cells according to the formula:
        if x is odd -> get (x-1, y), (x-1, y+1), (x, y-1), (x, y+1)
                            (x+1, y), (x+1, y+1)
        if x is even -> get (x-1, y), (x-1, y-1), (x, y-1), (x, y+1)
                            (x+1, y), (x+1, y-1)"""
        x, y = pos
        # maximum x and y dimensions.
        xdim, ydim = self._maximums

        if x % 2 == 1:
            # define adjacent cells for odd case.
            cells = [   
                        (max(x - 1, 0), y), 
                        (max(x - 1, 0), min(y + 1, ydim)), 
                        (x, max(y - 1, 0)), 
                        (x, min(y + 1, ydim)),
                        (min(x + 1, xdim), y), 
                        (min(x + 1,xdim), min(y + 1, ydim))
                    ]
        else:
            # define adjacent cells for even case.
            cells = [
                        (max(x - 1, 0), y), 
                        (max(x - 1, 0), max(y - 1, 0)), 
                        (x, max(y - 1, 0)), 
                        (x, min(y + 1, ydim)),
                        (min(x + 1, xdim), y), 
                        (min(x + 1, xdim), max(y - 1, 0))
                    ]

        adjacent = []
        for cell in cells:
            # get the actual object in the cell, also ensure that cell != pos.
            if cell == pos:
                continue
            x, y = cell

            try:
                adjacent.append(self.array[int(y)][int(x)])
            except IndexError:
                continue

        # return the unique set of valid adjacent cells.
        return set(adjacent)


            


