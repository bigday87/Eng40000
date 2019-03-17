#!/usr/bin/python
import argparse
import time
import os
import datetime
import sys
from influxdb import InfluxDBClient
import serial
ser = serial.Serial('/dev/ttyAMA0', 38400)


import RPi.GPIO as GPIO


LedPin = 38    # pin11

Settemp = 21

#LowTemp = 21 # turn on temp
#HighTemp= 25 # turn off temp
#from sense_hat import SenseHat

power1 = 0.0
power2 = 0.0
power3 = 0.0
power4 = 0.0
temp1 = 0.0
temp2 = 0.0
temp3 = 0.0
temp4 = 0.0


#sense=SenseHat()
 
# Set required InfluxDB parameters.
# (this could be added to the program args instead of beeing hard coded...)
host = "localhost" #Could also set local ip address
port = 8086
user = "root"
password = "root"
 
# Sample period (s).
# How frequently we will write sensor data from SenseHat to the database.
sampling_period = 10

def setup():
    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
    GPIO.setup(LedPin, GPIO.OUT)   # Set LedPin's mode is output
    GPIO.output(LedPin, GPIO.HIGH) # Set LedPin high(+3.3V) to turn on led
    
    #response = ser.readline()
  
def destroy():
    GPIO.output(LedPin, GPIO.LOW)   # led off
    GPIO.cleanup()     
  
def get_args():
    '''This function parses and returns arguments passed in'''
    # Assign description to the help doc
    parser = argparse.ArgumentParser(description='Program writes measurements data from SenseHat to specified influx db.')
    # Add arguments
    parser.add_argument(
        '-db','--database', type=str, help='Database name', required=True)
    parser.add_argument(
        '-sn','--session', type=str, help='Session', required=True)
    now = datetime.datetime.now()
    parser.add_argument(
        '-rn','--run', type=str, help='Run number', required=False,default=now.strftime("%Y%m%d%H%M"))
    
    # Array of all arguments passed to script
    args=parser.parse_args()
    # Assign args to variables
    dbname=args.database
    runNo=args.run
    session=args.session
    return dbname, session,runNo

def testcase1():
    power1 = 0
    power2 = 0
    power3 = 0
    power4 = 0
    temp1 = 0
    temp2 = 0
    temp3 = 0
    temp4 = 0
    

    
def get_data_points():
    # Get the three measurement values from the SenseHat sensors
    
    # temperature = os.popen("vcgencmd measure_temp").readline()
    response = ser.readline()
    z = response.split(",")
    timestamp=datetime.datetime.utcnow().isoformat()
    try:
        power1 = float(z[0])
        power2 = float(z[1])
        power3 = float(z[2])
        power4 = float(z[3])
        temp1 = float(z[4])
        temp2 = float(z[5])
        temp3 = float(z[6])
        temp4 = float(z[7][:-2])
        if (Settemp - temp4) == 0:
            coeff1 = 0
        else:
            coeff1 = power1/(Settemp-temp4)

    #pressure = sense.get_pressure()
    #humidity = sense.get_humidity()
    # Get a local timestamp
    
    # Create Influxdb datapoints (using lineprotocol as of Influxdb >1.1)
        
    except ValueError: 
        power1 = 0.0
        power2 = 0.0
        power3 = 0.0
        power4 = 0.0
        temp1 = 0.0
        temp2 = 0.0
        temp3 = 0.0
        temp4 = 0.0
        coeff1 = 0.0
    
    
    datapoints = [
            {
                "measurement": session,
                "tags": {"runNum": runNo,
                },
                "time": timestamp,
                "fields": {
                    "power1":power1,
                    "power2":power2,
                    "power3":power3,
                    "power4":power4,
                    "temp1":temp1,
                    "temp2":temp2,
                    "temp3":temp3,
                    "temp4":temp4,
                    "coeff1":coeff1,
                    }
                }
            ]
    return datapoints

def blink():
    #response = ser.readline()
    #z = response.split(",")
    #y =  float(z[07][:-2])
    if temp4 < (Settemp-1):
        GPIO.output(LedPin, GPIO.LOW)  # led on
    elif temp4 > (Settemp+1):
        GPIO.output(LedPin, GPIO.HIGH) # led off
  

# Match return values from get_arguments()
# and assign to their respective variables
dbname, session, runNo =get_args()   
print "Session: ", session
print "Run No: ", runNo
print "DB name: ", dbname

# Initialize the Influxdb client
client = InfluxDBClient(host, port, user, password, dbname)
        
try:
     setup()
     while True:
        # Write datapoints to InfluxDB
        datapoints=get_data_points()
        bResult=client.write_points(datapoints)
        print("Write points {0} Bresult:{1}".format(datapoints,bResult))
        blink()
            
        # Wait for next sample
        time.sleep(sampling_period)
        
        # Run until keyboard ctrl-c
except KeyboardInterrupt:
    destroy()
    ser.close()
    print ("Program stopped by keyboard interrupt [CTRL_C] by user. ")
