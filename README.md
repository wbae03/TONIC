# Temperature Output N' Integrative Cooling (TONIC)
This is a PID temperature controller designed for the VODCA cryo-microscope.

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
After installing the packages, ensure the scripts can communicate with the power supply and the thermocouple. Plug-in the instruments into the computer before finding their respective ports.
1) Input the power supply port name in line 59 of the PID_main.py script. The port name can be found in Device Manager after installing the appropriate software driver for the power supply.

    ![image](https://github.com/user-attachments/assets/00bb2309-d767-44ff-80fb-f72eba4aea22)

    ![Screenshot 2024-10-25 165303](https://github.com/user-attachments/assets/7ddb22ca-6eec-42b5-a592-70b3605942ea)

3) Input the National Instrument (NI) thermocouple port name in line 9 of the Ni_DAQ_mx.py script. The port name can be found in the NIMAX program that comes installed with the appropriate software drivers for NI devices.

    ![image](https://github.com/user-attachments/assets/900fc31a-8355-45f6-b0b5-bf8ab1caddaf)

    ![Screenshot 2024-10-25 165051](https://github.com/user-attachments/assets/3066a2d0-4dc1-4e8d-8d8d-14fcae66aa6a)

Running the PID_main.py script should prompt with instructions on program usage, if everything has been set up correctly.

