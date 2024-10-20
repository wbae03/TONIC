# Real-time plotting

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

'''
# Initialize temperatures and time
current_target_temp = 0
current_actual_temp = 0
time_elapsed = 0

# Data lists
times = []
target_temps = []
actual_temps = []

'''




# Function to initialize the plot
def init():
    target_line.set_data([], [])
    actual_line.set_data([], [])
    return target_line, actual_line

# Function to update the plot
def update(frame):
    target_line.set_data(times, target_temps)
    actual_line.set_data(times, actual_temps)
    
    # Adjust the x-axis limit if necessary
    ax.set_xlim(0, max(10, time_elapsed + 1))
    
    return target_line, actual_line

# Set up the animation
ani = animation.FuncAnimation(fig, update, init_func=init, blit=True, interval=100)

# Show the plot in a non-blocking way
plt.ion()
plt.show()

# Main loop where temperatures are updated
while time_elapsed <= 100:  # Replace with your actual loop condition
    # Update the target and actual temperatures
    current_target_temp =   # Example ramp, replace with your logic
    current_actual_temp =   # Example reading, replace with your actual probe value
    
    # Append the current time and temperatures to the lists
    times.append(time_elapsed)
    target_temps.append(current_target_temp)
    actual_temps.append(current_actual_temp)
    
    # Pause to simulate time passing, replace with your actual time interval
    time.sleep(1)
    
    # Increment the time elapsed
    time_elapsed += 1
    
    # Update the plot
    plt.draw()
    plt.pause(0.01)

# Close the plot after the loop is done
plt.ioff()
plt.show()