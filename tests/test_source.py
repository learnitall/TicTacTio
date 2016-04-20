#!/usr/bin/env python
"""
Use nose2 to test the classes and functions found in the tttio package
"""

import logging
import os
import datetime
from nose2.tools import such
from tttio import ai, boards, tttoe

with such.A("system running on linux, windows or osx, python version 2.7") as it:

    with it.having("a working trainer class instance"):
        @it.has_setup
        def setup():
            # creates the trainer class
            it.trainer = ai.TTTrainer(100)
            it.trainer.genStop = 2

        @it.has_teardown
        def teardown():
            del it.trainer

        @it.should("pass through 10 generations of training by calling TTTrainer.train w/o any errors")
        def test():
            start = datetime.datetime.now()
            logging.info("Start time: {}".format(start))
            result = it.trainer.train()
            logging.info("End time: {}. Result had a fitness score of {}.".format(datetime.datetime.now() - start,
                                                                                  result))

    with it.having("a working checkForWin method in a board instance"):
        @it.has_setup
        def setup():  # defines test_cases as {who_should_win: [board to use], [last moves to check]} and creates board
            # ties will be tested in a new layer
            it.test_cases = \
            {'x':
                {
                    'row':
                        {
                            '1': [[['x', 'x', 'x'], ['o', '', 'o'], ['', 'o', '']], [(3, 1), (2, 1), (1, 1)]],
                            '2': [[['o', 'o', 'o'], ['x', 'x', 'x'], ['', '', '']], [(1, 2), (2, 2), (3, 2)]],
                            '3': [[['o', '', 'o'], ['', 'o', ''], ['x', 'x', 'x']], [(1, 3), (2, 3), (3, 3)]],
                        },
                    'col':
                        {
                            '1': [[['x', 'o', 'o'], ['x', '', 'o'], ['x', '', '']], [(1, 1), (1, 2), (1, 3)]],
                            '2': [[['o', 'x', ''], ['o', 'x', ''], ['', 'x', 'o']], [(2, 1), (2, 2), (2, 3)]],
                            '3': [[['o', '', 'x'], ['o', '', 'x'], ['o', '', 'x']], [(3, 1), (3, 2), (3, 3)]]
                        },
                    'd':
                        {
                            'lr': [[['x', 'o', 'o'], ['o', 'x', 'x'], ['o', 'x', 'x']], [(1, 1), (2, 2), (3, 3)]],
                            'rl': [[['o', 'o', 'x'], ['x', 'x', 'o'], ['x', 'x', 'o']], [(3, 1), (2, 2), (1, 3)]]
                        }
                },
             'o':
                {
                    'row': {},
                    'col': {},
                    'd': {}
                }
             }

            # switches the x's and the o's in the 'x' test case and assigns it to the 'o' key in the test_cases dict
            for winType, case in it.test_cases['x'].items():
                for typeLoc, board_case in case.items():
                    copied_board = [[['x' if marker == 'o' else 'o' if marker == 'x' else '' for marker in row] for row
                                     in board_case[0]], board_case[1]]
                    it.test_cases['o'][winType][typeLoc] = copied_board

            it.board = boards.TTTBoard()

        @it.has_teardown
        def teardown():
            del it.test_cases
            del it.board

        @it.should('evaluate each test board to the correct win status using the checkForWin method')
        def test():
            start = datetime.datetime.now()
            for marker, test in it.test_cases.items():
                for winType, case in test.items():
                    for typeLoc, board_case in case.items():
                        board, last_moves = board_case
                        it.board.sBoard = board
                        for last_move in last_moves:
                            shouldRet = (marker, winType + ':' + typeLoc)
                            logging.debug("Testing: Board: {}, Last move: {}, Should return {}".format(
                                it.board.sBoard, last_move, shouldRet))
                            success = it.board.checkForWin(last_move)
                            logging.debug("Returned success: {}".format(success))
                            assert success == shouldRet

            finished = (datetime.datetime.now() - start).total_seconds()
            num_tests = len(it.test_cases['x']) * 2
            cpm = num_tests / finished
            logging.info("Done")
            logging.info("{} board checks done in {} ({} checks per second)".format(num_tests, finished, cpm))

    with it.having('all data files are in the correct location'):
        @it.has_setup
        def setup():
            # forms the path HERE/../data b/c the package is setup like this: TicTacTio -> (tests, data, etc.)
            it.data_dir = os.path.join(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'), 'data')
            it.data_files = ['ai_default.txt', 'background.jpg']

        @it.has_teardown
        def teardown():
            del it.data_dir
            del it.data_files

        @it.should('have files named ai_default and background.jpg inside the data folder')
        def test():
            for data_file in it.data_files:
                data_file_loc = os.path.join(it.data_dir, data_file)
                logging.info("Testing if {} exists".format(data_file_loc))
                assert os.path.exists(data_file_loc)

    with it.having('asserted pygame is installed'):
        @it.should('import and initate pygame without any issues')
        def test():
            logging.info("Importing pygame")
            import pygame
            result = pygame.init()
            logging.info("Result of initiating pygame: {}".format(result))
            try:
                assert result[1] == 0
            except:
                if result[1] == 1 and pygame.mixer.get_init() is None:
                    logging.warning("WARNING: pygame mixer is not initializing properly, however since this is not "
                                    "required the test passes")
                else:
                    raise AssertionError()

    with it.having('a properly working start menu instance'):
        @it.has_setup
        def setup():
            it.start_menu = tttoe.TTTGameStartMenu

        @it.has_teardown
        def teardown():
            del it.start_menu

        @it.should('initiate without any errors being raise')
        def test():
            logging.info("Checking to see if screen exists...")
            window_size = it.start_menu.calculateWindowSize()
            if window_size[0] == 0 or window_size[1] == 0:
                logging.warning("Unable to properly test start menu, as the screen size was calculated to be invalid "
                                "(is a monitor being used?)")
            else:
                logging.info("Creating start menu")
                it.start_menu()
                logging.info("Start menu created")

it.createTests(globals())
