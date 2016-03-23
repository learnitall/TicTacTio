"""
Simple Tic Tac Toe game for machine learning purposes

1 | 2 | 3
4 | 5 | 6
7 | 8 | 9

Written by Ryan Drew, 2016

TODO:
(1) Need to add logging support for more classes besides TTTLanHumanPlayer
(2) Need to post onto github
(3) Need to have a 'play again' feature for TTTLanHumanPlayer
(4) Need function to draw a line through a three in a row
(5) Should have some sort of GUI to create a (network) game
"""

import pygame
import datetime
import logging
import socket

logging.basicConfig(format='%(asctime)s:%(module)s:%(message)s', level=logging.DEBUG)
pygame.init()


class TTTBoard(object):
    """
    Represents a tic-tac-toe board. Has methods for checking if a player has won and placing moves.
    """

    def __init__(self):
        """
        Create the board ([ROW:[col], ROW:[col], ROW:[col]])
        :return: None
        """

        self.sBoard = self.genBoard()

    def genBoard(self):
        """
        Generates a blank board and returns it
        """

        return [[" " for a in range(3)] for b in range(3)]

    def copyBoard(self):
        """
        Returns a copy of self.sBoard
        """

        return [[a for a in b] for b in self.sBoard]

    def printBoard(self):
        """
        Prints out the string representation of the board
        :return: None
        """

        for x in self.sBoard:
            print x

    def getEmptySpace(self):
        """
        Returns an empty space found on the board. Returns None if there is none
        """

        for a in self.sBoard:
            for b in a:
                if b == ' ':
                    y = self.sBoard.index(a)
                    return self.sBoard[y].index(b) + 1, y + 1

        return None

    def getPiece(self, pos):
        """
        Returns the piece found in the given position
        """

        return self.sBoard[pos[1] - 1][pos[0] - 1]

    def translateNumToPos(self, num):
        """
        Converts a num representation of a move on the board (1-9) to a pos representation of a move on a board
        (col, row) and returns it
        """

        if num > 6:
            return num - 6, 3
        elif num > 3:
            return num - 3, 2
        else:
            return num, 1

    def getWinningMoves(self, sBoard=None):
        """
        Returns the winning moves on the tic-tac-toe board as (col, row)
        :param sBoard: specify board to check
        """

        if sBoard is None:
            sBoard = self.sBoard

        winningMoves = {'x': [], 'o': []}
        testBoard = self.copyBoard()
        for row in range(len(sBoard)):
            for col in range(len(sBoard[row])):
                if sBoard[row][col] == " ":
                    for piece in ['x', 'o']:
                        testBoard[row][col] = piece
                        result = self.checkForWin(testBoard)
                        if result is not None and result != 't':
                            winningMoves[piece].append((col + 1, row + 1))

                    testBoard[row][col] = " "
        return winningMoves

    def isValidMove(self, pos):
        """
        Returns True if the move at pos is valid (aka if the space at pos is empty) and False if it isn't
        """

        return self.getPiece(pos) == " "

    def setPiece(self, pos, marker):
        """
        Sets the marker for a certain position in self.sBoard
        :return: None
        """

        self.sBoard[pos[1] - 1][pos[0] - 1] = marker

    def checkForWin(self, sBoard=None):
        """
        Checks to see if there is a three in a row somewhere
        :param sBoard: specify board to check
        :return: 'x' if x has won, 'o' if o has won, 't', if there is a tie, if else then None
        """

        if sBoard is None:
            sBoard = self.sBoard

        # check for a horizontal win
        for a in sBoard:
            if ''.join(a) == 'xxx':
                return 'x'
            elif ''.join(a) == 'ooo':
                return 'o'

        # check for a vertical win
        for c in range(3):
            s = ""
            for b in range(3):
                s += sBoard[b][c]
            if s == 'xxx':
                return 'x'
            elif s == 'ooo':
                return 'o'

        s = ""
        for i in range(3):
            s += sBoard[i][i]
        if s == "xxx":
            return 'x'
        elif s == 'ooo':
            return 'o'

        s = ""
        for i in range(3):
            s += sBoard[i][2-i]
        if s == 'xxx':
            return 'x'
        elif s == 'ooo':
            return 'o'

        for d in sBoard:
            for e in d:
                if e == ' ':
                    return None

        return 't'


