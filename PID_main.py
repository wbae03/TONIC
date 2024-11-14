# PID_Temperature_Control_Main

# Import packages
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from colorama import init
import math
import os
import pandas as pd
import threading
import csv
from datetime import datetime, timedelta
import msvcrt

# Import scripts
from bk1902b import BK1902B
import Ni_DAQ_mx as daq
import PID_calculator as pid

# Defining ANSI escape colours
RED = "\33[91m"
BLUE = "\33[94m"
GREEN = "\033[32m"
YELLOW = "\033[93m"
PURPLE = '\033[0;35m' 
CYAN = "\033[36m"
LBLUE = "\033[94m"
END = "\033[0m"
BOLD = "\033[1m"
LGREEN = "\033[92m"
LRED = "\033[91m"

print(f'\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n{RED}[PROGRAM] > {END}Initializing TONIC... User note: TONIC is only compatible with the \'BK Precision 1902 Power Supply\' and the \'NI DAQ TC01 Thermocouple.\'')

timestr = time.strftime("%Y%m%d") #_%H%M%S")

# Directory to access TONIC settings file
os.environ["USERPROFILE"]
save_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
settings_directory = 'TONIC'

#===================== Default settings if no _TONIC_Properties.txt detected ===============================

# Offset value from target temperatures, which the PID will try to achieve. This is useful if the temperature-system keeps over/undershooting.
boundary = 0

# How many times the program will process the current temperature and target temperature deviance per second.
# This essentially means how many times the script will tell the power supply to output a voltage to adapt the temperature per second.
# How many times feasible depends on processing speed of computer and power supply limitations. Hardware components may be damaged if it is too high. 
# 3 seems to be a good number.
control_per_second = 3

# in volts
maximum_voltage = 20

# Check device manager to find correct COM#
power_supply_port = 'COM4'

# Default PID values
P = 2.65

I = 0.00000000025

D = 0

# Visualize the PID values on the graph for diagnostics or PID optimization
use_PID_diagnostics = False

#====================== Import settings from _TONIC_Properties.txt =============================================

try:

    os.mkdir(save_path + '/TONIC/')

    print(f"\n{RED}[PROGRAM] > {END}Directory '% s' created!" % settings_directory)

except FileExistsError:

    print(f"\n{RED}[PROGRAM] > {END}Directory '% s' already exists!" % settings_directory)

    try:

        with open(os.path.join(save_path, settings_directory, '_TONIC_Properties.txt'), 'r') as f:

            reader = csv.reader(f, delimiter='=')

            rows = list(reader)

            # Ensure there are enough rows before accessing
            power_supply_port = rows[0][1].strip()

            maximum_voltage = float(rows[2][1].strip())

            boundary = float(rows[4][1].strip())

            use_PID_diagnostics = bool(rows[6][1].strip())

            control_per_second = int(rows[8][1].strip())

            P = float(rows[10][1].strip())

            I = float(rows[12][1].strip())

            D = float(rows[14][1].strip())

    except FileNotFoundError: 

        print("No '_TONIC_PROPERTIES.txt' file exists.")

#==========================================================================================================

# Establish connection with power supply USB port
try:

    with BK1902B(power_supply_port) as psu:

        psu.disable_output()

except:

    print(f'\n{RED} ERROR! The port {power_supply_port} is unavailable or undetectable on the computer.{END}')

    exit()

print(f'\n{RED}[PROGRAM] > {END}Please enter a new file name for the cooling experiment that you are going to do.')

custom_name = input(f'\n{GREEN}[USER INPUT] > {END}{YELLOW}Create New Filename:{END} ')

#====================== Real-time Temperature Graph Initialization =============================================

# Initialize plot data
time_axes = []

temperature_axes = []

target_temperatures = []

target_time = []

P_axes = []

I_axes = []

D_axes = []

# Set up the figure and axis
fig_rtp, ax = plt.subplots()

ax.set_xlabel('Time (s)')

ax.set_ylabel('Temperature (°C)')

ax.grid()

# Initialize the temperature plots
target_line, = ax.plot([], [], lw=2, color='#006078', label='Target Temperature')

actual_line, = ax.plot([], [], lw=2, color='#82BAC4', label='Actual Temperature')

# Initialize PID plots
if use_PID_diagnostics == True:

    P_line, = ax.plot([], [], lw=2, color='green', label='Proportional')

    I_line, = ax.plot([], [], lw=2, color='blue', label='Integral')

    D_line, = ax.plot([], [], lw=2, color='red', label='Derivative')

    ax.set_ylabel('Temperature (°C) & PID Value')

