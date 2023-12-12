import pygame
import sys
import random
import math
import os
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

TESTMODE = True

run_time_limit = 600  # seconds

# Initialize Pygame
pygame.init()

# define timestep
timestep = 1/20 # each frame is defined as 1/20 of a second

# define food cadence
food_cadence = 250 # frequency with which food is dropped in seconds
first_food_drop = 50 # time at which first food is dropped
food_drop_amount = 50 # 50 food is added each time

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
        speed = 1
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

    food_available = 0

    def __init__(self):
        # Initialize histories for tracking simulation variables
        self.arrivals_history = []  # Track cumulative number of ants that have returned
        self.departures_history = []  # Track cumulative number of ants that have departed
        self.foraging_ants_history = []  # Track number of ants currently foraging
        self.alpha_history = []  # Track the alpha values over time
        self.food_available_history = []  # Track the food available over time

        # Set up matplotlib subplots for each variable
        self.fig, self.axs = plt.subplots(4, 1)
        self.arrivals_line, = self.axs[0].plot([], [], label='Arrivals')
        self.departures_line, = self.axs[0].plot([], [], label='Departures')
        self.ants_line, = self.axs[1].plot([], [], label='Foraging Ants')
        self.alpha_line, = self.axs[2].plot([], [], label='Alpha')
        self.food_available_line, = self.axs[3].plot([], [], label='Food Available')

        # add x axis labels
        self.axs[0].set_xlabel('Time (s)')
        self.axs[1].set_xlabel('Time (s)')
        self.axs[2].set_xlabel('Time (s)')
        self.axs[3].set_xlabel('Time (s))')

        # set window size
        self.fig.set_size_inches(12, 8)
        # add space between subplots
        self.fig.subplots_adjust(hspace=0.5)


        plt.ion()  # Interactive mode for live updates

    def update(self, frame):
        # Update each line in the plot with new data
        if self.arrivals_history:
            # Set data for each plot line, scaling the x-axis to time in seconds
            self.arrivals_line.set_data(np.arange(len(self.arrivals_history)) * timestep, self.arrivals_history)
            self.departures_line.set_data(np.arange(len(self.departures_history)) * timestep, self.departures_history)
            self.ants_line.set_data(np.arange(len(self.foraging_ants_history)) * timestep, self.foraging_ants_history)
            self.alpha_line.set_data(np.arange(len(self.alpha_history)) * timestep, self.alpha_history)
            self.food_available_line.set_data(np.arange(len(self.food_available_history)) * timestep, self.food_available_history)

            # Adjust axes limits dynamically and refresh the plot
            for ax in self.axs:
                ax.relim()
                ax.autoscale_view()

            # Redraw and flush events for interactive update
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

            # Set labels for each subplot
            self.axs[0].set_ylabel('Arrivals/Departures')
            # add legend
            self.axs[0].legend()
            self.axs[1].set_ylabel('Foraging Ants')
            self.axs[2].set_ylabel('Alpha')
            self.axs[3].set_ylabel('Food Available')

    def track_all(self, arrivals, departures, foraging_ants, alpha):
        # Track all simulation variables in their respective histories
        # Increment arrivals and departures history cumulatively
        if not self.arrivals_history:
            self.arrivals_history.append(arrivals)
        else:
            self.arrivals_history.append(self.arrivals_history[-1] + arrivals)
        if not self.departures_history:
            self.departures_history.append(departures)
        else:
            self.departures_history.append(self.departures_history[-1] + departures)

        # Update foraging ants and alpha histories with current values
        self.foraging_ants_history.append(foraging_ants)
        self.alpha_history.append(alpha)
        self.food_available_history.append(self.food_available)

    def add_food(self, amount):
        self.food_available += amount

    def remove_food(self, amount):
        self.food_available -= amount

    def save_results_to_graphs(self):

        # Save the final plot to a file named after the food cadence
        self.fig.savefig(f'results_{food_cadence}.png')

