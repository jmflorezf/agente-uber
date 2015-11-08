#!/usr/bin/env python3

"""
Execution of taxi driver problem using genetic algorithms
"""


import genetic_models
import models


r1 = models.Request(models.Point(0,0),models.Point(1,5), 1)
r2 = models.Request(models.Point(2,3),models.Point(3,5), 1)
r3 = models.Request(models.Point(1,4),models.Point(5,8), 4)

paths = [genetic_models.Path(path)
         for path in genetic_models.make_random_population([r1, r2, r3],8)]

for path in paths:
    print(path)
    print(path.fitness(models.Point(0,0)))
    print()