# Add a legend
ax.legend()

# Function to initialize the plot
def init():

    target_line.set_data([], [])

    actual_line.set_data([], [])

    if use_PID_diagnostics == True:

        P_line.set_data([], [])

        I_line.set_data([], [])

        D_line.set_data([], [])

        return target_line, actual_line, P_line, I_line, D_line
    
    return target_line, actual_line

# Function to update the plot
def update(frame):

    target_line.set_data(target_time, target_temperatures_rtp)

    actual_line.set_data(time_axes, temperature_axes)
    
    # Adjust the x-axis limit if necessary
    ax.set_xlim(0, max(target_time))

    ax.set_ylim(final_temperature - 1, 10)

    if use_PID_diagnostics == True:

        P_line.set_data(time_axes, P_axes)

        I_line.set_data(time_axes, I_axes)

        D_line.set_data(time_axes, D_axes)

        ax.set_ylim(min(target_temperatures), 30)

        return target_line, actual_line, P_line, I_line, D_line
    
    return target_line, actual_line

pid.set_PID(P, I, D)

#==========================================================================================================

# make save folder
try: 

    os.mkdir(save_path + '/TONIC/' + f'{timestr}_{custom_name}')

    print(f"\n{RED}[PROGRAM] > {END}Directory '% s' created!" % custom_name)

except FileExistsError:

    print(f"\n{RED}[PROGRAM] > {END}Directory '% s' already exists!" % custom_name)

save_directory = os.path.join(save_path, 'TONIC', f'{timestr}_{custom_name}')

#==================== User Input for Temperature Ramp =============================================================

current_temperature = daq.main()

print(f'\n{RED}[PROGRAM] > {END}The current temperature reading from the temperature probe is:', current_temperature, ' C.')

print(f'\n{RED}[PROGRAM] > {END}Please input the below values to get the desired temperature ramp {RED}(+/- signs matter!!){END}: \n{YELLOW}(1) Temperature (C){END}\n{YELLOW}(2) Seconds{END}')

input_valid = False

while input_valid == False:

    temperature_input = input(f'\n{GREEN}[USER INPUT] > {END}{YELLOW}(1) Temperature (C):{END} > ')

    try:

        if isinstance(float(temperature_input), float):

            input_valid = True

            temperature_input = float(temperature_input)
    
    except:

        print(f'\n{RED}[PROGRAM] > {END}Invalid input. Please give a numerical value.')

# Reset this for the next loop
input_valid = False

while input_valid == False:

    second_input = input(f'\n{GREEN}[USER INPUT] > {END}{YELLOW}(2) Seconds:{END} > ')

    try:

        if isinstance(float(second_input), float):

            input_valid = True

            second_input = float(second_input)

    except:

        print(f'\n{RED}[PROGRAM] > {END}Invalid input. Please give a numerical value.')

ramp = round(temperature_input/second_input, 3)

input_valid = False

while input_valid == False:

    # Enter a starting temperature for the ramp
    init_temperature = input(f'\n{RED}[PROGRAM] > {END}Next, please enter the {YELLOW}starting temperature (C){END} for the program {RED}(+/- signs matter!!){END}.\n\n{GREEN}[USER INPUT] > {END}')

    try:

        if isinstance(float(init_temperature), float):

            input_valid = True

            init_temperature = float(init_temperature)

    except:

        print(f'\n{RED}[PROGRAM] > {END}Invalid input. Please give a numerical value.')

input_valid = False

while input_valid == False:

    final_temperature = input(f'\n{RED}[PROGRAM] > {END}Finally, enter the {YELLOW}final temperature (C){END} for the program {RED}(+/- signs matter!!){END}.\n\n{GREEN}[USER INPUT] > {END}')

    try:

        if isinstance(float(final_temperature), float):

            input_valid = True

            final_temperature = float(final_temperature)

    except:

        print(f'\n{RED}[PROGRAM] > {END}Invalid input. Please give a numerical value.')

# ramp duration in seconds
ramp_duration = (final_temperature - init_temperature) / ramp

# round to nearest second. Must be in whole seconds; the program will only change temperatures every whole-integer second.
ramp_duration = math.ceil(ramp_duration) 

# If the time is negative that the temperature ramp is not logical. Force shut down program.
if ramp_duration < 0: 

    close = input(f'\n{RED}The inputted values are not logical. The ramp does not agree with the specific initial and final temperatures. Please restart the program by pressing any key.{END}')
    
    exit()

