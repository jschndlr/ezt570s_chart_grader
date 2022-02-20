from csv import DictReader
import datetime as dt
from statistics import pstdev

fileundertest = 'test.csv'
time_format = '%H:%M:%S'
workingfile = open(fileundertest)
reader = DictReader(workingfile)
isFirstRun = True
isCooling = False
isHeating = False
errorList = []

def report_transition(starttime, row):
    start = dt.datetime.strptime(starttime, time_format)
    end = dt.datetime.strptime(row['Time'], time_format)
    et = end - start
    start_format = round(et.seconds / 60, 1)
    print("From {} to {} in {} minutes...".format(starttemp, target, start_format))

def report_control(list, setpoint):
    print("Control evaluation at {} : low: {} high: {} stdDev: {}".format(setpoint, min(list),max(list), round(pstdev(list),2)))

for row in reader:
    #initialize previousSP with first SP found
    if(isFirstRun):
        previousSP = float(row['TEMPERATURE SP'])
        isFirstRun = False
    else:
        #start tracking a transition when current SP has changed from previousSP
        #If setpoint has changed
        if(float(row['TEMPERATURE SP']) != previousSP):
            report_control(errorList, previousSP)
            errorList = []
            #set transition start temp to previous setpoint
            starttemp = previousSP
            #set transition target to new setpoint
            target = float(row['TEMPERATURE SP'])
            #set transition start time
            starttime = row['Time']
            #print("Tracking transition from {} to {} started at {}".format(starttemp, target, starttime))
            #if new SP is lower than old, set transition type to cooling and vice versa
            isCooling = ( previousSP > target)
            isHeating = (previousSP < target)
            #set previous to existing SP prior to next check
            previousSP = float(row['TEMPERATURE SP'])
        #if SP has not changed, check to see if the target has been achieved and report the transition time
        else:
            if(isCooling):
                if(float(row['TEMPERATURE PV']) <= float(target)):
                    #print("target achieved @ ", row['Time'])
                    isCooling = False
                    report_transition(starttime, row)
            elif(isHeating): 
                if(float(row['TEMPERATURE PV']) >= float(target)):
                    #print("target achieved @ ", row['Time'])
                    isHeating = False
                    report_transition(starttime, row)
            else:
                #If its not heating or cooling and the SP didnt change then the process must be in control
                #calculate the error between SP and PV, add it to a list to calculate min/max/stddev, once the SP changes again, dump the stats to print and erase
                pv = round(float(row['TEMPERATURE PV']),1)
                sp = round(float(row['TEMPERATURE SP']),1)
                error = round(pv - sp, 1)
                errorList.append(error)
report_control(errorList, previousSP)
print('Finished!')


