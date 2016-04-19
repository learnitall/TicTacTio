#!/usr/bin/env python
"""
Contains all the tic-tac-toe board classes (one graphical, one non-graphical). The boards use a grid system for each
space on the tic tac toe board that looks like this:
Grid layout:
1 | 2 | 3
4 | 5 | 6
7 | 8 | 9
Coordinates are written as (col, row). These boards can be easily define independently of games and players and
controlled by calling their methods.
"""

import pygame


class TTTBoard(object):
    """
    Represents a tic-tac-toe board. Has methods for checking if a player has won and placing moves. Non-graphical
    """

    def __init__(self):
        """
        Create the board ([ROW:[col], ROW:[col], ROW:[col]])
        :return: None
        """

        self.sBoard = self.genBoard()
        self.moves = 0
        self.MAXMOVESTIE = 8

    def setMoves(self, mvs):
        """
        Allows someone to set the number of moves for the board
        """

        self.moves = mvs

    def getMoves(self):
        """
        Returns self.moves
        """

        return self.moves

    def incrementMoves(self):
        """
        Increments self.moves by one
        """

        self.moves += 1

    def genBoard(self):
        """
        Generates a blank board and returns it
        """

        return [[" " for a in range(3)] for b in range(3)]

    def reset(self):
        """
        Resets the board to be blank and sets the moves to zero
        """

        self.moves = 0
        self.sBoard = self.genBoard()

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

    @staticmethod
    def translateNumToPos(num):
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

    def isValidMove(self, pos):
        """
        Returns True if the move at pos is valid (aka if the space at pos is empty) and False if it isn't
        """

        return self.getPiece(pos) == " "

    def setPiece(self, pos, marker):
        """
        Sets the marker for a certain position in self.sBoard. If marker is 0, defaults to x, 1 defaults to o
        :return: None
        """

        if marker == 1:
            marker = 'x'
        elif marker == 0:
            marker = 'o'
        self.sBoard[pos[1] - 1][pos[0] - 1] = marker

    def _checkBlockedCR(self, col_row, piece):
        """
        Used in the checkForBlocks method. Returns true if the piece blocks other pieces in colrow (which is a string
        representation of a col or a row).
        """

        blockedPiece = 'x' if piece == 'o' else 'x'
        return ((blockedPiece + blockedPiece) in col_row and piece in col_row) or col_row == \
                                                                                  (blockedPiece + piece + blockedPiece)

    def checkForBlocks(self, lastMove):
        """
        Checks if lastMove blocks any opponents and returns True if it does and False if it doesn't
        :param lastMove: The last move that was placed on the board, ([col, row]).
        """

        col = lastMove[0]
        row = lastMove[1]
        piece = self.getPiece(lastMove)

        if self._checkBlockedCR(''.join([self.getPiece((x, row)) for x in range(1, 4)]), piece) or \
                self._checkBlockedCR(''.join([self.getPiece((col, y)) for y in range(1, 4)]), piece) or \
           self._checkBlockedCR(''.join([self.getPiece((i, i)) for i in range(1, 4)]), piece) or \
                self._checkBlockedCR(''.join([self.getPiece((3 - i, i)) for i in range(1, 4)]), piece):
            return True

    def checkForWin(self, lastMove, retInt=False):
        """
        Checks to see if there is a three in a row somewhere
        :param lastMove: The last move that was placed on the board, ([col, row]). Increases efficiency
        :param retInt: if True will return 1 if x wins, 0 if o wins and 2 if a tie
        :return: 'x' if x has won, 'o' if o has won, 't', if there is a tie, if else then None
        """

        # check for tie
        if self.moves == self.MAXMOVESTIE:
            return ('t', 'na') if retInt is False else 2

        col = lastMove[0]
        row = lastMove[1]

        # check for a horizontal win
        checkedRow = ''.join([self.getPiece((x, row)) for x in range(1, 4)])
        if checkedRow == 'xxx': return ('x', 'row:{}'.format(row)) if retInt is False else 0
        elif checkedRow == 'ooo': return ('o', 'row:{}'.format(row)) if retInt is False else 1

        # check for a column win
        checkedCol = ''.join([self.getPiece((col, y)) for y in range(1, 4)])
        if checkedCol == 'xxx': return ('x', 'col:{}'.format(col)) if retInt is False else 0
        elif checkedCol == 'ooo': return ('o', 'col:{}'.format(col)) if retInt is False else 1

        # check for diagonal win
        # check for diagonal from left to right
        checkedDiag = ''.join([self.getPiece((i, i)) for i in range(1, 4)])
        if checkedDiag == 'xxx': return ('x', 'd:lr') if retInt is False else 0
        elif checkedDiag == 'ooo': return ('o', 'd:lr') if retInt is False else 1

        # check for diagonal from right to left
        checkedDiagRL = ''.join([self.getPiece((4 - i, i)) for i in range(1, 4)])
        if checkedDiagRL == 'xxx': return ('x', 'd:rl') if retInt is False else 0
        elif checkedDiagRL == 'ooo': return ('o', 'd:rl') if retInt is False else 1

        return None, None


class TTTGraphicalBoard(TTTBoard):
    """
    Graphical wrapper for the TTTBoard class. Draws x's, o's and a cursor on a window using pygame. The window's default
    size is 600 by 600 pixels.
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

    def reset(self):
        """
        Resets the board to its default in order to start a new game
        """

        self.cursorPos = [1, 1]
        self.cursorShow = False
        self.updateCursor()
        super(TTTGraphicalBoard, self).reset()
        self.initUI()

    def initUI(self):
        """
        Draws the grid onto the given screen
        :return:
        """

        self.screen.fill((255, 255, 255))
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

    def displayWinner(self, winner):
        """
        Draws a line through the three in a row that one the game using the appropriate players color.
        :param winner: Output of self.checkForWin
        """

        result = winner[1].split(":")
        color = self.xCol if winner[0] == 'x' else self.oCol
        if result[0] == "row":
            x1 = self.gridPos[0]
            y1 = self.gridPos[1] + ((int(result[1]) - 1) * (self.sqSize[1] + self.lw)) + \
                 (self.sqSize[1] / 2.0)
            x2 = self.gridPos[0] + self.gridSize[0]
            y2 = y1
            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), self.lw)
            pygame.display.flip()
        elif result[0] == "col":
            x1 = self.gridPos[0] + ((int(result[1]) - 1) * (self.sqSize[0] + self.lw)) + \
                 (self.sqSize[0] / 2.0)
            y1 = self.gridPos[1]
            x2 = x1
            y2 = self.gridPos[1] + self.gridSize[1]
            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), self.lw * 2)
            pygame.display.flip()
        elif result[0] == "d":
            x1 = self.gridPos[0]
            y1 = self.gridPos[1]
            x2 = self.gridPos[0] + self.gridSize[0]
            y2 = self.gridPos[1] + self.gridSize[1]
            if result[1] == 'lr':
                pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), self.lw * 2)
                pygame.display.flip()
            else:
                pygame.draw.line(self.screen, color, (x1, y2), (x2, y1), self.lw * 2)
                pygame.display.flip()

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