input_valid = False

while input_valid == False:

    # Confirm the provided values
    print(f'\n{RED}[PROGRAM] > {END}\nThe given temperature ramp is:{YELLOW}', ramp, f'C/second{END}.\nThe given start temperature is:{YELLOW}', init_temperature,f'C{END}.\nThe given final temperature is:{YELLOW}', final_temperature,f'C{END}.\nThe calculated duration of the temperature ramp process will be:{YELLOW}', ramp_duration,f'seconds{END}.\nPlease confirm the desired temperature ramp {RED}(+/- signs matter!!){END}.\nPress {YELLOW}[ENTER]{END} to start an initial cooldown/warmup to the starting temperature, followed by the temperature ramp process.')
    
    start_program = input(f'\n{GREEN}[USER INPUT] > {END}')

    if start_program == '': 
        
        input_valid = True

    else:

        print(f'\n{RED}[PROGRAM] > {END}Invalid input. Please give a numerical value.')

# List containing the target temperatures
for i in range(ramp_duration):

    target_temperatures.append(round(init_temperature + ramp * i, 5))

# List containing corresponding target times to achieve desired temperatures.
for t in target_temperatures:

    # subtract from target_temperatures[0] to get 0 seconds at the initial temperature
    target_time.append((t - target_temperatures[0]) / ramp) 

#============================= START TEMPERATURE CONTROL ==========================================
with BK1902B(power_supply_port) as psu:

    print(f'\n{YELLOW}[TEMPERATURE RAMP - INITIALIZING] > {END}Resetting power supply output to obtain initial temperature (',init_temperature,' C). Please wait until the actual temperature has reached the target initial temperature before starting.')
    
    psu.disable_output()

    # To prevent short circuit, current must be high to prevent power supply from going into C.C mode instead of C.V.
    psu.set_current(10) 
    
    psu.set_voltage(0)
    
    time.sleep(2)
    
    psu.enable_output()

    def bk1902b(set_voltage, power_supply_port):

        psu.set_voltage(set_voltage)

        output = psu.get_display()

        return output

    target_temperatures_rtp = []

    for i in range(len(target_time)):

        target_temperatures_rtp.append(init_temperature)

    #================== Wait for temperature equilibrium & user to begin temperature ramp ===================================
    begin_ramp = False

    def get_input():

        global begin_ramp

        # dummy input variable to halt code until input is given
        keystrk=input(f"\n{RED}[PROGRAM] > {END}Please press {YELLOW}[ENTER]{END} when you are ready to begin the temperature ramp and have started recording.")
        
        begin_ramp = True
        
        print(f'\n{GREEN}[TEMPERATURE RAMP - INITIALIZING] > {END}Beginning Temperature Ramp. Press {GREEN}ENTER{END} to terminate ramp.')

        timestr = time.strftime("%Y%m%d_%H%M%S")

    # start multi-thread to animate progress bar while graphing plot and controlling temperature
    n = threading.Thread(target=get_input)

    n.start()

    ani = animation.FuncAnimation(fig_rtp, update, init_func=init, frames=9999999, interval=10, blit = False)

    # Show the plot in a non-blocking way
    plt.ion()

    plt.show()

    initialization_time = time.time()

    datetime_initialization_time = datetime.now()

    reset_integral_loop = True

    # Plot the temperature plot while waiting
    while begin_ramp == False:

        # get thermocouple reading
        current_temperature = daq.main()

        temperature_axes.append(current_temperature)

        if use_PID_diagnostics == True:

            set_voltage, Px, Ix, Dx = pid.PID(init_temperature, current_temperature)

            P_axes.append(Px)

            I_axes.append(Ix)

            D_axes.append(Dx)

        # Voltage output as zero if temperature dips below target
        if current_temperature < init_temperature + boundary:

            psu.disable_output()

        else:

            psu.enable_output()

            set_voltage, Px, Ix, Dx = pid.PID(init_temperature, current_temperature) # MV = manipulated variable; ie the variable we control to influence temperature... output voltage!

            if set_voltage > maximum_voltage:

                # Ensures set voltage does not go over the maximum allowed
                set_voltage = maximum_voltage

            voltage_output = bk1902b(set_voltage, power_supply_port)

        time.sleep(0.3)

        initialization_end_time = time.time()

        # Append to time axes for plotting
        time_axes.append(initialization_end_time - initialization_time)

        plt.draw()

        plt.pause(0.01)

