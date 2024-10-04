# PID_Temperature_Control_Main

#from multiprocessing import Process # allows for multiple functions to be run at once/same time
#import numpy as np
#import matplotlib.pyplot as plt
#from scipy.integrate import odeint
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#import nidaqmx
#from nidaqmx.constants import TerminalConfiguration
import time
#import threading
#import keyboard
from colorama import init
import math
import os
import pandas as pd
import threading
import csv

#from datetime import datetime
#import argparse
import time
#from ctypes import windll #

from bk1902b import BK1902B


import Ni_DAQ_mx as daq
import PID_calculator as pid
#import bk_precision_1900_control as bk




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

timestr = time.strftime("%Y%m%d") #_%H%M%S")


# VARIABLES TO CONTROL THE POWER SUPPLY AND TEMPERATURE CONTROL

print(f'\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n{RED}[PROGRAM] > {END}Initializing TONIC... User note: TONIC is only compatible with the \'BK Precision 1902 Power Supply\' and the \'NI DAQ TC01 Thermocouple.\'')

os.environ["USERPROFILE"]

save_path = os.path.join(os.environ["USERPROFILE"], "Desktop")

settings_directory = 'TONIC'

#Default Settings when no txt file given

boundary = 0

control_per_second = 3 # in 1 second, the program will tell the power supply to output a voltage x many times.
# warning: the power supply components may fry and get damaged if it switches too fast

maximum_voltage = 20 # in volts

power_supply_port = 'COM5' # check device manager to make sure. Power supply should be COM5


# Default Values
P = 2.65
I = 0.00000000025
D = 0


try:
    with BK1902B(power_supply_port) as psu:
        psu.disable_output()
except:
    print(f'\n{RED} ERROR! The port {power_supply_port} is unavailable or undetectable on the computer.{END}')
    exit()


print(f'\n{RED}[PROGRAM] > {END}Please enter a new file name for the cooling experiment that you are going to do.')
custom_name = input(f'\n{GREEN}[USER INPUT] > {END}{YELLOW}Create New Filename:{END} ')





#Import new settings from ToNIC folder
try:
    os.mkdir(save_path + '/TONIC/')

    print(f"\n{RED}[PROGRAM] > {END}Directory '% s' created!" % settings_directory)

except FileExistsError:

    print(f"\n{RED}[PROGRAM] > {END}Directory '% s' already exists!" % settings_directory)

    try:
        with open(os.path.join(save_path, settings_directory, '_TONIC_Properties.txt'), 'r') as f:
            reader = csv.reader(f, delimiter='=')

            rows = list(reader)
            #for i, row in enumerate(rows):
            #    print(f"Row {i}: {row}")

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

# Real time grapher

time_axes = []

temperature_axes = []

target_temperatures = []

target_time = []

P_axes = []
I_axes = []
D_axes = []

# Set up the figure and axis
fig_rtp, ax = plt.subplots()
#ax.set_xlim(0, 10)  # Time axis limit
#ax.set_ylim(0, 100)  # Temperature axis limit
ax.set_xlabel('Time (s)')
ax.set_ylabel('Temperature (°C)')
ax.grid()

use_PID_diagnostics = True

# Initialize the lines to be updated
target_line, = ax.plot([], [], lw=2, color='#006078', label='Target Temperature')
actual_line, = ax.plot([], [], lw=2, color='#82BAC4', label='Actual Temperature')

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


# make save folder


try: 
    os.mkdir(save_path + '/TONIC/' + f'{timestr}_{custom_name}')

    print(f"\n{RED}[PROGRAM] > {END}Directory '% s' created!" % custom_name)

except FileExistsError:

    print(f"\n{RED}[PROGRAM] > {END}Directory '% s' already exists!" % custom_name)

save_directory = os.path.join(save_path, 'TONIC', f'{timestr}_{custom_name}')




pid.set_PID(P, I, D)





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


input_valid = False # reset it for next loop

while input_valid == False:

    second_input = input(f'\n{GREEN}[USER INPUT] > {END}{YELLOW}(2) Seconds:{END} > ')

    try:
        if isinstance(float(second_input), float):
            input_valid = True
            second_input = float(second_input)

    except:
        print(f'\n{RED}[PROGRAM] > {END}Invalid input. Please give a numerical value.')

ramp = round(temperature_input/second_input, 3)


# Then, enter a starting temperature for the ramp

input_valid = False

while input_valid == False:

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


# calculate the ramp duration:

#init_temperature + ramp * t = final_temperature

ramp_duration = (final_temperature - init_temperature) / ramp # in seconds

ramp_duration = math.ceil(ramp_duration) # rounds up to nearest second. Must be in whole seconds, as the program will attempt to change temperatures every whole integer second.

if ramp_duration < 0: # if the time is negative, that means that the inputted ramp, T0 and Tf are not logical... so force shut down program
    close = input(f'\n{RED}The inputted values are not logical. The ramp does not agree with the specific initial and final temperatures. Please restart the program by pressing any key.{END}')
    exit()

input_valid = False

