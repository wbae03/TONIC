#PID

# Proportional, Integration, Derivative Temperature Controller Practice

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import numpy as np
import matplotlib.pyplot as plt
import time


# Global variables to store history of objects during calculations

#current_time = 1 #0
integral = 0
time_prev = 0 #-1e-6
e_prev = 0

'''
def start_PID_time(duration):
    global current_time
    current_time = time.time()
    return

'''


'''
NOTE TO FUTURE SELF

FOR BK1902B CONNECTED TO THE PELTIER THROUGH A 10 OHM RESISTOR ON THE + OUTPUT HAS IDEAL SETTINGS OF:

# work on this when i get the 1 ohm resistor, this is rllyyy good!!!
Kp = 2.2
Ki = 0.00000000001
Kd = 0


i like this better ( no resistors)
Kp = 1.5
Ki = 0.000000000007
Kd = 0


boundary = 0

control_per_second = 2 # in 1 second, the program will tell the power supply to output a voltage x many times.

maximum_voltage = 6 # in volts

'''
Kp = 2.65
Ki = 0.000000000
Kd = 0
first_pass = True

# PID calculates value of manipulated variable (MV) based on measured value and setpoint value
# note: measurement = process value! aka current measurement

def set_PID(P, I, D):

    global Kp, Ki, Kd

    Kp = P
    
    Ki = I

    Kd = D

    #print('PID coefficient values set to:', Kp, Ki, Kd)

    return

def reset_integral():

    global first_pass

    first_pass = True

def PID(setpoint, measurement):

    global Kp, Ki, Kd, first_pass

    global current_time, integral, time_prev, e_prev
    
    current_time = time.time()

    # Value of offset - when the error is equal zero
    offset = 0 # was 320, useful to influence MV

    # PID calculations
    e = setpoint - measurement

    P = Kp*e

    #time_difference = current_time - time_prev

    #print('time difference', time_difference)
    integral = integral + Ki*e*(current_time - time_prev)


    # anti windup mechanism for integral
    integral = max(min(integral, 0), -50) # chat gpt added this... 
    #  integral term is responsible for eliminating the steady-state error by accumulating the error over time. However, if the system is unable to correct the error due to actuator limitations (e.g., the cooling power can only be increased or decreased up to a certain limit), the integral term can keep increasing (or decreasing) without bound. This situation is known as integral windup. When the actuator eventually becomes unsaturated, the large integral term can cause significant overshoot or oscillations.
    # Inner min Function:

    #min(integral, 10): This ensures that the value of integral does not exceed 10. If integral is greater than 10, it returns 10; otherwise, it returns the current value of integral.
    #Outer max Function:

    #max(..., -10): This ensures that the value of integral is not less than -10. If the result of the min function is less than -10, it returns -10; otherwise, it returns the result of the min function.

    time_difference = current_time - time_prev
    if time_difference == 0:
        time_difference = 1e-6 #to prevent division by zero

    D = Kd*(e - e_prev)/time_difference
    
    # calculate manipulated variable - MV
    MV = offset + P + integral + D

    # update stored data for next iteration

    if first_pass == True:

        integral = 0
        first_pass = False

    e_prev = e
    time_prev = current_time
    MV = -MV + 1.1
    return MV, P, integral, D #1.1 due to power supply having a minimum 1.1 v


def return_PID_values():

    return Kp, Ki, Kd