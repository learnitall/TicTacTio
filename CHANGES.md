# Changelog for TicTacTio

## 0.9.1
---

* Added multiprocessing to TTTrainer class, making training the A.I. quicker
* Changed way in which games are initiated, from the perspective of creating players
* Added stream handler to logger and allowed for log files to be rotated
* Fixed some issues with the readme file

## 0.9
---

* Single player game-mode has been added
* New start menu
* Changed project structure:
    * Put python files into packages, complete with init files
    * Created setup.py, setup.cfg, MANIFESTS.in, VERSION.txt
* *Alot* of code has been rewritten to promote efficiency and readability
* Added some test files, which are found in the tests package and run using nose2
* The old tttoe module is now split up into three:
    1. boards.py, containing all the board classes
    2. players.py, containing all of the player classes
    3. tttoe.py, containing the new game menu and all of the game classes
* Added support for [Travis-CI](https://www.travis-ci.org/)
* Added support for [Coveralls](https://www.coveralls.io)
* Updated readme, which includes adding badges
* Conversion over to MIT license from GNU GPLv3
* Added data directory, containing the background image to the game menu and the ai information
* Created this changelog

## 0.1
---

* Initial Release