while input_valid == False:

    print(f'\n{RED}[PROGRAM] > {END}\nThe given temperature ramp is:{YELLOW}', ramp, f'C/second{END}.\nThe given start temperature is:{YELLOW}', init_temperature,f'C{END}.\nThe given final temperature is:{YELLOW}', final_temperature,f'C{END}.\nThe calculated duration of the temperature ramp process will be:{YELLOW}', ramp_duration,f'seconds{END}.\nPlease confirm the desired temperature ramp {RED}(+/- signs matter!!){END}.\nPress {YELLOW}[ENTER]{END} to start an initial cooldown/warmup to the starting temperature, followed by the temperature ramp process.')
    start_program = input(f'\n{GREEN}[USER INPUT] > {END}')

    if start_program == '': 
        input_valid = True

    else:
        print(f'\n{RED}[PROGRAM] > {END}Invalid input. Please give a numerical value.')



# make a list containing the temperatures

#target_temperatures = []

for i in range(ramp_duration):

    target_temperatures.append(round(init_temperature + ramp * i, 5))

#print(f'\n{RED}[PROGRAM] > {END}The target temperatures are expected to be:', target_temperatures, f'.\nThe program will attempt to meet the temperatures over the course of{YELLOW}', ramp_duration,f' seconds{END}.')

# GRAPHING STUFF

# target temperature over time already given by the above

#target_time = []

for t in target_temperatures:

    target_time.append((t - target_temperatures[0]) / ramp) # subtract from target_temperatures[0] to get 0 seconds at the initial temperature
    #target_time.append(abs(t * 1/ramp))

#print('target time', target_time)

#temperature_axes = []

#time_axes = []

# Set up the animation