# add food
def add_food(food_list, num_food, nest, ant_list, simulation_tracker):
    for i in range(num_food):
        # create food at origin
        food = Food(0, 0)
        # move food to random location until it is not colliding with other objects
        while food.rect.colliderect(nest.rect) or food.rect.collidelist(food_list) != -1 or food.rect.collidelist(ant_list) != -1 :
            # move food to random location
            food.move()
        food_list.append(food)
    simulation_tracker.add_food(len(food_list))

# Main game loop
def main():

    # track total distance travelled by ants as a measure of efficiency
    total_distance_travelled = 0

    global TESTMODE
    frame_count = 0

    plt.ion()
    simulation_tracker = SimulationTracker()

    # create nest object and draw it
    nest = Entity(width // 2, height // 2, os.path.join("images", "nest.webp"), (100, 100))

    # create list of ants
    ant_list = []
    # start with one ant in the middle of the screen
    ant = Ant(width // 2, height // 2)
    ant_list.append(ant)

    # create list of food
    food_list = []

    clock = pygame.time.Clock()

    food_count = 0
    alpha = 0.01 # alpha 0
    departures = 0

    while frame_count*timestep < run_time_limit:
        frame_count += 1

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
                simulation_tracker.remove_food(1)
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
        alpha, departures, foraging_ants = get_departures(alpha, departures, arrivals, len(ant_list))
   
        # add new ants to ant list
        for i in range(departures):
            ant = Ant(width // 2, height // 2)
            ant_list.append(ant)
  
        # move and draw ants
        for ant in ant_list:
            ant.move()
            # add distance travelled by ant to total distance travelled
            total_distance_travelled += 2


        if not TESTMODE:

            screen.fill(background_color)

            for ant in ant_list:
                ant.draw()

            for food in food_list:
                food.draw()

            nest.draw()


                
            # clock.tick(20)

            pygame.display.flip()
        
        # update graph every 5 seconds
        if frame_count % 100 == 0:
            simulation_tracker.update(0)

        for ant in ant_list:
            for food in food_list:
                if ant.rect.colliderect(food.rect) and ant.returning_with_food == False:
                    # delete food
                    food_list.remove(food)
                    # send ant back to nest
                    ant.return_to_nest(nest.x, nest.y)
                    ant.collect_food()
                    food_count += 1
                    # move on to the next ant (since an ant can hit multiple foods)
                    break

        # def track_all(self, food_eaten_increment, foraging_ants, alpha):
        # update simulation tracker
        simulation_tracker.track_all(arrivals, departures, len(ant_list), alpha)

        if (frame_count-first_food_drop/timestep) % (food_cadence/timestep) == 0:
            add_food(food_list, food_drop_amount, nest, ant_list, simulation_tracker)


    # Save results to graphs at the end of the simulation
    simulation_tracker.save_results_to_graphs()

    print(f"Total distance travelled by ants: {total_distance_travelled}")


# should see 0.15 to 1.2 ants per sec)
# def get_departures(alpha_prev, departure_prev, arrivals, foraging_ants, c=0.602, q=0.2, d=0, alpha_0=0.01):
def get_departures(alpha_prev, departure_prev, arrivals, foraging_ants, c=0.6, q=0.2, d=0.05, alpha_0=0.01):
    """
    Calculate the number of ants departing for foraging.
    alpha_prev: Previous rate of outgoing foragers
    departure_prev: Previous departure count
    arrivals: Number of ants arriving in the current time slot
    foraging_ants: Current number of ants out foraging
    Returns updated rate, departure count, and foraging ants count
    """
    alpha_n = max(alpha_prev - q * departure_prev + c * arrivals - d, alpha_0)
    alpha_n=  0.05
    D_n = np.random.poisson(alpha_n)
    foraging_ants += D_n
    return alpha_n, D_n, foraging_ants


# Run the simulation
if __name__ == "__main__":
    main()
