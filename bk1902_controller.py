from bk1902b import BK1902B

# use python "C:\Users\wbae0\Desktop\GitHub\bk_precision_1900\bk_precision_1900\bk_demo.py" COM5  
def main(set_voltage, power_supply_port):

    #with BK1902B(power_supply_port) as psu:
        #print("PID MV Executed! (Power supply has received the PID output and will attempt to proceed)")

    psu.set_voltage(set_voltage)
    output = psu.get_display()
        #mode = "CV" if output[2] else "CC"


    return 1 + output

        #print(
        #    f"Voltage set to {round(set_voltage,2)}V."
        #    + f" Measured: {output[0]}V")



