#!/usr/bin/env python
"""
Graphical tic-tac-toe game written using pygame. Uses classes from the players and boards modules. To use, simply create
an instance of TTTGame and call its main method. Will exit when the game is over and return the winner as a string
('t', 'x' or 'o').
"""

import os
import logging
from shutil import copyfile
import webbrowser
import threading
import pygame
from boards import TTTGraphicalBoard
import ai
from players import TTTHumanPlayer, TTTAiPlayer, TTTPlayer


_here = os.path.abspath(os.path.dirname(__file__))
BACKGROUND_PATH = os.path.join(_here, os.path.join(os.path.join('..', 'data'), 'background.jpg'))
PATH_TO_AI = ai.DEFAULT_AI_PATH


def exportLog(export_to_folder):
    """
    Copies the log file created in the tttio package to the folder in export_to_folder
    :return: None
    """

    copyfile(os.path.join(_here, 'log.log'), os.path.join(export_to_folder, 'log.log'))


class TTTGame(object):
    """
    Takes a board, two players and a control panel and starts a ttt game.
    """

    def __init__(self, x_first=True, players=(), singleplayer=False,
                 screen=None, size=(620, 620), board_size=(600, 600), board_offset=(10, 10), lw=10):
        """
        Create the game
        :param x_first: If True, then x will go first, otherwise o will.
        :param players: Players to use in the game. Only one player can be passed, however it must still be inside
        a tuple
        :param singleplayer: If True (and one player was passed in the players kwarg), will make sure that
        there is one ai player and one human player, if false will make sure there are two human players. If
        no players were passed in the players arg then a human player will always be assigned to the o game piece
        and if singleplayer is true, then an ai player will be assigned to the x piece, otherwise
        if singleplayer is false then another human player will be assigned to the x piece.
        :param screen: Pygame screen object to use for the game.
        :param screen, size, board_size, board_offset, lw: options to be passed to the TTTGraphicalBoard.
        :return: None
        """

        if screen is None:
            self.screen = pygame.display.set_mode(size)
            pygame.display.set_caption("Tic Tac Ti/o")
        else:
            self.screen = screen
            size = self.screen.get_size()
            board_size = (size[0] - 20, size[1] - 20)
        self.screen.fill((255, 255, 255))

        self.clock = pygame.time.Clock()
        self.fps = 60
        self.exit = False
        self.gameOver = False
        self.turn = 'x' if x_first is True else 'o'

        self.bs = board_size
        self.bo = board_offset
        self.blw = lw
        self.size = size
        self.board = TTTGraphicalBoard(self.screen, self.bs, self.bo, self.blw)

        self.players = {'x': None, 'o': None}
        if len(players) > 0:
            for player in players[:2]:
                if not isinstance(player, TTTPlayer):
                    if issubclass(player, TTTPlayer):
                        self.players[player.gp] = player
                else:
                    # this bit of code checks to make sure the getMove() function of the TTTPlayer instance is
                    # overwritten.
                    try:
                        result = player.getMove()
                        assert result != 'myMove'  # returned by default getMove() func that needs to be overwritten
                    except TypeError:  # raised when more or less args are passed than expected
                        pass
                    except AssertionError:
                        raise AttributeError("The getMove method of the player instance with game piece {} was not "
                                             "overwritten!".format(player.gp))

                    self.players[player.gp] == player  # this is unreachable if the assertion fails
            # makes other player a human player if singleplayer is false or it is true and an ai player was given,
            # makes other player an ai player if singleplayer is true and a human player was given
            if len(players) == 1:
                gps = ['x', 'o']
                # this setup allows for gp[1] to be the opposite game piece to gp[0] (gp[0] == 'o', gp[1] == 'x', and
                # vice versa)
                for gp in [gps, gps[::-1]]:
                    if self.players[gp[0]] is None:
                        if singleplayer is True:
                            if isinstance(self.players[gp[1]], TTTAiPlayer):
                                self.players[gp[0]] = TTTHumanPlayer(gp[0])
                            else:
                                self.players[gp[0]] = TTTAiPlayer(gp[0], PATH_TO_AI)
                        else:
                            self.players[gp[0]] = TTTHumanPlayer(gp[0])
        else:
            if singleplayer is True:
                self.players['x'] = TTTAiPlayer('x', PATH_TO_AI)
            else:
                self.players['x'] = TTTHumanPlayer('x', control_set="wasd")

            self.players['o'] = TTTHumanPlayer('o', control_set="arrows")

        for gp in ['x', 'o']:
            self.players[gp].setGame(self)

    def main(self):
        """
        Start the game
        :return: None
        """

        logging.info("Starting game")
        self.board.initUI()
        winner = None

        while not self.exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True
                elif not self.gameOver:
                    currentPlayer = self.players[self.turn]
                    move = currentPlayer.getMove()
                    self.turn = 'x' if self.turn == 'o' else 'o'

                    winner = self.board.checkForWin(move)[0]
                    if winner in ['x', 'o', 't']:
                        logging.info("Game has ended with status: {}".format(winner))
                        self.gameOver = True
                        self.board.displayWinner(self.board.checkForWin(move))
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                            self.gameOver = False
                            self.board.reset()
                            self.board.initUI()
                    elif event.key in [pygame.K_ESCAPE, pygame.K_DELETE, pygame.K_BACKSPACE]:
                        self.exit = True

            pygame.display.flip()
            self.clock.tick(self.fps)

        self.exit = False
        self.gameOver = False
        self.board.reset()
        return winner
        
    
