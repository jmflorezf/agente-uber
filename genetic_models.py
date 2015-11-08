#!/usr/bin/env python3

"""
Models used to find a solution to the taxi driver problem
using genetic algorithms.
"""


from models import Destination, MAX_PASSENGERS, Point, Request
import random


class Path:
    def __init__(self, dest_list, origin=Point(0,0)):
        self._dest_list = dest_list
        self._origin = origin
        self._requests = list(set(dest.request for dest in self._dest_list))
        self._valid = None
        self._fitness = None

    @property
    def is_valid(self):
        if self._valid is not None:
            return self._valid
        
        passengers = []
        amount = 0
        
        for dest in self._dest_list:
            if dest.is_pickup:
                if dest.request.passengers + amount <= MAX_PASSENGERS:
                    passengers.append(dest.request)
                    amount += dest.request.passengers
                else:
                    # More passengers than it can pick up
                    self._valid = False
            else:
                if dest.request in passengers:
                    passengers.remove(dest.request)
                    amount -= dest.request.passengers
                else:
                    # Hasn't picked up this request
                    self._valid = False

        self._valid = True
        return self._valid

    @property
    def fitness(self):
        if not self.is_valid:
            return 0

        if self._fitness is not None:
            return self._fitness
        
        distance = 0
        cur_point = self._origin

        for point in self._dest_list:
            distance += cur_point.dist(point)
            cur_point = point

        reward = 0
        for request in self._requests:
            reward += request.reward

        self._fitness = reward / distance

        return self._fitness

    def mutate(self):
        """Return a new path obtained by swapping two random requests"""
        request1 = random.choice(self._requests)
        request2 = random.choice(self._requests)
        while request2 == request1:
            request2 = random.choice(self._requests)

        for i, dest in enumerate(self._dest_list):
            if dest.request == request1:
                if dest.is_pickup:
                    r1_pickup = i
                else:
                    r1_drop_off = i
            elif dest.request == request2:
                if dest.is_pickup:
                    r2_pickup = i
                else:
                    r2_drop_off = i

        new_dest_list = self._dest_list[:]

        # Swap
        (new_dest_list[r1_pickup],
         new_dest_list[r2_pickup]) = (new_dest_list[r2_pickup],
                                      new_dest_list[r1_pickup])

        (new_dest_list[r1_drop_off],
         new_dest_list[r2_drop_off]) = (new_dest_list[r2_drop_off],
                                        new_dest_list[r1_drop_off])

        return Path(new_dest_list)

    def crossover(self, other):
        """Creates a new path by performing crossover"""
        request = random.choice(self._requests)

        for i, dest in enumerate(self._dest_list):
            if dest.request == request:
                if dest.is_pickup:
                    pickup = i
                else:
                    drop_off = i

        new_dest_list = [None] * len(self._dest_list)
        new_dest_list[pickup] = self._dest_list[pickup]
        new_dest_list[drop_off] = self._dest_list[drop_off]

        i = 0
        for dest in other._dest_list:
            if dest.request == request:
                continue

            while new_dest_list[i] is not None:
                i += 1

            new_dest_list[i] = dest

        return Path(new_dest_list)

    def __eq__(self, other):
        if isinstance(other, Path) and self._dest_list == other._dest_list:
            return True
        else:
            return False

    def __repr__(self):
        return str(self._dest_list)

    def __str__(self):
        return self.__repr__()


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


class RankedPath:
    def __init__(self, path, value):
        self.path = path
        self.value = value


class GeneticAlgorithm:
    def __init__(self,
                 request_amount=100,
                 taxi_origin=Point(0,0),
                 population_size=10,
                 max_generations=100,
                 mutation_rate=0.01):
        self.population_size = population_size
        self.max_generations = max_generations
        self.mutation_rate = mutation_rate
        self.taxi_origin = taxi_origin

        requests = []
        for _ in range(request_amount):
            origin = Point(random.randint(0, 50), random.randint(0, 50))
            destination = Point(random.randint(0, 50), random.randint(0, 50))
            passengers = random.randint(1, 4)

            requests.append(Request(origin, destination, passengers))

        self._population = make_random_population(requests, population_size)

    @property
    def fittest(self):
        return max(self._population, key=lambda x: x.fitness)

    def run(self):
        self.stats()
        for _ in range(self.max_generations):
            self.next_generation()
        self.stats()

    def stats(self):
        fittest = max(self._population,
                      key=lambda x: x.fitness)
        print('Maximum fitness:', fittest.fitness)

        total = 0
        for sol in self._population:
            total += sol.fitness

        print('Average fitness:', total / len(self._population))
        print()

    def next_generation(self):
        total_fitness = 0
        max_fitness = float('-inf')
        best = 0
        for i, sol in enumerate(self._population):
            total_fitness += sol.fitness
            if sol.fitness > max_fitness:
                best = i
                max_fitness = sol.fitness

##        relative_fitness = [(s.fitness / total_fitness, s)
##                            for s in self._population]
##
##        sorted_fitness = sorted(relative_fitness,
##                                key=lambda x: x[0],
##                                reverse=True)

        ranked_paths = [RankedPath(path, path.fitness/total_fitness)
                        for path in self._population]
        
##        for fitness, path in sorted_fitness:
##            accum += fitness
##            ranked_paths.append(RankedPath(path, accum))
        
        new_gen = [self._population[best]]
        while len(new_gen) < self.population_size:
            r1 = preferent_choice(ranked_paths)
            r2 = preferent_choice(ranked_paths)

            while r1 == r2:
                r2 = preferent_choice(ranked_paths)

            parent1 = r1.path
            parent2 = r2.path

            child = self._make_child(parent1, parent2)

##            while child not in new_gen:
##                child = self._make_child(parent1, parent2)

            new_gen.append(child)

        self._population = new_gen


    def _make_child(self, parent1, parent2):
        child = parent1.crossover(parent2)
        if random.random() <= self.mutation_rate:
            child = child.mutate()

        return child


def make_random_population(requests, size):
    population = []
    options = [Destination(request, True) for request in requests]
    for _ in range(size):
        new_path = Path(random_path(options))
        while new_path in population:
            new_path = Path(random_path(options))
            
        population.append(new_path)

    return population

def preferent_choice(ranked_paths):
    r = random.random()
    selection = 0
    s = 0

    for i, ranked_path in enumerate(ranked_paths):
        s += ranked_path.value
        selection = i
        if s >= r:
            break

    return ranked_paths[selection]


def simulate_path(path, origin=Point(0,0)):
    passengers = 0
    distance = 0
    reward = 0
    prev_point = origin
    print('Beginning at', origin)
    print()

    for dest in path._dest_list:
        distance += prev_point.dist(dest)
        prev_point = dest

        request = dest.request
        if dest.is_pickup:
            print('Picking up %d passengers at %s' % (request.passengers,
                                                      dest))
        else:
            print('Dropping off %d passengers at %s' % (request.passengers,
                                                        dest))
            reward += request.reward
        print()

    print()
    print('Distance traversed:', distance)
    print('Total reward:', reward)
