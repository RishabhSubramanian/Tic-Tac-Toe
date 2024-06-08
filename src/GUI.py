import sys
import numpy as np
from typing import Callable, Optional
from time import time
import pygame as pg
from TicTacToe import TicTacToe


class Button:
    """
    Class for a pg button
    """

    x: int
    y: int
    font: pg.font.Font
    text: str
    surface: pg.Surface
    rect: pg.Rect

    def __init__(self, text: str, pos: tuple[int, int], font: pg.font.Font, size: tuple[int, int],
                 foreground_color: str, boxed: bool, rect_color: Optional[str] = None) -> None:
        """
        Constructor for class
        """
        if ((not boxed) ^ (rect_color is None)):
            raise ValueError('Rectangle color must be specified only if the button is boxed')
        
        self.x, self.y = pos
        self.font = font
        self.surface = pg.Surface(size, pg.SRCALPHA)
        self.rect = pg.Rect(self.x, self.y, size[0], size[1])
        self.change(text, foreground_color, rect_color, boxed)

    def change(self, text: str, foreground_color: str, rect_color: Optional[str], boxed: bool) -> None:
        self.text = text
        self.surface.fill((0, 0, 0, 0))
        min_size = min(self.rect.width, self.rect.height)
        if boxed:
            assert rect_color
            pg.draw.rect(self.surface, rect_color, (0, 0, self.rect.width, self.rect.height),
                        int(min_size//40), int(min_size//4))
        rendered_text = self.font.render(text, True, foreground_color)
        self.surface.blit(rendered_text, ((self.rect.width - rendered_text.get_size()[0])/2, (self.rect.height - rendered_text.get_size()[1])/2))

    def show(self, screen: pg.Surface) -> None:
        screen.blit(self.surface, (self.x, self.y))

    def click(self, event: pg.event.Event) -> bool:
        x, y = pg.mouse.get_pos()
        if event.type == pg.MOUSEBUTTONDOWN:
            if pg.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    return True
        return False


BACKGROUND_COLOR = "#5F5F5F"
PIECES: dict[int, tuple[str, str]] = {
    1: ('X', '#A7C7E7'),
    2: ('O', '#FFD1DC'),
    3: ('V', '#C1E1C1'),
    4: ('M', '#FDFD96')
}


class GUI:
    """
    Class of the GUI for the game
    """

    screen: pg.Surface
    size: tuple[int, int]
    screen_type: int
    draw_functions: dict[int, Callable]
    buttons: dict[Button, Callable]
    fonts: dict[str, pg.font.Font]
    clock: pg.time.Clock
    starting_time: float
    num_players: int

    def __init__(self, width: int, height: int) -> None:
        """
        Constructor for class
        """
        pg.init()
        self.size = (width, height)
        self.screen = pg.display.set_mode(self.size, pg.RESIZABLE)
        pg.display.set_caption('Tic-Tac-Toe')
        self.screen_type = 0

        self.draw_functions = {
            0: self.draw_starting_screen,
            1: self.draw_player_selection,
            2: self.draw_game_screen
        }
        self.buttons = {}

        self.fonts = {
            'Huge Arcade': pg.font.Font("assets/fonts/arcade_font.ttf", min(height//3, width//2)),
            'Big Arcade': pg.font.Font("assets/fonts/arcade_font.ttf", min(height//10, width//7)),
            'Small Arcade': pg.font.Font("assets/fonts/arcade_font.ttf", min(height//20, width//14)),
            'Unicode': pg.font.Font("assets/fonts/unicode_font.ttf", min(height//30, width//20))
        }

        self.clock = pg.time.Clock()
        self.starting_time = time()
        self.num_players = 2

    def incr_num_players(self) -> None:
        if self.num_players < 4:
            self.num_players += 1

    def decr_num_players(self) -> None:
        if self.num_players > 2:
            self.num_players -= 1

    def next_screen(self) -> None:
        self.screen_type = (self.screen_type + 1) % 3

    def draw_starting_screen(self) -> None:
        assert self.screen_type == 0

        self.screen.fill(BACKGROUND_COLOR)

        title_text = self.fonts["Big Arcade"].render('Tic  Tac  Toe', True, '#A7C7E7')
        self.screen.blit(title_text, (self.size[0]/2 - title_text.get_size()[0]/2,
                                      self.size[1]/4 * (1 + np.sin(time() - self.starting_time)/10)))

        player_num_size = min(self.size[0]/7, self.size[1]/7)
        player_num_display = pg.Rect(self.size[0]/5, 3*self.size[1]/4, player_num_size, player_num_size)
        pg.draw.rect(self.screen, "#FFFFFF", player_num_display, int(player_num_size//20),
                     border_top_right_radius=int(player_num_size//4), border_bottom_right_radius=int(player_num_size//4))
        num_players_text = self.fonts["Small Arcade"].render(str(self.num_players), True, '#FFD1DC')
        self.screen.blit(num_players_text, (self.size[0]/5 + player_num_size/2 - num_players_text.get_size()[0]/2,
                                            3*self.size[1]/4 + player_num_size/2 - num_players_text.get_size()[1]/2))
        up_button = Button('↑', (self.size[0]//5 + int(player_num_size)//10, 3*self.size[1]//4),
                           self.fonts['Unicode'], (int(player_num_size)//10, int(player_num_size)//2),
                           "#FFD1DC", False)
        down_button = Button('↓', (self.size[0]//5 + int(player_num_size)//10, 3*self.size[1]//4 + int(player_num_size)//2),
                           self.fonts['Unicode'], (int(player_num_size)//10, int(player_num_size)//2),
                           "#FFD1DC", False)
        up_button.show(self.screen)
        down_button.show(self.screen)

        next_button = Button('Next', (4*self.size[0]//5 - 2*int(player_num_size), 3*self.size[1]//4), self.fonts['Small Arcade'],
                             (2*int(player_num_size), int(player_num_size)), "#FFD1DC", True, "#FFFFFF")
        next_button.show(self.screen)

        self.buttons = {
            up_button: self.incr_num_players,
            down_button: self.decr_num_players,
            next_button: self.next_screen
        }

    def draw_player_selection(self) -> None:
        assert self.screen_type == 1

        self.screen.fill(BACKGROUND_COLOR)

        padding = (self.size[0]//20, self.size[1]//20)
        table_dims = (9*self.size[0]//10, 9*self.size[1]//10)

        pg.draw.rect(self.screen, "#FFFFFF", pg.Rect(padding[0], padding[1], *table_dims),
                     min(padding)//8, min(padding))
        
        pg.draw.line(self.screen, "#FFFFFF", (padding[0], self.size[1]//2),
                     (self.size[0] - 11*padding[0]//10, self.size[1]//2), min(padding)//8)
        # pg.draw.line(self.screen, "#FFFFFF", (padding[0], 3*self.size[1]//4),
        #              (self.size[0] - 11*padding[0]//10, 3*self.size[1]//4), min(padding)//8)
        
        col_length = table_dims[0]/self.num_players
        for col in range(1,self.num_players):
            pg.draw.line(self.screen, "#FFFFFF", (padding[0] + col_length*col, padding[1]),
                         (padding[0] + col_length*col, self.size[1] - padding[1]), min(padding)//8)
            piece = self.fonts['Huge Arcade'].render(PIECES[col][0], True, PIECES[col][1])
            self.screen.blit(piece, (col_length*(col - 1/2), self.size[1]/4 - piece.get_height()/2 + piece.get_height()/20 * np.sin(time() - self.starting_time)))

        piece = self.fonts['Huge Arcade'].render(PIECES[self.num_players][0], True, PIECES[self.num_players][1])
        self.screen.blit(piece, (col_length*(col + 1/2), self.size[1]/4 - piece.get_height()/2 + piece.get_height()/20 * np.sin(time() - self.starting_time)))

    def draw_game_screen(self) -> None:
        assert self.screen_type == 2

        self.screen.fill(BACKGROUND_COLOR)

    def run(self) -> None:
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                
                if event.type == pg.VIDEORESIZE:
                    self.size = (event.w, event.h)
                    self.screen = pg.display.set_mode(self.size, pg.RESIZABLE)
                
                for button in self.buttons:
                    if button.click(event):
                        self.buttons[button]()

            self.draw_functions[self.screen_type]()

            pg.display.flip()
            self.clock.tick(60)

gui = GUI(1300, 800)

gui.run()