def checkMenuInstance(func):
    """
    This wrapper is used for the methods in the next classes that display menus, for it checks to make sure that the
    given menu to display is of the TTTGameMenu class. Because this function is going to be used in methods, the
    checkAndCall function needs a self argument.
    """

    def checkAndCall(self, menu):
        if isinstance(menu, TTTGameMenu):
            func(self, menu)
        else:
            raise TypeError("Given menu is of type {} and not an instance of the TTTGameMenu class".format(type(menu)))
    return checkAndCall


class TTTGameMenuItem(object):
    """
    This is an option class for the game menu and is essentially just a click-able label on the screen.
    """

    def __init__(self, name, parent, pos, next_menu=None, just_text=False):
        """
        Create the game menu
        :param name: What text to display on the screen
        :param parent: Parent menu that holds this item
        :param pos: (item number from top, total number of items)
        :param next_menu: The Next menu to display after this option is clicked on. If None, doAction will be executed
        :param just_text: If this is true, then this item will only act as text and will not do anything when clicked
        or when hovered over
        instead
        """

        self.name = name
        self.parent = parent
        self.hovered = False
        self.nextMenu = next_menu
        self.pos = pos
        self.justText = just_text  # event if this item is justText, the hovered fonts are created for compatibility

        # make sure the font is small enough for the text to fit onto the screen
        font_no_hovered = self.parent.runner.fontNoHovered
        size = self.parent.runner.fontNoHoveredSize
        padding = 10 if self.justText else 100
        while font_no_hovered.size(self.name)[0] > self.parent.screen.get_size()[0] - padding:
            size -= 1
            font_no_hovered = pygame.font.SysFont(self.parent.runner.fontName, size)

        font_hovered = self.parent.runner.fontHovered
        size = self.parent.runner.fontHoveredSize
        while font_hovered.size(self.name)[0] > self.parent.screen.get_size()[0] - 10:
            size -= 1
            font_hovered = pygame.font.SysFont(self.parent.runner.fontName, size)
            font_hovered.set_bold(True)

        # render the text
        self.textHovered = font_hovered.render(self.name, 1, self.parent.runner.fontHoveredColor)
        self.textHoveredWidth = self.textHovered.get_rect().width
        self.textHoveredHeight = self.textHovered.get_rect().height
        self.textHoveredPos = [((self.parent.screen.get_width() / 2.0) - (self.textHoveredWidth / 2.0)),
                               (self.parent.screen.get_height() / (self.pos[1] + 1) * (self.pos[0] + 1))]

        self.textNoHovered = font_no_hovered.render(self.name, 1, self.parent.runner.fontNoHoveredColor)
        self.textNoHoveredWidth = self.textNoHovered.get_rect().width
        self.textNoHoveredHeight = self.textNoHovered.get_rect().height
        self.textNoHoveredPos = [((self.parent.screen.get_width() / 2.0) - (self.textNoHoveredWidth / 2.0)),
                                 (self.parent.screen.get_height() / (self.pos[1] + 1) * (self.pos[0] + 1))]

    def __repr__(self):
        """
        :return: the name attribute
        """

        return self.name

    @checkMenuInstance
    def setNextMenu(self, menu):
        """
        Accessor method for the nextMenu attribute.
        """

        self.nextMenu = menu

    def checkHovered(self):
        """
        Determines if the mouse is hovering over this option. Will change status of self.hovered as it does so.
        """

        if not self.justText:
            if self.hovered:
                rect = pygame.Rect(self.textHoveredPos, (self.textHoveredWidth, self.textHoveredHeight))
            else:
                rect = pygame.Rect(self.textNoHoveredPos, (self.textNoHoveredWidth, self.textNoHoveredHeight))

            self.hovered = rect.collidepoint(*pygame.mouse.get_pos())
            return self.hovered
        else:
            return False

    def draw(self):
        """
        Draws itself on the screen. Will draw the text with the appropriate font based on whether it is hovered by the
        mouse or not
        """

        if not self.justText:
            if self.hovered:
                self.parent.screen.blit(self.textHovered, self.textHoveredPos)
            else:
                self.parent.screen.blit(self.textNoHovered, self.textNoHoveredPos)
        else:
            self.parent.screen.blit(self.textNoHovered, self.textNoHoveredPos)

    def _doNothing(self):
        """
        Do nothing action that can be used when the action for an item should just do nothing.
        """

        pass

    def action(self):
        """
        Function to be executed if this option is clicked on and the next menu is not defined. Should be redefined.
        """

        self._doNothing()

    def clicked(self):
        """
        Function to be called if this option is clicked on. Will check if another game menu exists and if one does, will
        display it. Otherwise it will call action (which should be overwitten by the time this method is called).
        """

        if isinstance(self.nextMenu, TTTGameMenu):
            return self.parent.display(self.nextMenu)
        else:
            return self.action()


