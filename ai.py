"""
Module for creating an AI to play tic-tac-toe by training a neural network using genetic algorithms (WIP).

Workflow consists of creating two populations of neural networks using the TTTNeuralNetwork class. The populations
of neural networks are matched against each other in a game of tic-tac-toe using the TTTNeuralGame class and the
fitness of each neural network is calculated. After this is one, a certain percentage of the neural networks are
killed off and replaced with the offspring of the top neural networks. Finally, mutations are applied and a new
generation begins. The workflow stops when the fitness score of the top percentage of networks hasn't changed.

Written by Ryan D. 2016
"""


from numpy import random
from random import randrange
import math
import datetime
from graphics import *
from tttoe import TTTBoard


class TTTNeuron(object):
    """
    Representation of a sigmoid neuron.
    """

    def __init__(self, num_inputs=10):
        """
        Create the neuron
        :param num_inputs: Number of inputs this neuron will receive.
        :return: None
        """

        self.numInputs = num_inputs
        self.weights = []
        self.WEIGHTSRANGE = (-1.0, 1.0)
        self.bias = 0
        self.BIASRANGE = (-7.5, 7.5)
        self.generate()

    def __repr__(self):
        """
        Representation of the class as a string. Represented as "<BIAS><WEIGHTS>"
        """

        return_str = "{:.2f} ".format(self.bias)
        for x in self.weights[:]:
            return_str += ("{:.2f} ".format(x))

        return return_str[:-1]

    def _genWeights(self):
        """
        Generates and returns random weights of type double inside self.WEIGHTSRANGE, one for each input.
        """

        return [float("{:0.3f}".format(str(random.uniform(*self.WEIGHTSRANGE)))) for x in range(self.numInputs)]

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

    def calculate(self, inputs):
        """
        Weights the inputs, adds the bias, sends it to _sigmoid and then returns the output.
        :param inputs: Array of inputs that should be the same length as self.numInputs
        """

        if len(inputs) != self.numInputs:
            raise ValueError("Number of inputs is larger than expected")

        sum = self.bias
        for x in range(len(inputs)):
            sum += inputs[x] * self.weights[x]

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

        While executing the task, there is a 50% chance that the task will also be done to the bias.
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

            weight1 = self.weights[randWeight]
            self.weights[randWeight] = self.weights[randWeight2]
            self.weights[randWeight2] = weight1