class TTTGraphicalBoard(TTTBoard):
    """
    Represents a tic-tac-toe board. Draws x's, o's and cursors
    """

    def __init__(self, screen, size=(600, 600), offset=(10, 10), line_width=10):
        """
        Create the board's graphic objects
        :param screen: screen to draw onto
        :param size: size to make the board (tuple)
        :param offset: amount to add to x's and y's for padding purposes (tuple)
        :param line_width: width of grid lines
        :return: None
        """

        super(TTTGraphicalBoard, self).__init__()

        self.screen = screen
        self.size = size
        self.lw = line_width
        self.lColor = (0, 0, 0)
        self.offset = offset
        self.background = pygame.Rect(self.offset[0], self.offset[1], self.size[0], self.size[1])
        self.backCol = (230, 230, 230)
        self.sqSize = ((self.size[0] - (self.offset[0] * 2 + self.lw * 2)) / 3,
                       (self.size[1] - (self.offset[1] * 2 + self.lw * 2)) / 3)
        self.gridPos = (self.offset[0] * 2, self.offset[1] * 2)
        self.gridSize = (self.size[0] - self.offset[0] * 2, self.size[1] - self.offset[1] * 2)
        self.grid = [pygame.Rect(self.gridPos[0] + self.sqSize[0], self.gridPos[1], self.lw, self.gridSize[1]),
                     pygame.Rect(self.gridPos[0], self.gridPos[1] + self.sqSize[1], self.gridSize[0], self.lw)]
        self.grid.append(self.grid[0].move(self.sqSize[0] + self.lw, 0))
        self.grid.append(self.grid[1].move(0, self.sqSize[1] + self.lw))
        self.cw = self.lw / 2
        self.cursor = pygame.Rect(self.gridPos[0], self.gridPos[1],
                                  self.gridPos[0] + self.sqSize[0] - self.offset[0] - self.lw - self.cw * 2,
                                  self.gridPos[1] + self.sqSize[1] - self.offset[1] - self.lw - self.cw * 2)
        self.cursorPos = [1, 1]
        self.cursorShow = False
        self.curCol = (150, 150, 150)

        self.xCol = (0, 0, 255)
        self.oCol = (255, 0, 0)

        self.updateCursor()

    def initUI(self):
        """
        Draws the grid onto the given screen
        :return:
        """

        pygame.draw.rect(self.screen, self.backCol, self.background)
        for x in self.grid:
            pygame.draw.rect(self.screen, self.lColor, x)

        pygame.draw.rect(self.screen, self.curCol, self.cursor, self.cw)

    def drawX(self, pos, color=None):
        """
        Draws the o piece in the given position
        :param pos: (col, row)
        :param color: Custom color can be passed, default is blue
        :return: None
        """

        if color is None:
            color = self.xCol

        x1 = self.gridPos[0] + ((pos[0] - 1) * (self.sqSize[0] + self.lw)) + self.offset[0]
        y1 = self.gridPos[1] + ((pos[1] - 1) * (self.sqSize[1] + self.lw)) + self.offset[1]
        x2 = self.sqSize[0] + x1 - self.offset[0] - self.lw
        y2 = self.sqSize[1] + y1 - self.offset[1] - self.lw

        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), self.lw)
        pygame.draw.line(self.screen, color, (x1, y2), (x2, y1), self.lw)

        self.setPiece(pos, "x")

    def drawO(self, pos, color=None):
        """
        Draws the X piece in the given position
        :param pos: (col, row)
        :param color: Custom color can be passed. default is red
        :return: None
        """

        if color is None:
            color = self.oCol

        x = self.gridPos[0] + ((pos[0] - 1) * (self.sqSize[0] + self.lw)) + self.sqSize[0] / 2
        y = self.gridPos[1] + ((pos[1] - 1) * (self.sqSize[1] + self.lw)) + self.sqSize[1] / 2
        radius = (self.sqSize[0] - self.lw * 2) / 2
        pygame.draw.circle(self.screen, color, (x, y), radius, self.lw)

        self.setPiece(pos, "o")

    def updateCursor(self, color=None):
        """
        Redraws the cursor in case it has been moved
        :param color: Specify custom color to use
        :return: None
        """

        if color is None:
            color = self.curCol

        pygame.draw.rect(self.screen, self.backCol, self.cursor, self.cw)
        self.cursor.topleft = ((self.cursorPos[0] - 1) * (self.sqSize[0] + self.lw) + self.gridPos[0] + self.cw,
                               (self.cursorPos[1] - 1) * (self.sqSize[1] + self.lw) + self.gridPos[1] + self.cw)
        if self.cursorShow is True:
            pygame.draw.rect(self.screen, color, self.cursor, self.cw)

    def mvCurRight(self):
        """
        Moves the cursor to the right one square.
        :return: None
        """

        if self.cursorPos[0] < 3:
            self.cursorPos = (self.cursorPos[0] + 1, self.cursorPos[1])

    def mvCurLeft(self):
        """
        Moves the cursor to the left one square.
        :return: None
        """

        if self.cursorPos[0] > 1:
            self.cursorPos = (self.cursorPos[0] - 1, self.cursorPos[1])

    def mvCurUp(self):
        """
        Moves the cursor to up one square.
        :return: None
        """

        if self.cursorPos[1] > 1:
            self.cursorPos = (self.cursorPos[0], self.cursorPos[1] - 1)

    def mvCurDown(self):
        """
        Moves the cursor down one square.
        :return: None
        """

        if self.cursorPos[1] < 3:
            self.cursorPos = (self.cursorPos[0], self.cursorPos[1] + 1)

    def callable(self, *args, **kwargs):
        """
        Empty function to be called when the enter and shift keys are pressed.
        """

        pass