class TTTGameMenuBG(pygame.sprite.Sprite):
    """
    Used to hold the background.jpg of a game menu as a sprite. Helps prevent lots of overlapping and scaling.
    """

    def __init__(self, image_file, (left, top), size):
        """
        Setup the background.jpg. Background image is found at image_file and will be located on the window.
        """

        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_file)
        self.size = size
        pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = left, top


class TTTGameMenu(object):
    """
    This class is used to hold information about a menu the player would see while in the start screen (by
    menu I mean a list of options, which are pieces of click-able text on the screen that when clicked, either take the
    user to a new menu with new options or start a game).
    """

    def __init__(self, name, runner, items, background_path):
        """
        Create the menu
        :param runner: Displays game menus and manages the navigation of the menu by the user
        :param name: This game menu's name
        :param items: List of strings to act as names for the menu items
        :param fonts: [Not hovered, not hovered color, hovered, hovered color]
        :param background_path: path to background.jpg image to display
        """

        self.runner = runner
        self.screen = runner.getScreen()
        self.name = name
        self.setBackground(background_path)
        self.items = [TTTGameMenuItem(items[x], self, (x, len(items))) for x in range(len(items))]
        self.itemDict = {}
        for item in self.items:
            self.itemDict[item.name] = item

    def __repr__(self):
        """
        Returns self.options
        """

        return "{} menu".format(self.name)

    def addItemActions(self, actions):
        """
        Function to be execute that will add action functions passed in the actions arg to each item item held in
        itemDict
        :param actions: Dictionary: {item_name: function}
        """

        for item_name, action_func in actions.items():
            self.itemDict[item_name].action = action_func

    def draw(self):
        """
        Draws this menu onto the screen
        """

        self.screen.fill((255, 255, 255))
        self.screen.blit(self.background.image, self.background.rect)
        for key, item in self.itemDict.items():
            item.draw()

    def setBackground(self, background_path):
        """
        Set the background.jpg to the image located at background_path
        """

        self.background = TTTGameMenuBG(background_path, (0, 0), self.screen.get_size())

    @checkMenuInstance
    def display(self, menu):
        """
        Calls the runner to display menu, if menu is an instance of a TTTGameMenu class
        :param menu: Instance of TTTGameMenu class
        """

        self.runner.setCurrentMenu(menu)


