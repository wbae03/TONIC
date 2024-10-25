# PID_Temperature_Control_Main

# READ ME
# this script has not been updated or checked for successful execution.
# swap this script with PID_main.py in the main directory if you want to use a PWM controller instead of PID.
# run this script as you would for PID_main.py.



import numpy as np
import matplotlib.pyplot as plt
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

#from datetime import datetime
#import argparse
import time
#from ctypes import windll #

from bk1902b import BK1902B


import Ni_DAQ_mx as daq
import PID_calculator as pid
#import bk_precision_1900_control as bk

#timeBeginPeriod = windll.winmm.timeBeginPeriod
#timeBeginPeriod(1)


# VARIABLES TO CONTROL THE POWER SUPPLY AND TEMPERATURE CONTROL

boundary = 0

control_per_second = 3 # in 1 second, the program will tell the power supply to output a voltage x many times.
# warning: the power supply components may fry and get damaged if it switches too fast

maximum_voltage = 6.5 # in volts

power_supply_port = 'COM5' # check device manager to make sure. Power supply should be COM5



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



### First, enter a desired temperature ramp in celsius per second ()

print(f'\n{RED}[PROGRAM] > {END}Initializing TONIC... User note: TONIC is only compatible with the \'BK Precision 1902 Power Supply\' and the \'NI DAQ TC01 Thermocouple.\'')

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

    init_temperature = input(f'\n{RED}[PROGRAM] > {END}Next, please enter the starting temperature (C) for the program {RED}(+/- signs matter!!){END}.\n\n{GREEN}[USER INPUT] > {END}')

    try:
        if isinstance(float(init_temperature), float):
            input_valid = True
            init_temperature = float(init_temperature)

    except:
        print(f'\n{RED}[PROGRAM] > {END}Invalid input. Please give a numerical value.')


input_valid = False

while input_valid == False:

    final_temperature = input(f'\n{RED}[PROGRAM] > {END}Finally, enter the final temperature (C) for the program {RED}(+/- signs matter!!){END}.\n\n{GREEN}[USER INPUT] > {END}')

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

    print(f'\n{RED}[PROGRAM] > {END}\nThe given temperature ramp is:{YELLOW}', ramp, f'C/second{END}.\nThe given start temperature is:{YELLOW}', init_temperature,f'C{END}.\nThe given final temperature is:{YELLOW}', final_temperature,f'C{END}.\nThe calculated duration of the temperature ramp process will be:{YELLOW}', ramp_duration,f'seconds{END}.\nPlease confirm the desired temperature ramp {RED}(+/- signs matter!!){END}.\nPress {YELLOW}[ENTER]{END} to start a 30-second preparation to reach the initial temperature, followed by the temperature ramp process.')
    start_program = input(f'\n{GREEN}[USER INPUT] > {END}')

    if start_program == '': 
        input_valid = True

    else:
        print(f'\n{RED}[PROGRAM] > {END}Invalid input. Please give a numerical value.')



# make a list containing the temperatures

target_temperatures = []

for i in range(ramp_duration):

    target_temperatures.append(round(init_temperature + ramp * i, 5))

print(f'\n{RED}[PROGRAM] > {END}The target temperatures are expected to be:', target_temperatures, f'.\nThe program will attempt to meet the temperatures over the course of{YELLOW}', ramp_duration,f' seconds{END}.')

# GRAPHING STUFF

# target temperature over time already given by the above

target_time = []

for t in target_temperatures:

    target_time.append((t - target_temperatures[0]) / ramp) # subtract from target_temperatures[0] to get 0 seconds at the initial temperature
    #target_time.append(abs(t * 1/ramp))

#print('target time', target_time)

temperature_axes = []

time_axes = []


