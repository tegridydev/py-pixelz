import numpy as np
import json
from particle import Particle

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = np.full((height, width), None, dtype=object)

    def add_particle(self, x, y, particle_type):
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.grid[y, x] is None:
                self.grid[y, x] = Particle(x, y, particle_type)

    def update(self):

        for y in range(self.height - 1, -1, -1):
            for x in range(self.width):
                if self.grid[y, x]:
                    self.grid[y, x].update(self.grid, self)

    def save(self, filename):
        data = [
            {
                'x': x, 'y': y, 'type': particle.type,
                'temperature': particle.temperature,
                'life': particle.life,
                'velocity': particle.velocity.tolist()
            }
            for y, row in enumerate(self.grid)
            for x, particle in enumerate(row)
            if particle is not None
        ]
        with open(filename, 'w') as f:
            json.dump(data, f)

    def load(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        self.grid = np.full((self.height, self.width), None, dtype=object)
        for item in data:
            particle = Particle(item['x'], item['y'], item['type'])
            particle.temperature = item['temperature']
            particle.life = item['life']
            particle.velocity = np.array(item['velocity'])
            self.grid[item['y'], item['x']] = particle
