'''
Notes:
1) rest encoded by -1

to do
0) find easy way to categorize notes in chord vs notes not in chord to...
1) finish all fitness function parameters
2) try the following duration probabilities: 70 quarter, 20 eighth, 10 sixteenth
3) mut3 is a bit overpowering right now...
'''

import random
from ga_midi import create_midi_file
from mutation import mutate
from fitness import calc_fitness
from chords import create_chord_progression

# duration in durk units: 1 === a 32nd note....32  === a whole note
# return duration that corresponds to one of following notes:
#   32nd: 1 16th: 2, 8th: 4, quarter: 8, half: 16 AND
#   dotted 16th: 3, dotted 8th: 6, dotted quarter: 12
# in all, 1, 2, 3, 4, 6, 8, 12, 16
def choose_duration(simple=False):
    """Returns a random duration in durk units
    
    Args:
        simple (bool, optional): Defaults at False.  If True, only considers notes of duration 8 or 16 durks.  Otherwise, considers durations in list: [1, 2, 3, 4, 6, 8, 12, 16]
    
    Returns:
        int: duration in unit durks
    """
    possible_durations = []
    if simple:
        possible_durations = [8, 16]
    else:
        possible_durations = [1, 2, 3, 4, 6, 8, 12, 16]

    return possible_durations[random.randint(0, len(possible_durations) - 1)]


# returns list of (fitness, genotype)
# fitness holds junk value (-99)-- fitness function used to evaluate it
def initialize_chromosomes(n, d, chord_progression, ngram_generate=None):
    """initializes a list of n chromosomes of musical length d for GA
    
    Args:
        n (int): number of chromosomes to be generated
        d (int): total duration, in durks, of song (and given chord progression)
        chord_progression ((int, int)[]): chord progression of song as list of (chord_root, dur)
        ngram_generate (None, optional): Defaults at None.  If true, then uses ngram pipeline to initialize chromosomes.  Otherwise, randomly initializes.
    
    Returns:
        (int, (int, int)[])[]: Returns list of chromosomes
    """
    chromosomes = []
    for _ in range(n):  # makes n chromosomes
        fitness = -99
        genotype = []
        if not ngram_generate:
            total_duration = 0
            while total_duration < d:
                # choose rest 12.5% of time for extended_degree
                extended_degree = random.randint(1, 21)
                if random.randint(1, 8) == 8:
                    extended_degree = -1

                duration = choose_duration(simple=True)  # DANGER this is really important!
                while (duration + total_duration > d):
                    duration = choose_duration()  # ensures duration of chromosomes equal to d

                genotype.append((extended_degree, duration))
                total_duration += duration
        else:
            genotype = ngram_generate()

        fitness = calc_fitness(genotype, chord_progression)
        chromosomes.append((fitness, genotype))
    return chromosomes


# returns weighted choice in choices
def weighted_choice(choices):
    """returns weighted choice from list of choices
    
    Args:
        choices ((type, float)[]): list of (choice, weight) tuples 
    
    Returns:
        type: returns choice picked.  Can be of any type
    """
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w >= r:
            return c
        upto += w
    assert False, "Shouldn't get here"


# specify size and probabilty best individual in pool wins
# deterministic selection of best individual when p =1
# 1-way tournament (tourn_size = 1) equivalent to random selection
def tournament_selection(chromosomes, tourn_size, prob):
    """tournament selection where, given size and probabilty, selects based on weights a winner
    
    Args:
        chromosomes ((int, (int, int)[])[]): List of chromosomes
        tourn_size (int): size of tournament
        prob (float): probability used based on classic tournament selection
    
    Returns:
        (int, (int, int)[])[]): winning chromosome from the tournament
    """
    # first randomly select tourn_size individuals from chromosomes
    competitors = []
    while len(competitors) < tourn_size:
        to_append = chromosomes[random.randint(0, len(chromosomes) - 1)]
        if to_append not in competitors:
            competitors.append(to_append)

    competitors.sort(key=lambda x: x[0])  # sort by increasing fitness
    weighted_probs = []
    for i in range(0, tourn_size):
        weighted_probs.append(prob * ((1 - prob) ** i))

    return weighted_choice(zip(competitors, weighted_probs))


# one point crossover
# returns child chromosome
def crossover(parent1, parent2, d):
    """One point crossover
    
    Args:
        parent1 (int, (int, int)[])[]): chromosome of parent1
        parent2 (int, (int, int)[])[]): chromosome of parent2
        d (int): Total duration, in durks, of song
    
    Returns:
        ((int, int)[],(int, int)[]): returns two child genotypes in form (genotype1, genotype2)
    """
    genotype1 = parent1[1]
    genotype2 = parent2[1]

    new_genotype1 = []
    new_genotype2_first = []
    new_genotype2_last = []

    # pick random number between 0 and d
    split = random.randint(0, d)

    total_dur = 0
    add_to_genotype1 = True
    for i, (ed, dur) in enumerate(genotype1):
        total_dur += dur
        if not add_to_genotype1:
            new_genotype2_last.append((ed, dur))
        elif total_dur == split:
            new_genotype1.append((ed, dur))
            add_to_genotype1 = False
        elif total_dur > split:
            new_genotype1.append((ed, (split - (total_dur - dur))))
            new_genotype2_last.append((ed, (dur - (split - (total_dur - dur)))))
            add_to_genotype1 = False
        else:
            new_genotype1.append((ed, dur))

    total_dur = 0
    add_to_genotype2 = True
    for i, (ed, dur) in enumerate(genotype2):
        total_dur += dur
        if not add_to_genotype2:
            new_genotype1.append((ed, dur))
        elif total_dur == split:
            new_genotype2_first.append((ed, dur))
            add_to_genotype2 = False
        elif total_dur > split:
            new_genotype2_first.append((ed, (split - (total_dur - dur))))
            new_genotype1.append((ed, (dur - (split - (total_dur - dur)))))
            add_to_genotype2 = False
        else:
            new_genotype2_first.append((ed, dur))

    new_genotype2 = new_genotype2_first + new_genotype2_last

    return (new_genotype1, new_genotype2)


