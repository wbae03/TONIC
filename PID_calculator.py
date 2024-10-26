#PID

# Import packages
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import numpy as np
import matplotlib.pyplot as plt
import time

# Global variables to store history of objects during calculations
integral = 0

time_prev = 0 #-1e-6

e_prev = 0

Kp = 2.65

Ki = 0.000000000

Kd = 0

first_pass = True

# PID calculates value of manipulated variable (MV) based on measured value and setpoint value
# Note: The measurement is the same as the 'process value' aka the current measurement.

def set_PID(P, I, D):

    global Kp, Ki, Kd

    Kp = P
    
    Ki = I

    Kd = D

    return

def reset_integral():

    global first_pass

    first_pass = True

def PID(setpoint, measurement):

    global Kp, Ki, Kd, first_pass

    global current_time, integral, time_prev, e_prev
    
    current_time = time.time()

    # Value of offset - when the error is equal zero
    offset = 0

    # PID calculations
    e = setpoint - measurement

    P = Kp*e

    integral = integral + Ki*e*(current_time - time_prev)

    # Anti-windup mechanism for integral, to prevent integral values from going crazy extreme. Added with ChatGPT's suggestion.
    # The integral term is responsible for eliminating the steady-state error by accumulating the error over time. 
    # However, if the system is unable to correct the error due to actuator limitations (e.g., the cooling power can only be increased or decreased up to a certain limit), 
    # the integral term can keep increasing (or decreasing) without bound. This situation is known as integral windup. When the actuator eventually becomes unsaturated, 
    # the large integral term can cause significant overshoot or oscillations.
    integral = max(min(integral, 0), -50) # chat gpt added this... 

    time_difference = current_time - time_prev

    if time_difference == 0:

        # To prevent division by zero, use a very small number instead.
        time_difference = 1e-6

    D = Kd*(e - e_prev)/time_difference
    
    # calculate manipulated variable - MV
    MV = offset + P + integral + D

    # Update stored data for next iteration
    if first_pass == True:

        integral = 0

        first_pass = False

    e_prev = e

    time_prev = current_time

    #Because the power supply used has a minimum voltage of ~ 1.1V
    MV = -MV + 1.1

    return MV, P, integral, D 

def return_PID_values():

    return Kp, Ki, Kd