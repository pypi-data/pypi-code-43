# -*- coding: utf-8 -*-
"""
https://medium.com/@rinu.gour123/python-genetic-algorithms-with-artificial-intelligence-b8d0c7db60ac
"""
import random
import datetime

geneSet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!."
target = "Hello World!"
random.seed()

def gen_parent(length):
    genes=[]
    while len(genes)<length:
        sampleSize = min(length-len(genes),len(geneSet))
        genes.extend(random.sample(geneSet,sampleSize))
    return "".join(genes)

def get_fitness(guess):
    return sum(1 for expected, actual in zip(target, guess) if expected == actual)

def mutate(parent):
    index = random.randrange(0, len(parent))
    childGenes = list(parent)
    newGene,alternate = random.sample(geneSet,2)
    childGenes[index] = alternate if newGene == childGenes[index] else newGene
    return "".join(childGenes)

def display(guess, start_time):
    timeDiff = datetime.datetime.now() - start_time
    fitness = get_fitness(guess)
    print("{}\t{}\t{}".format(guess,fitness,timeDiff))


start_time = datetime.datetime.now()
bestParent = gen_parent(len(target))
bestFitness = get_fitness(bestParent)
display(bestParent, start_time)

while True:
    child = mutate(bestParent)
    childFitness = get_fitness(child)
    if bestFitness >= childFitness:
        continue
    display(child, start_time)
    if childFitness >= len(bestParent):
        break
    bestFitness = childFitness
    bestParent = child

print("the end!!!")