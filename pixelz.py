import pygame
import numpy as np
import random
import json


WIDTH, HEIGHT = 800, 600
CELL_SIZE = 4
GRID_WIDTH, GRID_HEIGHT = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE


BLACK = (0, 0, 0)
SAND_COLOR = (194, 178, 128)
WATER_COLOR = (0, 119, 190)
ROCK_COLOR = (120, 120, 120)
FIRE_COLOR = (255, 69, 0)
SMOKE_COLOR = (105, 105, 105)
WOOD_COLOR = (139, 69, 19)
STEAM_COLOR = (220, 220, 220)
PLANT_COLOR = (0, 128, 0)
EXPLOSIVE_COLOR = (255, 0, 0)

class Particle:
    def __init__(self, x, y, particle_type):
        self.x = x
        self.y = y
        self.type = particle_type
        self.life = 100 if particle_type in ['fire', 'explosive'] else -1
        self.temperature = 20  # Room temperature in Celsius

    def update(self, grid, world):
        if self.type == 'sand':
            self.update_sand(grid)
        elif self.type == 'water':
            self.update_water(grid, world)
        elif self.type == 'fire':
            self.update_fire(grid, world)
        elif self.type == 'smoke':
            self.update_smoke(grid)
        elif self.type == 'steam':
            self.update_steam(grid, world)
        elif self.type == 'plant':
            self.update_plant(grid, world)
        elif self.type == 'explosive':
            self.update_explosive(grid, world)


        self.apply_temperature_effects(grid, world)

    def update_sand(self, grid):
        if self.y + 1 < GRID_HEIGHT:
            if grid[self.y + 1][self.x] is None:
                grid[self.y][self.x], grid[self.y + 1][self.x] = None, self
                self.y += 1
            elif grid[self.y + 1][self.x].type in ['water', 'steam']:
                grid[self.y][self.x], grid[self.y + 1][self.x] = grid[self.y + 1][self.x], self
                self.y += 1
            elif self.x > 0 and grid[self.y + 1][self.x - 1] is None:
                grid[self.y][self.x], grid[self.y + 1][self.x - 1] = None, self
                self.y += 1
                self.x -= 1
            elif self.x + 1 < GRID_WIDTH and grid[self.y + 1][self.x + 1] is None:
                grid[self.y][self.x], grid[self.y + 1][self.x + 1] = None, self
                self.y += 1
                self.x += 1

    def update_water(self, grid, world):
        if self.temperature >= 100:
            grid[self.y][self.x] = Particle(self.x, self.y, 'steam')
            return

        if self.y + 1 < GRID_HEIGHT:
            if grid[self.y + 1][self.x] is None:
                grid[self.y][self.x], grid[self.y + 1][self.x] = None, self
                self.y += 1
            elif self.x > 0 and grid[self.y][self.x - 1] is None:
                grid[self.y][self.x], grid[self.y][self.x - 1] = None, self
                self.x -= 1
            elif self.x + 1 < GRID_WIDTH and grid[self.y][self.x + 1] is None:
                grid[self.y][self.x], grid[self.y][self.x + 1] = None, self
                self.x += 1

    def update_fire(self, grid, world):
        self.life -= 1
        if self.life <= 0:
            grid[self.y][self.x] = Particle(self.x, self.y, 'smoke')
            return

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    if grid[ny][nx]:
                        if grid[ny][nx].type == 'wood':
                            grid[ny][nx] = Particle(nx, ny, 'fire')
                        elif grid[ny][nx].type == 'water':
                            self.life = 0
                            grid[self.y][self.x] = Particle(self.x, self.y, 'steam')
                            return
                        elif grid[ny][nx].type == 'plant':
                            grid[ny][nx] = Particle(nx, ny, 'fire')
                        elif grid[ny][nx].type == 'explosive':
                            grid[ny][nx].life = 0  # Trigger explosion

        if random.random() < 0.1:
            if self.y > 0 and grid[self.y - 1][self.x] is None:
                grid[self.y - 1][self.x] = Particle(self.x, self.y - 1, 'smoke')

    def update_smoke(self, grid):
        if self.y > 0 and random.random() < 0.8:
            if grid[self.y - 1][self.x] is None:
                grid[self.y][self.x], grid[self.y - 1][self.x] = None, self
                self.y -= 1
            elif self.x > 0 and grid[self.y - 1][self.x - 1] is None:
                grid[self.y][self.x], grid[self.y - 1][self.x - 1] = None, self
                self.y -= 1
                self.x -= 1
            elif self.x + 1 < GRID_WIDTH and grid[self.y - 1][self.x + 1] is None:
                grid[self.y][self.x], grid[self.y - 1][self.x + 1] = None, self
                self.y -= 1
                self.x += 1
        elif random.random() < 0.05:
            grid[self.y][self.x] = None

    def update_steam(self, grid, world):
        if self.temperature < 100:
            grid[self.y][self.x] = Particle(self.x, self.y, 'water')
            return

        if self.y > 0 and random.random() < 0.8:
            if grid[self.y - 1][self.x] is None:
                grid[self.y][self.x], grid[self.y - 1][self.x] = None, self
                self.y -= 1
            elif self.x > 0 and grid[self.y - 1][self.x - 1] is None:
                grid[self.y][self.x], grid[self.y - 1][self.x - 1] = None, self
                self.y -= 1
                self.x -= 1
            elif self.x + 1 < GRID_WIDTH and grid[self.y - 1][self.x + 1] is None:
                grid[self.y][self.x], grid[self.y - 1][self.x + 1] = None, self
                self.y -= 1
                self.x += 1
        elif random.random() < 0.05:
            grid[self.y][self.x] = None

    def update_plant(self, grid, world):
        if random.random() < 0.01:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = self.x + dx, self.y + dy
                    if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                        if grid[ny][nx] is None and random.random() < 0.2:
                            grid[ny][nx] = Particle(nx, ny, 'plant')

    def update_explosive(self, grid, world):
        self.life -= 1
        if self.life <= 0:
            self.explode(grid, world)

    def explode(self, grid, world):
        radius = 5
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx*dx + dy*dy <= radius*radius:
                    nx, ny = self.x + dx, self.y + dy
                    if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                        if grid[ny][nx] is None or grid[ny][nx].type != 'rock':
                            grid[ny][nx] = Particle(nx, ny, 'fire')

    def apply_temperature_effects(self, grid, world):

        total_temp = self.temperature
        count = 1
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and grid[ny][nx]:
                    total_temp += grid[ny][nx].temperature
                    count += 1
        self.temperature = total_temp / count


        if self.type == 'water' and self.temperature >= 100:
            grid[self.y][self.x] = Particle(self.x, self.y, 'steam')
        elif self.type == 'steam' and self.temperature < 100:
            grid[self.y][self.x] = Particle(self.x, self.y, 'water')