with BK1902B(power_supply_port) as psu:
    print(f'\n{YELLOW}[TEMPERATURE RAMP - INITIALIZING] > {END}Resetting power supply output to obtain initial temperature (',init_temperature,' C)')
    psu.disable_output()
    psu.set_current(10) # to prevent short circuit, current must be high to prevent power supply from going into C.C mode instead of C.V.
    psu.set_voltage(0)
    time.sleep(5)
    psu.enable_output()

    def bk1902b(set_voltage, power_supply_port):

        #with BK1902B(power_supply_port) as psu:
            #print("PID MV Executed! (Power supply has received the PID output and will attempt to proceed)")

        psu.set_voltage(set_voltage)
        output = psu.get_display()
            #mode = "CV" if output[2] else "CC"


        return output


    t_end = time.time() + 10 # 30 second

    while time.time() < t_end:

        # get thermocouple reading

        current_temperature = daq.main()

        # calculate a set voltage

        if current_temperature < init_temperature + boundary:

            psu.disable_output()

            print(f'{YELLOW}[TEMPERATURE RAMP - INITIALIZING] > {END}\nCurrent Temperature is:{YELLOW}', current_temperature, f' C{END}.\nTarget Temperature is:{YELLOW}', init_temperature,f' C{END}.')

            print('Power Supply Disabled')

        else:

            psu.enable_output()

            set_voltage = pid.PID(init_temperature, current_temperature) # MV = manipulated variable; ie the variable we control to influence temperature... output voltage!

            print(f'{YELLOW}[TEMPERATURE RAMP - INITIALIZING] > {END}\nCurrent Temperature is:{YELLOW}', current_temperature, f' C{END}.\nTarget Temperature is:{YELLOW}', init_temperature,f' C{END}.')#\n The attempted voltage set will be:{YELLOW}', set_voltage,f' V{END}.')

            if set_voltage > maximum_voltage:

                print(f'{RED}[PROGRAM] > {END}The attempted voltage (',set_voltage,' V) to be set exceeds the maximum voltage (', maximum_voltage,' V) defined in the code.')
                
                set_voltage = maximum_voltage # ensures set voltage does not go over

            # attempt to apply the set voltage

            #bk1902b(set_voltage, power_supply_port)
            #bk.main(set_voltage, power_supply_port)

            voltage_output = bk1902b(set_voltage, power_supply_port)

            print(f'The power supply has a voltage output of:{YELLOW}', voltage_output[0],f' V{END}.')

    print(f'{YELLOW}[TEMPERATURE RAMP - INITIALIZING] > {END}Bootup time deviation: ', time.time() - t_end, ' seconds.')



    