class TTTPlayer(object):
    """
    Base ttt player.
    """

    def __init__(self, game_piece, game):
        """
        Create the player
        :param game_piece: 'x' or 'o'
        :param game: the TTTGame class, that holds the game board and other important variables needed
        :return: None
        """

        if game_piece != 'x' and game_piece != 'o':
            raise TypeError("Game piece is not 'x' or 'o'")
        else:
            self.gp = game_piece
        self.game = game

        if self.gp == 'x':
            self.curCol = self.game.board.xCol
        elif self.gp == 'o':
            self.curCol = self.game.board.oCol

    def playPiece(self, pos, draw=True, color=None):
        """
        Tells the board to put a piece down in pos
        :param pos: (col, row)
        :param draw: is this is false, then just the string representation of the board is updated
        :param color: custom color to use for the piece.
        :return: None
        """

        if self.gp == 'x':
            if draw:
                self.game.board.drawX(pos, color)
            else:
                self.game.board.setPiece(pos, 'x')
        elif self.gp == 'o':
            if draw:
                self.game.board.drawO(pos, color)
            else:
                self.game.board.setPiece(pos, 'o')

    def getMove(self, timeout=60):
        """
        'Abstract' class for the getMove function. Should be overwritten.
        :param timeout: how many seconds the player has to make a move.
        :return: (col, row) of player's chosen move
        """

        return "This function has not been overwritten!"


