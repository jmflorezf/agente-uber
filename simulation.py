#!/usr/bin/env python3

"""
Description
"""


import models
import random


agent = models.Agent(models.Point(0,0))

for _ in range(600):
    if random.random() < 0.1 and len(agent.requests) <= 30:
        origin = models.Point(random.randint(0, 50), random.randint(0, 50))
        destination = models.Point(random.randint(0, 50), random.randint(0, 50))
        agent.perceive([models.Request(origin, destination, random.randint(1, 4))])

    agent.act()

print('Distance traversed: {0}'.format(agent.distance_traversed))
print('Total rewards: {0}'.format(agent.total_rewards))
