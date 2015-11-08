#!/usr/bin/env python3

"""
Execution of taxi driver problem using genetic algorithms
"""


from genetic_models import GeneticAlgorithm, simulate_path


g = GeneticAlgorithm(population_size=10,
                     request_amount=70,
                     max_generations=20000,
                     mutation_rate=0.05)

g.run()

##simulate_path(g.fittest)