class TTTNeuralNet(object):
    """
    Tic-Tac-Toe Neural network object. Has 10 input neurons (nine for each space on the board, one for whose turn
    it is), one hidden network containing nine neurons and nine output neurons.
    """

    def __init__(self, layers=None):
        """
        Create the neural net.
        :param layers: A nested array: [[Input Layer neurons], [Hidden Layer neurons], [Output Layer neurons]] that is
        used to specify layers to use instead of creating random ones.
        :return: None
        """

        self.NUMINPUT = 10
        self.NUMHIDDEN = 9
        self.NUMOUTPUT = 9
        self.layers = layers if layers is not None else [[]] * 3
        self.inputLayer, self.hiddenLayer, self.outputLayer = self.layers[:]
        self.fitness = 0  # this is a placeholder for when it is in a population.
        if layers is None:
            self.create()

    def create(self):
        """
        Creates the layers.
        """

        self.inputLayer = [TTTNeuron() for x in range(self.NUMINPUT)]
        self.hiddenLayer = [TTTNeuron() for y in range(self.NUMHIDDEN)]
        self.outputLayer = [TTTNeuron(num_inputs=9) for z in range(self.NUMOUTPUT)]

    @staticmethod
    def _feedLayer(input_set, layer):
        """
        Feeds a layer the input set and returns the output.
        :param input_set: Inputs to give to the layer.
        :param layer: List of TTTNeuron objects to give the input to.
        """

        return [layer[x].calculate(input_set) for x in range(len(layer))]

    def feed(self, input_set):
        """
        Takes in a list of 10 inputs to use (in order of <TURN><SQ1><SQ2>, etc.) and then returns the output.
        """

        return self._feedLayer(self._feedLayer(self._feedLayer(input_set, self.inputLayer), self.hiddenLayer),
                               self.outputLayer)

    def mutate(self):
        """
        Selects a random neuron in one of the layers and calls its mutate function.
        """

        randLayer = random.randint(0, 2)
        if randLayer == 0:
            layer = self.inputLayer
        elif randLayer == 1:
            layer = self.hiddenLayer
        else:
            layer = self.outputLayer

        layer[random.randint(0, len(layer))].mutate()

    def breed(self, nn):
        """
        Breeds itself with the given neural network by doing one of the following:
        Swap a single weight in one of the neurons
        Swap all of the weights in one of the neurons
        Swap all of the weights in an entire (randomly chosen) layer (has less of a change of occurring).
        :param nn: neural network to breed with.
        :return: Two new offspring/TTTNeuralNet objects
        """

        randTask = random.uniform(0, 1) * 3

        # 5% chance of all the weights in a layer being swapped
        if randTask < 0.15:
            randLayer = random.randint(0, 3)
            if randLayer == 0:
                return [TTTNeuralNet(layers=[nn.inputLayer, self.hiddenLayer, self.outputLayer]),
                        TTTNeuralNet(layers=[self.inputLayer, nn.hiddenLayer, nn.outputLayer])]
            elif randLayer == 1:
                return [TTTNeuralNet(layers=[self.inputLayer, nn.hiddenLayer, self.outputLayer]),
                        TTTNeuralNet(layers=[nn.inputLayer, self.hiddenLayer, nn.outputLayer])]
            else:
                return [TTTNeuralNet(layers=[self.inputLayer, self.hiddenLayer, nn.outputLayer]),
                        TTTNeuralNet(layers=[nn.inputLayer, nn.hiddenLayer, self.outputLayer])]

        # 47.5% chance of all the weights in one of the neurons being swapped. code copy and pasted to save time- I
        # know its wrong to do so and it needs to change
        elif randTask < 1.575:
            randLayer = random.randint(0, 3)
            if randLayer == 0:
                layer1 = self.inputLayer
                layer2 = nn.inputLayer
                rn1 = random.randint(0, len(layer1))  # r = random, n = neuron, l = layer
                rn2 = random.randint(0, len(layer2))
                l1n = layer1[rn1]
                layer1[rn1] = layer2[rn2]
                layer2[rn2] = l1n
                return [TTTNeuralNet(layers=[layer1, self.hiddenLayer, self.outputLayer]),
                        TTTNeuralNet(layers=[layer2, nn.hiddenLayer, nn.outputLayer])]
            elif randLayer == 1:
                layer1 = self.hiddenLayer
                layer2 = nn.hiddenLayer
                rn1 = random.randint(0, len(layer1))  # r = random, n = neuron, l = layer
                rn2 = random.randint(0, len(layer2))
                l1n = layer1[rn1]
                layer1[rn1] = layer2[rn2]
                layer2[rn2] = l1n
                return [TTTNeuralNet(layers=[self.inputLayer, layer1, self.outputLayer]),
                        TTTNeuralNet(layers=[nn.inputLayer, layer2, nn.outputLayer])]
            else:
                layer1 = self.outputLayer
                layer2 = nn.outputLayer
                rn1 = random.randint(0, len(layer1))  # r = random, n = neuron, l = layer
                rn2 = random.randint(0, len(layer2))
                l1n = layer1[rn1]
                layer1[rn1] = layer2[rn2]
                layer2[rn2] = l1n
                return [TTTNeuralNet(layers=[self.inputLayer, self.hiddenLayer, layer1]),
                        TTTNeuralNet(layers=[nn.inputLayer, nn.hiddenLayer, layer2])]

        # 47.5% chance of one of the weights in one of the neurons being swapped
        else:
            randLayer = random.randint(0, 3)
            if randLayer == 0:
                layer1 = self.inputLayer
                layer2 = nn.inputLayer
                rn1 = random.randint(0, len(layer1))  # r = random, n = neuron, l = layer, w = weight
                rn2 = random.randint(0, len(layer2))
                l1n = layer1[rn1]
                l2n = layer2[rn2]

                wIndex = random.randint(0, len(l1n.weights))
                w1Backup = l1n.weights[wIndex]
                l1n.weights[wIndex] = l2n.weights[wIndex]
                l2n.weights[wIndex] = w1Backup
                layer1[rn1] = l1n
                layer2[rn2] = l2n
                return [TTTNeuralNet(layers=[layer1, self.hiddenLayer, self.outputLayer]),
                        TTTNeuralNet(layers=[layer2, nn.hiddenLayer, nn.outputLayer])]
            elif randLayer == 1:
                layer1 = self.hiddenLayer
                layer2 = nn.hiddenLayer
                rn1 = random.randint(0, len(layer1))  # r = random, n = neuron, l = layer, w = weight
                rn2 = random.randint(0, len(layer2))
                l1n = layer1[rn1]
                l2n = layer2[rn2]

                wIndex = random.randint(0, len(l1n.weights))
                w1Backup = l1n.weights[wIndex]
                l1n.weights[wIndex] = l2n.weights[wIndex]
                l2n.weights[wIndex] = w1Backup
                layer1[rn1] = l1n
                layer2[rn2] = l2n
                return [TTTNeuralNet(layers=[self.inputLayer, layer1, self.outputLayer]),
                        TTTNeuralNet(layers=[nn.inputLayer, layer2, nn.outputLayer])]
            else:
                layer1 = self.outputLayer
                layer2 = nn.outputLayer
                rn1 = random.randint(0, len(layer1))  # r = random, n = neuron, l = layer, w = weight
                rn2 = random.randint(0, len(layer2))
                l1n = layer1[rn1]
                l2n = layer2[rn2]

                wIndex = random.randint(0, len(l1n.weights))
                w1Backup = l1n.weights[wIndex]
                l1n.weights[wIndex] = l2n.weights[wIndex]
                l2n.weights[wIndex] = w1Backup
                layer1[rn1] = l1n
                layer2[rn2] = l2n
                return [TTTNeuralNet(layers=[self.inputLayer, self.hiddenLayer, layer1]),
                        TTTNeuralNet(layers=[nn.inputLayer, nn.hiddenLayer, layer2])]

    def draw(self, window_title="Neural Network"):
        """
        Draws itself on the screen in a new window
        """

        size = (850, 1200)
        radius = 35
        xStart = radius + 50
        yStart = radius + 50
        weightFactor = 2
        win = GraphWin(window_title, size[0], size[1])

        x = xStart
        y = yStart
        centers = []
        layers = [self.inputLayer, self.hiddenLayer, self.outputLayer]
        for a in layers:
            layer = []
            for b in a:
                layer.append(Point(x, y))
                y += 800 / len(a) + radius
            centers.append(layer)
            x += size[0] / 3.0 + radius
            y = yStart

        # draw the connections
        for layer in range(len(centers))[:-1]:
            for point in centers[layer]:
                for point2 in centers[layer + 1]:
                    line = Line(point, point2)
                    indexNeuron1 = centers[layer].index(point)
                    neuron2 = layers[layer + 1][centers[layer + 1].index(point2)]
                    weight = (neuron2.weights[indexNeuron1] + 1) * weightFactor
                    print weight
                    print neuron2
                    line.setWidth(weight)
                    line.draw(win)

        # draw the neurons
        for layer in centers:
            for neuron in layer:
                cir = Circle(neuron, radius / 1.5)
                cir.setOutline('black')
                cir.setFill('white')
                cir.draw(win)


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
        self.breedingRate = self.killingRate / 2

        self.nets = []
        self.createNeuralNets()

    def createNeuralNets(self):
        """
        Creates the population of neural nets and stores them in self.nets
        """

        for x in range(self.population):
            self.nets.append(TTTNeuralNet())

    def sort(self, reverse=False):
        """
        Sorts the population based on fitness score lowest to highest. The score must be calculated for each net
        before the pop can be properly sorted
        :param reverse: if True, will sort then nets in descending order.
        """

        self.nets = sorted(self.nets, key=lambda net: net.fitness, reverse=reverse)

    def randomize(self):
        """
        Moves the neural networks into random positions
        """

        randomNets = []
        for x in self.nets:
            randIndex = randrange(0, self.population)
            randomNets.insert(randIndex, x)

    def mutate(self):
        """
        Mutates (self.mutationRate)% of the population by calling a neural networks mutate function
        """

        mutated = [-1]
        for x in range(int(self.population * self.mutationRate)):
            mutateIndex = -1
            while mutateIndex not in mutated:
                mutateIndex = random.randint(0, self.population - 1)
            self.nets[mutateIndex].mutate()
            mutated.append(mutateIndex)

    def breed(self):
        """
        Breeds the top (self.breedingRate)% of the population by calling the neural networks breed function
        """

        newNets = []
        self.sort(reverse=True)
        for x in range(0, int(self.population * self.breedingRate), 2):
            b = self.nets[x].breed(self.nets[x + 1])
            newNets.append(b[0])
            newNets.append(b[1])
        for y in newNets:
            self.nets.append(y)

    def cut(self):
        """
        Kills the lower (self.killingRate)%
        :return: None
        """

        self.sort()
        for index in range(int(self.population * self.breedingRate)):
            del self.nets[0]