with BK1902B(power_supply_port) as psu:




    print(f'\n{YELLOW}[TEMPERATURE RAMP - INITIALIZING] > {END}Resetting power supply output to obtain initial temperature (',init_temperature,' C). Please wait until the actual temperature has reached the target initial temperature before starting.')
    psu.disable_output()
    psu.set_current(10) # to prevent short circuit, current must be high to prevent power supply from going into C.C mode instead of C.V.
    psu.set_voltage(0)
    time.sleep(2)
    psu.enable_output()



    def bk1902b(set_voltage, power_supply_port):

        #with BK1902B(power_supply_port) as psu:
            #print("PID MV Executed! (Power supply has received the PID output and will attempt to proceed)")

        psu.set_voltage(set_voltage)
        output = psu.get_display()
            #mode = "CV" if output[2] else "CC"


        return output


    target_temperatures_rtp = []
    

    for i in range(len(target_time)):

        target_temperatures_rtp.append(init_temperature)

    
    # WAIT FOR USER TO BEGIN THE RAMP!!!

    begin_ramp = False

    def get_input():
        global begin_ramp
        keystrk=input(f"\n{RED}[PROGRAM] > {END}Please press {YELLOW}[ENTER]{END} when you are ready to begin the temperature ramp and have started recording.")
        begin_ramp = True
        print(f'\n{GREEN}[TEMPERATURE RAMP - INITIALIZING] > {END}Beginning Temperature Ramp...')

        timestr = time.strftime("%Y%m%d_%H%M%S")


    n = threading.Thread(target=get_input)

    n.start()

    ani = animation.FuncAnimation(fig_rtp, update, init_func=init, frames=9999999, interval=10, blit = False)

    # Show the plot in a non-blocking way
    plt.ion()

    plt.show()

    initialization_time = time.time()

    reset_integral_loop = True

    while begin_ramp == False:

        # get thermocouple reading

        current_temperature = daq.main()

        temperature_axes.append(current_temperature)

        if use_PID_diagnostics == True:
            set_voltage, Px, Ix, Dx = pid.PID(init_temperature, current_temperature)
            P_axes.append(Px)
            I_axes.append(Ix)
            D_axes.append(Dx)

        # calculate a set voltage

        if current_temperature < init_temperature + boundary:

            psu.disable_output()

            # sets integral to 0
            #if reset_integral_loop == True:

            #    pid.reset_integral()

            #    reset_integral_loop = False

        else:

            psu.enable_output()

            #set_voltage, Px, Ix, Dx = pid.PID(t, current_temperature) # MV = manipulated variable; ie the variable we control to influence temperature... output voltage!
            set_voltage, Px, Ix, Dx = pid.PID(init_temperature, current_temperature) # MV = manipulated variable; ie the variable we control to influence temperature... output voltage!

            #print('PID', P_axes, I_axes, D_axes)

            if set_voltage > maximum_voltage:
                
                set_voltage = maximum_voltage # ensures set voltage does not go over

            voltage_output = bk1902b(set_voltage, power_supply_port)

        


        time.sleep(0.3)

        initialization_end_time = time.time()
        time_axes.append(initialization_end_time - initialization_time) # attaches the time spent running this code.

        plt.draw()

        plt.pause(0.01)




    # TEMPERATURE RAMP PROGRAM

    target_temperatures_rtp = target_temperatures # for real time plot

    start_time = time.time() # keep track of time during ramp program


    # reset the axes

    time_axes = []

    temperature_axes = []

    P_axes = []
    I_axes = []
    D_axes = []

    #time_axes.append(0) # attaches the time spent running this code.

    
    break_loop = False



    for t in target_temperatures: # where the good stuff (meaty code) lies.



        for x in range(control_per_second):
            #if t == target_temperatures[-1]: # if last element is reached
            #    break


            t0 = time.time()

            # get thermocouple reading

            current_temperature = daq.main()

            temperature_axes.append(current_temperature)

            # calculate a set voltage


            # for main use
            # print(f'\n{GREEN}[TEMPERATURE RAMP - RUNNING] > {END}\nCurrent Temperature is:{YELLOW}', current_temperature, f' C{END}.\nTarget Temperature is:{YELLOW}', t,f' C{END}.')            
            
            # P I D values

            if use_PID_diagnostics == True:
                #Px, Ix, Dx = pid.return_PID_values()

                set_voltage, Px, Ix, Dx = pid.PID(t, current_temperature)
                P_axes.append(Px)
                I_axes.append(Ix)
                D_axes.append(Dx)


            #if current_temperature < t + boundary:
                
                #psu.disable_output()

                #print('Power Supply Disabled')

            
            
            #else:


            set_voltage, Px, Ix, Dx = pid.PID(t, current_temperature) # MV = manipulated variable; ie the variable we control to influence temperature... output voltage!

            # print(f'The power supply will attempt to set a voltage of:{YELLOW}', set_voltage,f' V{END}.')


            if set_voltage > maximum_voltage:

                # print(f'{RED}[PROGRAM] > {END}The attempted voltage (',set_voltage,' V) to be set exceeds the maximum voltage (', maximum_voltage,' V) defined in the code.')
                
                set_voltage = maximum_voltage # ensures set voltage does not go over

            psu.enable_output()

            voltage_output = bk1902b(set_voltage, power_supply_port)

            #print(f'{RED}[PROGRAM] > {END}The power supply has a voltage output of:{YELLOW}', voltage_output[0],f' V{END}.')



            tf = time.time()

            x = tf - t0 # note to coder: the entire processes above (3 functions) takes ~ 0.8 ms to execute... so the 1-x below will be about ~ 0.2ms to compensate to 1 second

            time_axes.append(tf - start_time) # attaches the time spent running this code.

            #print('Time of 1 cycle:', x)

            try:

                #print(1/control_per_second - x)
                plt.draw()
                plt.pause(0.01)


                tf = time.time()

                loop_duration = tf - t0 # in case pltdraw takes up more time

                
                time.sleep(max(0, 1/control_per_second - loop_duration)) # sleep for the remaining time after considering the time taken to s


            except:
                psu.disable_output()
                print(f'\n{RED}ERROR!! The program is unable to alter the voltage each second to influence a change in temperature per second... This may be due to slow processing speed, either from a slow computer, power supply, or thermocouple. A possible solution is to either direct the processing power to the computer and instruments (close background processes), or to alter the code so temperature changes every >1 second... (Do this by altering the time.sleep() function above the line where this print statement lies.){END}')
                close = input(f'\nThe power supply will reset to 0 V. Press any key to terminate the program.')
                close()


    end_time = time.time()
    elapsed_time = round(end_time - start_time, 2)
    print(f'\n\n{RED}[PROGRAM] > {END}The ramp program took: {YELLOW}', elapsed_time, f'{END} seconds to complete, in contrast to the expected runtime of: ', ramp_duration, ' seconds. (Absolute deviation = ', abs(elapsed_time - ramp_duration),' seconds)')

    # reset to original temp quickly program

    print(f'\n{PURPLE}[TEMPERATURE RAMP - TERMINATING] > {END}Ramp program has reached the final temperature (', final_temperature,' C).\nResetting power supply output to 0 V.')

    psu.disable_output()

    Kp, Ki, Kd = pid.return_PID_values()

    # Close the plot after the loop is done
    plt.ioff()

    plt.savefig(os.path.join(save_directory, f'{timestr}_{custom_name}_P({Kp})_I({Ki})_D({Kd}).png'))
    
    plt.show()

    plt.close() # closes most recent plot
        







   

    #plt.savefig(save_path + '/TONIC/' + timestr + '_' + custom_name + '_' + 'PID' + property_str + '_Ramp_Graph.png') # MUST be above the plt show line.

    #plt.show()


    # save raw data as csv

    d = {'Time (s)': time_axes, 'Temperature (C)': temperature_axes, 'Target Ramp (C/s)': ramp, 'Starting T': init_temperature, 'Final Target T': final_temperature}

    export_temperature_data = pd.DataFrame(d)

    export_temperature_data.to_csv(os.path.join(save_directory, f'{timestr}_{custom_name}.csv') )
                                   



    '''
    t_end = time.time() + 30 # 30 second

    while time.time() < t_end:
        time.sleep(1)

        current_temperature = daq.main()

        print(f'\n{PURPLE}[TEMPERATURE RAMP - TERMINATING] > {END}Turning off power supply... Current temperature is: (',current_temperature,f' C)')

    '''
print(f'\n{PURPLE}[PROGRAM] > {END}The program has concluded!')