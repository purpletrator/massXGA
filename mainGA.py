#first draft of GA algorithm for function optimization using penalty functions and mass extinct
#this algorithm is based around the function
#f(x) = gx^4 + fx^3 + ex^2 + dx + csin(x) + bcos(x) + a
#NUM_VALs will alter what the exact function is, as described below

#supporting module imports
import GAops
import GAgraphing
from GAindiv import individual

#standard python library imports
import pickle
import math
import argparse
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import random
random.seed()

#Global Variables / Constants
CONST_POPSIZE = 100     #size of population
CONST_RANDPERGEN = (int)(0.5 * CONST_POPSIZE) #random individuals to add per generation
                                              #note that this is not used, though it may be implemented later
CONST_BITS = 7 #number of bits in each value of each individual
CONST_NUM_POINTS = 20 #number of random points to generate between each critical point (see initialize_points())
CROSSOVER_RATE = 0.80 #rate of crossover
MUTATION_BITS_RATE = 0.01 #rate of mutation
TOURNAMENT_SIZE = 3 #tournament size
TOURNAMENT_PROBABILITY = 0.75 #probability most fit individual wins in tournament
NUM_VALS = 4 #determines the function--1 means just a, 2 means a,b, 3 means a,b,c, etc.
             #longest function possible: f(x) = gx^4 + fx^3 + ex^2 + dx + csin(x) + bcos(x) + a, NUM_VALS = 7

#this is a counter to hold the total iterations thus far
#note: this is not a constant, but it is used similarly to the other constants so it goes into the constants list
TOTAL_GENS = 0
constants = [CONST_POPSIZE, CONST_BITS, CONST_RANDPERGEN, CONST_NUM_POINTS,
                CROSSOVER_RATE, MUTATION_BITS_RATE, 
                TOURNAMENT_SIZE, TOURNAMENT_PROBABILITY, NUM_VALS,
                TOTAL_GENS]

LAST_CHANGE = 0


#counter reporting the number of mutations per generation
num_mutations = 0


#Function to initialize the points to fit a line to
#Inputs: 
#         a,b,c,...z: parameters for best fit line
#         int numPoints: the number of random points to be generated between each critical point
#Returns: List containing tuples of coordinates
def initialize_points():
    #this function generates the critical points of the graph, 
    #then stochastically adds in more points between the critical points

    points = []
    critPoints = []

    #critical points
    #note: these can be changed to whatever to make the random points 
    #tend to be linear, quadratic, cubic, logarithmic, or whatever
    #the other points will be generated between these points to essentially make a set of points
    #that are roughly linear/quadratic/cubic/logarithmic, but with noise to make it 
    #more difficult for the algorithm to optimize
    critPoints.append((-50.,-50.))
    critPoints.append((0.,0.))
    critPoints.append((50.,50.)) 

    #randomly determine points between the critical points
    for i in range(len(critPoints) - 1):
        points.append(critPoints[i])
        p1 = critPoints[i]
        p2 = critPoints[i+1]

        #make sure we assign the smaller coordinates to x1,y1 so we generate one between x1/y1 and x2/y2
        x1 = p1[0] if p1[0] <= p2[0] else p2[0]
        x2 = p1[0] if p1[0] >= p2[0] else p2[0]
        y1 = p1[1] if p1[1] <= p2[1] else p2[1]
        y2 = p1[1] if p1[1] >= p2[1] else p2[1]
        for j in range(CONST_NUM_POINTS):
            #this will generate a integer number between x1 and x2 (or y1/y2)
            newX = random.randint(x1, x2) + random.random()
            newY = random.randint(y1, y2) + random.random()
            points.append((newX, newY))

    points.append(critPoints[-1])

    #sort points in the list by x value
    points.sort(key = lambda point: point[0])
    return points

'''
Main function for iterating from generation to generation
Inputs: 
    -population: population of all individuals
    -points: set of points to match a curve onto
    -bestFit: current best fitness score

Outputs:
    -newPop: new population after GA operations
    -bestFit: new best fitness
'''
def iterate(population, points, bestFit, subproc=False):
    global num_mutations
    global LAST_CHANGE

    #selection
    newPop = GAops.selection(population, points, TOURNAMENT_SIZE, TOURNAMENT_PROBABILITY)
    
    #crossover
    GAops.crossover(newPop, CROSSOVER_RATE)

    #mutation
    num_mutations = 0
    num_mutations += GAops.mutate_bits(newPop, MUTATION_BITS_RATE)

    #sorting population by fitness (best to worst)
    newPop.sort(key=lambda indiv: indiv.calculate_fitness(points), reverse=False)

    #check if there's a new best individual
    if newPop[0].calculate_fitness(points) < bestFit:
        bestFit = newPop[0].calculate_fitness(points)
        LAST_CHANGE = TOTAL_GENS


    #printing information on the generation
    if not subproc:
        print("=" * 60)
        print("GENERATION " + str(TOTAL_GENS + 1))
        print("\nNumber of mutations: " + str(num_mutations))
        print("Best this gen: " + str(newPop[0].calculate_fitness(points)))
        print("\nLast change in fitness: Generation " + str(LAST_CHANGE))
        print("Best Fitness Overall: " + str(bestFit))
        print("=" * 60 + "\n")

    return newPop, bestFit

