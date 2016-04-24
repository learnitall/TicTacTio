#!/usr/bin/env python
"""
Module containing all the player classes for the TicTacToe game. These should not be define directley and instead
only defined by the game classes
"""

import datetime
import logging
import socket
import pygame
import ai


class TTTPlayer(object):
    """
    Base ttt player. All subclasses must have the game_piece as the first argument, in
    order to preserve compatibility with the way that the TTTGame class is set up.
    """

    def __init__(self, game_piece):
        """
        Create the player
        :param game_piece: 'x' or 'o'
        :return: None
        """

        if game_piece != 'x' and game_piece != 'o':
            raise ValueError("Invalid game piece: {}. Game piece should be either 'x' or 'o'".format(game_piece))
        else:
            self.gp = game_piece

        self.game = None
        self.curCol = None

    def setCursorCol(self):
        """
        (Re)sets the cursor color to the board's color for this classes game piece
        :return: The color the cursor was set to
        """

        if self.gp == 'x':
            self.curCol = self.game.board.xCol
        elif self.gp == 'o':
            self.curCol = self.game.board.oCol

        return self.curCol

    def setGame(self, game):
        """
        Sets self.game to the given one
        """

        self.game = game
        self.setCursorCol()

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
        'Abstract' getMove function. Should be overwritten.
        :param timeout: how many seconds the player has to make a move.
        :return: (col, row) of player's chosen move
        """

        return "mymove"


class TTTHumanPlayer(TTTPlayer):
    """
    Human TTT Player
    """

    def __init__(self, game_piece, control_set="wasd"):
        """
        Create the player
        :param game_piece: 'x' or 'o'
        :param control_set: can be 'wasd' or 'arrows'
        :return: None
        """

        super(TTTHumanPlayer, self).__init__(game_piece)
        self.control_set = control_set
        self.controls = []
        self.values = []
        self.keys = []

    def setGame(self, game):
        """
        Overwrites parent class' setGame method. Calls the parent's method and then self.setControls
        """

        super(TTTHumanPlayer, self).setGame(game)
        self.setControls()

    def setControls(self):
        """
        Setups the controls for the class. setGame must be called first in order for this to run correctly
        """

        self.controls = []
        self.values = [self.game.board.callable, self.game.board.mvCurUp, self.game.board.mvCurDown,
                       self.game.board.mvCurLeft, self.game.board.mvCurRight]
        if self.control_set == "arrows":
            self.keys = [pygame.K_RETURN, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
        else:
            self.keys = [pygame.K_SPACE, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]

        for i in range(len(self.keys)):
            self.controls.append([self.keys[i], self.values[i]])

    def getMove(self, timeout=60):
        """
        Gets a move from the player and returns the player's chosen position.
        :param timeout: how many seconds the player has to make a move
        :return: (col, row) of player's chosen move
        """

        # need to track position, add a conditional in while loop to check for enter key
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
            self.playPiece(move)
            # if showing the cursor is not disabled then it will appear inbetween turns and after the game has ended
            self.game.board.cursorShow = False
            self.game.board.cursorPos = self.game.board.getEmptySpace()
            if self.game.board.cursorPos is not None:
                self.game.board.updateCursor()
            pygame.display.flip()
            self.game.clock.tick(self.game.fps)
            return move


class TTTAiPlayer(TTTPlayer):
    """
    A.I. TTT player.
    """

    def __init__(self, game_piece, neural_net, default=False):
        """
        Create the ai player
        :param neural_net: Path to an exported neural net to be used as the brains of the A.I.
        :param default: Load the default neural net that comes with this package found at data/ai_default.txt. If
        this argument is True then the neural_net argument will be ignored
        """

        super(TTTAiPlayer, self).__init__(game_piece)
        if default:
            self.neuralNet = ai.TTTNeuralNet.load(ai.DEFAULT_AI_PATH)
        else:
            self.neuralNet = ai.TTTNeuralNet.load(neural_net)

    def getMove(self, timeout=60):
        """
        Gets the necessary input from the board then calls the TTTNeuralNet's getMove function, passing said input
        :param timeout: Added to match signature of method in parent class
        """

        move = self.game.board.translateNumToPos(self.neuralNet.getMove(self.game.turn, self.game.board.sBoard))
        self.playPiece(move)
        self.game.board.cursorPos = self.game.board.getEmptySpace()
        if self.game.board.cursorPos is not None:
            self.game.board.updateCursor()

        pygame.display.flip()
        self.game.clock.tick(self.game.fps)
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {}))  # posting an event keeps the game loop going
        return move


# this is here for when the multiplayer will be properly added
class _TTTLanHumanPlayer(TTTHumanPlayer):
    """
    LAN human player for playing online with other people. Works by creating a TCP stream connection in a socket on port
    54541. During the player's turn, this class will send cursor and move information to the other instance and
    vice-versa. This is still a work in progress
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
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.exit = True

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

        move = None  # need to set to global status
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
            win = self.game.board.checkForWin(move)[0]
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
