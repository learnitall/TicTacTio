#!/usr/bin/env python
"""
Module for creating an AI to play tic-tac-toe by training a neural network using genetic algorithms (WIP).

Workflow consists of creating two populations of neural networks using the TTTNeuralNetwork class. The populations
of neural networks are matched against each other in a game of tic-tac-toe using the TTTNeuralGame class and the
fitness of each neural network is calculated. After this is one, a certain percentage of the neural networks are
killed off and replaced with the offspring of the top neural networks. Finally, mutations are applied and a new
generation begins. The workflow stops when the fitness score of the top percentage of networks hasn't changed.

Logging config occurs in the __init__.py file included in this package
"""

from numpy import random
import math
import os
import multiprocessing as mp
import logging
from boards import TTTBoard


_here = os.path.abspath(os.path.dirname(__file__))
_data = os.path.join(os.path.join(_here, '..'), 'data')
DEFAULT_AI_PATH = os.path.join(_data, 'ai_default.txt')
AI_PATH = os.path.join(_data, 'ai.txt')

# values add or subtracted to a nets fitness while it is being trained (based on the circumstances)
GAMEWIN = 30
GAMELOSS = -30
TIEGAME = 15
BLOCKOPP = 10
OVERLAPDOC = -40


class TTTNeuron(object):
    """
    Representation of a sigmoid neuron.
    """

    def __init__(self, layer, num_inputs=10, weights=None, bias=None):
        """
        Create the neuron
        :param: layer: The layer this neuron is found in.
        :param num_inputs: Number of inputs this neuron will receive.
        :param weights: List of weights that will be used as this neurons weights. If None, weights will be generated
        :param bias: Value for the bias to specify. If None, weights will be generated
        :return: None
        """

        self.layer = layer
        self.numInputs = num_inputs
        self.weights = weights if weights is not None else []
        self.bias = bias if bias is not None else 0
        self.WEIGHTSRANGE = (-1, 1)
        self.BIASRANGE = (-7.5, 7.5)
        if weights is None and bias is None:
            self.generate()

    def __repr__(self):
        """
        Representation of the class as a string.
        """

        return "<{};{};{}>".format(
            self.layer, self.bias, ','.join(["{:.2f}".format(i) for i in self.weights]))

    def _genWeights(self):
        """
        Generates and returns random weights of type double inside self.WEIGHTSRANGE, one for each input.
        """

        return [float("{:0.3f}".format(random.uniform(*self.WEIGHTSRANGE))) for x in range(self.numInputs)]

    def _genBias(self):
        """
        Generates and returns a random bias of type double inside self.BIASRANGE.
        """

        return random.uniform(*self.BIASRANGE)

    def generate(self):
        """
        Initiates itself with random values.
        """

        self.weights = self._genWeights()
        self.bias = self._genBias()

    @staticmethod
    def _sigmoid(x):
        """
        Sends x through a logistic sigmoid function and returns the output
        """

        return 1 / (1 + math.exp(-x))

    def feed(self, inputs):
        """
        Weights the inputs, adds the bias, sends it to _sigmoid and then returns the output.
        :param inputs: Array of inputs that should be the same length as self.numInputs
        """

        if len(inputs) != self.numInputs:
            raise ValueError("Number of inputs is larger than expected")

        sum = self.bias
        for index, inp in enumerate(inputs):
            sum += inp * self.weights[index]

        return self._sigmoid(sum)

    def mutate(self):
        """
        Mutates this neural network by selecting a random weight and doing one of the following:
        Replacing it with a new random value
        Multiplying it by a number between 0.5 and 1.5
        Adding or subtracting a random number between 0 and 1
        Changing the polarity of it
        Recreate all of the weights to a new random value
         or swapping it out with another weight.

        While executing a selected task, there is a 50% chance that the task will also be done to the bias.
        :return: None
        """

        randWeight = random.randint(0, len(self.weights))
        randTask = random.randint(0, 6)

        if randTask == 0:  # replace weight with random value
            self.weights[randWeight] = random.uniform(*self.WEIGHTSRANGE)
            if random.random() < 0.5:
                self.bias = random.uniform(*self.BIASRANGE)

        elif randTask == 1:  # multiple by a random value between 0.5 and 1.5
            self.weights[randWeight] *= random.uniform(0.5, 1.5)
            if random.random() < 0.5:
                self.bias *= random.uniform(0.5, 1.5)

        elif randTask == 2:  # add or subtract a random value between -1 and 1
            self.weights[randWeight] += random.uniform(-1, 1)
            if random.random() < 0.5:
                self.bias += random.uniform(-1, 1)

        elif randTask == 3:  # change the polarity
            self.weights[randWeight] *= -1.0
            if random.random() < 0.5:
                self.bias *= -1.0

        elif randTask == 4:  # re-create itself
            self._genWeights()
            if random.random() < 0.5:
                self._genBias()

        else:  # swap two of the weights
            randWeight2 = randWeight
            while randWeight2 == randWeight:
                randWeight2 = random.randint(0, len(self.weights))
            weight = self.weights[randWeight]
            self.weights[randWeight] = self.weights[randWeight2]
            self.weights[randWeight2] = weight