'''
Test function to show all the individuals in population by bitstring and values
inputs: 
    population: population of individuals
'''
def test_print(population):
    for indiv in population:
        print(indiv.get_bitstring() + ' ' + ' '.join([str(val) for val in indiv.get_values()]))
    print("Number of individuals: " + str(len(population)))


'''
This function saves a state
Inputs:
    population: population of individuals
    points: list containing points to fit a line onto
    fname: [optional] file name to save to
Actions:
    saves data to a pickle file to be read in later
'''
def save_point(population, points, fname=''):
    #this is the only one of the global variables that can change
    constants[-1] = TOTAL_GENS

    #data to be saved
    data = [population, points, constants]
    if fname == '':
        fname = 'checkpoint_' + str(TOTAL_GENS) + '.pickle'

    #dump into a pickle file
    pickle.dump(data, open(fname, 'wb'))

'''
This function loads a previously saved state
Inputs:
    filepath: path to a pickle file containing input
Actions:
    adjusts constants and loads in points from another save state
'''
def read_from_checkpoint(filepath):
    #read in saved data
    data = pickle.load(open(filepath, 'rb'))
    population = data[0]
    points = data[1]
    constants = data[2]
    print(constants)

    #adjusting constants (loading in save data)
    global CONST_POPSIZE, CONST_BITS, CONST_RANDPERGEN, CONST_NUM_POINTS
    global CROSSOVER_RATE, MUTATION_BITS_RATE
    global TOURNAMENT_SIZE, TOURNAMENT_PROBABILITY, NUM_VALS
    global TOTAL_GENS

    CONST_POPSIZE = constants[0]
    CONST_BITS = constants[1]
    CONST_RANDPERGEN = constants[2]
    CONST_NUM_POINTS = constants[3]
    CROSSOVER_RATE = constants[4]
    MUTATION_BITS_RATE = constants[5]
    TOURNAMENT_SIZE = constants[6]
    TOURNAMENT_PROBABILITY = constants[7]
    NUM_VALS = constants[8]
    TOTAL_GENS = constants[9]

    return population, points

'''
This is basically a slimmed-down version of main() with no error checking or print statements,
except for the ones the script calling this script relies upon.
This method is only used for scripts calling this as a subprocess; see main() for comments
'''
def run_subprocess_version(fname):
    global LAST_CHANGE
    global TOTAL_GENS

    points = pickle.load(open(fname, 'rb'))
    population = []

    for i in range(CONST_POPSIZE):
        memberVals = [''.join(random.choice(['0', '1']) 
                        for j in range(CONST_BITS))
                        for k in range(NUM_VALS)]

        member = individual(memberVals)
        population.append(member)

    population.sort(key=lambda indiv: indiv.calculate_fitness(points), reverse=False)
    bestFitness = population[0].calculate_fitness(points)

    ipt = input("Enter the number of generations to iterate through: ")
    newBestFit = -1
    numGens = int(ipt)
    for i in range(numGens):
        if bestFitness == 0.0:
            break
        population, newBestFit = iterate(population, points, bestFitness, True)
        bestFitness = newBestFit
        TOTAL_GENS += 1

    print(bestFitness)
    print(LAST_CHANGE)
    print("Process Finished")


