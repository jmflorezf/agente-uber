#!/usr/bin/env python3

"""
Description
"""


MAX_PASSENGERS = 4


def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0
    

class Agent:
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
            self.requests += requests

            self.destinations = self._best_path()
                
    def act(self):
        if not self.destinations:
            if self.passengers:
                self.destinations = self._best_path()
            elif self.requests:
                nearest_request = min(self.requests,
                                         key=lambda x:
                                             x.origin.dist(self.pos))
                self.destinations = [Destination(nearest_request, True)]
                
        if self.destinations:
            dest = self.destinations[0]
            if dest == self.pos:
                self.destinations.pop(0)
                
                if dest.is_pickup:
                    self._pick_up(dest.request)
                else:
                    self._drop_off(dest.request)

                self.destinations = self._best_path()
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
        if self.current_passengers + request.passengers > MAX_PASSENGERS:
            raise Exception('Tried to pick up more passengers than allowed')
            
        self.passengers.append(request)
        self.requests.remove(request)
        
        if request.passengers == 1:
            print('Picking up 1 passenger ', end='')
        else:
            print('Picking up {0} passengers '.format(request.passengers), end='')

        print('at {0}'.format(request.origin))
        print('Currently transporting {0} passengers'
              .format(self.current_passengers))
        print()

    def _drop_off(self, request):
        self.passengers.remove(request)
        self.total_rewards += request.reward

        print('Droping off {0} passengers at {1}'.format(
            request.passengers,
            request.destination))

        print('Currently transporting {0} passengers'
              .format(self.current_passengers))
        print('Reward: {0}'.format(request.reward))
        print()

    def _best_path(self):
        destinations = [Destination(r, False)
                                 for r in sorted(self.passengers,
                                     key=lambda x:
                                         x.destination.dist(self.pos))]
        
        if not self.passengers:
            return []

        if not self.requests or self.current_passengers == MAX_PASSENGERS:
            return destinations

        options = [r
                   for r in self.requests
                   if r.passengers + self.current_passengers <= MAX_PASSENGERS]

        if not options:
            return destinations
        
        print('Calculating best path...')
        print()

        pos = self.pos
        passengers = self.passengers

        # Determine destination rectangle
        current_set = [r.destination for r in passengers] + [pos]
        dest_rect = Rectangle(current_set)

        def delta(request):
            rect = Rectangle([pos, request.origin, request.destination])
            d = rect.delta(dest_rect)

            return d

        # Order options by delta
        ordered_opts = sorted([(delta(o), o) for o in options],
                              key=lambda x: x[0])

        s_passengers = self.current_passengers

        for d, option in ordered_opts:
            if s_passengers == MAX_PASSENGERS:
                break
            
            if d <= option.reward and \
                   s_passengers + option.passengers <= MAX_PASSENGERS:
                destinations.append(Destination(option, True))
                s_passengers += option.passengers

        destinations = sorted(destinations, key=lambda d: d.dist(self.pos))

        print('Best path determined:', destinations)
        print()
        
        return destinations

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

class Rectangle:
    def __init__(self, points):
        if points:
            self.min_x = min(points, key=lambda p: p.x).x
            self.max_x = max(points, key=lambda p: p.x).x
            self.min_y = min(points, key=lambda p: p.y).y
            self.max_y = max(points, key=lambda p: p.y).y

    def delta(self, other):
        xd = 0
        yd = 0
        if self.min_x < other.min_x:
            xd += abs(self.min_x - other.min_x)
        if self.max_x > other.max_x:
            xd += abs(self.max_x - other.max_x)
        if self.min_y < other.min_y:
            yd += abs(self.min_y - other.min_y)
        if self.max_y > other.max_y:
            yd += abs(self.max_y - other.max_y)

        return 2 * xd + 2 * yd

    def __repr__(self):
        return '<Rect: (%d, %d, %d, %d)>' % (self.min_x,
                                             self.max_x,
                                             self.min_y,
                                             self.max_y)