class TTTNeuralNet(object):
    """
    Tic-Tac-Toe Neural network object. Has 10 input neurons (nine for each space on the board, one for whose turn
    it is), one hidden network containing nine neurons and nine output neurons.
    """

    pieceValues = [0.001, 0.01, 0]  # x, o, empty

    def __init__(self, layers=None, fitness=0):
        """
        Create the neural net.
        :param layers: A nested array: [[Input Layer neurons], [Hidden Layer neurons], [Output Layer neurons]] that is
        used to specify layers containing neurons to use instead of creating random ones.
        :param fitness: Used to specify fitness to start out with
        :return: None
        """

        self.NUMINPUT = 10
        self.NUMHIDDEN = 9
        self.NUMOUTPUT = 9
        self.layers = layers if layers is not None else self.create()
        self.inputLayer, self.hiddenLayer, self.outputLayer = self.layers[:]
        self.fitness = fitness  # this is a placeholder for when it is in a population.
        self.mutateChances = [0.05,  # 5% chance of executing mutate task 1
                              47.55,  # 47.5% chance of executing mutate task 2
                              1]  # 47.5% chance of executing mutate task 3

    def __repr__(self):
        """
        Returns fitness
        """

        return str(self.fitness)

    @classmethod
    def load(cls, file_path):
        """
        Opens up the file found at file_path and reads its contents consisting of a stored TTTNeuralNet object
        in order to return a new TTTNeuralNet object. The file at file_path should be the result of the export function
        found below.
        """

        if not os.path.exists(file_path):
            raise IOError("{} does not exist!".format(file_path))
        else:
            input_layer, hidden_layer, output_layer = [], [], []
            with open(file_path, 'r') as fp:
                content = fp.read().strip().split("\n")

            if len(content) < 28:
                raise ValueError("The file {} does not contain enough lines to be the result of the export \n"
                                 "method in this class!".format(file_path))
            else:
                for line in content:
                    layer, bias, weights = line.strip('<>').split(";")
                    neuron = TTTNeuron(layer, weights=[float(x) for x in weights.split(',')], bias=float(bias),
                                       num_inputs=9 if layer == "output" else 10)
                    if layer == "input":
                        input_layer.append(neuron)
                    elif layer == "hidden":
                        hidden_layer.append(neuron)
                    else:
                        output_layer.append(neuron)

            return TTTNeuralNet(layers=[input_layer, hidden_layer, output_layer])

    def export(self, file_path):
        """
        Creates a new txt file at file_path, replacing the existing file at that location if needed, containing the
        output of the __repr__ function of each neuron found in this network, separated by newlines
        """

        with open(file_path, 'w') as exportFile:
            for layer in self.layers:
                for neuron in layer:
                    exportFile.write(neuron.__repr__() + "\n")

    def copy(self):
        """
        Returns a new Neural Network that is exactly like this one
        """

        return TTTNeuralNet(layers=[x for x in self.layers], fitness=self.fitness)

    def create(self):
        """
        Returns layers of neurons.
        """

        return [[TTTNeuron("input") for x in range(self.NUMINPUT)],
                [TTTNeuron("hidden") for y in range(self.NUMHIDDEN)],
                [TTTNeuron("output", num_inputs=9) for z in range(self.NUMOUTPUT)]]

    @staticmethod
    def _feedLayer(input_set, layer):
        """
        Feeds a layer the input set and returns the output.
        :param input_set: Inputs to give to the layer.
        :param layer: List of TTTNeuron objects to give the input to.
        """

        return [layer[x].feed(input_set) for x in range(len(layer))]

    def feed(self, input_set):
        """
        Takes in a list of 10 inputs to use (in order of <TURN><SQ1><SQ2>, etc.) and then returns the output.
        """

        return self._feedLayer(self._feedLayer(self._feedLayer(input_set, self.inputLayer), self.hiddenLayer),
                               self.outputLayer)

    def getMove(self, turn, sBoard):
        """
        Translates the pieces on the sBoard to ints, feeds itself the input and then returns the position on the board
        in which it will move (in the 'int' notation, that is one of the positions on the board labeled 1-9)
        :param turn: x or o for who the current turn it is
        :param sBoard: String representation of a tic tac toe board.
        """

        input_set = [self.pieceValues[0] if turn == 'x' else self.pieceValues[1]]
        [input_set.extend([self.pieceValues[0] if b == 'x' else self.pieceValues[1] for b in a]) for a in sBoard]

        output = self.feed(input_set)
        highest = 0
        for index, out in enumerate(output):
            if out > output[highest]:
                highest = index
        return highest + 1

    def mutate(self):
        """
        Selects a random neuron in one of the layers and calls its mutate function.
        """

        randLayer = random.randint(0, 2)
        self.layers[randLayer][random.randint(0, len(self.layers[randLayer]))].mutate()

    def breed(self, nn):
        """
        Breeds itself with the given neural network by doing one of the following:
        (1)Swap a single weight between two random neurons
        (2)Swap two neurons in one random layer
        (3)Swap all of the neurons in a random layer (has less of a change of occurring).
        :param nn: neural network to breed with.
        :return: Two new offspring/TTTNeuralNet objects
        """

        randTask = random.uniform(0, 1)
        randLayer = random.randint(0, 3)
        children = [TTTNeuralNet(layers=self.layers), TTTNeuralNet(layers=nn.layers)]

        if randTask <= self.mutateChances[0]:  # all the neurons in a layer being swapped
            x = children[0].layers[randLayer]
            children[0].layers[randLayer] = children[1].layers[randLayer]
            children[1].layers[randLayer] = x

        elif randTask <= self.mutateChances[1]:  # 47.5% chance of two neurons swapping weights
            randNeuron = random.randint(len(children[0].layers[randLayer]))
            x = children[0].layers[randLayer][randNeuron]
            children[0].layers[randLayer][randNeuron] = children[1].layers[randLayer][randNeuron]
            children[1].layers[randLayer][randNeuron] = x

        else:  # 47.5% chance of a two weights being swapped between two neurons
            randNeuron = random.randint(len(children[0].layers[randLayer]))
            randWeight = random.randint(len(children[0].layers[randLayer][randNeuron].weights))
            x = children[0].layers[randLayer][randNeuron][randWeight]
            children[0].layers[randLayer][randNeuron].weights[randWeight] = \
                children[1].layers[randLayer][randNeuron].weights[randWeight]
            children[1].layers[randLayer][randNeuron].weights[randWeight] = x

        return children