# WAIT FOR USER TO BEGIN THE RAMP!!!

    begin_ramp = False

    def get_input():
        global begin_ramp
        keystrk=input(f"{RED}[PROGRAM] > {END}Please press {YELLOW}[ENTER]{END} when you have started recording using the Toupview software on the other laptop.")
        begin_ramp = True
        print('Beginning Temperature Ramp...')

    n = threading.Thread(target=get_input)
    n.start()

    while begin_ramp == False:



        # get thermocouple reading

        current_temperature = daq.main()

        # calculate a set voltage

        if current_temperature < init_temperature + boundary:

            psu.disable_output()

        else:

            psu.enable_output()

            set_voltage = pid.PID(init_temperature, current_temperature) # MV = manipulated variable; ie the variable we control to influence temperature... output voltage!

            if set_voltage > maximum_voltage:
                
                set_voltage = maximum_voltage # ensures set voltage does not go over

            voltage_output = bk1902b(set_voltage, power_supply_port)




    # TEMPERATURE RAMP PROGRAM

    start_time = time.time() # keep track of time during ramp program

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

            print(f'{GREEN}[TEMPERATURE RAMP - RUNNING] > {END}\nCurrent Temperature is:{YELLOW}', current_temperature, f' C{END}.\nTarget Temperature is:{YELLOW}', t,f' C{END}.')

            if current_temperature > t:
                
                psu.enable_output()
                psu.set_voltage(maximum_voltage)
                #output = psu.get_display()


            else:

                psu.disable_output()



            '''
            psu.enable_output()

            set_voltage = pid.PID(t, current_temperature) # MV = manipulated variable; ie the variable we control to influence temperature... output voltage!

            print(f'{GREEN}[TEMPERATURE RAMP - RUNNING] > {END}\nCurrent Temperature is:{YELLOW}', current_temperature, f' C{END}.\nTarget Temperature is:{YELLOW}', t,f' C{END}.\nThe attempted voltage set will be:{YELLOW}', set_voltage,f' V{END}.')

            if set_voltage > maximum_voltage:

                print(f'{RED}[PROGRAM] > {END}The attempted voltage (',set_voltage,' V) to be set exceeds the maximum voltage (', maximum_voltage,' V) defined in the code.')
                
                set_voltage = maximum_voltage # ensures set voltage does not go over
            
            

            if current_temperature < t + boundary:
                
                psu.disable_output()

                print('Power Supply Disabled')

            
            
            else:
                voltage_output = bk1902b(set_voltage, power_supply_port)

                print(f'The power supply has a voltage output of:{YELLOW}', voltage_output[0],f' V{END}.')

            '''

            tf = time.time()

            x = tf - t0 # note to coder: the entire processes above (3 functions) takes ~ 0.8 ms to execute... so the 1-x below will be about ~ 0.2ms to compensate to 1 second

            print('Time of 1 cycle:', x)

            try:
                #print(1/control_per_second - x)
                time.sleep(1/control_per_second - x) # sleep for the remaining time after considering the time taken to s
                time_axes.append(tf - start_time) # attaches the time spent running this code.

            except:
                print(f'{RED}ERROR!! The program is unable to alter the voltage each second to influence a change in temperature per second... This may be due to slow processing speed, either from a slow computer, power supply, or thermocouple. A possible solution is to either direct the processing power to the computer and instruments (close background processes), or to alter the code so temperature changes every >1 second... (Do this by altering the time.sleep() function above the line where this print statement lies.){END}')
                close = input(f'\nPress any key to reset the power supply output back to the initial temperature output.')
                break_loop = True
                break
        
        if break_loop == True:
            break
        
        


        

    end_time = time.time()
    elapsed_time = round(end_time - start_time, 2)
    print(f'\n\n{RED}[PROGRAM] > {END}The ramp program took: {YELLOW}', elapsed_time, f'{END} seconds to complete, in contrast to the expected runtime of: ', ramp_duration, ' seconds.\n(Absolute deviation = ', abs(elapsed_time - ramp_duration),' seconds)')

    # reset to original temp quickly program

    print(f'\n{PURPLE}[TEMPERATURE RAMP - TERMINATING] > {END}Ramp program has reached the final temperature (', final_temperature,' C).\nResetting power supply output to 0 V')

    psu.disable_output()


    fig = plt.figure()
    ax1 = fig.add_subplot()
    ax1.plot(target_time, target_temperatures, marker = 'd', label='Target Ramp')
    ax1.plot(time_axes, temperature_axes, marker="d", label='Actual Ramp')
    
    Kp, Ki, Kd = pid.return_PID_values()
    property_str = '(_bound_Vmax_'  + str(boundary) + '_' + str(maximum_voltage) + '_@10ohmresistor)'    
    ax1.set_title('VODCA & TONIC Temperature vs Time')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Temperature (C)')
    ax1.legend(loc='upper right')
    ax1.grid()


    os.environ["USERPROFILE"]

    save_path = os.path.join(os.environ["USERPROFILE"], "Desktop")

    timestr = time.strftime("%Y%m%d_%H%M%S")

    plt.savefig(save_path + '/TONIC/' + timestr + 'PWM' + property_str + '_Ramp_Graph.png') # MUST be above the plt show line.

    plt.show()


    # save raw data as csv

    d = {'Time (s)': time_axes, 'Temperature (C)': temperature_axes, 'Temperature Ramp (C/s)': ramp, 'Starting Target Temperature': init_temperature, 'Final Target Temperature': final_temperature}

    export_temperature_data = pd.DataFrame(d)

    export_temperature_data.to_csv(save_path + '/TONIC/' + timestr + '_Ramp_Graph.csv') # MUST be above the plt show line



    '''
    t_end = time.time() + 40 # 40 second

    while time.time() < t_end:

        # get thermocouple reading

        current_temperature = daq.main()

        # calculate a set voltage

        if current_temperature < init_temperature + boundary:
            
            psu.disable_output()

            print(f'{PURPLE}[TEMPERATURE RAMP - INITIALIZING] > {END}\nCurrent Temperature is:{YELLOW}', current_temperature, f' C{END}.\nTarget Temperature is:{YELLOW}', init_temperature,f' C{END}.')

            print('Power Supply Disabled')


        else:

            psu.enable_output()

            set_voltage = pid.PID(init_temperature, current_temperature) # MV = manipulated variable; ie the variable we control to influence temperature... output voltage!

            print(f'{PURPLE}[TEMPERATURE RAMP - TERMINATING] > {END}\nCurrent Temperature is:{YELLOW}', current_temperature, f' C{END}.\nTarget Temperature is:{YELLOW}', init_temperature,f' C{END}.\n The attempted voltage set will be:{YELLOW}', set_voltage,f' V{END}.')

            if set_voltage > maximum_voltage:

                print(f'{PURPLE}[PROGRAM] > {END}The attempted voltage (',set_voltage,' V) to be set exceeds the maximum voltage (', maximum_voltage,' V) defined in the code.')
                
                set_voltage = maximum_voltage # ensures set voltage does not go over

            # attempt to apply the set voltage

            voltage_output = bk1902b(set_voltage, power_supply_port)

            print(f'The power supply has a voltage output of:{YELLOW}', voltage_output[0],f' V{END}.')

    print(f'\n{PURPLE}[TEMPERATURE RAMP - TERMINATING] > {END}Shutdown time deviation: ', time.time() - t_end, ' seconds.')
    '''


    t_end = time.time() + 30 # 30 second

    while time.time() < t_end:
        time.sleep(1)

        current_temperature = daq.main()

        print(f'\n{PURPLE}[TEMPERATURE RAMP - TERMINATING] > {END}Turning off power supply... Current temperature is: (',current_temperature,f' C)')

print(f'\n{RED}[PROGRAM] > {END}The program has concluded!')