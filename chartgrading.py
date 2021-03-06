#TODO: Pre-grade data to define which events are on and off and what state the controller is in RAMPING, SOAKING, LINEAR RAMPING, ETC

from csv import DictReader, DictWriter
import datetime as dt
from statistics import pstdev

pv_name = 'HUMIDITY PV'
sp_name = 'HUMIDITY SP'
fileundertest = 'test.csv'
outputfile = 'test1.csv'
time_format = '%H:%M:%S'
fieldnames = ['Type', 'From', 'Target', 'ElapsedTime', 'ControlLow', 'ControlHigh', 'StandardDeviation']
workingfile = open(fileundertest)
recordfile = open(outputfile, 'a', newline='')
reader = DictReader(workingfile)
writer = DictWriter(recordfile, fieldnames=fieldnames)
isFirstRun = True
isCooling = False
isHeating = False
errorList = []
writer.writeheader()

def report_transition(starttime, row, setpoint, target):
    start = dt.datetime.strptime(starttime, time_format)
    end = dt.datetime.strptime(row['Time'], time_format)
    et = end - start
    start_format = round(et.seconds / 60, 1)
    print("From {} to {} in {} minutes...".format(starttemp, target, start_format))
    writer.writerow({'Type': 'Transition', 'From': setpoint, 'Target': target, 'ElapsedTime': et})

def report_control(list, setpoint):
    if(len(list) < 1):
        print("report_control method called with no control data! skipping....")
        return
    print("Control evaluation at {} : low: {} high: {} stdDev: {}".format(setpoint, min(list),max(list), round(pstdev(list),2)))
    writer.writerow({'Type': 'Control', 'From': setpoint, 'Target': setpoint, 'ElapsedTime': "0.0", 'ControlLow': min(list), 'ControlHigh': max(list), 'StandardDeviation': round(pstdev(list),2)})


for row in reader:
    #initialize previousSP with first SP found
    if(isFirstRun):
        previousSP = float(row[sp_name])
        isFirstRun = False
    else:
        #start tracking a transition when current SP has changed from previousSP
        #If setpoint has changed
        if(float(row[sp_name]) != previousSP):
            report_control(errorList, previousSP)
            errorList = []
            #set transition start temp to previous setpoint
            starttemp = previousSP
            #set transition target to new setpoint
            target = float(row[sp_name])
            #set transition start time
            starttime = row['Time']
            #print("Tracking transition from {} to {} started at {}".format(starttemp, target, starttime))
            #if new SP is lower than old, set transition type to cooling and vice versa
            isCooling = ( previousSP > target)
            isHeating = (previousSP < target)
            #set previous to existing SP prior to next check
            previousSP = float(row[sp_name])
        #if SP has not changed, check to see if the target has been achieved and report the transition time
        else:
            if(isCooling):
                if(float(row[pv_name]) <= float(target)):
                    #print("target achieved @ ", row['Time'])
                    isCooling = False
                    report_transition(starttime, row, starttemp, target)
            elif(isHeating): 
                if(float(row[pv_name]) >= float(target)):
                    #print("target achieved @ ", row['Time'])
                    isHeating = False
                    report_transition(starttime, row, starttemp, target)
            else:
                #If its not heating or cooling and the SP didnt change then the process must be in control
                #calculate the error between SP and PV, add it to a list to calculate min/max/stddev, once the SP changes again, dump the stats to print and erase
                pv = round(float(row[pv_name]),1)
                sp = round(float(row[sp_name]),1)
                error = round(pv - sp, 1)
                errorList.append(error)
report_control(errorList, previousSP)
print('Finished!')