def loadAI(path_to_net):
    """
    Copies path_to_net to ai.txt, so that it may be used in the game
    :param path_to_net: Path to txt file containing the results of the export method in the TTTNeuralNet class
    :return: 1 if failure, 0 if success
    """

    # try loading the file first to see if it's valid
    testNet = TTTNeuralNet()
    try:
        testNet.load(path_to_net)
    except Exception:
        raise TypeError("The net found at {} is not valid: {}".format(path_to_net, Exception.message))

    here = os.path.abspath(os.path.dirname(__file__))
    testNet.export(os.path.join(os.path.join(os.path.join(here, ".."), "data"), "ai.txt"))


class TTTPopulation(object):
    """
    Represents a population of neural networks (WIP).
    """

    def __init__(self, population):
        """
        Create the population
        """

        self.population = population
        self.mutationRate = 0.20
        self.killingRate = 0.3
        self.diminishRate = 0.01  # percentage the population decreases each generation
        self.breedingRate = (self.killingRate / 2) - self.diminishRate  # allows for the population to slowly die off

        self.nets = []
        self.createNeuralNets()

    def createNeuralNets(self):
        """
        Creates the population of neural nets and stores them in self.nets
        """

        self.nets = [TTTNeuralNet() for i in range(self.population)]

    def sort(self, reverse=True):
        """
        Sorts the population based on fitness score highest to lowest. The score must be calculated for each net
        before the pop can be properly sorted
        :param reverse: if False, will sort then nets in ascending order.
        """

        self.nets = sorted(self.nets, reverse=reverse)

    def randomize(self):
        """
        Moves the neural networks into random positions
        """

        random.shuffle(self.nets)

    def _mutate(self):
        """
        Mutates (self.mutationRate)% of the population by calling a neural networks mutate function
        """

        mutateIndex = 0
        mutated = []
        for x in range(int(self.population * self.mutationRate)):
            while mutateIndex in mutated:
                mutateIndex = random.randint(0, self.population)
            mutated.append(mutateIndex)

        for x in mutated:
            self.nets[x].mutate()

    def _breed(self):
        """
        Breeds the top (self.breedingRate)% of the population by calling the neural networks breed function. Expects
        the neural networks to be sorted in descending order based on fitness
        """

        for x in range(0, int(self.population * self.breedingRate), 2):
            self.nets.extend(self.nets[x].breed(self.nets[x + 1]))

    def _cut(self):
        """
        Kills the lower (self.killingRate)%. Expects the neural networks to be sorted into descending order based on
        fitness
        :return: None
        """

        for index in range(int(self.population * self.breedingRate)):
            del self.nets[len(self.nets) - 1]

    def nextGen(self):
        """
        Calls sort, _cut, _breed, and _mutate and then returns the neural net with the highest fitness
        """

        self.sort()
        fittest = self.nets[0].copy()
        self._cut()
        self._breed()
        self._mutate()
        for net in self.nets:
            net.fitness = 0
        return fittest


