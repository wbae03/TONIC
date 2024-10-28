# Temperature Output N' Integrative Cooling (TONIC)
This is a PID temperature controller designed for the VODCA cryo-microscope, in conjunction with the BK Precision Model 1902B DC Power Supply and the NI USB-TC01 Temperature Input Device.

The Vienna Optical Droplet Crystallization Analyzer (VODCA) is a cryo-microscope with a broad range of applications, ranging from high-speed analysis of interfacial freezing to observing freezing processes on the order of 5 um droplets. The Temperature Output N’ Integrative Cooling (TONIC) program mediates cross-talk between the power supply, the thermocouple, and the Peltier element of the VODCA setup. It uses a Proportional-Integral-Derivative (PID) controller algorithm to influence the change in the current temperature readings (from the thermocouple) to better match the target temperature, by altering the voltage output of the power supply. For documentation on VODCA-TONIC, visit https://docs.google.com/document/d/1b3AB6vaoNrQW7lSJdcsT5cyGzrHcWwvLPJI8qmbZbpc/edit?usp=sharing.

## Installation
Provided you have a code editor such as Visual Studio Code on Win 8/10:
Install required packages using pip on the console:

```
example of installation with pip:

pip install [] 
$ python -m pip install []

Required Packages:

pip install numpy
pip install matplotlib
pip install colorama
pip install pandas
pip install bk_precision_1900
pip install nidaqmx
pip install scipy
```
After installing the packages, ensure the scripts can communicate with the power supply and the thermocouple. Plug-in the instruments into the computer before finding their respective ports. To view the port names, the appropriate software drivers must be installed for the BK Precision Model 1902B DC Power Supply and the NI USB-TC01 Temperature Input Device. Details may be found in the document link above.

1) Input the power supply port name in line 59 of the PID_main.py script. The port name can be found in Device Manager after installing the appropriate software driver for the power supply.

    ![image](https://github.com/user-attachments/assets/00bb2309-d767-44ff-80fb-f72eba4aea22)

    ![image](https://github.com/user-attachments/assets/9cf5e231-974f-47e4-880a-5f05a20ef2ea)

3) Input the National Instrument (NI) thermocouple port name in line 9 of the Ni_DAQ_mx.py script. The port name can be found in the NIMAX program that comes installed with the appropriate software drivers for NI devices.

    ![image](https://github.com/user-attachments/assets/900fc31a-8355-45f6-b0b5-bf8ab1caddaf)

    ![image](https://github.com/user-attachments/assets/b28e8e08-306c-4775-b1dd-c5730d415af7)

# Running
Running the PID_main.py script should prompt with instructions on program usage, if everything has been set up correctly.
- Instructions include the input of a temperature ramp, starting temperature and ending temperature.

While the scripts run, a live temperature-time plot will be shown.
The program will attempt to reach equilibrium with the initial temperature. When the user feels confident that the starting temperature is stable/achieved, they may tell the script to begin the ramp.
This start the temperature ramp and temperature-time data collection.

# Data Save
In the current version, TONIC **MUST** run to completion (ie. reach the final temperature) for the data to be saved as an Excel spreadsheet. I had trouble implementing a function to listen for a 'cancel-experiment' event. I believe parallel processing may be the way to achieve this, but I am not sure.
