import numpy as np
import matplotlib.pyplot as plt

def get_departures(alpha_prev, departure_prev, arrivals, foraging_ants, c=0.1, q=0.05, d=0.0, alpha_0=0.01):
    # Update alpha based on the model equations
    alpha_n = max(alpha_prev - q * departure_prev + c * arrivals - d, alpha_0)

    # Simulate departures using a Poisson distribution
    D_n = np.random.poisson(alpha_n)

    # Update the number of ants out foraging
    foraging_ants += D_n

    return alpha_n, D_n, foraging_ants

def get_arrivals(foraging_ants, food_available):
    # Adjust the success probability based on food availability using a logistic function
    p_max = 0.9  # Maximum success probability
    p_min = 0.1  # Minimum success probability
    k = 0.1      # Steepness of the logistic curve
    food_factor = 0.01  # Adjust this factor based on the impact of food availability

    # Calculate the adjusted success probability
    p = p_min + (p_max - p_min) / (1 + np.exp(-k * (food_available - 10 * foraging_ants * food_factor)))

    # Use the adjusted probability in the binomial distribution
    A_n = np.random.binomial(foraging_ants, p)

    # Update the number of ants out foraging and the amount of food available
    foraging_ants -= A_n
    food_available += A_n

    return A_n

def simulate_foraging(num_time_slots):
    # Arrays to store results
    alpha_values = np.zeros(num_time_slots)
    departure_counts = np.zeros(num_time_slots)
    arrival_counts = np.zeros(num_time_slots)
    foraging_ants_counts = np.zeros(num_time_slots)
    food_available_values = np.zeros(num_time_slots)  # New array for food availability

    # Initial number of ants out foraging and food available
    foraging_ants = 0
    food_available = 10  # Initial amount of food available

    for n in range(num_time_slots):
        # Update values based on the previous time slot and arrivals/departures during the time slot
        # calculate number of ants that return to the nest
        A_n = get_arrivals(foraging_ants, food_available)
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
    plt.subplot(3, 1, 1)
    plt.plot(time_slots, alpha_values, label='Alpha (Rate of Outgoing Foragers)')
    plt.plot(time_slots, departure_counts, label='Departure Counts')
    plt.plot(time_slots, arrival_counts, label='Arrival Counts', linestyle='--', alpha=0.7)
    plt.xlabel('Time Slots')
    plt.legend()

    # Plot for Foraging Ants Counts
    plt.subplot(3, 1, 2)
    plt.plot(time_slots, foraging_ants_counts, label='Foraging Ants Counts', linestyle='-', alpha=0.7)
    plt.xlabel('Time Slots')
    plt.legend()

    # Plot for Food Availability
    plt.subplot(3, 1, 3)
    plt.plot(time_slots, food_available_values, label='Food Availability', linestyle='-', alpha=0.7, color='green')
    plt.xlabel('Time Slots')
    plt.legend()

    plt.tight_layout()
    plt.show()

    return

# Simulate foraging over 100 time slots (you can adjust this)
num_time_slots = 100
alpha_values, departure_counts, arrival_counts, foraging_ants_counts, food_available_values = simulate_foraging(num_time_slots)
# plot everything
plot_results(num_time_slots, alpha_values, departure_counts, arrival_counts, foraging_ants_counts, food_available_values)
