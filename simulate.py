import numpy as np
import matplotlib.pyplot as plt

def get_departures(alpha_prev, departure_prev, arrivals, foraging_ants, c=0.602, q=0.05, d=0.01, alpha_0=0.03):
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

def get_arrivals(foraging_ants, food_available):
    """
    Calculate the number of ants returning to the nest.
    foraging_ants: Current number of ants out foraging
    food_available: Current food availability
    Returns number of ants arriving, updated foraging ant count and food availability
    """
    p_max = 0.8
    p_min = 0
    k = 0.1
    f_factor = 0.01

    p = p_min + (p_max - p_min) / (1 + np.exp(-k * (food_available - f_factor)))
    p = max(food_available / 100, p_min)

    successful_returns = sum(np.random.binomial(1, p, foraging_ants))
    unsuccessful_returns = np.sum(np.random.binomial(1, 0.05, foraging_ants - successful_returns))

    A_n = np.sum(successful_returns)
    foraging_ants -= A_n + unsuccessful_returns
    food_available = max(food_available - A_n, 0)

    return A_n, foraging_ants, food_available

def simulate_foraging(num_time_slots):
    """
    Simulate the foraging behavior over a number of time slots.
    num_time_slots: Total number of time slots to simulate
    Returns arrays of alpha, departure counts, arrival counts, foraging ants counts, and food availability
    """
    alpha_values = np.zeros(num_time_slots)
    departure_counts = np.zeros(num_time_slots)
    arrival_counts = np.zeros(num_time_slots)
    foraging_ants_counts = np.zeros(num_time_slots)
    food_available_values = np.zeros(num_time_slots)

    alpha_values[0] = 1
    foraging_ants = 0
    food_available = 0

    for n in range(num_time_slots):
        if n == num_time_slots/4 or n == 3*num_time_slots/4:
            food_available += 100

        A_n, foraging_ants, food_available = get_arrivals(foraging_ants, food_available)
        alpha_values[n], departure_counts[n], foraging_ants = get_departures(alpha_values[n-1], departure_counts[n-1], A_n, foraging_ants)
        arrival_counts[n] = A_n
        foraging_ants_counts[n] = foraging_ants
        food_available_values[n] = food_available

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