class TTTrainer(object):
    """
    Trains two populations
    """

    def __init__(self):
        """
        Create the training object
        """

        self.nnPopulation = 50000
        self.pop1 = TTTPopulation(self.nnPopulation)
        self.pop2 = TTTPopulation(self.nnPopulation)
        self.pops = [self.pop1, self.pop2]
        # if the fitness score hasn't changed in self.genCutOff generations, the testing is stopped
        self.genCutOff = 200

    def train(self):
        """
        Trains the neural networks and returns the one with the highest fitness score.
        """

        print "starting"

        # generations the top fitness score hasn't changed
        generation = 0
        gensSame = 0
        previousFitness = -100

        while gensSame < self.genCutOff:
            for x in self.pops:
                print "randomizing"
                x.randomize()

            print "calculating"
            for net in range(self.nnPopulation):
                self.calcFitness(self.pop1.nets[net], self.pop2.nets[net])

            for x in self.pops:
                print "cutting"
                x.cut()
                print "breeding"
                x.breed()
                print "mutating"
                x.mutate()

            # check if the highest fitness has changed
            self.pop1.sort(reverse=True)
            self.pop2.sort(reverse=True)
            if self.pop1.nets[0].fitness > self.pop2.nets[0].fitness:
                highest = self.pop1.nets[0].fitness
            else:
                highest = self.pop1.nets[0].fitness

            if highest == previousFitness:
                gensSame += 1
            previousFitness = highest

            if True:  # generation % 100 == 0:
                print "Generation: {}, Highest fitness: {}".format(generation, highest)
            generation += 1

        if self.pop1.nets[0].fitness > self.pop2.nets[0].fitness:
            return self.pop1.nets[0]
        else:
            return self.pop1.nets[1].fitness

    @staticmethod
    def calcFitness(nn1, nn2):
        """
        Calculates the fitness of nn1 and nn2.
        :param nn1: Neural network 1
        :param nn2: Neural network 2
        :return: The fitness scores for each neural network [fitness1, fitness2]
        """

        board = TTTBoard()
        winner = False
        turnAssignment = random.randint(0, 2)
        if turnAssignment == 0:
            x = nn1
            o = nn2
        else:
            x = nn2
            o = nn1
        turn = 'x'

        gameWin = 30
        blockOpp = 10
        setupWin = 13
        moveDoc = 0
        overlapDoc = 30
        moveInCenter = 5
        tieGame = 15
        gameLoss = 30

        translate = {'x': 3, 'o': 4, ' ': 0}

        x.fitness = 0
        o.fitness = 0
        while not winner:
            input = [translate[turn]]
            for a in board.sBoard:
                for b in a:
                    input.append(translate[b])

            if turn == 'x':
                output = x.feed(input)
                highIndex = 0
                for c in range(len(output[1:])):
                    if output[c] > output[highIndex]:
                        highIndex = c
                move = board.translateNumToPos(highIndex + 1)

                # check if move is valid
                if board.isValidMove(move) is False:
                    x.fitness -= overlapDoc
                    move = board.getEmptySpace()

                # check if move is in the center
                if move == (2, 2):
                    x.fitness += moveInCenter

                # check if move blocks opponent or wins game
                winningMoves = board.getWinningMoves()
                if move in winningMoves['o']:
                    x.fitness += blockOpp
                if move in winningMoves['x']:
                    x.fitness += gameWin
                    o.fitness -= gameLoss
                    winner = True

                # checks if move sets up for a win
                testBoard = board.copyBoard()
                testBoard[move[1] - 1][move[0] - 1] = 'x'
                x.fitness += (len(board.getWinningMoves(sBoard=testBoard)['x']) - len(winningMoves['x'])) * setupWin

                # deduct moveDoc points for one move
                x.fitness -= moveDoc
                # place move on the board
                board.setPiece(move, 'x')
                # check if move placed created a tie game
                if board.checkForWin() == 't':
                    winner = True
                    x.fitness += tieGame
                    o.fitness += tieGame
                # change whose turn it is
                turn = 'o'

            else:
                output = o.feed(input)
                highIndex = 0
                for c in range(len(output[1:])):
                    if output[c] > output[highIndex]:
                        highIndex = c
                move = board.translateNumToPos(highIndex + 1)

                # check if move is valid
                if board.isValidMove(move) is False:
                    o.fitness -= overlapDoc
                    move = board.getEmptySpace()

                if move == (2, 2):
                    x.fitness += moveInCenter
                # check if move blocks opponent or wins game
                winningMoves = board.getWinningMoves()
                if move in winningMoves['o']:
                    o.fitness += blockOpp
                if move in winningMoves['o']:
                    o.fitness += gameWin
                    x.fitness -= gameLoss
                    winner = True

                # checks if move sets up for a win
                testBoard = board.copyBoard()
                testBoard[move[1] - 1][move[0] - 1] = 'o'
                o.fitness += (len(board.getWinningMoves(sBoard=testBoard)['o']) - len(winningMoves['o'])) * setupWin

                # deduct moveDoc points for one move
                o.fitness -= moveDoc
                # place move on the board
                board.setPiece(move, 'o')
                # check to see if placing the move created a tie game
                if board.checkForWin() == 't':
                    winner = True
                    x.fitness += tieGame
                    o.fitness += tieGame
                # change whose turn it is
                turn = 'x'

        return board


def main():
    pop = 7000
    print "Generating a population of {} neural nets".format(pop)
    start = datetime.datetime.now()
    pop = TTTPopulation(pop)
    del pop
    time = datetime.datetime.now() - start
    print "Take taken: {}.{} seconds.".format(time.seconds, str(time.microseconds)[:3])

    print "Initiating trainer"
    trainer = TTTrainer()
    trainer.train()

if __name__ == '__main__':
    main()