#==================== Start Temperature Ramp Program ===============================================================

    # Temperatures for real time plot
    target_temperatures_rtp = target_temperatures

    # keep track of time during ramp program
    start_time = time.time()

    # reset the axes
    time_axes = []

    temperature_axes = []

    P_axes = []

    I_axes = []

    D_axes = []
    
    break_loop = False

    # Temperature control of ramp
    for t in target_temperatures:

        for x in range(control_per_second):

            t0 = time.time()

            # Get thermocouple reading
            current_temperature = daq.main()

            # Append to temperature axes
            temperature_axes.append(current_temperature)

            # Obtain PID values
            if use_PID_diagnostics == True:

                set_voltage, Px, Ix, Dx = pid.PID(t, current_temperature)

                P_axes.append(Px)

                I_axes.append(Ix)

                D_axes.append(Dx)

            set_voltage, Px, Ix, Dx = pid.PID(t, current_temperature) 

            # Set voltage does not exceed maximum defined voltage
            if set_voltage > maximum_voltage:
                
                set_voltage = maximum_voltage

            psu.enable_output()

            voltage_output = bk1902b(set_voltage, power_supply_port)

            tf = time.time()

            # The processes above takes ~ 0.8 ms to execute... so the 1-x below will be about ~ 0.2ms to compensate to 1 second
            x = tf - t0 

            # Time spent running code is saved as seconds
            time_axes.append(tf - start_time)

            # For diagnostic purposes
            #print('Time of 1 cycle:', x)

            try:

                # For diagnostic purposes
                #print(1/control_per_second - x)

                plt.draw()

                plt.pause(0.01)

                tf = time.time()

                # Account for time spent drawing the plot
                loop_duration = tf - t0

                # Sleep for the remaining time
                time.sleep(max(0, 1/control_per_second - loop_duration))

            except:

                psu.disable_output()

                print(f'\n{RED}ERROR!! The program is unable to alter the voltage each second to influence a change in temperature per second... This may be due to slow processing speed, either from a slow computer, power supply, or thermocouple. A possible solution is to either direct the processing power to the computer and instruments (close background processes), or to alter the code so temperature changes every >1 second... (Do this by altering the time.sleep() function above the line where this print statement lies.){END}')
                
                close = input(f'\nThe power supply will reset to 0 V. Press any key to terminate the program.')
                
                close()
        
        ### EXIT LOOP ON 'ENTER' INPUT ##

        if msvcrt.kbhit():
            if msvcrt.getwche() == '\r':
                print(f'\n{RED}[PROGRAM] >{END} Ramp terminated by user.\n')
                break
        ##############################

    end_time = time.time()

    elapsed_time = round(end_time - start_time, 2)

    print(f'\n\n{RED}[PROGRAM] > {END}The ramp program took: {YELLOW}', elapsed_time, f'{END} seconds to complete, in contrast to the expected runtime of: ', ramp_duration, ' seconds. (Absolute deviation = ', abs(elapsed_time - ramp_duration),' seconds)')

    #================================================================================================================================


    print(f'\n{PURPLE}[TEMPERATURE RAMP - TERMINATING] > {END}Ramp program has reached the final temperature (', final_temperature,' C).\nResetting power supply output to 0 V.')

    # Reset temperature back to whatever 0V gets you.
    psu.disable_output()
        
#======================== SAVING DATA ===============================================================================================

    saved_time_data = []

    # Convert the seconds of the cooling ramp into system datetime
    for t in time_axes:
        
        new_time_format = datetime_initialization_time + timedelta(seconds=t)

        saved_time_data.append(new_time_format.strftime("%Y%m%d_%H%M%S"))

    # Save raw data as csv
    d = {'Time (YMD_HMS)': saved_time_data, 'Time (seconds)': time_axes,'Temperature (C)': temperature_axes, 'Target Ramp (C/s)': ramp, 'Starting T': init_temperature, 'Final Target T': final_temperature}

    export_temperature_data = pd.DataFrame(d)

    export_temperature_data.to_csv(os.path.join(save_directory, f'{timestr}_{custom_name}.csv') )
                                   
    print(f'\n{PURPLE}[PROGRAM] > {END}The program has concluded!')

#========= SAVING GRAPH ======================================
    Kp, Ki, Kd = pid.return_PID_values()

    # Close the plot after the loop is done
    plt.ioff()

    plt.savefig(os.path.join(save_directory, f'{timestr}_{custom_name}_P({Kp})_I({Ki})_D({Kd}).png'))
    
    plt.show()

    # Closes most recent plot
    plt.close()