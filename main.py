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

# Initialize Pygame
pygame.init()

# define timestep
timestep = 1/20 # each frame is defined as 1/20 of a second

# define food cadence
food_cadence = 2000 # frequency with which food is dropped in seconds
first_food_drop = 250 # time at which first food is dropped
food_drop_amount = 20 # food added each time

run_time_limit = 2000

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

    def __init__(self, c):

        self.c = c
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

        # Save the final plot to results folder as a file named after the c value
        self.fig.savefig(os.path.join("results", f"simulation_results_c={self.c}.png"))

# add food
def spawn_food(food_list, num_food, nest, ant_list, simulation_tracker):
    for i in range(num_food):
        # create food at origin
        food = Food(0, 0)
        # move food to random location until it is not colliding with other objects
        while food.rect.colliderect(nest.rect) or food.rect.collidelist(food_list) != -1 or food.rect.collidelist(ant_list) != -1 :
            # move food to random location
            food.move()
        food_list.append(food)
    simulation_tracker.add_food(num_food)

# Main game loop
def main(c=0.602, q=0.05, d=0, alpha_min=0.01, visible=True):

    # track total distance travelled by ants as a measure of efficiency
    total_distance_travelled = 0
    # track maximum number of active foragers
    max_foragers = 0
    # track average time taken to collect all food
    time_taken_list = []

    global TESTMODE
    frame_count = 0

    plt.ion()
    simulation_tracker = SimulationTracker(c)

    # create nest object and draw it
    nest = Entity(width // 2, height // 2, os.path.join("images", "nest.webp"), (100, 100))

    # create list of ants
    ant_list = []

    # create list of food
    food_list = []

    clock = pygame.time.Clock()

    alpha = 0 # alpha 0
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
                if simulation_tracker.food_available == 0:
                    # print time taken to collect all food
                    time_taken = frame_count*timestep - food_added_time
                    # print(f"Time taken to collect all food: {time_taken}")
                    time_taken_list.append(time_taken)
            elif ant.has_left_nest and ant.rect.colliderect(nest.rect):
                # ant has hit nest but does not have food
                # delete ant but do not add to arrivals
                ant_list.remove(ant)
                
   
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # get number of ants to add using get_departures function
        alpha, departures, foraging_ants = get_departures(alpha, departures, arrivals, len(ant_list), c=c, q=q, d=d, alpha_min=alpha_min)
   
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
        
        # if visible:
            # update graph 
        # if frame_count % 1000 == 0:
        #     simulation_tracker.update(0)

        for ant in ant_list:
            for food in food_list:
                if ant.rect.colliderect(food.rect) and ant.returning_with_food == False:
                    # delete food
                    food_list.remove(food)
                    # send ant back to nest
                    ant.return_to_nest(nest.x, nest.y)
                    ant.collect_food()
                    # move on to the next ant (since an ant can hit multiple foods)
                    break

        # def track_all(self, food_eaten_increment, foraging_ants, alpha):
        # update simulation tracker
        simulation_tracker.track_all(arrivals, departures, len(ant_list), alpha)

        if (frame_count-first_food_drop/timestep) % (food_cadence/timestep) == 0:
            spawn_food(food_list, food_drop_amount, nest, ant_list, simulation_tracker)
            food_added_time = frame_count*timestep

        # update max foragers
        if len(ant_list) > max_foragers:
            max_foragers = len(ant_list)



    # Save results to graphs at the end of the simulation
    simulation_tracker.save_results_to_graphs()

    # print(f"Total distance travelled by ants: {total_distance_travelled/1000} thousand steps")
    # print(f"Maximum number of foragers: {max_foragers}")

    # check if time_taken_list is empty
    if not time_taken_list:        
        # print error message
        print("No food collected")

    # close figure
    plt.close()

    return np.mean(time_taken_list), total_distance_travelled, max_foragers


# should see 0.15 to 1.2 ants per sec)
# def get_departures(alpha_prev, departure_prev, arrivals, foraging_ants, c=0.602, q=0.2, d=0, alpha_min=0.01):
def get_departures(alpha_prev, departure_prev, arrivals, foraging_ants, c, q, d, alpha_min):
    """
    Calculate the number of ants departing for foraging.
    alpha_prev: Previous rate of outgoing foragers
    departure_prev: Previous departure count
    arrivals: Number of ants arriving in the current time slot
    foraging_ants: Current number of ants out foraging
    Returns updated rate, departure count, and foraging ants count
    """
    alpha_n = max(alpha_prev - q * departure_prev + c * arrivals - d, alpha_min)
    # alpha_n=  1
    D_n = np.random.poisson(alpha_n*timestep)
    foraging_ants += D_n
    return alpha_n, D_n, foraging_ants

def run_experiments():
    for c in [0.1, 0.3, 0.6, 0.9]:
        print(f"Running experiment with c={c}")
        main(c=c)
    return

def run_multiple(N):
    for c in [0.1, 0.3, 0.602, 0.9]:
        print(f"======== Running experiment with c={c} =========")
        all_times_taken = []
        all_distances_travelled = []
        all_max_foragers = []

        for i in range(N):
            # print(f"===== Running simulation {i+1} =====")
            times_taken, total_distance_travelled, max_foragers = main(visible=False, c=c)
            all_times_taken.append(times_taken)
            all_distances_travelled.append(total_distance_travelled)
            all_max_foragers.append(max_foragers)

        print(f"Average time taken to collect all food: {np.mean(all_times_taken)}")
        print(f"Average distance travelled by ants: {np.mean(total_distance_travelled)}")
        print(f"Average maximum number of foragers: {np.mean(max_foragers)}")
    

    
# Run the simulation
if __name__ == "__main__":
    # main()
    # run_experiments()
    run_multiple(10)
