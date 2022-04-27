import serial
import time

ser = serial.Serial(port = '/dev/ttyUSB0', baudrate = 115200,
                    timeout = .5)

def read():
    cont = True
    while(cont):
        t=ser.readline()
        if(len(t)==0):
            cont = False
        else:
            t=t
            #print(t)
            
def WaitReady():
    cont = True
    while(cont):
        ser.write(b"?\n")
        r = ser.readline().decode('ascii')
        t = r.split("|")
        if t[0]=="<Idle":
            print("")
            return 1
        read() #ok...
        print(".", end="")

def send(gcode):
    print("sending :",gcode)
    gcode += "\n"
    ser.write(gcode.encode('ascii'))
    read()
    WaitReady()
    
time.sleep(1)
read()

