import pygame
import sys
import random
import math
import os
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Harvester Ant Algorithm Simulation")

# Define background colour as very light green-brown
background_color = (200, 200, 150)

class Entity:
    def __init__(self, x, y, image_path, scale):
        self.x = x
        self.y = y
        self.angle = 0  # New attribute for the rotation angle
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, scale)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def draw(self):
        rotated_image = pygame.transform.rotate(self.image, math.degrees(-self.angle))
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect.topleft)
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

    def move(self, speed):
        pass  # This will be implemented in the subclasses

class Food(Entity):
    def __init__(self, x, y):
        image_path = os.path.join("images", "seed.webp")
        super().__init__(x, y, image_path, (20, 20))
        # randomise angle
        self.angle = random.uniform(0, 2 * math.pi)

    def move(self):
        self.x = random.randint(0, width - self.rect.width)
        self.y = random.randint(0, height - self.rect.height)
        self.rect.center = (self.x, self.y)
        

class Ant(Entity):

    # add boolean attribute for if ant is retruning to nest
    returning_with_food = False 

    # add boolean attribute for if ant has left nest
    has_left_nest = False

    def __init__(self, x, y):
        image_path = os.path.join("images", "ant.png")    
        super().__init__(x, y, image_path, (30, 30))
        self.angle = random.uniform(0, 2 * math.pi)

    def move(self):
        speed = 2
        new_x = self.x + speed * math.cos(self.angle)
        new_y = self.y + speed * math.sin(self.angle)
        # vary angle slightly if ant is not returning to nest
        if not self.returning_with_food:
            self.vary_direction()

        if 0 <= new_x <= width - self.rect.width and 0 <= new_y <= height - self.rect.height:
            self.x = new_x
            self.y = new_y
            self.rect.center = (self.x, self.y)
        else:
            self.angle = random.uniform(0, 2 * math.pi)

    def vary_direction(self):
        # vary angle by a small amount
        self.angle += random.uniform(-0.1, 0.1)

    def return_to_nest(self, nest_x, nest_y):
        # set returning to nest to true
        self.returning_with_food = True
        # get angle between ant and nest
        home_x = nest_x - self.x
        home_y = nest_y - self.y
        angle_to_home = math.atan2(home_y, home_x)
        # change angle to be towards nest
        self.angle = angle_to_home


    def collect_food(self):
        # add food to image of ant with size 30x30
        self.image = pygame.image.load(os.path.join("images", "ant_with_food.png"))
        self.image = pygame.transform.scale(self.image, (30, 30))

class SimulationTracker:
    def __init__(self):
        self.arrivals_history = []
        self.foraging_ants_history = []
        self.alpha_history = []

        self.fig, self.axs = plt.subplots(3, 1)
        self.arrivals_line, = self.axs[0].plot([], [], label='Food Eaten')
        self.ants_line, = self.axs[1].plot([], [], label='Foraging Ants')
        self.alpha_line, = self.axs[2].plot([], [], label='Alpha')

        plt.ion()  # Turn on interactive mode

    def update(self, frame):
        if self.arrivals_history:
            self.arrivals_line.set_data(range(len(self.arrivals_history)), self.arrivals_history)
            self.ants_line.set_data(range(len(self.foraging_ants_history)), self.foraging_ants_history)
            self.alpha_line.set_data(range(len(self.alpha_history)), self.alpha_history)

            for ax in self.axs:
                ax.relim()
                ax.autoscale_view()

            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

            # add axes labels
            self.axs[0].set_ylabel('Arrivals')
            self.axs[1].set_ylabel('Foraging Ants')
            self.axs[2].set_ylabel('Alpha')

    def track_all(self, ants_returned_in_this_time_period, foraging_ants, alpha):
        if not self.arrivals_history:
            self.arrivals_history.append(ants_returned_in_this_time_period)
        else:
            self.arrivals_history.append(self.arrivals_history[-1] + ants_returned_in_this_time_period)

        # Update foraging ants and alpha histories
        self.foraging_ants_history.append(foraging_ants)
        self.alpha_history.append(alpha)

    def save_results_to_graphs(self):
        # Save results to graphs
        self.axs[0].set_title('Food Eaten')
        self.axs[1].set_title('Foraging Ants')
        self.axs[2].set_title('Alpha')

        self.axs[0].set_xlabel('Time Slots')
        self.axs[1].set_xlabel('Time Slots')
        self.axs[2].set_xlabel('Time Slots')

        self.axs[0].legend()
        self.axs[1].legend()
        self.axs[2].legend()

        self.fig.savefig('results.png')