class World:
    def __init__(self):
        self.grid = np.full((GRID_HEIGHT, GRID_WIDTH), None, dtype=object)

    def add_particle(self, x, y, particle_type):
        grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            if self.grid[grid_y][grid_x] is None:
                self.grid[grid_y][grid_x] = Particle(grid_x, grid_y, particle_type)

    def update(self):
        for y in range(GRID_HEIGHT - 1, -1, -1):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    self.grid[y][x].update(self.grid, self)

    def draw(self, screen):
        particle_surface = pygame.Surface((WIDTH, HEIGHT))
        particle_surface.fill(BLACK)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    color = self.get_particle_color(self.grid[y][x])
                    pygame.draw.rect(particle_surface, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        screen.blit(particle_surface, (0, 0))

    def get_particle_color(self, particle):
        if particle.type == 'sand':
            return SAND_COLOR
        elif particle.type == 'water':
            return WATER_COLOR
        elif particle.type == 'rock':
            return ROCK_COLOR
        elif particle.type == 'fire':
            return FIRE_COLOR
        elif particle.type == 'smoke':
            return SMOKE_COLOR
        elif particle.type == 'wood':
            return WOOD_COLOR
        elif particle.type == 'steam':
            return STEAM_COLOR
        elif particle.type == 'plant':
            return PLANT_COLOR
        elif particle.type == 'explosive':
            return EXPLOSIVE_COLOR
        else:
            return BLACK

    def save(self, filename):
        data = []
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    data.append({
                        'x': x,
                        'y': y,
                        'type': self.grid[y][x].type,
                        'temperature': self.grid[y][x].temperature,
                        'life': self.grid[y][x].life
                    })
        with open(filename, 'w') as f:
            json.dump(data, f)

    def load(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        self.grid = np.full((GRID_HEIGHT, GRID_WIDTH), None, dtype=object)
        for item in data:
            particle = Particle(item['x'], item['y'], item['type'])
            particle.temperature = item['temperature']
            particle.life = item['life']
            self.grid[item['y']][item['x']] = particle

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.Font(None, 24)
        text = font.render(self.text, True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    world = World()

    current_type = 'sand'
    brush_size = 3
    eraser_mode = False

    font = pygame.font.Font(None, 36)


    buttons = [
        Button(10, HEIGHT - 40, 80, 30, "Sand", SAND_COLOR),
        Button(100, HEIGHT - 40, 80, 30, "Water", WATER_COLOR),
        Button(190, HEIGHT - 40, 80, 30, "Rock", ROCK_COLOR),
        Button(280, HEIGHT - 40, 80, 30, "Fire", FIRE_COLOR),
        Button(370, HEIGHT - 40, 80, 30, "Wood", WOOD_COLOR),
        Button(460, HEIGHT - 40, 80, 30, "Plant", PLANT_COLOR),
        Button(550, HEIGHT - 40, 80, 30, "Explosive", EXPLOSIVE_COLOR),
        Button(640, HEIGHT - 40, 80, 30, "Erase", (150, 150, 150)),
    ]


    save_button = Button(10, 10, 80, 30, "Save", (0, 255, 0))
    load_button = Button(100, 10, 80, 30, "Load", (0, 0, 255))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    brush_size = min(10, brush_size + 1)
                elif event.button == 5:
                    brush_size = max(1, brush_size - 1)
                elif event.button == 1:
                    pos = pygame.mouse.get_pos()
                    for button in buttons:
                        if button.is_clicked(pos):
                            if button.text == "Erase":
                                eraser_mode = not eraser_mode
                            else:
                                current_type = button.text.lower()
                                eraser_mode = False
                    if save_button.is_clicked(pos):
                        world.save("sandbox_save.json")
                    elif load_button.is_clicked(pos):
                        world.load("sandbox_save.json")

        if pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            for dx in range(-brush_size, brush_size + 1):
                for dy in range(-brush_size, brush_size + 1):
                    if dx*dx + dy*dy <= brush_size*brush_size:
                        if eraser_mode:
                            grid_x, grid_y = (x + dx*CELL_SIZE) // CELL_SIZE, (y + dy*CELL_SIZE) // CELL_SIZE
                            if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                                world.grid[grid_y][grid_x] = None
                        else:
                            world.add_particle(x + dx*CELL_SIZE, y + dy*CELL_SIZE, current_type)

        world.update()

        screen.fill(BLACK)
        world.draw(screen)

        # UI
        for button in buttons:
            button.draw(screen)
        save_button.draw(screen)
        load_button.draw(screen)

        text = font.render(f"Type: {current_type.capitalize()}", True, (255, 255, 255))
        screen.blit(text, (200, 10))
        text = font.render(f"Brush Size: {brush_size}", True, (255, 255, 255))
        screen.blit(text, (400, 10))
        if eraser_mode:
            text = font.render("Eraser Mode", True, (255, 0, 0))
            screen.blit(text, (600, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
