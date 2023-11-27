import pygame
import sys
import random
import math
import os
import time
import matplotlib.pyplot as plt

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Harvester Ant Algorithm Simulation")

# Define colors
white = (255, 255, 255)

class Entity:
    def __init__(self, x, y, image_path, scale):
        self.x = x
        self.y = y
        self.angle = 0  # New attribute for the rotation angle
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, scale)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def draw(self):
        rotated_image = pygame.transform.rotate(self.image, math.degrees(self.angle))
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect.topleft)
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

    def move(self, speed):
        pass  # This will be implemented in the subclasses

class Food(Entity):
    def __init__(self, x, y):
        image_path = os.path.join("images", "food.png")
        super().__init__(x, y, image_path, (100, 100))

    def move(self):
        self.x = random.randint(0, width - self.rect.width)
        self.y = random.randint(0, height - self.rect.height)
        self.rect.center = (self.x, self.y)

class Ant(Entity):
    def __init__(self, x, y):
        image_path = os.path.join("images", "ant.png")
        super().__init__(x, y, image_path, (30, 30))
        self.angle = random.uniform(0, 2 * math.pi)

    def move(self):
        speed = 15
        new_x = self.x + speed * math.cos(self.angle)
        new_y = self.y + speed * math.sin(self.angle)

        if 0 <= new_x <= width - self.rect.width and 0 <= new_y <= height - self.rect.height:
            self.x = new_x
            self.y = new_y
            self.rect.center = (self.x, self.y)
        else:
            self.angle = random.uniform(0, 2 * math.pi)

class SimulationTracker:
    def __init__(self):
        self.food_eaten_history = []

    def track_food_eaten(self, food_count):
        if not self.food_eaten_history:
            self.food_eaten_history.append(food_count)
        else:
            self.food_eaten_history.append(self.food_eaten_history[-1] + food_count)

    def save_results_to_graphs(self):
        time_points = list(range(1, len(self.food_eaten_history) + 1))
        plt.plot(time_points, self.food_eaten_history, marker='o', linestyle='-', color='b')
        plt.title('Cumulative Food Eaten Over Time')
        plt.xlabel('Time')
        plt.ylabel('Cumulative Food Eaten')
        plt.grid(True)
        plt.savefig('cumulative_food_eaten_graph.png')
        plt.show()

# Main game loop
def main():

    




    ant = Ant(width // 2, height // 2)
    food = Food(100, 100)
    simulation_tracker = SimulationTracker()

    clock = pygame.time.Clock()
    start_time = time.time()
    run_time_limit = 10  # seconds

    while time.time() - start_time < run_time_limit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(white)

        ant.move()
        ant.draw()

        food.draw()

        if ant.rect.colliderect(food.rect):
            print("Ant hits the food")
            food.move()
            simulation_tracker.track_food_eaten(1)

        pygame.display.flip()

        clock.tick(30)

    # Save results to graphs at the end of the simulation
    simulation_tracker.save_results_to_graphs()

# Run the simulation
if __name__ == "__main__":
    main()