# Main game loop
def main():
    plt.ion()

    # create nest object and draw it
    nest = Entity(width // 2, height // 2, os.path.join("images", "nest.webp"), (100, 100))
    nest.draw()

    # create list of ants
    ant_list = []
    # start with one ant in the middle of the screen
    ant = Ant(width // 2, height // 2)
    ant_list.append(ant)

    # Create 100 food objects
    food_list = []
    for i in range(100):
        # create food at origin
        food = Food(0, 0)
        # move food to random location until it is not colliding with other objects
        while food.rect.colliderect(nest.rect) or food.rect.collidelist(food_list) != -1 or food.rect.collidelist(ant_list) != -1 :
            # move food to random location
            food.move()
        food_list.append(food)

    simulation_tracker = SimulationTracker()

    clock = pygame.time.Clock()
    start_time = time.time()
    run_time_limit = 60  # seconds

    food_count = 0
    alpha = 0.01 # alpha 0
    departures = 0

    while time.time() - start_time < run_time_limit:
        screen.fill(background_color)

        arrivals = 0

        # check if ant has left nest yet
        for ant in ant_list:
            if ant.has_left_nest == False:
                # check if ant has left nest
                if not ant.rect.colliderect(nest.rect):
                    ant.has_left_nest = True

        for ant in ant_list:
            # check if ant has food and has returned to nest
            if ant.returning_with_food and ant.rect.colliderect(nest.rect):
                # remove this ant from the list   
                ant_list.remove(ant)
                arrivals += 1
            elif ant.has_left_nest and ant.rect.colliderect(nest.rect):
                # ant has hit nest but does not have food
                # delete ant but do not add to arrivals
                ant_list.remove(ant)
                
   

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # get number of ants to add using get_departures function
        # def get_departures(alpha_prev, departure_prev, arrivals, foraging_ants, c=0.602, q=0.05, d=0.01, alpha_0=0.03):
        # return alpha_n, D_n, foraging_ants

        alpha, departures, foraging_ants = get_departures(alpha, departures, arrivals, len(ant_list))
   
        # add new ants to ant list
        for i in range(departures):
            ant = Ant(width // 2, height // 2)
            ant_list.append(ant)


        # every 30 frames, add new ants
        # if pygame.time.get_ticks() % 30 == 0:
        #     # use poisson distrubution to determine number of ants to add based on amount of food eaten
        #     # get amount of food eaten in last 30 frames

        #     # print amount of food eaten in last 30 frames
        #     print("food count this time period: ", food_count)
        #     # use poisson distribution to determine number of ants to add
        #     rate_constant = 2  # Adjust this value based on your desired rate of ant additions
        #     num_ants_to_add = np.random.poisson(food_count * rate_constant, 1)
            
        #     # add a minimum of 1 ant
        #     if num_ants_to_add[0] == 0:
        #         num_ants_to_add[0] = 1
        #     # print number of ants to add
        #     print("number of ants to add: ", num_ants_to_add)
        #     # add new ants to ant list
        #     for i in range(num_ants_to_add[0]):
        #         ant = Ant(width // 2, height // 2)
        #         ant_list.append(ant)

        #     # reset food count
        #     food_count = 0

  


        # move and draw ants
        for ant in ant_list:
            ant.move()
            ant.draw()

        # draw food
        for food in food_list:
            food.draw()

        # draw nest
        nest.draw()

        for ant in ant_list:
            for food in food_list:
                if ant.rect.colliderect(food.rect) and ant.returning_with_food == False:
                    # might need to take account that an ant can hit multiple foods.
                    # print("Ant hits the food")
                    # delete food
                    food_list.remove(food)
                    # send ant back to nest
                    ant.return_to_nest(nest.x, nest.y)
                    ant.collect_food()

                    food_count += 1

        # def track_all(self, food_eaten_increment, foraging_ants, alpha):
        # update simulation tracker
        simulation_tracker.track_all(arrivals, len(ant_list), alpha)
        # update graph every 30 frames
        if pygame.time.get_ticks() % 30 == 0:
            simulation_tracker.update(0)

        pygame.display.flip()
        clock.tick(30)

    # Save results to graphs at the end of the simulation
    simulation_tracker.save_results_to_graphs()


# should see 0.15 to 1.2 ants per sec)
def get_departures(alpha_prev, departure_prev, arrivals, foraging_ants, c=0.602, q=0.2, d=0, alpha_0=0.01):
# def get_departures(alpha_prev, departure_prev, arrivals, foraging_ants, c=0.4, q=0.05, d=0.05, alpha_0=0.03):
    """
    Calculate the number of ants departing for foraging.
    alpha_prev: Previous rate of outgoing foragers
    departure_prev: Previous departure count
    arrivals: Number of ants arriving in the current time slot
    foraging_ants: Current number of ants out foraging
    Returns updated rate, departure count, and foraging ants count
    """
    alpha_n = max(alpha_prev - q * departure_prev + c * arrivals - d, alpha_0)
    D_n = np.random.poisson(alpha_n)
    foraging_ants += D_n
    return alpha_n, D_n, foraging_ants


# Run the simulation
if __name__ == "__main__":
    main()
