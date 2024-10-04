# Ni DAQ mx

import nidaqmx


#start: bool = False
#period: float = 0.1 # every 100 ms ??
#logTimeInMinutes: int = 1
#
'''
def measure_temperature(taskDev, devName):
        
        samples_per_channel = 1 # was 10

        data = ThermoTaskDev.read(samples_per_channel)
        #print(f"{data}")

        #SampleAvg = sum(data)/len(data)

        data = (sum(data) - 32) / (9/5) # convert F to C
        #print(f"{SampleAvg}")

        return data

'''
def main():

    devName = 'Dev1' # name of the device; check NI MAX program

    with nidaqmx.Task() as ThermoTaskDev:
        ThermoChannel = ThermoTaskDev.ai_channels.add_ai_thrmcpl_chan("Dev1/ai0",
                                             name_to_assign_to_channel="Thermocouple",
                                             min_val=-60.0,
                                             max_val=100.0, units=nidaqmx.constants.TemperatureUnits.DEG_F,
                                             thermocouple_type=nidaqmx.constants.ThermocoupleType.K,
                                             cjc_source=nidaqmx.constants.CJCSource.BUILT_IN)

        #data = measure_temperature(ThermoTaskDev, devName)

        samples_per_channel = 1 # was 10

        data = ThermoTaskDev.read(samples_per_channel)
        #print(f"{data}")

        #SampleAvg = sum(data)/len(data)

        data = (sum(data) - 32) / (9/5) # convert F to C
        #print(f"Temperature is currently at {data} C")

        return data

'''
loop = ''

while True:

    main()

    loop = input('')
    
'''