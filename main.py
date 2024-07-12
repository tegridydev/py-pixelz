import pygame
import sys
import numpy as np
from world import World


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

def get_particle_color(particle):
    color_map = {
        'sand': SAND_COLOR,
        'water': WATER_COLOR,
        'rock': ROCK_COLOR,
        'fire': FIRE_COLOR,
        'smoke': SMOKE_COLOR,
        'wood': WOOD_COLOR,
        'steam': STEAM_COLOR,
        'plant': PLANT_COLOR,
        'explosive': EXPLOSIVE_COLOR
    }
    return color_map.get(particle.type, BLACK)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    world = World(GRID_WIDTH, GRID_HEIGHT)

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

    particle_surface = pygame.Surface((WIDTH, HEIGHT))

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
                        grid_x, grid_y = (x + dx*CELL_SIZE) // CELL_SIZE, (y + dy*CELL_SIZE) // CELL_SIZE
                        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                            if eraser_mode:
                                world.grid[grid_y, grid_x] = None
                            else:
                                world.add_particle(grid_x, grid_y, current_type)

        world.update()

        particle_surface.fill(BLACK)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if world.grid[y, x]:
                    color = get_particle_color(world.grid[y, x])
                    pygame.draw.rect(particle_surface, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        screen.blit(particle_surface, (0, 0))

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
    sys.exit()

if __name__ == "__main__":
    main()
