#!/usr/bin/env python3

"""
Description
"""


import random


MAX_PASSENGERS = 4


def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0
    

class Agent:
    max_pasengers = MAX_PASSENGERS
    
    def __init__(self, start_pos):
        self.destinations = None
        self.passengers = list()
        self.pos = start_pos
        self.requests = list()
        self.total_rewards = 0
        self.distance_traversed = 0

        print('Agent beginning at %s' % start_pos)
        print()

    def perceive(self, requests):
        if requests:
            print('Request received, calculating best path...')
            print()
            self.requests += requests

            # Passengers
            options = [Destination(req, False) for req in self.passengers]
            # Requests
            options += [Destination(req, True) for req in self.requests]

            best_path = self._best_path(options)

            self.destinations = best_path.to_list()

            print('Best path determined:', best_path , '\n')                
    def act(self):
        if self.destinations:
            dest = self.destinations[0]
            if dest == self.pos:
                self.destinations.pop(0)
                
                if dest.is_pickup:
                    self._pick_up(dest.request)
                else:
                    self._drop_off(dest.request)
            else:
                # Move towards destination
                if dest.x != self.pos.x:
                    self.pos.x += sign(dest.x - self.pos.x)
                else:
                    self.pos.y += sign(dest.y - self.pos.y)
                self.distance_traversed += 1
        else:
            print('No requests. Idle.\n')

    @property
    def current_passengers(self):
        total = 0
        for request in self.passengers:
            total += request.passengers

        return total

    def _pick_up(self, request):
        self.passengers.append(request)
        self.requests.remove(request)
        
        if request.passengers == 1:
            print('Picking up 1 passenger ', end='')
        else:
            print('Picking up {0} passengers '.format(request.passengers), end='')

        print('at {0}'.format(request.origin))
        print('Currently transporting {0} passengers'.format(self.current_passengers))
        print()

    def _drop_off(self, request):
        self.passengers.remove(request)
        self.total_rewards += request.reward

        print('Droping off {0} passengers at {1}'.format(
            request.passengers,
            request.destination))

        print('Reward: {0}'.format(request.reward))
        print()

    def _best_path(self, options):
        paths = Path([self.pos],
                     None,
                     self.current_passengers,
                     options).extend()
        min_cost = float('inf')
        extended = True

        while extended:
            extended = False
            for path in paths:
                if path.can_extend and path.cost <= min_cost:
                    extended = True
                    paths.remove(path)
                    paths += path.extend()
                    paths = sorted(paths, key=lambda path: path.cost)
                    min_cost = paths[0].cost
                    break

        return paths[0]

    def _simulate_paths(self, options, passengers):
        if not options:
            yield list()
        else:
            for i, option in enumerate(options):
                cur_options = options[:]
                cur_passengers = passengers
                if option.is_pickup:
                    if option.request.passengers + cur_passengers <= \
                       MAX_PASSENGERS:
                        cur_passengers += option.request.passengers
                        cur_options.append(Destination(option.request, False))
                    else:
                        continue
                else:
                    cur_passengers -= option.request.passengers
                other_opts = cur_options[:i] + cur_options[i+1:]
                for path in self._simulate_paths(other_opts, cur_passengers):
                    yield [option] + path

    def _calculate_reward(self, path):
        prev_dest = self.pos
        dist = 0
        reward = 0

        for next_dest in path:
            dist += prev_dest.dist(next_dest)
            prev_point = next_dest
            if next_dest.is_pickup:
                reward += next_dest.request.reward

        if dist != 0:
            return reward / dist
        else:
            return 0

class Request:
    def __init__(self, origin, destination, passengers):
        self.origin = origin
        self.destination = destination
        self.passengers = passengers

    def __repr__(self):
        return '<Request: ({0}, {1}) -> ({2}, {3})>'.format(
            self.origin.x,
            self.origin.y,
            self.destination.x,
            self.destination.y)

    @property
    def reward(self):
        return self.origin.dist(self.destination)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def dist(self, other):
        # Manhattan distance
        return abs(self.x - other.x) + abs(self.y - other.y)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '({0}, {1})'.format(self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Destination(Point):
    def __init__(self, request, is_pickup):
        if is_pickup:
            point = request.origin
        else:
            point = request.destination
            
        super().__init__(point.x, point.y)
        self.is_pickup = is_pickup
        self.request = request

    @property
    def passengers(self):
        return self.request.passengers

    def destination(self):
        if not self.is_pickup:
            raise TypeError('This PathNode is already a destination')

        return Destination(self.request, False)

class Path:
    def __init__(self,
                 path,
                 next_node,
                 passengers,
                 options,
                 prev_cost=0):
        # Can only be extended if there are options left
        self.can_extend = bool(options)
        self.options = options

        # The amount of passengers for this simulated run
        self.passengers = passengers

        # Path is the route so far, next_node is the next step in the route
        if next_node:
            path += [next_node]
            
        self._path = path
        
        if not next_node:
            self.cost = prev_cost
        else:
            self.cost = prev_cost + path[-1].dist(path[-2])

    def extend(self):
        new_paths = []
        for i, option in enumerate(self.options):
            cur_options = self.options[:]
            cur_passengers = self.passengers
            if option.is_pickup:
                if option.passengers + cur_passengers <= MAX_PASSENGERS:
                    cur_passengers += option.passengers
                    cur_options.append(option.destination())
                else:
                    continue
            else:
                cur_passengers -= option.passengers
                
            other_opts = cur_options[:i] + cur_options[i+1:]
            new_paths.append(Path(self._path[:],
                                  option,
                                  cur_passengers,
                                  other_opts,
                                  self.cost))
        return new_paths

    def to_list(self):
        return self._path[1:]

    def __repr__(self):
        return '%s' % self._path

    def __str__(self):
        return self.__repr__()


agent = Agent(Point(0,0))

for _ in range(200):
    if random.random() < 0.1 and len(agent.requests) <= 5:
        origin = Point(random.randint(0, 10), random.randint(0, 10))
        destination = Point(random.randint(0, 10), random.randint(0, 10))
        agent.perceive([Request(origin, destination, random.randint(1, 4))])

    agent.act()

print('Distance traversed: {0}'.format(agent.distance_traversed))
print('Total rewards: {0}'.format(agent.total_rewards))
