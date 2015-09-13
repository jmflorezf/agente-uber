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
        self.destination = None
        self.passengers = list()
        self.pos = start_pos
        self.requests = list()
        self.total_rewards = 0
        self.distance_traversed = 0

        print('Agent beginning at {0}'.format(start_pos))
        print()

    def perceive(self, requests):
        if requests:
            self.requests += requests

    def act(self):
        # TODO: Add actual logic here
        if self.destination:
            dest = self.destination
            if dest == self.pos:
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
            self.destination = Destination(self.requests.pop(0), True)

    @property
    def current_passengers(self):
        total = 0
        for request in self.passengers:
            total += request.passengers

        return total

    def _pick_up(self, request):
        self.passengers.append(request)
        self.destination = Destination(request, False)
        
        if request.passengers == 1:
            print('Picking up 1 passenger ', end='')
        else:
            print('Picking up {0} passengers '.format(request.passengers), end='')

        print('at {0}'.format(request.origin))
        print('Currently transporting {0} passengers'.format(self.current_passengers))
        print()

    def _drop_off(self, request):
        self.passengers.remove(request)
        self.destination = None
        self.total_rewards += request.reward

        print('Droping off {0} passengers at {1}'.format(
            request.passengers,
            request.destination))

        print('Reward: {0}'.format(request.reward))
        print()

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
        # Manhattan distance
        return abs(self.origin.x - self.destination.x) + \
               abs(self.origin.y - self.destination.y)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

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


agent = Agent(Point(0,0))

for _ in range(100):
    if not agent.requests:
        origin = Point(random.randint(0, 10), random.randint(0, 10))
        destination = Point(random.randint(0, 10), random.randint(0, 10))
        agent.perceive([Request(origin, destination, random.randint(1, 4))])

    agent.act()

print('Distance traversed: {0}'.format(agent.distance_traversed))
print('Total rewards: {0}'.format(agent.total_rewards))
