[![Build Status](https://travis-ci.org/DevelopForLizardz/TicTacTio.svg?branch=master)](https://travis-ci.org/DevelopForLizardz/TicTacTio) 
[![Coverage Status](https://coveralls.io/repos/github/DevelopForLizardz/TicTacTio/badge.svg?branch=master)](https://coveralls.io/github/DevelopForLizardz/TicTacTio?brance=master)
[![Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg)](https://www.python.org/download/releases/2.7/)
[![GitHub license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://opensource.org/licenses/MIT)

#TicTacTio

###*A project made to learn stuff*

## Overview
---

TicTacTio was born out of a need to learn basic machine learning concepts after watching a video created by 
[Sethbling](https://www.youtube.com/channel/UC8aG3LDTDwNR1UQhSn9uVrw) where he used genetic algorithms and neural 
networks to create an A.I. that played Super Mario World (you can check it out [here]
(https://www.youtube.com/watch?v=qv6UVOQ0F44&noredirect=1)). I had wanted to replicate that project without essentially
just doing the same thing, so I decided to (1) write everything from scratch and (2) to adapt the A.I. to TicTacToe, 
which would be an easier game to write the A.I. for. Doing these two things would allow me to get the most amount of 
experience and control out of this project. Also, I thought that it would be a good idea to use this project
as a learning tool for other areas of programming besides machine learning, (which is why there are features like 
mutliplayer).

The A.I. is just a neural network composed of sigmoid neurons (10 in the input layer, 10 in a hidden layer and
nine in the output layer). The input given to the neural network consists of whose turn it is (x or o) and every space 
on the board (each space has a state of x, o, or empty) and before the input is fed into the net, each game piece 
is assigned a certain value (I used 10 for x, 5 for o and 0 for empty). Something interesting that I noticed is that the
larger distribution between each game piece value, the more variant the output of the neural net would be. For example,
at first I had set the values to 2 for x, 1 for o, and 0 for empty and each neural net would output the same space
no matter the input. Anyway, the output of the neural network is nine floats, (each float representing a space on the 
board) and whichever float had the highest value is the space on the board that the A.I. will place its piece.

Training the neural networks using genetic algorithms was kind-of a weird process: Two populations of neural networks
were created, each neural net in one population would go head to head in a game of tic-tac-toe with a each neural
net in the other population with the fitness for each net being scored along the way. As soon as the games were finished
the top two fittest nets of each population were picked out, bred, a lower percentage of the nets were killed and then
a certain percentage of the population was mutated. Which the max generations have been reached or the highest 
fitness score has stayed the same for a set amount of generations the training has ended and the fittest neural net
is exported to a file. (To see the actual values that I used at each step, see the A.I. module).

Eventually, I do want to add a gradient descent training workflow and just hard code an algorithm [something like this
one](http://neverstopbuilding.com/minimax) to see how they compare. 

## Dependencies<a name="dependencies"></a>
---

* [Python](www.python.org)
    * TicTacTio is run with Python2.7, which can be installed using apt:
   ```
   sudo apt-get install python2.7
   ```

* [Pygame](www.pygame.org)
    * All of the GUI was written with pygame, which can yet again be installed with apt: 
    ```
    sudo apt-get install python-pygame
    ```
    
* [Nose2](https://nose2.readthedocs.org/en/latest/)
    * Used to run test scripts. This one is installed using pip:
    ```
    sudo pip install nose2
    ```
    
***Note:*** apt is specific to certain linux distros (Mint, Ubuntu, etc.). Be sure to use the package manager for your
operating system.

## Installation
---

Installation is pretty simple, and only requires 6 steps: 

1. Install [dependencies](#dependencies)
2. Download zip of [master branch](https://github.com/DevelopForLizardz/TicTacTio/archive/master.zip)
3. Unpack using an archive manager
4. Run the setup.py file:
```
python setup.py install
```

## Starting the game
---

To start the game, just import and execute.

```python
from tttio import tttoe
tttoe.main()
```

## Running tests
---

Running tests is pretty easy, just cd into the package directory and then run nose2.

*Please note:* The nose2.cfg file is necessary in order for the tests to work, as it enables both the layers plugin and
log capture. If for some reason the cfg file isn't being loaded (I've had issues with this in the past), make sure to 
enable these manually:

```
nose2 --plugin nose2.plugins.layers --log-capture
```

## License - MIT
--- 

Copyright (c) 2016 Ryan Drew

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.