def calcFitness(nn1, nn2):
    """
    Calculates the fitness of nn1 and nn2 by placing them against each other in a game of tic-tac-toe. Each
    neural network will have a chance to go first
    :param nn1: Neural network 1
    :param nn2: Neural network 2
    :return: The fitness scores for each neural network [fitness1, fitness2]
    """

    gameOver = False
    overlapCounter = 0  # if 2
    turn = 0  # 0 for x, 1 for o
    players = [nn1, nn2]
    board = TTTBoard()

    while not gameOver and overlapCounter < 2:
        endTurn = False  # this will allow for the 'turn checker' to end turns, yet keep the turns cycling
        while not endTurn:

            move = board.translateNumToPos(players[turn].getMove(turn, board.sBoard))

            # check if move was valid, if not end turn, deduct points and add 1 to overlap counter
            if not board.isValidMove(move):
                players[turn].fitness += OVERLAPDOC
                overlapCounter += 1
                turn = int(not turn)
                endTurn = True

            board.setPiece(move, turn)

            # check if move blocks opponent
            if board.checkForBlocks(move) is True:
                players[turn].fitness += BLOCKOPP

            # check if move wins game
            gameStatus = board.checkForWin(move, retInt=True)
            if gameStatus == turn:
                players[turn].fitness += GAMEWIN
                players[int(not turn)].fitness += GAMELOSS
                gameOver = True
            elif gameStatus == 2:  # 2 is for a tie
                players[turn].fitness += TIEGAME
                players[int(not turn)].fitness += TIEGAME
                gameOver = True


