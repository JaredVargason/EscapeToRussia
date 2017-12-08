#Inspired by Seth Bling's Lua implementation of NEAT.
import math
import random
import copy
from game import Game
import pygame
from sys import argv

Buttons = ['R', 'L', 'Space']

Inputs = 12*12+1 #numboxes
Outputs = len(Buttons)

Population = 300 
DeltaDisjoint = 2.0
DeltaWeights = 0.4
DeltaThreshold = 1.0

StaleSpecies = 15
MutateConnectionsChance = 0.25
PerturbChance = 0.90
CrossoverChance = 0.75
LinkMutationChance = 2.0
NodeMutationChance = 0.50
BiasMutationChance = 0.40
StepSize = 0.1
DisableMutationChance = 0.4
EnableMutationChance = 0.2

TimeoutConstant = 20
MaxNodes = 1000000

def sigmoid(x):
    return 2/(1+math.exp(-4.9 * x)) - 1

class Pool():
    innovation = Outputs
    genesThisGeneration = {} 
    def __init__(self):
        self.timeout = TimeoutConstant
        self.innovation = 0
        self.species = []
        self.generation = 0
        self.innovation = Outputs 
        self.currentSpecies = 0
        self.currentGenome = 0
        self.currentFrame = 0
        self.maxFitness = 0
    
    def newInnovation():
        Pool.innovation += 1
        return Pool.innovation

    def nextGenome(self):
        self.currentGenome += 1
        if self.currentGenome >= len(self.species[self.currentSpecies].genomes):
            self.currentGenome = 0
            self.currentSpecies += 1
            if self.currentSpecies >= len(self.species):
                self.newGeneration()
                self.currentSpecies = 0 

    def fitnessAlreadyMeasured(self):
        species = self.species[self.currentSpecies]
        genome = species.genomes[self.currentGenome]

        return genome.fitness != 0

    def rankGlobally(self):
        ranking = []
        for species in self.species:
            for g in species.genomes:
                ranking.append(g)
        
        ranking.sort(key=lambda x: x.fitness)

        for index, item in enumerate(ranking):
            item.globalRank = index 

    def getInnovationNumber(gene):
        for pair, value in Pool.genesThisGeneration.items():
            if pair[0] == gene.into and pair[1] == gene.out:
                return value
        innovation = Pool.newInnovation()
        Pool.addGeneThisGeneration(gene, innovation)
        return innovation

    def addGeneThisGeneration(gene, innovation):
        Pool.genesThisGeneration[(gene.into, gene.out)] = innovation

    def totalAverageFitness(self):
        total = 0
        for species in self.species:
            total += species.averageFitness
        
        return total

    def cullSpecies(self, cutToOne):
        for species in self.species:
            species.genomes.sort(key=lambda x: x.fitness, reverse=True)

            remaining = math.ceil(len(species.genomes)/2)
            if (cutToOne):
                remaining = 1

            while len(species.genomes) > remaining:
                species.genomes.pop()
    
    def removeStaleSpecies(self):
        survived = [] 
        for species in self.species:
            species.genomes.sort(key=lambda x: x.fitness, reverse=True)

            if species.genomes[0].fitness > species.topFitness:
                species.topFitness = species.genomes[0].fitness
                species.staleness = 0
            
            else:
                species.staleness += 1

            if species.staleness < StaleSpecies or species.topFitness >= self.maxFitness:
                survived.append(species)
            
        self.species = survived
        
    def removeWeakSpecies(self):
        survived = []
        total = self.totalAverageFitness()
        for species in self.species:
            breed = math.floor(species.averageFitness / total * Population)
            if breed >= 1:
                survived.append(species)
        
        self.species = survived

    def addToSpecies(self, child):
        foundSpecies = False
        for species in self.species:
            if not foundSpecies and Genome.sameSpecies(child, species.genomes[0]):
                species.genomes.append(child)
                foundSpecies = True
        
        if not foundSpecies:
            childSpecies = Species()
            childSpecies.genomes.append(child)
            self.species.append(childSpecies)
    
    def newGeneration(self):
        self.writeFile('v2gen' + str(self.generation) + '.txt')
        self.cullSpecies(False)
        self.rankGlobally()
        self.removeStaleSpecies()
        self.rankGlobally()
        for species in self.species:
            species.calculateAverageFitness()
        self.removeWeakSpecies()
        self.genesThisGeneration = {}
        Pool.innovation = 1

        total = self.totalAverageFitness()
        children = []
        for species in self.species:
            breed = math.floor(species.averageFitness / total * Population) - 1
            for i in range(breed):
                children.append(species.breedChild())
        self.cullSpecies(True)
        while len(children) + len(self.species) < Population:
            species = self.species[random.randrange(0, len(self.species))]
            children.append(species.breedChild())
        for child in children:
            self.addToSpecies(child)
        
        self.generation += 1
        print('Entering generation ' + str(self.generation) + '...')

    def savePool(self):
        filename = "trump" + self.generation
        self.writeFile(filename)

    def writeFile(self,filename):        
        wFile = open(filename, 'w')
        wFile.write(str(self.generation) + '\n')
        wFile.write(str(self.maxFitness) + '\n')
        wFile.write(str(len(self.species)) + '\n')

        for n, species in enumerate(self.species):
            wFile.write(str(species.topFitness) + '\n')
            wFile.write(str(species.staleness) + '\n')
            wFile.write(str(len(species.genomes)) + '\n')
            for m, genome in enumerate(species.genomes):
                wFile.write(str(genome.fitness) + '\n')
                wFile.write(str(genome.maxneuron) + '\n')
                for mutation, rate in genome.mutationRates.items():
                    wFile.write(mutation + '\n')
                    wFile.write(str(rate) + '\n')
                wFile.write('done\n')

                wFile.write(str(len(genome.genes)) + '\n')
                for l,gene in enumerate(genome.genes):
                    wFile.write(str(gene.into) + '\n')
                    wFile.write(str(gene.out) + '\n')
                    wFile.write(str(gene.weight) + '\n')
                    wFile.write(str(gene.innovation) + '\n')
                    if gene.enabled:
                        wFile.write('1\n')
                    else:
                        wFile.write('0\n')
        
        wFile.close()
    
    @staticmethod
    def loadFile(filename):
        pool = Pool()
        with open(filename, 'r') as f:
            pool.generation = int(f.readline().rstrip())
            pool.maxFitness = float(f.readline().rstrip())
            numSpecies = int(f.readline().rstrip())
            for s in range(numSpecies):
                species = Species()
                pool.species.append(species)
                species.topFitness = float(f.readline().rstrip())
                species.staleness = int(f.readline().rstrip())
                numGenomes = int(f.readline().rstrip())
                for g in range(numGenomes):
                    genome = Genome()
                    species.genomes.append(genome)
                    genome.fitness = float(f.readline().rstrip())
                    genome.maxneuron = int(f.readline().rstrip())
                    line = f.readline().rstrip()
                    while line != "done":
                        genome.mutationRates[line] = float(f.readline().rstrip())
                        line = f.readline().rstrip()
                    numGenes = int(f.readline().rstrip())
                    for n in range(numGenes):
                        gene = Gene() 
                        genome.genes.append(gene)
                        gene.into = int(f.readline().rstrip())
                        gene.out = int(f.readline().rstrip())
                        gene.weight = float(f.readline().rstrip())
                        gene.innovation = int(f.readline().rstrip())
                        enabled = f.readline().rstrip()
                        if enabled == "1":
                            gene.enabled = True
                        else:
                            gene.enabled = False
        
        return pool
        
