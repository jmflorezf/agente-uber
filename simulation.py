#!/usr/bin/env python3

"""
Description
"""


def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0
    

class Agent:
    def __init__(self, start_pos):
        self.destination = None
        self.passengers = list()
        self.pos = start_pos
        self.requests = list()

    def perceive(requests):
        if requests:
            self.requests += requests

    def act(self):
        # TODO: Add actual logic here
        if self.destination:
            if self.destination == self.pos:
                if destination.pickup:
                    self.passengers.append(destination.request)
                else:
                    self.passengers.remove(destination.request)
            else:
                # Move towards destination
                if destination.x != self.pos.x:
                    pos.x += sign(destination.x - self.pos.x)
                else:
                    pos.y += sign(destination.y - self.pos.y)
        else:
            self.destination = self.requests.pop(0)
