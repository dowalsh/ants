import numpy as np
import matplotlib.pyplot as plt

def get_departures(alpha_prev, departure_prev, arrivals, foraging_ants, c=0.602, q=0.05, d=0.01, alpha_0=0.01):
    
    # Update alpha based on the model equations
    alpha_n = max(alpha_prev - q * departure_prev + c * arrivals - d, alpha_0)
    # print("Here we go")
    # # print the name and value of each part of this equation
    # print("alpha_prev: ", alpha_prev)
    # print("-q * departure_prev: ", q * departure_prev)
    # print("c * arrivals: ", c * arrivals)


    # Simulate departures using a Poisson distribution
    D_n = np.random.poisson(alpha_n)
    # print D_n and its value
    # print("D_n: ", D_n)


    # Update the number of ants out foraging
    foraging_ants += D_n

    return alpha_n, D_n, foraging_ants

import numpy as np

def get_arrivals(foraging_ants, food_available):
    # Adjust the success probability based on food availability
    p_max = 0.8  # Maximum success probability
    p_min = 0  # Minimum success probability
    k = 0.1      # Steepness of the logistic curve
    f_factor = 0.01  # Adjust this factor based on the impact of food availability

    # Calculate the adjusted success probability using a logistic function
    p = p_min + (p_max - p_min) / (1 + np.exp(-k * (food_available - f_factor)))
    p = food_available / 100
    p = max(p, p_min)
    # print(p)

    # issue lies with the fact that foraging ants have a small possibility of never returning to the nest. 
    # This inflatest the number of foraging ants. Need a way to model ants returning to the nesst empty handed
    # Might need to track ants as they leave and put a maximum time for them to return.

    # Use the adjusted probability in a binomial distribution for each individual ant

    # lets actually temporarily remove random variability here
    # successful_returns = round(p*foraging_ants)
    successful_returns = np.random.binomial(1, p, foraging_ants)


    unsuccessful_returns = np.sum(np.random.binomial(1, 0.05, foraging_ants - successful_returns))
    print("foraging_ants: ", foraging_ants)
    print("successful returns: ", successful_returns)

    # Calculate the total number of ants successfully returning
    A_n = np.sum(successful_returns)

    # Update the number of ants out foraging and the amount of food available
    foraging_ants -= A_n
    foraging_ants -= unsuccessful_returns

    if food_available > 0:
        food_available -= A_n  # Decrease food availability based on the number of ants returning
    if food_available < 0:
        food_available = 0     # Food availability cannot be negative

    # Return both the updated foraging ant population and food availability
    return A_n, foraging_ants, food_available

def simulate_foraging(num_time_slots):
    # Arrays to store results
    alpha_values = np.zeros(num_time_slots)
    departure_counts = np.zeros(num_time_slots)
    arrival_counts = np.zeros(num_time_slots)
    foraging_ants_counts = np.zeros(num_time_slots)
    food_available_values = np.zeros(num_time_slots)  # New array for food availability

    # set initial value of alpha
    alpha_values[0] = 1

    # Initial number of ants out foraging and food available
    foraging_ants = 10
    food_available = 5  # Initial amount of food available is zero

    for n in range(num_time_slots):

        # Update food availability one time
        if(n == num_time_slots/2):
            food_available += 100

        # Update values based on the previous time slot and arrivals/departures during the time slot
        # calculate number of ants that return to the nest
        A_n, foraging_ants, food_available = get_arrivals(foraging_ants, food_available)
        alpha_values[n], departure_counts[n], foraging_ants = get_departures(alpha_values[n-1], departure_counts[n-1], A_n, foraging_ants)
        arrival_counts[n] = A_n
        foraging_ants_counts[n] = foraging_ants
        food_available_values[n] = food_available  # Store the current food availability

    return alpha_values, departure_counts, arrival_counts, foraging_ants_counts, food_available_values

# plot everything
def plot_results(num_time_slots, alpha_values, departure_counts, arrival_counts, foraging_ants_counts, food_available_values):

    # Plotting the results
    time_slots = np.arange(num_time_slots)
    # Plot for Alpha, Departure Counts, and Arrival Counts
    plt.figure(figsize=(12, 8))
    
    plt.subplot(4, 1, 1)
    plt.plot(time_slots, departure_counts, label='Departure Counts')
    plt.plot(time_slots, arrival_counts, label='Arrival Counts', linestyle='--', alpha=0.7)
    plt.xlabel('Time Slots')
    plt.legend()

    # Plot for alpha
    plt.subplot(4, 1, 2)
    plt.plot(time_slots, alpha_values, label='Alpha (Rate of Outgoing Foragers)')
    plt.xlabel('Time Slots')
    plt.legend()

    # Plot for Foraging Ants Counts
    plt.subplot(4, 1, 3)
    plt.plot(time_slots, foraging_ants_counts, label='Foraging Ants Counts', linestyle='-', alpha=0.7)
    plt.xlabel('Time Slots')
    plt.legend()

    # Plot for Food Availability
    plt.subplot(4, 1, 4)
    plt.plot(time_slots, food_available_values, label='Food Availability', linestyle='-', alpha=0.7, color='green')
    plt.xlabel('Time Slots')
    plt.legend()

    plt.tight_layout()
    plt.show()

    return

# Simulate foraging over 100 time slots (you can adjust this)
num_time_slots = 1000
alpha_values, departure_counts, arrival_counts, foraging_ants_counts, food_available_values = simulate_foraging(num_time_slots)
# plot everything
plot_results(num_time_slots, alpha_values, departure_counts, arrival_counts, foraging_ants_counts, food_available_values)
