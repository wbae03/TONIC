# Ni DAQ mx

# Import packages
import nidaqmx

def main():

    # Name of the temperature probe port. Check NIMAX for NI instruments.
    devName = 'Dev2'

    with nidaqmx.Task() as ThermoTaskDev:
        ThermoChannel = ThermoTaskDev.ai_channels.add_ai_thrmcpl_chan("Dev2/ai0",
                                             name_to_assign_to_channel="Thermocouple",
                                             min_val=-60.0,
                                             max_val=100.0, units=nidaqmx.constants.TemperatureUnits.DEG_F,
                                             thermocouple_type=nidaqmx.constants.ThermocoupleType.K,
                                             cjc_source=nidaqmx.constants.CJCSource.BUILT_IN)

        # The amount of channels to take temperature measurements from. Default is 1. Higher channels provides more precision, but slows computing process which can cause script to fail.
        samples_per_channel = 1

        data = ThermoTaskDev.read(samples_per_channel)

        # Convert from Farenheit to Celsius
        data = (sum(data) - 32) / (9/5)

        # For diagnostics
        #print(f"Temperature is currently at {data} C")

        return data

# For diagnostics
'''
loop = ''

while True:

    main()

    loop = input('')
    
'''