def main():
    global num_mutations
    global LAST_CHANGE
    LAST_CHANGE = TOTAL_GENS

    #argument parser makes it a little easier to skip the file dialog
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--checkpoint", 
        help="[Flag] Continue from existing checkpoint", action="store_true")
    parser.add_argument("-p", "--points", 
        help="[String] Read in pickle file containing set of points", default='')
    parser.add_argument("--subprocess", action="store_true",
        help="Do not use. For use with scripts calling this as a subscript.")
    args = parser.parse_args()
    use_checkpoint = args.checkpoint
    cmdpoints = args.points
    checkpoint = False
    subproc = args.subprocess

    #preparing the screen to show messagebox/filedialog
    root = tk.Tk()
    root.withdraw()

    if subproc:
        run_subprocess_version(cmdpoints)
        return


    if use_checkpoint:
        #ask user if they actually wanted to open a file (just in case they did -c and didn't mean to)
        result = messagebox.askquestion("Open Existing Data", "Would you like to continue from an existing checkpoint?")
        if result=='yes':
            #open file dialog to find filepath
            #Note: no error catching in case of a bad filename, users can just rerun the program
            checkpoint=True
            filepath = filedialog.askopenfilename()
            print(filepath)
            population, points = read_from_checkpoint(filepath)

    #first time run, initializing data
    if not checkpoint:
        #set of all points
        if cmdpoints == '':
            points = initialize_points()
        else:
            points = pickle.load(open(cmdpoints, 'rb'))

        #this will hold the population
        population = []

        #initialize all members of the population
        for i in range(CONST_POPSIZE):
            #these are two's complement bit strings
            memberVals = [''.join(random.choice(['0', '1']) 
                            for j in range(CONST_BITS))
                            for k in range(NUM_VALS)]

            member = individual(memberVals)
            #adding member to the population
            population.append(member)


        #sort by fitness score
        population.sort(key=lambda indiv: indiv.calculate_fitness(points), reverse=False)

    #printing out the function to be optimized
    #gx^4 + fx^3 + ex^2 + dx + csin(x) + bcos(x) + a
    fxnVals = ['gx^4', 'fx^3', 'ex^2', 'dx', 'csin(x)', 'bcos(x)', 'a']
    function = ''
    for i in range(len(fxnVals)):
        if (i + NUM_VALS) >= len(fxnVals):
            function += ' + ' + fxnVals[i]
    function = function[3:] #(removes the ' + ' at the front of the string)

    #printing initial data
    print("\n")
    print("-" * 60)
    print("Function Optimizer Genetic Algorithm by Aidan Lakshman")
    print("University of Central Florida Evolutionary Computation Lab\n")

    print("Algorithm parameters:\n")
    print("Function to optimize: " + function)
    print("Population size: " + str(CONST_POPSIZE))
    print("Number of points generated: " + str(CONST_NUM_POINTS))
    print("Crossover rate: " + str(100 * CROSSOVER_RATE) + "%")
    print("Mutation rate: " + str(100* MUTATION_BITS_RATE) + "%")
    print("Tournament size: " + str(TOURNAMENT_SIZE))
    print("Tournament rate: " + str(TOURNAMENT_PROBABILITY * 100) + "%")
    print("\nCurrent generation: " + str(TOTAL_GENS) + "\n\n")

    #number of generations to iterate through
    global TOTAL_GENS
    numGens = -1

    ipt = ''
    prevIpt = ipt

    #initial best fitness
    bestFitness = population[0].calculate_fitness(points)

    #show initial population
    GAgraphing.graph_pop(points, population)

    #loop to iterate over population
    while ipt.lower() != 'quit':
        prevIpt = ipt

        print("Enter 'quit' to quit, or 'save' to save a checkpoint")
        ipt = input("Enter the number of generations to iterate through: ")

        #saving data to a checkpoint
        if ipt.lower() == 'save':
            print("Warning: entering a filename that already exists will overwrite the file!")
            fname = input("Enter the filename to save to: ")
            if fname == '':
                save_point(population, points)
            else:
                save_point(population, points, fname)

        #exit loop if user calls quit
        elif ipt == 'quit':
            break

        #testing
        elif ipt == 'print':
            test_print(population)

        #error checking
        elif ipt.isdigit() == False and ipt != '':
            print("\n\nPlease enter a positive integer.\n\n")
            continue

        #otherwise, iterate as many times as specified
        else:
            #no input implies user wants the same thing again
            if ipt == '':
                ipt = prevIpt

            newBestFit = -1
            numGens = int(ipt)
            for i in range(numGens):
                if bestFitness == 0.0:
                    print("Function optimized after " + str(TOTAL_GENS) + " generations.\n\n")
                    break
                population, newBestFit = iterate(population, points, bestFitness)
                bestFitness = newBestFit
                TOTAL_GENS += 1
            GAgraphing.graph_pop(points, population)


    #gives users one last chance to save
    '''
    ipt = input("Would you like to save? (y/n): ")
    if ipt == 'y':
        print("Warning: entering a filename that already exists will overwrite the file!")
        fname = input("Enter the filename to save to: ")

        if fname == '':
            save_point(population, points)
        else:
            save_point(population, points, fname)
    '''

if __name__ == "__main__":
    main()