class Species():
    def __init__(self):
        self.topFitness = 0
        self.staleness = 0
        self.genomes = []
        self.averageFitness = 0
    
    def calculateAverageFitness(self):
        total = 0

        for genome in self.genomes:
            total += genome.globalRank
        
        self.averageFitness = total / len(self.genomes)
    
    def breedChild(self):
        child = None
        if random.random() < CrossoverChance:
            g1 = self.genomes[random.randrange(0, len(self.genomes))]
            g2 = self.genomes[random.randrange(0, len(self.genomes))]
            child = Genome.crossover(g1, g2)
        
        else:
            g = self.genomes[random.randrange(0, len(self.genomes))]
            child = copy.copy(g)
        
        child.mutate()

        return child
        
            
class Gene():
    def __init__(self):
        self.into = 0
        self.out = 0
        self.weight = 0.0
        self.enabled = True
        self.innovation = 0

class Genome():
    def __init__(self):
        self.genes = []
        self.fitness = 0
        self.adjustedFitness = 0
        self.network = {}
        self.maxneuron = 0
        self.globalRank = 0
        self.mutationRates = {}
        self.mutationRates['connections'] = MutateConnectionsChance
        self.mutationRates['link'] = LinkMutationChance
        self.mutationRates['bias'] = BiasMutationChance
        self.mutationRates['node'] = NodeMutationChance
        self.mutationRates['enable'] = EnableMutationChance
        self.mutationRates['disable'] = DisableMutationChance
        self.mutationRates['step'] = StepSize
    
    def __copy__(self):
        genome2 = Genome()
        for gene in self.genes:
            genome2.genes.append(copy.copy(gene))
        genome2.maxneuron = self.maxneuron
        genome2.mutationRates['connections'] = self.mutationRates['connections']
        genome2.mutationRates['link'] = self.mutationRates['link']
        genome2.mutationRates['bias'] = self.mutationRates['bias']
        genome2.mutationRates['node'] = self.mutationRates['node']
        genome2.mutationRates['enable'] = self.mutationRates['enable']
        genome2.mutationRates['disable'] = self.mutationRates['disable']

        return genome2

    
    @staticmethod
    def basicGenome():
        genome = Genome()
        genome.maxneuron = Inputs
        genome.mutate()

        return genome

    def generateNetwork(self):
        network = {}
        network['neurons'] = {}

        for i in range(0,Inputs):
            network['neurons'][i] = Neuron()

        for o in range(0, Outputs):
            network['neurons'][MaxNodes + o] = Neuron()
        
        self.genes.sort(key = lambda x: x.out)

        for gene in self.genes:
            if gene.enabled:
                if gene.out not in network['neurons']:
                    network['neurons'][gene.out] = Neuron()
                neuron = network['neurons'][gene.out]
                neuron.incoming.append(gene)
                if gene.into not in network['neurons']:
                    network['neurons'][gene.into] = Neuron()
        
        self.network = network

    def evaluateNetwork(self, inputs):
        if len(inputs) != Inputs:
            print('wrong num of inputs: expected ' + str(Inputs) + ' but got ' + str(len(inputs)))
            return {}

        for i in range(0, Inputs):
            self.network['neurons'][i].value = inputs[i]

        for key, neuron in self.network['neurons'].items():
            total = 0
            for incoming in neuron.incoming:    
                other = self.network['neurons'][incoming.into]
                total = total + incoming.weight * other.value

            if len(neuron.incoming) > 0:
                neuron.value = sigmoid(total)
        
        outputs = {}
        for o in range(0, Outputs):
            button = Buttons[o]
            if self.network['neurons'][MaxNodes + o].value > 0:
                outputs[button] = True
            else:
                outputs[button] = False
        
        return outputs


    def randomNeuron(self, nonInput):
        neurons = {}
        if not nonInput:
            for i in range(Inputs):
                neurons[i] = True
        
        for o in range(Outputs):
            neurons[MaxNodes + o] = True

        for gene in self.genes:
            if not nonInput or gene.into > Inputs:
                neurons[gene.into] = True

            if not nonInput or gene.out > Inputs:
                neurons[gene.out] = True

        neuron, value = random.choice(list(neurons.items()))

        return neuron

    def containsGene(self, link):
        for gene in self.genes:
            if gene.into == link.into and gene.out == link.out:
                return True
        
        return False

    def pointMutate(self):
        step = self.mutationRates['step']

        for gene in self.genes:
            if random.random() < PerturbChance:
                gene.weight = gene.weight + random.random() * step*2 - step
            else:
                gene.weight = random.random() * 4 - 2

    def linkMutate(self, forceBias):
        neuron1 = self.randomNeuron(False)
        neuron2 = self.randomNeuron(True)
        newLink = Gene()

        if neuron1 <= Inputs and neuron2 <= Inputs:
            return

        if neuron2 <= Inputs:
            temp = neuron1
            neuron1 = neuron2
            neuron2 = temp 
        
        newLink.into = neuron1
        newLink.out = neuron2

        if forceBias:
            newLink.into = Inputs - 1

        if self.containsGene(newLink):
            return

        newLink.innovation = Pool.getInnovationNumber(newLink)
        newLink.weight = random.random()*4-2
        self.genes.append(newLink)
    
    def nodeMutate(self):
        if len(self.genes) == 0:
            return

        self.maxneuron = self.maxneuron + 1

        gene = self.genes[random.randrange(0, len(self.genes))]
        if not gene.enabled:
            return

        gene.enabled = False

        gene1 = copy.copy(gene)
        gene1.out = self.maxneuron
        gene1.weight = 1.0
        gene1.innovation = Pool.getInnovationNumber(gene1) 
        gene1.enabled = True
        self.genes.append(gene1)

        gene2 = copy.copy(gene)
        gene2.into = self.maxneuron
        gene2.innovation = Pool.getInnovationNumber(gene2) 
        gene2.enabled = True
        self.genes.append(gene2)
    
    def enableDisableMutate(self, enable):
        candidates = []
        for gene in self.genes:
            if gene.enabled == (not enable):
                candidates.append(gene)
        
        if len(candidates) == 0:
            return

        gene = candidates[random.randrange(0, len(candidates))]
        gene.enabled = not gene.enabled

    def mutate(self):
        for mutation, rate in self.mutationRates.items():
            if random.random() > .5:
                self.mutationRates[mutation] = .95 * rate
            
            else:
                self.mutationRates[mutation] = 1.05263 * rate

        if random.random() < self.mutationRates['connections']:
            self.pointMutate()
    
        n = self.mutationRates["link"]
        while(n > 0):
            if random.random() < n:
                self.linkMutate(False)
            n = n - 1

        n = self.mutationRates["bias"]
        while(n > 0):
            if random.random() < n:
                self.linkMutate(True)
            n = n - 1

        n = self.mutationRates["node"]
        while(n > 0):
            if random.random() < n:
                self.nodeMutate()
            n = n - 1

        n = self.mutationRates["enable"]
        while(n > 0):
            if random.random() < n:
                self.enableDisableMutate(True)
            n = n - 1

        n = self.mutationRates["disable"]
        while(n > 0):
            if random.random() < n:
                self.enableDisableMutate(False)
            n = n - 1

    @staticmethod
    def crossover(g1, g2):
        if g2.fitness > g1.fitness:
            tempg = g1
            g1 = g2
            g2 = tempg

        child = Genome()

        innovations2 = {}
        for gene in g2.genes:
            innovations2[gene.innovation] = gene
        
        for gene1 in g1.genes:
            if gene1.innovation in innovations2 and random.randint(1,2) == 1 and innovations2[gene1.innovation].enabled:  
                child.genes.append(copy.copy(innovations2[gene1.innovation]))
            else:
                child.genes.append(copy.copy(gene1)) 

        child.maxneuron = max(g1.maxneuron, g2.maxneuron)
        for mutation, rate in g1.mutationRates.items():
            child.mutationRates[mutation] = rate

        return child

    @staticmethod
    def disjoint(genome1, genome2):
        i1 = {} 
        for gene in genome1.genes:
            i1[gene.innovation] = True

        i2 = {} 
        for gene in genome2.genes:
            i2[gene.innovation] = True
        
        disjointGenes = 0
        for gene in genome1.genes:
            if gene.innovation not in i2:
                disjointGenes += 1
        
        for gene in genome2.genes:
            if gene.innovation not in i1:
                disjointGenes += 1
        
        return disjointGenes / max(len(genome1.genes), len(genome2.genes))

    @staticmethod
    def weights(genome1, genome2):
        i2 = {}
        for gene in genome2.genes: 
            i2[gene.innovation] = gene
        
        total = 0
        coincident = 0

        for gene in genome1.genes:
            if gene.innovation in i2:
                gene2 = i2[gene.innovation]
                total = total + math.fabs(gene.weight - gene2.weight)
                coincident = coincident + 1

        if coincident == 0:
            return 0 

        return total / coincident

    @staticmethod
    def sameSpecies(genome1, genome2):
        dd = DeltaDisjoint*Genome.disjoint(genome1, genome2)
        dw = DeltaWeights * Genome.weights(genome1, genome2)
        if dw > 0:
            return dd + dw < DeltaThreshold

        else:
            return dd + dw < (DeltaThreshold - 0.5)

    