class TTTGameStartMenu(object):
    """
    Class representing the start menu for the tic tac toe game. Will start the appropriate game based on the items the
    user clicks on.
    """

    def __init__(self, screen=None, menus=None, menuProgression=None, menuActions=None, textItems=None, fonts=None,
                 background=None):
        """
        Create teh start menu.
        :param screen: Screen to draw on.
        :param menus: Dictionary containing {'MenuName': ['Menu item name 1', 'menu item name 2', etc.]}.
        Should contain one menu named "Start", which is the first menu displayed.
        :param menuProgression:  Dictionary containing: {'menu name': 'parent menu name'} for all menus that will
        be accessible. Should contain one menu named "Start", which is the first menu displayed.
        :param menuActions: Dictionary containing: {'menu name': {'item name': item's action function}}. Will set
        the appropriate item's action function the the one found in the dict.
        :param textItems: Dictionary containing: {'menu name': {'item name': True or False}}. If the item name's value
        is True, its justText attribute will be set to True
        :param fonts: Tuple containing: (pygame font object to use when text is not being hovered over, color for
        previous (not hovered) font, pygame font object to use when text is being hovered over, color for previous
        (hovered) font)
        :param background: Path to background.jpg image for the menus
        """

        logging.info("Initiating start menu")
        self.screen = screen if screen is not None else self.createScreen()
        self.exit = False
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.showMouse = True
        self.currentItem = 0  # used for when user is controlling with keyboard
        if fonts is None:
            self.fontName = "Courier New"
            self.fontNoHoveredSize = 30
            self.fontHoveredSize = 32
            self.fontNoHovered = pygame.font.SysFont(self.fontName, self.fontNoHoveredSize)
            self.fontNoHoveredColor = (150, 150, 150)
            self.fontHovered = pygame.font.SysFont(self.fontName, self.fontHoveredSize)
            self.fontHovered.set_bold(True)
            self.fontHoveredColor = (200, 200, 200)
            self.fonts = (self.fontNoHovered, self.fontNoHoveredColor, self.fontHovered, self.fontHoveredColor)
        else:
            self.fontNoHovered, self.fontNoHoveredColor, self.fontHovered, self.fontHoveredColor = fonts
            self.fonts = fonts

        self.background = background if background is not None else BACKGROUND_PATH
        self.currentMenu = None

        if menus is None and menuProgression is None and menuActions is None and textItems is None:
            copyright_text = "Copyright (C) Ryan Drew 2016"
            source_text = "Source code is on Github"
            license_text = "Distributed under TAC's of the MIT license"
            license_text2 = "(a copy is included in the source code)"
            self.menus = {'StartMen': ['Singleplayer', 'Multiplayer', 'About', 'Quit'],
                          'Singleplayer': ['Player goes first', 'A.I. goes first', 'Back'],
                          'Multiplayer': ['Online Local (Coming Soon!)', 'Same keyboard', 'Back'],
                          'About': [copyright_text, license_text, license_text2, source_text, 'Back']
                          }

            # the menu name in the key is accessible from the menus in the value list
            self.menuProgression = {'StartMen': ['Singleplayer', 'Multiplayer', 'About'],
                                    'Singleplayer': ['StartMen'],
                                    'Multiplayer': ['StartMen'],
                                    'About': ['StartMen']}

            self.textItems = {
                'About': {
                    copyright_text: True,
                    license_text: True,
                    license_text2: True
                }
            }

            github_link = 'https://github.com/DevelopForLizardz/TicTacTio.git'
            self.menuActions = {
                'StartMen': {
                    'Quit': self.exitLoop
                },
                'Singleplayer': {
                    'Player goes first': TTTGame(x_first=False, screen=self.screen, singleplayer=True).main,
                    'A.I. goes first': TTTGame(x_first=True, screen=self.screen, singleplayer=True).main
                },
                'Multiplayer': {
                    'Same keyboard': TTTGame(screen=self.screen).main
                },
                'About': {
                    source_text: threading.Thread(target=webbrowser.open, name="open_source_url_thread",
                                                  args=[github_link], kwargs={'new': 2}).start
                }
            }
        for menuName, items in self.menus.items():
            self.menus[menuName] = TTTGameMenu(menuName, self, items, self.background)

        for menuName, menu in self.menus.items():  # for each menu in self.menus
            # for each menu listed in self.menuProgression under the menuName key that will has an item that when
            # clicked will display menu
            for accessFromMenu in self.menuProgression[menuName]:
                try:  # try to access the 'Back' item and set its next menu to menu
                    self.menus[accessFromMenu].itemDict['Back'].setNextMenu(menu)
                except KeyError:  # if the 'Back' item is not present
                    try:  # try to access an item that has the name of menuName and set its next menu to menu
                        self.menus[accessFromMenu].itemDict[menuName].setNextMenu(menu)
                    except KeyError:  # if there is no item by the name menuItem, then log a warning message
                        logging.warning("Unable to bind the {} menu to the {} menu automatically. "
                                        "There is no menu item named 'back' or {} in the {} menu".format(
                                            accessFromMenu, menuName, accessFromMenu))

        for menu, itemDicts in self.menuActions.items():
            for itemName, itemAction in itemDicts.items():
                self.menus[menu].itemDict[itemName].action = itemAction
        for menuName, itemBools in self.textItems.items():
            for itemName, justText in itemBools.items():
                self.menus[menuName].itemDict[itemName].justText = justText

        self.setCurrentMenu(self.menus['StartMen'])

    @staticmethod
    def calculateWindowSize():
        """
        Calculates the size of the window based on the dimensions of the screen (window is set to 4/5ths of screen
        rounded to the least int)
        :return: (w, h)
        """

        return (int(pygame.display.Info().current_h * (4 / 5.0)), ) * 2

    def createScreen(self):
        """
        Creates the screen that will be used to draw on. Sets the size of the surface to a square where each side
        is 4/5ths of the current screens height.
        :return: The screen object
        """

        size = self.calculateWindowSize()
        logging.debug("Size was calculated to: {}".format(size))
        display = pygame.display.set_mode(size)
        pygame.display.set_caption("Tic Tac Ti/o")
        return display

    def exitLoop(self):
        """
        sets self.exit to True
        """

        self.exit = True

    def _passable(self):
        """
        Function that doesn't do anything. For use when an error occurs while creating the action functions for the
        options in the game menu
        """

        pass

    def returnToStart(self):
        """
        sets the current menu to the start menu
        """

        self.setCurrentMenu(self.menus['Start'])

    def updateMouseVisibility(self):
        """
        Shows or hide the mouse based on the showMouse attribute
        """

        if self.showMouse:
            pygame.mouse.set_visible(True)
        else:
            pygame.mouse.set_visible(False)

    def getScreen(self):
        """
        :return: The screen being stored in self.screen
        """

        return self.screen

    @checkMenuInstance
    def setCurrentMenu(self, menu):
        """
        Sets the currently displayed menu to menu and draws it to the screen
        :param menu: Instance of the TTTGameMenu class
        """

        if isinstance(menu, TTTGameMenu):
            self.currentMenu = menu
            self.currentMenu.draw()

    def start(self):
        """
        Starts up the game menu, allowing the user to navigate through it.
        """

        logging.info("Starting main loop for start menu")
        self.currentMenu.draw()

        while not self.exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True
                elif event.type == pygame.KEYDOWN:
                    if event.key not in [pygame.K_RETURN, pygame.K_SPACE]:
                        if event.key in [pygame.K_DOWN, pygame.K_s]:
                            self.showMouse = False
                            self.updateMouseVisibility()
                            if self.currentItem < len(self.currentMenu.items) - 1:
                                self.currentMenu.items[self.currentItem].hovered = False
                                self.currentItem += 1
                                self.currentMenu.items[self.currentItem].hovered = True
                        elif event.key in [pygame.K_UP, pygame.K_w]:
                            self.showMouse = False
                            self.updateMouseVisibility()
                            if self.currentItem > 0:
                                self.currentMenu.items[self.currentItem].hovered = False
                                self.currentItem -= 1
                                self.currentMenu.items[self.currentItem].hovered = True
                    else:
                        self.currentMenu.items[self.currentItem].hovered = False
                        self.showMouse = True
                        self.updateMouseVisibility()
                        self.currentMenu.items[self.currentItem].clicked()
                        self.currentItem = 0
                elif self.showMouse:
                    for item in self.currentMenu.items:
                        # hover state will always be checked
                        if item.checkHovered() and event.type == pygame.MOUSEBUTTONDOWN:
                            item.clicked()
                            break

                self.currentMenu.draw()
                pygame.display.flip()
                self.clock.tick(self.fps)

        logging.info("Ending main loop of start menu")


def main():
    pygame.init()
    TTTGameStartMenu().start()

if __name__ == '__main__':
    main()