# runs ga on
# population of size n
# returns list of chromosomes in descending order by fitness (highest fitness first)
def ga(chord_progression, n=40, num_iter=200, prob_local=.5, ngram_generate=None):
    """genetic algorithm
    
    Args:
        chord_progression ((int, int)[]): chord progression which is a list of (chord_root, duration)
        n (int, optional): Defaults at 40.  Population size.
        num_iter (int, optional): Defaults at 200.  Specifies number of iterations of GA before termination
        prob_local (float, optional): Defaults at .5.  Probability of mutations
        ngram_generate (None, optional): Defaults at None.  If True, use ngram to initialize population.  Otherwise, randomly initialize.
    
    Returns:
        (int, (int, int)[]))[]: Chromosome list of final generation in the genetic algorithm
    """
    d = sum([d for (_, d) in chord_progression])  # d is total duration of song
    chromosome_list = initialize_chromosomes(n, d, chord_progression, ngram_generate=ngram_generate)  # list of (fitness, genotype)
    elitism_coef = 25  # how many elites to keep in each round

    for i in range(0, num_iter):
        new_chromosome_list = []
        # Elitism?
        # keep the highest fitness chromosome
        chromosome_list.sort(key=lambda x: x[0])  # sort by increasing fitness

        to_print = str(i) + ". " + str(chromosome_list[-1][0])
        print to_print
        for i, chrom in enumerate(reversed(chromosome_list)):
            if i >= elitism_coef:
                break
            new_chromosome_list.append(chrom)
        # new_chromosome_list.append(chromosome_list[-1])

        # Crossover n times
        for i in range(n-elitism_coef):
            parent1 = tournament_selection(chromosome_list, 4, .9)
            parent2 = tournament_selection(chromosome_list, 4, .9)
            (child1_genotype, child2_genotype) = crossover(parent1, parent2, d)

            # calculate fitness of both children, and add higher to chromosomes
            fitness1 = calc_fitness(child1_genotype, chord_progression)
            fitness2 = calc_fitness(child2_genotype, chord_progression)

            if fitness1 > fitness2:
                new_chromosome_list.append((fitness1, child1_genotype))
            else:
                new_chromosome_list.append((fitness2, child2_genotype))

        # Mutate based on certain probabilities
        # decide on hill-climbing (don't replace parent if it was not at
        # least as fit!)
        for i, chrom in enumerate(new_chromosome_list):
            if i < elitism_coef:  # maintain elitism
                continue

            old_genotype = chrom[1][:]
            old_fitness = chrom[0]

            new_genotype = mutate(chrom, d, prob_local=prob_local)  # 1
            new_fitness = calc_fitness(new_genotype, chord_progression)
            if new_fitness >= old_fitness:  # hill climbing implemented here
                new_chromosome_list[i] = (new_fitness, new_genotype)
            else:
                new_chromosome_list[i] = (old_fitness, old_genotype)


        chromosome_list = new_chromosome_list

    chromosome_list.sort(reverse=True, key=lambda x: x[0])  # sort by decreasing fitness
    return chromosome_list

def run(ngram_generate=None,num_iter=800):
    """runs genetic algorithm in main.  Creates midi file with jazz improvisation of winning chromosome.
    Also prints out relevant information.
    
    Args:
        ngram_generate (None, optional): Defaults at None.  If True, use ngram to initialize population.  Otherwise, randomly initialize.
        num_iter (int, optional): Defaults at 200.  Specifies number of iterations of GA before termination
    
    Returns:
        TYPE: Description
    """
    # hard coded chord progression for 12 bar blues
    chord_progression = create_chord_progression()  # list of (chord, duration)
    # chromosomes = ga(chord_progression, n=40, num_iter=800, prob_local=.2)
    chromosomes = ga(chord_progression, n=40, num_iter=num_iter, prob_local=.2, ngram_generate=ngram_generate)  # n=300, p=.8 works well!4
    print [f for (f, _) in chromosomes]
    create_midi_file(chromosomes[0], chord_progression)
    print "Final Fitness: " + str(chromosomes[0][0])
    # print "Num durks: " + str(sum([d for (_, d) in chromosomes[1][1]]))
    print "Best Genotype: \n" + str(chromosomes[0][1])
    print "Detailed Fitness: " + str(calc_fitness(chromosomes[0][1], chord_progression, detailed=True))
    return chromosomes[0][1]


if __name__ == "__main__":
    run()