class Neuron():
    def __init__(self):
        self.incoming = [] 
        self.value = 0.0

class Learn():

    def __init__(self, pool=None):
        if pool == None:
            self.pool = Pool()
            self.game = Game()
            self.controller = {'R': False, 'L': False, 'Space': False}
            for i in range(0, Population):
                basic = Genome.basicGenome()
                self.pool.addToSpecies(basic)
        
        else:
            self.pool = pool
            self.game = Game()
            self.controller = {'R': False, 'L': False, 'Space': False}

    def initializeRun(self):
        self.game.setupGame()
        self.pool.currentFrame = 0
        species = self.pool.species[self.pool.currentSpecies]
        species.genomes[self.pool.currentGenome].generateNetwork()
        self.pool.timeout = TimeoutConstant

    def evaluateCurrent(self):
        species = self.pool.species[self.pool.currentSpecies]
        genome = species.genomes[self.pool.currentGenome]

        inputs = self.game.getInputs(self.game.getTrumpBlockPositionX(), self.game.getTrumpBlockPositionY())
        inputs.append(1)
        controller = genome.evaluateNetwork(inputs)

        if (controller['R'] and controller['L']):
            controller['L'] = controller['R'] = False
        
        return controller
    
    def learnTrumpJump(self):
        while True:
            species = self.pool.species[self.pool.currentSpecies]
            genome = species.genomes[self.pool.currentGenome]
            self.initializeRun()
            self.game.updateUI(self.pool.generation, len(self.pool.species), self.pool.maxFitness, Population)
            runMaxFitness = -100
            while self.game.trump.alive:
                if self.pool.currentFrame % 5 == 0: 
                    self.controller = self.evaluateCurrent()

                self.pool.timeout -= 1 

                if self.game.trump.position > runMaxFitness:
                    runMaxFitness = self.game.trump.position 
                    self.pool.timeout = TimeoutConstant

                timeoutBonus = self.pool.currentFrame / 4
                if self.pool.timeout + timeoutBonus <= 0:
                    break

                self.pool.currentFrame += 1
                
                self.game.advance_frame_learn(self.controller)
            
            self.game.cleanupGame()

            fitness = self.game.trump.position - self.pool.currentFrame / 2
            if fitness == 0:
                fitness = -1
            
            genome.fitness = fitness
            if fitness > self.pool.maxFitness:
                self.pool.maxFitness = fitness

            self.pool.currentSpecies = 0
            self.pool.currentGenome = 0
            while self.pool.fitnessAlreadyMeasured():
                self.pool.nextGenome() 

if __name__ == '__main__':
    if len(argv) == 2: 
        pool = Pool.loadFile(argv[1])
        learn = Learn(pool)
        learn.learnTrumpJump()

    elif len(argv) == 3:
        if argv[2] == "top": 
            pool = Pool.loadFile(argv[1])
            maxFitness = maxs = maxg = 0

            for s, species in enumerate(pool.species):
                for g, genome in enumerate(species.genomes):
                    if genome.fitness > maxFitness:
                        maxs = s
                        maxg = g
                        maxFitness = genome.fitness
            
            pool.currentSpecies = maxs
            pool.currentGenome = maxg
            learn = Learn(pool)
            learn.learnTrumpJump()

        else:
            print("Unknown argument " + argv[2] + "; Need argument 'top' for playback of top species")


    else:
        learn = Learn()
        learn.learnTrumpJump()
    