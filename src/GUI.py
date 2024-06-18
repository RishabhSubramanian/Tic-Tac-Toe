import sys
import numpy as np
from typing import Callable, Optional
import time
import pygame as pg
from TicTacToe import TicTacToe
from Bot import Bot

class Button:
    """
    Class for a pygame button
    
    Attributes:
        x [float]: The x-coordinate of the button.
        y [float]: The y-coordinate of the button.
        font [pg.font.Font]: The font to use for the button text.
        text [str]: The text to display on the button.
        surface [pg.Surface]: The surface of the button.
        rect [pg.Rect]: The rectangle bounding box of the button.
    
    Methods:
        change: Changes the text and appearance of the button.
        show: Displays the button on the screen.
        click: Checks if the button has been clicked and returns True if it has.
    """

    x: float
    y: float
    font: pg.font.Font
    text: str
    surface: pg.Surface
    rect: pg.Rect

    def __init__(self, text: str, pos: tuple[float, float], font: pg.font.Font, size: tuple[float, float],
                 foreground_color: str, boxed: bool, rect_color: Optional[str] = None) -> None:
        """
        Initializes the button with the given parameters.

        Arguments:
            text [str]: The text to display on the button.
            pos [tuple[float, float]]: The position of the button.
            font [pg.font.Font]: The font to use for the button text.
            size [tuple[float, float]]: The size of the button.
            foreground_color [str]: The color of the text on the button.
            boxed [bool]: Whether the button is boxed or not.
            rect_color [Optional[str]]: The color of the rectangle of the button. Only required if
                the button is boxed.
        """
        if ((not boxed) ^ (rect_color is None)):
            raise ValueError('Rectangle color must be specified only when the button is boxed')

        self.x, self.y = pos
        self.font = font
        self.surface = pg.Surface(size, pg.SRCALPHA)
        self.rect = pg.Rect(self.x, self.y, size[0], size[1])
        self.change(text, foreground_color, rect_color, boxed)

    def change(self, text: str, foreground_color: str, rect_color: Optional[str], boxed: bool) -> None:
        """
        Changes the text and appearance of the button.
        
        Arguments:
            text [str]: The new text to display on the button.
            foreground_color [str]: The color of the text on the button.
            rect_color [Optional[str]]: The color of the rectangle of the button. Only required if
                the button is boxed.
            boxed [bool]: Whether the button is boxed or not.
        """
        self.text = text
        self.surface.fill((0, 0, 0, 0))
        min_size = min(self.rect.width, self.rect.height)
        if boxed:
            assert rect_color
            pg.draw.rect(self.surface, rect_color, (0, 0, self.rect.width, self.rect.height),
                        int(min_size//20), int(min_size//4))
        rendered_text = self.font.render(text, True, foreground_color)
        self.surface.blit(rendered_text, ((self.rect.width - rendered_text.get_size()[0])/2,
                                          (self.rect.height - rendered_text.get_size()[1])/2))

    def show(self, screen: pg.Surface) -> None:
        """
        Displays the button on the screen.
        
        Arguments:
            screen [pg.Surface]: The screen to display the button on.
        """
        screen.blit(self.surface, (self.x, self.y))

    def click(self, event: pg.event.Event) -> bool:
        """
        Checks if the button has been clicked and returns True if it has.
        
        Arguments:
            event [pg.event.Event]: The event to check for a click.
        
        Returns [bool]: True if the button has been clicked.
        """
        x, y = pg.mouse.get_pos()
        if event.type == pg.MOUSEBUTTONDOWN:
            if pg.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    return True
        return False


BACKGROUND_COLOR = "#5F5F5F" # Dark grey
PIECES: list[tuple[str, str]] = [('X', '#A7C7E7'), ('O', '#FFD1DC'),
                                 ('V', '#C1E1C1'), ('W', '#FDFD96')] # Piece characters and their colors

class GUI:
    """
    Class of the GUI for the game
    
    Attributes:
        screen [pg.Surface]: The pygame screen object.
        screen_size [tuple[int, int]]: The size of the screen.
        screen_type [int]: The type of screen to display.
        draw_functions [dict[int, Callable]]: Maps the screen type to the functions to draw each screen.
        buttons [list[tuple[Button, Callable]]]: The buttons on the screen and the functions they call.
        fonts [dict[str, pg.font.Font]]: The fonts to use for the text on the screen.
        clock [pg.time.Clock]: The pygame clock object.
        starting_time [float]: The time the game started. Used for animations.
        num_players [int]: The number of players in the game.
        board_size [int]: The size of the board (number of rows or columns).
        player_types [list[bool]]: The types of each player (human or bot). True for bot, False for human.
        bots [list[Optional[Bot]]]: The bot objects for each player. None if the player is human.
        game [TicTacToe]: The game object.
    
    Methods:
        incr_num_players: Increases the number of players in the game.
        decr_num_players: Decreases the number of players in the game.
        incr_board_size: Increases the size of the board.
        decr_board_size: Decreases the size of the board.
        next_screen: Changes screen_type to the next screen.
        start_game: Changes screen_type to the game screen and initializes the game object.
        change_player_type: Changes the player type of the given player.
        draw_starting_screen: Draws the starting screen of the game to the screen.
        draw_player_selection: Draws the player selection screen of the game to the screen.
        draw_game_screen: Draws the game screen with the current game state to the screen.
        run: Main loop of the game.
    """

    screen: pg.Surface
    screen_size: tuple[int, int]
    screen_type: int
    draw_functions: dict[int, Callable]
    buttons: list[tuple[Button, Callable]]
    fonts: dict[str, pg.font.Font]
    clock: pg.time.Clock
    starting_time: float
    num_players: int
    board_size: int
    player_types: list[bool]
    bots: list[Optional[Bot]]
    game: TicTacToe

    def __init__(self, width: int, height: int) -> None:
        """
        Initializes the GUI with the given screen size.
        
        Arguments:
            width [int]: The width of the screen.
            height [int]: The height of the screen.
        """
        pg.init()
        self.screen_size = (width, height)
        self.screen = pg.display.set_mode(self.screen_size, pg.RESIZABLE)
        pg.display.set_caption('Tic-Tac-Toe')
        pg.display.set_icon(pg.image.load("assets/images/icon.png"))
        self.screen_type = 0

        self.draw_functions = {
            0: self.draw_starting_screen,
            1: self.draw_player_selection,
            2: self.draw_game_screen
        }
        self.buttons = []

        self.clock = pg.time.Clock()
        self.starting_time = time.time()
        self.num_players = 2
        self.board_size = 3
        self.player_types = [False, False]
        self.bots = [None, None]

        self.fonts = {
            'Huge Arcade': pg.font.Font("assets/fonts/Press_Start_2P.ttf", min(height//7, width//4)),
            'Big Arcade': pg.font.Font("assets/fonts/Press_Start_2P.ttf", min(height//20, width//14)),
            'Small Arcade': pg.font.Font("assets/fonts/Press_Start_2P.ttf", min(height//30, width//21)),
            'Tiny Arcade': pg.font.Font("assets/fonts/Press_Start_2P.ttf", min(height//40, width//28)),
            'Unicode': pg.font.Font("assets/fonts/Falling_Sky.otf", min(height//30, width//20)),
            'Piece': pg.font.Font("assets/fonts/Press_Start_2P.ttf", int(9*min((9*self.screen_size[0]/10)/self.board_size,
                                                                            (16*self.screen_size[1]/25)/self.board_size)/10))
        }

    def incr_num_players(self) -> None:
        """
        Increases the number of players in the game.
        """
        if self.num_players < 4:
            if self.board_size != 3:
                self.num_players += 1
                self.player_types += [False]
                self.bots += [None]

    def decr_num_players(self) -> None:
        """
        Decreases the number of players in the game.
        """
        if self.num_players > 2:
            self.num_players -= 1
            self.player_types.pop()

    def incr_board_size(self) -> None:
        """
        Increases the size of the board.
        """
        if self.board_size < 7:
            self.board_size += 1
            new_size = int(9*min((9*self.screen_size[0]/10)/self.board_size,
                                 (16*self.screen_size[1]/25)/self.board_size)/10)
            self.fonts['Piece'] = pg.font.Font("assets/fonts/Press_Start_2P.ttf", new_size)

    def decr_board_size(self) -> None:
        """
        Decreases the size of the board.
        """
        if self.board_size > 4:
            self.board_size -= 1
            new_size = int(9*min((9*self.screen_size[0]/10)/self.board_size,
                                 (16*self.screen_size[1]/25)/self.board_size)/10)
            self.fonts['Piece'] = pg.font.Font("assets/fonts/Press_Start_2P.ttf", new_size)
        elif self.board_size == 4:
            if self.num_players == 2:
                self.board_size -= 1
                new_size = int(9*min((9*self.screen_size[0]/10)/self.board_size,
                                        (16*self.screen_size[1]/25)/self.board_size)/10)
                self.fonts['Piece'] = pg.font.Font("assets/fonts/Press_Start_2P.ttf", new_size)

    def next_screen(self) -> None:
        """
        Changes screen_type to the next screen.
        """
        self.screen_type = (self.screen_type + 1) % 3

    def start_game(self) -> None:
        """
        Changes screen_type to the game screen and initializes the game object.
        """
        self.screen_type = 2
        self.buttons = []
        self.game = TicTacToe(self.num_players, self.board_size)
        for i in range(self.num_players):
            if self.player_types[i]:
                self.bots[i] = Bot(self.game, i+1)

    def change_player_type(self, player: int):
        """
        Changes the player type of the given player.
        """
        self.player_types[player-1] = not self.player_types[player-1]

    def draw_starting_screen(self) -> None:
        """
        Draws the starting screen of the game to the screen.
        """
        assert self.screen_type == 0

        self.screen.fill(BACKGROUND_COLOR)

        title_text = self.fonts["Big Arcade"].render('TIC-TAC-TOE', True, '#A7C7E7')
        self.screen.blit(title_text, (self.screen_size[0]/2 - title_text.get_size()[0]/2,
                                      self.screen_size[1]/4 * (1 + np.sin(time.time() - self.starting_time)/10)))

        box_size = min(self.screen_size[0]/7, self.screen_size[1]/7)

        player_text = self.fonts['Small Arcade'].render('PLAYERS', True, '#A7C7E7')
        self.screen.blit(player_text, (self.screen_size[0]/5 + box_size/2 - player_text.get_width()/2,
                                       self.screen_size[1]/2 - box_size/2))
        player_num_display = pg.Rect(self.screen_size[0]/5, self.screen_size[1]/2, box_size, box_size)
        pg.draw.rect(self.screen, "#FFFFFF", player_num_display, int(box_size//20),
                     border_top_right_radius=int(box_size//4), border_bottom_right_radius=int(box_size//4))
        num_players_text = self.fonts["Small Arcade"].render(str(self.num_players), True, '#FFD1DC')
        self.screen.blit(num_players_text, (self.screen_size[0]/5 + box_size/2 - num_players_text.get_size()[0]/2,
                                            self.screen_size[1]/2 + box_size/2 - num_players_text.get_size()[1]/2))
        num_up_button = Button('↑', (self.screen_size[0]/5 + int(box_size)/10, self.screen_size[1]/2),
                           self.fonts['Unicode'], (int(box_size)/10, int(box_size)/2),
                           "#FFD1DC", False)
        num_down_button = Button('↓', (self.screen_size[0]/5 + int(box_size)/10, self.screen_size[1]/2 + int(box_size)/2),
                           self.fonts['Unicode'], (int(box_size)/10, int(box_size)/2),
                           "#FFD1DC", False)
        num_up_button.show(self.screen)
        num_down_button.show(self.screen)
        
        size_title_text = self.fonts['Small Arcade'].render('SIZE', True, '#A7C7E7')
        self.screen.blit(size_title_text, (4*self.screen_size[0]/5 - box_size/2 - size_title_text.get_width()/2,
                                       self.screen_size[1]/2 - box_size/2))
        size_display = pg.Rect(4*self.screen_size[0]/5 - box_size, self.screen_size[1]/2, box_size, box_size)
        pg.draw.rect(self.screen, "#FFFFFF", size_display, int(box_size//20),
                     border_top_left_radius=int(box_size//4), border_bottom_left_radius=int(box_size//4))
        size_text = self.fonts["Small Arcade"].render(str(self.board_size), True, '#FFD1DC')
        self.screen.blit(size_text, (4*self.screen_size[0]/5 - box_size/2 - size_text.get_size()[0]/2,
                                            self.screen_size[1]/2 + box_size/2 - size_text.get_size()[1]/2))
        size_up_button = Button('↑', (4*self.screen_size[0]/5 - 2*int(box_size)/10, self.screen_size[1]/2),
                           self.fonts['Unicode'], (int(box_size)/10, int(box_size)/2),
                           "#FFD1DC", False)
        size_down_button = Button('↓', (4*self.screen_size[0]/5 - 2*int(box_size)/10, self.screen_size[1]/2 + int(box_size)/2),
                           self.fonts['Unicode'], (int(box_size)/10, int(box_size)/2),
                           "#FFD1DC", False)
        size_up_button.show(self.screen)
        size_down_button.show(self.screen)

        next_button = Button('NEXT', (self.screen_size[0]/2 - int(box_size), 3*self.screen_size[1]/4),
                             self.fonts['Small Arcade'], (2*int(box_size), int(box_size)),
                             "#FFD1DC", True, "#FFFFFF")
        next_button.show(self.screen)

        self.buttons = [
            (num_up_button, self.incr_num_players),
            (num_down_button, self.decr_num_players),
            (size_up_button, self.incr_board_size),
            (size_down_button, self.decr_board_size),
            (next_button, self.next_screen)
        ]

    def draw_player_selection(self) -> None:
        """
        Draws the player selection screen of the game to the screen.
        """
        assert self.screen_type == 1

        self.screen.fill(BACKGROUND_COLOR)

        padding = (self.screen_size[0]/20, self.screen_size[1]/20)
        table_dims = (9*self.screen_size[0]/10, 8*self.screen_size[1]/10)

        pg.draw.rect(self.screen, "#FFFFFF", pg.Rect(padding[0], padding[1], *table_dims),
                     int(min(padding)//8), int(min(padding)))

        pg.draw.line(self.screen, "#FFFFFF", (padding[0], padding[1] + table_dims[1]/2),
                     (self.screen_size[0] - 11*padding[0]/10, padding[1] + table_dims[1]/2), int(min(padding)//8))

        col_length = table_dims[0]/self.num_players
        for col in range(1,self.num_players):
            pg.draw.line(self.screen, "#FFFFFF", (padding[0] + col_length*col, padding[1]),
                         (padding[0] + col_length*col, padding[1] + table_dims[1]), int(min(padding)//8))

        self.buttons = []
        box_size = min(col_length, table_dims[1]/3)
        for col in range(1, self.num_players + 1):
            piece = self.fonts['Huge Arcade'].render(PIECES[col-1][0], True, PIECES[col-1][1])
            self.screen.blit(piece, (padding[0] + col_length*(col - 1/2) - piece.get_width()/2,
                                     padding[1] + table_dims[1]/4 - piece.get_height()/2 +
                                     piece.get_height()/15 * np.sin(time.time() - self.starting_time)))

            font_name = 'Big Arcade' if self.num_players != 4 else 'Small Arcade'
            text_rendered = self.fonts[font_name].render('CPU?', True, '#FFFFFF')
            self.screen.blit(text_rendered, (padding[0] + col_length*(col - 1/2) - text_rendered.get_width()/2,
                                             padding[1] + 5*table_dims[1]/8 - text_rendered.get_height()/2))

            cpu_text = 'X' if self.player_types[col-1] else ''
            cpu_button = Button(cpu_text, (padding[0] + int(col_length*(col-1/2) - box_size/4), padding[1] + 3*table_dims[1]/4),
                                self.fonts[font_name], (int(0.5*box_size), int(0.5*box_size)),
                                PIECES[col-1][1], True, "#FFFFFF")
            cpu_button.show(self.screen)

            self.buttons.append((cpu_button, lambda player=col: self.change_player_type(player)))

        next_button = Button('START', (3*self.screen_size[0]/4, self.screen_size[1] - 2*padding[1]),
                             self.fonts['Tiny Arcade'], (3*self.screen_size[0]/16, padding[1]),
                             '#FFFFFF', True, '#FFFFFF')
        next_button.show(self.screen)

        self.buttons.append((next_button, self.start_game))

    def draw_game_screen(self) -> None:
        """
        Draws the game screen with the current game state to the screen.
        """
        assert self.screen_type == 2

        self.screen.fill(BACKGROUND_COLOR)

        cell_size = min((9*self.screen_size[0]/10)/self.board_size, (16*self.screen_size[1]/25)/self.board_size)
        padding = ((self.screen_size[0] - cell_size*self.board_size)/2, (4*self.screen_size[1]/5 - cell_size*self.board_size)/2)

        for i in range(1, self.board_size):
            pg.draw.line(self.screen, "#FFFFFF", (padding[0], padding[1] + i*cell_size),
                         (self.screen_size[0] - padding[0], padding[1] + i*cell_size), int(cell_size//20))
            pg.draw.line(self.screen, "#FFFFFF", (padding[0] + i*cell_size, padding[1]),
                         (padding[0] + i*cell_size, 4*self.screen_size[1]/5 - padding[1]), int(cell_size//20))

        for row in range(self.board_size):
            for col in range(self.board_size):
                cell = self.game.grid.get_cell((row, col))

                if self.game.game_over:
                    winning_line = self.game.winning_line()
                    assert winning_line is not None
                    if (row, col) in winning_line:
                        pg.draw.rect(self.screen, "#55B3A2", pg.Rect(padding[0]+(col+1/30)*cell_size,
                                                                     padding[1]+(row+1/30)*cell_size,
                                                                     0.95*cell_size, 0.95*cell_size))

                if cell != 0:
                    piece = self.fonts['Piece'].render(PIECES[cell-1][0], True, PIECES[cell-1][1])
                    self.screen.blit(piece, (padding[0] + (col+1/20)*cell_size + (cell_size - piece.get_width())/2,
                                            padding[1] + (row+1/20)*cell_size + (cell_size - piece.get_height())/2))

        if self.game.game_over:
            if len(self.game.winners()) > 1:
                winning_text = self.fonts['Big Arcade'].render('TIE', True, '#FFFFFF')
            else:
                winning_text = self.fonts['Big Arcade'].render(PIECES[self.game.winners()[0]-1][0] + ' HAS WON',
                                                               True, PIECES[self.game.winners()[0]-1][1])
            self.screen.blit(winning_text, (self.screen_size[0]/2 - winning_text.get_width()/2,
                                            9*self.screen_size[1]/10 - winning_text.get_height()/2))
        else:
            current_player = self.fonts['Huge Arcade'].render(PIECES[self.game.cur_player-1][0], True,
                                                              PIECES[self.game.cur_player-1][1])
            self.screen.blit(current_player, (self.screen_size[0]/4 - current_player.get_width()/2,
                                              9*self.screen_size[1]/10 - current_player.get_height()/2))

    def run(self) -> None:
        """
        Main loop of the game.
        """
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                
                if event.type == pg.VIDEORESIZE:
                    self.screen_size = (event.w, event.h)
                    self.screen = pg.display.set_mode(self.screen_size, pg.RESIZABLE)
                    self.fonts = {
                        'Huge Arcade': pg.font.Font("assets/fonts/Press_Start_2P.ttf", min(event.h//7, event.w//4)),
                        'Big Arcade': pg.font.Font("assets/fonts/Press_Start_2P.ttf", min(event.h//20, event.w//14)),
                        'Small Arcade': pg.font.Font("assets/fonts/Press_Start_2P.ttf", min(event.h//30, event.w//21)),
                        'Tiny Arcade': pg.font.Font("assets/fonts/Press_Start_2P.ttf", min(event.h//40, event.w//28)),
                        'Unicode': pg.font.Font("assets/fonts/Falling_Sky.otf", min(event.h//30, event.w//20)),
                        'Piece': pg.font.Font("assets/fonts/Press_Start_2P.ttf", int(9*min((9*self.screen_size[0]/10)/self.board_size,
                                                                                        (16*self.screen_size[1]/25)/self.board_size)/10))
                    }

                for button, func in self.buttons:
                    if button.click(event):
                        func()

            self.draw_functions[self.screen_type]()

            pg.display.flip()
            self.clock.tick(60)

            if self.screen_type == 2:
                if self.game.game_over:
                    time.sleep(2)
                    self.next_screen()
                elif self.player_types[self.game.cur_player-1]:
                    bot = self.bots[self.game.cur_player-1]
                    assert bot
                    move = bot.get_move()
                    self.game.try_move(move)
                else:
                    if 1 in pg.mouse.get_pressed():
                        x, y = pg.mouse.get_pos()
                        cell_size = min((9*self.screen_size[0]/10)/self.board_size, (16*self.screen_size[1]/25)/self.board_size)
                        padding = ((self.screen_size[0] - cell_size*self.board_size)/2, (4*self.screen_size[1]/5 - cell_size*self.board_size)/2)
                        row = int((y - padding[1])//cell_size)
                        col = int((x - padding[0])//cell_size)
                        if 0 <= row < self.board_size and 0 <= col < self.board_size:
                            self.game.try_move((row, col))