class TTTHumanPlayer(TTTPlayer):
    """
    Human TTT Player
    """

    def __init__(self, game_piece, game, control_set="wasd"):
        """
        Create the player
        :param game_piece: 'x' or 'o'
        :param game: the TTTGame class, that holds the game board and other important variables needed
        :param control_set: can be 'wasd' or 'arrows'
        :return: None
        """

        super(TTTHumanPlayer, self).__init__(game_piece, game)

        self.controls = []
        self.values = [self.game.board.callable, self.game.board.mvCurUp, self.game.board.mvCurDown,
                       self.game.board.mvCurLeft, self.game.board.mvCurRight]
        if control_set == "arrows":
            self.keys = [pygame.K_RETURN, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
        else:
            self.keys = [pygame.K_SPACE, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]

        for i in range(len(self.keys)):
            self.controls.append([self.keys[i], self.values[i]])

        self.game = game

    def getMove(self, timeout=60):
        """
        Gets a move from the player and returns the player's chosen position.
        :param timeout: how many seconds the player has to make a move
        :return: (col, row) of player's chosen move
        """

        # need to track position, add a conditional in while loop to check for enter key
        self.game.board.cursorPos = self.game.board.getEmptySpace()
        self.game.board.cursorShow = True
        self.game.board.updateCursor(color=self.curCol)

        start = datetime.datetime.now()
        # this will run for sixty seconds, when the key found at self.controls[0][0] is not pressed and will only exit
        # when the marker found at the cursor position is empty and when self.game.exit is True
        while (datetime.datetime.now() - start).seconds < timeout and not \
                (pygame.key.get_pressed()[self.controls[0][0]] and self.game.board.getPiece(
                    self.game.board.cursorPos) == " ") and self.game.exit is False:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.exit = True
                elif event.type == pygame.KEYDOWN:
                    pressed = pygame.key.get_pressed()
                    for button, action in self.controls:
                        if pressed[button]:
                            action()
                            self.game.board.updateCursor(self.curCol)

            pygame.display.flip()
            self.game.clock.tick(self.game.fps)

        else:
            move = self.game.board.cursorPos
            self.playPiece(move, draw=False)
            self.game.board.cursorShow = False
            self.game.board.cursorPos = self.game.board.getEmptySpace()
            if self.game.board.cursorPos is not None:
                self.game.board.updateCursor(color=self.curCol)
                self.playPiece(move)
            else:
                self.playPiece(move)
            pygame.display.flip()
            self.game.clock.tick(self.game.fps)


class TTTGame(object):
    """
    Takes a board, two players and a control panel and starts a ttt game.
    """

    def __init__(self, players=None, size=(620, 620), board_size=(600, 600), board_offset=(10, 10), lw=10):
        """
        Create the game
        :param players: List of two players to use for the game, should be a child of the TTTPlayer class.
        :return: None
        """

        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Tic Tac Toe")
        self.screen.fill((255, 255, 255))

        self.clock = pygame.time.Clock()
        self.fps = 60
        self.exit = False

        self.bs = board_size
        self.bo = board_offset
        self.blw = lw
        self.board = TTTGraphicalBoard(self.screen, self.bs, self.bo, self.blw)

        if players is None or \
                (len(players) < 2 and not (issubclass(players[0], TTTPlayer) and issubclass(players[1], TTTPlayer))):
            self.player1 = TTTHumanPlayer('x', self)
            self.player2 = TTTHumanPlayer('o', self, control_set="arrows")
        else:
            self.createPlayers()

    def createPlayers(self, p1_cons="arrows", p2_cons="wasd"):
        """
        Creates two human players. Can be called again to re-create players after initial in __init__
        :param p1_cons: controls to use for player 1 ("arrows" or "wasd")
        :param p2_cons: controls to use for player2 ("arrows" or "wasd")
        :return: None
        """

        self.player1 = TTTHumanPlayer('x', self, control_set=p1_cons)
        self.player2 = TTTHumanPlayer('o', self, control_set=p2_cons)

    def main(self):
        """
        Start the game
        :return: None
        """

        self.board.initUI()
        turn = 1
        winner = None

        while not self.exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True
                else:
                    if self.board.checkForWin() is None:
                        if turn == 1:
                            self.player1.getMove()
                            turn = 2
                        elif turn == 2:
                            self.player2.getMove()
                            turn = 1
                    elif self.board.checkForWin() == 'x':
                        winner = "x"
                        self.exit = True
                    elif self.board.checkForWin() == 'o':
                        winner = 'o'
                        self.exit = True
                    elif self.board.checkForWin() == 't':
                        winner = 't'
                        self.exit = True

            print self.board.getWinningMoves()
            pygame.display.flip()
            self.clock.tick(self.fps)

        return winner


class TTTLanHumanPlayer(TTTHumanPlayer):
    """
    LAN human player for playing online with other people. Works by creating a TCP stream connection in a socket on port
    54541. During the player's turn, this class will send cursor and move information to the other instance and
    vice-versa.
    """

    def __init__(self, game_piece, turn, remote_plr_addr, control_set="wasd", port=54541):
        """
        Create the network player.
        :param game_piece: 'x' or 'o'
        :param turn: True if this instance goes first, false if the remote player goes first
        :param remote_plr_addr: the remote player's address
        :param control_set: 'wasd' or 'arrows'
        :param port: default is 54541, but a custom one can be used
        :return: None
        """

        self.game = TTTGame()
        self.game.player1 = None
        self.game.player2 = None
        super(TTTLanHumanPlayer, self).__init__(game_piece, self.game, control_set=control_set)
        self.curCol = self.game.board.curCol
        self.turn = turn
        self.myPiece = game_piece
        if self.myPiece == 'x':
            self.oppPiece = 'o'
        else:
            self.oppPiece = 'x'

        self.values = [self.game.board.callable, self.netMvCurUp, self.netMvCurDown, self.netMvCurLeft,
                       self.netMvCurRight]
        for i in range(len(self.controls))[1:]:
            self.controls[i][1] = self.values[i]

        self.COMMLENGTH = 2
        self.TURNOVER = "oo"
        self.GAMEOVER = "1"  # result of game (t, x, o)
        self.MVCURRIGHT = "02"
        self.MVCURLEFT = "03"
        self.MVCURUP = "04"
        self.MVCURDOWN = "05"
        self.UPDATECUR = "07"
        self.PLAYMOVE = "8"  # + position of move
        self.EXIT = "09"
        self.commandKey = {}

        self.port = port
        self.myAddress = socket.gethostname()
        self.socket = None
        self.genSock()
        self.success = "Success!"
        self.remotePlayer = (remote_plr_addr, self.port)
        self.remotePlayerConn = None  # this will be used to send the remote player commands
        # self.connectToRemotePlayer()

    def main(self):
        """
        Begin the game.
        :return: None
        """

        logging.info("Starting game")
        self.game.board.initUI()
        self.game.board.cursorPos = self.game.board.getEmptySpace()
        self.game.board.cursorShow = True
        self.game.board.updateCursor(self.curCol)
        pygame.display.flip()
        self.game.clock.tick(self.game.fps)

        win = None
        while self.game.exit is False:
            if self.turn is True:
                self.gp = self.myPiece
                logging.info("It is my turn. Sending commands.")
                self.getMove()
            else:
                self.gp = self.oppPiece
                logging.info("It is the remote player's turn. Listening for commands.")
                self.listenForCommands()

        return win

    def netMvCurUp(self):
        """
        Moves the cursor up both on the remote player and locally.
        :return: None
        """

        self.sendCommand(self.MVCURUP)
        self.game.board.mvCurUp()

    def netMvCurDown(self):
        """
        Moves the cursor down on both the remote player and locally.
        :return: None
        """

        self.sendCommand(self.MVCURDOWN)
        self.game.board.mvCurDown()

    def netMvCurLeft(self):
        """
        Moves the cursor left on both the remote player and locally.
        :return: None
        """

        self.sendCommand(self.MVCURLEFT)
        self.game.board.mvCurLeft()

    def netMvCurRight(self):
        """
        Moves the cursor right on both the remote player and locally.
        :return: None
        """

        self.sendCommand(self.MVCURRIGHT)
        self.game.board.mvCurRight()

    def executeCommand(self, command):
        """
        Interprets the command sent from a remote player and executes the corresponding function.
        :param command: command to interpret
        :return: None
        """

        if command == self.MVCURUP:
            self.game.board.mvCurUp()
            self.game.board.updateCursor()

        elif command == self.MVCURDOWN:
            self.game.board.mvCurDown()
            self.game.board.updateCursor()

        elif command == self.MVCURRIGHT:
            self.game.board.mvCurRight()
            self.game.board.updateCursor()

        elif command == self.MVCURLEFT:
            self.game.board.mvCurLeft()
            self.game.board.updateCursor()

        elif command == self.UPDATECUR:
            self.game.board.updateCursor()

        elif command[0] == self.PLAYMOVE:
            move = self.intToCoord(command[1])
            self.playPiece(move, draw=False)
            self.game.board.cursorShow = False
            self.game.board.cursorPos = self.game.board.getEmptySpace()
            if self.game.board.cursorPos is not None:
                self.game.board.updateCursor(color=self.curCol)
                self.playPiece(move)
            else:
                self.playPiece(move)

        elif command == self.EXIT:
            self.game.exit = True

        elif command[0] == self.GAMEOVER:
            logging.info("The game has been reported over. The winner is {}".format(self.GAMEOVER[1]))
            self.game.exit = True
            self.disconnectRemotePlayer()

        elif command == self.TURNOVER:
            self.turn = True

        pygame.display.flip()
        self.game.clock.tick(self.game.fps)

    def connectToRemotePlayer(self):
        """
        Creates a connection with the remote player. How this is done is based on whether this player goes first or not.
        If this player goes first, it will try to initiate a connection with the other player who is going to act as
        a server. If the other player goes first, then this player will create a server and wait for a connection.
        :return: None
        """

        try:
            if self.turn is True:
                logging.info("It is this player's turn, therefore a connection with the other player will be "
                             "sought out.")
                self._connectRemotePlayer()
                self.remotePlayerConn = self.socket
            else:
                logging.info("It is the other player's turn, therefore a server will be set up to wait for "
                             "his/her connection.")
                self._listenForRemotePlayer()  # this will set self.remotePlayerConn automatically
        except Exception, e:
            logging.error("An error occurred while connecting to remote player: '{}'. Turn: '{}'".format(e, self.turn))

    def genSock(self):
        """
        Creates a new socket object sets it to self.socket
        """

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            pass
        except Exception, e:
            logging.error("Failure to bind socket to address '{}' on port {}: {}".format(self.myAddress, self.port, e),
                          exc_info=True)

    def listenForCommands(self):
        """
        Creates a server that listens for the other player to send commands.
        :return: None
        """

        logging.info("Starting to listen for commands")
        self.game.board.cursorPos = self.game.board.getEmptySpace()
        self.game.board.cursorShow = True
        self.game.board.updateCursor(color=self.curCol)
        while True:
            data = self.remotePlayerConn.recv(self.COMMLENGTH)
            logging.info("Received {}".format(data))

            if data:
                self.executeCommand(data)
                if data == self.TURNOVER:
                    break

    def _listenForRemotePlayer(self):
        """
        Listens for a remote player connection and then sets self.remotePlayerConn to the returned connection
        object
        :return: None
        """

        logging.info("Listening for player now")

        self.socket.bind((self.myAddress, self.port))
        self.socket.listen(1)
        while True:
            logging.info("Waiting for a connection from the remote player")
            connection, client_address = self.socket.accept()

            logging.info("Connection from: {}. Sending success message".format(client_address))
            connection.sendall(self.success)

            logging.info("Waiting 60 seconds for success message in return.")
            amount_received = 0
            amount_expected = len(self.success)
            response_message = ""
            start = datetime.datetime.now()
            while amount_received < amount_expected and (datetime.datetime.now() - start).seconds <= 60:
                data = connection.recv(len(self.success))
                amount_received += len(data)
                response_message += data

            if response_message == self.success:
                logging.info("Received success message from other player. Connection successful.")
                self.remotePlayerConn = connection
                return self.success
            else:
                raise Exception("Did not receive a success message in sixty seconds, instead got: '{}'".format(
                                response_message))
            # NOTE, the return and raise statements will break the while loop

    def _connectRemotePlayer(self):
        """
        Creates a connection to the remote player to send commands. Tries to connect for sixty seconds every three
        seconds
        :return: None
        """

        logging.info("Creating connection with remote player.")
        self.socket.connect(self.remotePlayer)

        logging.info("Waiting 60 seconds for a response")
        start = datetime.datetime.now()
        amount_received = 0
        amount_expected = len(self.success)
        response_message = ""
        while amount_received < amount_expected and (datetime.datetime.now() - start).seconds <= 60:
            data = self.socket.recv(len(self.success))
            amount_received += len(data)
            response_message += data

        if response_message == self.success:
            logging.info("Received '{}' in response to request for connection, sending "
                         "success message back".format(response_message))
            self.socket.sendall(self.success)
            return self.success
        else:
            raise Exception("Did not receive a success message in sixty seconds, instead got: '{}'".format(
                response_message))

    def disconnectRemotePlayer(self):
        """
        Closes the connection to the remote player that was used to send commands.
        :return: None
        """

        logging.info("Closing command connection with remote player")
        try:
            self.socket.close()
            self.socket.shutdown()
        except Exception, e:
            logging.warning("Failure to shut down socket: '{}'".format(e), exc_info=True)

    def sendCommand(self, command):
        """
        Creates a client that sends commands to the other player.
        :return: None
        """

        try:
            logging.info("Sending command {}".format(command))
            self.remotePlayerConn.sendall(command)
        except Exception, e:
            logging.warning("Failure to send command '{}': {}".format(command, e), exc_info=True)

    @staticmethod
    def coordToInt(coordinates):
        """
        Converts the tuple of coordinates of the game board to their integer representation
        :param coordinates: tuple of coordinates (col, row)
        :return: int value representing position on board
        """

        return coordinates[0] + (coordinates[1] - 1) * 3

    @staticmethod
    def intToCoord(intCoord):
        """
        Converts the int representation of coordinates to the tuple representation
        :param int: int coordinate to convert
        :return: tuple coordinate
        """

        intCoord = int(intCoord)

        if intCoord > 6:
            return intCoord - 6, 3
        elif intCoord > 3:
            return intCoord - 3, 2
        else:
            return intCoord, 1

    def getMove(self, timeout=60):
        """
        Gets a move from this player and sends all move information (such as cursor location) to the remote player.
        :param timeout: Max time to get a move.
        :return: None
        """

        try:
            self.game.board.cursorPos = self.game.board.getEmptySpace()
            self.game.board.cursorShow = True
            self.game.board.updateCursor(color=self.curCol)

            start = datetime.datetime.now()
            done = False
            while (datetime.datetime.now() - start).seconds < timeout and not (done and self.game.board.getPiece(
                    self.game.board.cursorPos) == " ") and self.game.exit is False:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.game.exit = True
                        self.sendCommand(self.EXIT)
                    elif event.type == pygame.KEYDOWN:
                        pressed = pygame.key.get_pressed()
                        if pressed[self.controls[0][0]]:
                            done = True
                        else:
                            for button, action in self.controls:
                                if pressed[button]:
                                    action()
                                    self.game.board.updateCursor(self.curCol)

                pygame.display.flip()
                self.game.clock.tick(self.game.fps)

            else:
                move = self.game.board.cursorPos
                self.sendCommand(self.PLAYMOVE + str(self.coordToInt(move)))
                self.playPiece(move, draw=False)
                self.game.board.cursorShow = False
                self.game.board.cursorPos = self.game.board.getEmptySpace()
                if self.game.board.cursorPos is not None:
                    self.game.board.updateCursor(color=self.curCol)
                    self.playPiece(move)
                else:
                    self.playPiece(move)
                pygame.display.flip()
                self.game.clock.tick(self.game.fps)
        finally:
            logging.info("Move received and sent to remote player. Checking for a win.")
            win = self.game.board.checkForWin()
            if win is not None:
                logging.info("Game is over. Result: {}. Sending game over message to other player".format(win))
                self.sendCommand(self.GAMEOVER + win)
                logging.info("Message sent, closing connection and exiting")
                self.disconnectRemotePlayer()
                self.game.exit = True
            else:
                logging.info("The game is not over yet. Ending turn now.")
                self.sendCommand(self.TURNOVER)
                self.turn = False


def main():
    game = TTTGame()
    game.main()

if __name__ == '__main__':
    main()
