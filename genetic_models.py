#!/usr/bin/env python3

"""
Models used to find a solution to the taxi driver problem
using genetic algorithms.
"""


from models import Destination, MAX_PASSENGERS
import functools
import random


class Path:
    def __init__(self, dest_list):
        self._dest_list = dest_list

    @property
    def is_valid(self):
        passengers = []
        amount = 0
        
        for dest in self._dest_list:
            if dest.is_pickup:
                if dest.request.passengers + amount <= MAX_PASSENGERS:
                    passengers.append(dest.request)
                    amount += dest.request.passengers
                else:
                    # More passengers than it can pick up
                    return False
            else:
                if dest.request in passengers:
                    passengers.remove(dest.request)
                    amount -= dest.request.passengers
                else:
                    # Hasn't picked up this request
                    return False

        return True

    def fitness(self, origin):
        distance = 0
        cur_point = origin

        for point in self._dest_list:
            distance += cur_point.dist(point)
            cur_point = point

        reward = 0
        request_set = set(dest.request for dest in self._dest_list)
        for request in request_set:
            reward += request.reward

        return reward / distance

    def __repr__(self):
        return str(self._dest_list)


def random_path(options, passengers=0):
    if not options:
        return []
    else:
        valid_options = [dest
                         for dest in options
                         if not dest.is_pickup
                             or dest.request.passengers +
                             passengers <= MAX_PASSENGERS]
        
        option = random.choice(valid_options)
        cur_options = options[:]
        
        if option.is_pickup:
            passengers += option.request.passengers
            cur_options.append(Destination(option.request, False))
        else:
            passengers -= option.request.passengers

        cur_options.remove(option)
        return [option] + random_path(cur_options, passengers)


def make_random_population(requests, size):
    population = []
    options = [Destination(request, True) for request in requests]
    for _ in range(size):
        new_path = random_path(options)
        while new_path in population:
            new_path = random_path(options)
            
        population.append(new_path)

    return population