def worker(queue):
    """
    Multiprocessing worker class that will take in a queue of nets and match them together
    """

    logging.info("Worker starting")
    total = 0
    while True:
        try:
            calcFitness(*queue.get(True, 0.1))
            total += 1
        except:  # queue is empty, raises error
            break
    logging.info("Worker ending, {} games played".format(total))


class TTTrainer(object):
    """
    Trains two populations. Logging module must be imported or the global variable logging must be accounted for.
    """

    def __init__(self, population):
        """
        Create the training object
        :param population: amount of neural networks to create
        :param xValue: Int value for x to be inputted into the neural networks
        :param oValue: Int value for o to be inputted into the neural networks
        :param emptyValue: Int value for empty spaces to be inputted into the neural networks
        """

        self.numPopulation = population
        self.populations = [TTTPopulation(self.numPopulation), TTTPopulation(self.numPopulation)]
        self.pop1, self.pop2 = self.populations[:]
        # if the top fitness score hasn't changed in self.genSameMax generations, the testing is stopped
        self.genSameMax = 200
        # testing stops after genStop many generations has been reached
        self.genStop = 250

    def train(self):
        """
        Trains the neural networks and returns the one with the highest fitness score.
        """

        logging.info("Starting training")

        generation = 1
        gensSame = 0
        previousFitness = TTTNeuralNet(fitness=-500)
        highest = None

        logging.info("Note: {} workers will be used- 1 for each cpu)".format(mp.cpu_count()))
        queues = [mp.Queue() for x in range(mp.cpu_count())]
        # holds indices for self.numPopulation that splits the pop into equal amounts based on how many cpus are
        # available (exmaple: if 4 cpus are available then it could look like this: [[0, 4], [4, 8], [8, 12], [12, 16]])
        ranges = []
        for x in range(mp.cpu_count()):
            ranges.append([int(self.numPopulation * (x / float(mp.cpu_count()))), int(
                                self.numPopulation * ((x + 1) / float(mp.cpu_count())))])

        while gensSame < self.genSameMax and generation <= self.genStop:
            logging.info("Starting generation {}".format(generation))

            logging.info("Randomizing populations")
            self.pop1.randomize()
            self.pop2.randomize()

            # matches every single net against one another.
            logging.info("Matching neural networks together")
            logging.debug("Filling queues with info")
            for queue in range(len(queues)):
                for net1 in self.pop1.nets[ranges[queue][0]:ranges[queue][1]]:
                    for net2 in self.pop2.nets:
                        queues[queue].put([net1, net2])

            logging.debug("Starting processes")
            processes = []
            for index in range(mp.cpu_count()):
                process = mp.Process(target=worker, args=(queues[index], ))
                process.start()
                processes.append(process)

            logging.debug("Waiting for calculations to complete...")
            for num, process in enumerate(processes):
                process.join()  # makes sure each process is finished before moving on

            logging.info("Fitness calculations complete. Ending generation.")
            fittest1 = self.pop1.nextGen()  # pcmr
            fittest2 = self.pop2.nextGen()

            highest = fittest1 if fittest1.fitness > fittest2.fitness else fittest2
            logging.info("Highest fitness of the generation: {}".format(highest))
            if highest.fitness == previousFitness.fitness:
                gensSame += 1
                logging.info("Fitness score is the same and now has been for {} generations".format(gensSame))
                previousFitness = highest.copy()
            else:
                logging.info("Fittest score has changed from {} to {}.".format(previousFitness, highest))
                previousFitness = highest.copy()
                gensSame = 0
            generation += 1

        if generation >= self.genStop:
            logging.info("Training has completed because the number of generations has exceeded the max")
        else:
            logging.info("Training has completed because the highest fitness score hasn't changed in {} "
                         "generations".format(self.genSameMax))

        # close down the queues
        for queue in queues:
            queue.close()

        return highest
