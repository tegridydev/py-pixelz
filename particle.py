import random
import numpy as np

class Particle:
    def __init__(self, x, y, particle_type):
        self.x = x
        self.y = y
        self.type = particle_type
        self.life = 100 if particle_type in ['fire', 'explosive'] else -1
        self.temperature = 20  # celisuz
        self.velocity = np.array([0.0, 0.0])  # [vx, vy]

    def update(self, grid, world):
        update_method = getattr(self, f"update_{self.type}", None)
        if update_method:
            update_method(grid, world)
        self.apply_temperature_effects(grid, world)

    def update_sand(self, grid, world):
        if self.y + 1 < world.height:
            if grid[self.y + 1, self.x] is None:
                grid[self.y, self.x], grid[self.y + 1, self.x] = None, self
                self.y += 1
            elif grid[self.y + 1, self.x].type in ['water', 'steam']:
                grid[self.y, self.x], grid[self.y + 1, self.x] = grid[self.y + 1, self.x], self
                self.y += 1
            else:
                for dx in [-1, 1]:
                    if 0 <= self.x + dx < world.width and grid[self.y + 1, self.x + dx] is None:
                        grid[self.y, self.x], grid[self.y + 1, self.x + dx] = None, self
                        self.y += 1
                        self.x += dx
                        break

    def update_water(self, grid, world):
        if self.temperature >= 100:
            grid[self.y, self.x] = Particle(self.x, self.y, 'steam')
            return


        self.velocity[1] += 0.1
        new_y = int(self.y + self.velocity[1])


        if new_y < world.height and grid[new_y, self.x] is None:
            grid[self.y, self.x], grid[new_y, self.x] = None, self
            self.y = new_y
        else:

            diag_dirs = [(-1, 1), (1, 1)]
            random.shuffle(diag_dirs)
            moved = False
            for dx, dy in diag_dirs:
                new_x, new_y = self.x + dx, self.y + dy
                if 0 <= new_x < world.width and new_y < world.height and grid[new_y, new_x] is None:
                    grid[self.y, self.x], grid[new_y, new_x] = None, self
                    self.x, self.y = new_x, new_y
                    moved = True
                    break

            if not moved:

                horizontal_dirs = [-1, 1]
                random.shuffle(horizontal_dirs)
                for dx in horizontal_dirs:
                    new_x = self.x + dx
                    if 0 <= new_x < world.width and grid[self.y, new_x] is None:
                        grid[self.y, self.x], grid[self.y, new_x] = None, self
                        self.x = new_x
                        break


                self.velocity[1] = 0


        self.velocity *= 0.9

    def update_fire(self, grid, world):
        self.life -= 1
        if self.life <= 0:
            grid[self.y, self.x] = Particle(self.x, self.y, 'smoke')
            return

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < world.width and 0 <= ny < world.height:
                if grid[ny, nx]:
                    if grid[ny, nx].type == 'wood':
                        grid[ny, nx] = Particle(nx, ny, 'fire')
                    elif grid[ny, nx].type == 'water':
                        self.life = 0
                        grid[self.y, self.x] = Particle(self.x, self.y, 'steam')
                        return

        if random.random() < 0.1 and self.y > 0 and grid[self.y - 1, self.x] is None:
            grid[self.y - 1, self.x] = Particle(self.x, self.y - 1, 'smoke')

    def update_smoke(self, grid, world):
        if self.y > 0 and random.random() < 0.8:
            directions = [(0, -1), (-1, -1), (1, -1)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < world.width and grid[ny, nx] is None:
                    grid[self.y, self.x], grid[ny, nx] = None, self
                    self.x, self.y = nx, ny
                    return
        elif random.random() < 0.05:
            grid[self.y, self.x] = None

    def update_steam(self, grid, world):
        if self.temperature < 100:
            grid[self.y, self.x] = Particle(self.x, self.y, 'water')
            return

        if self.y > 0 and random.random() < 0.8:
            directions = [(0, -1), (-1, -1), (1, -1)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < world.width and grid[ny, nx] is None:
                    grid[self.y, self.x], grid[ny, nx] = None, self
                    self.x, self.y = nx, ny
                    return
        elif random.random() < 0.05:
            grid[self.y, self.x] = None

    def update_plant(self, grid, world):
        if random.random() < 0.01:  # grow
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < world.width and 0 <= ny < world.height:
                    if grid[ny, nx] is None and random.random() < 0.2:
                        grid[ny, nx] = Particle(nx, ny, 'plant')
                        break

    def update_explosive(self, grid, world):
        self.life -= 1
        if self.life <= 0:
            self.explode(grid, world)

    def explode(self, grid, world):
        radius = 5
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx*dx + dy*dy <= radius*radius:
                    nx, ny = self.x + dx, self.y + dy
                    if 0 <= nx < world.width and 0 <= ny < world.height:
                        if grid[ny, nx] is None or grid[ny, nx].type != 'rock':
                            grid[ny, nx] = Particle(nx, ny, 'fire')

    def apply_temperature_effects(self, grid, world):
        neighbors = [
            grid[y, x] for y in range(max(0, self.y - 1), min(world.height, self.y + 2))
            for x in range(max(0, self.x - 1), min(world.width, self.x + 2))
            if grid[y, x] is not None
        ]
        if neighbors:
            self.temperature = (self.temperature + sum(n.temperature for n in neighbors)) / (len(neighbors) + 1)

        if self.type == 'water' and self.temperature >= 100:
            grid[self.y, self.x] = Particle(self.x, self.y, 'steam')
        elif self.type == 'steam' and self.temperature < 100:
            grid[self.y, self.x] = Particle(self.x, self.y, 'water')
